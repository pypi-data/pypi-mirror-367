# coding: utf-8
# Standard Python libraries
from io import IOBase
from pathlib import Path
from copy import deepcopy
from typing import Optional, Union
import random

import numpy as np

from yabadaba import load_query

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Calculation
from .relax_liquid import relax_liquid
from ...calculation_subset import (LammpsPotential, LammpsCommands, Units,
                                   AtommanSystemLoad, AtommanSystemManipulate)
from ...input import value

class RelaxLiquid(Calculation):
    """Class for managing dynamic relaxations"""

############################# Core properties #################################

    def __init__(self,
                 model: Union[str, Path, IOBase, DM, None]=None,
                 name: Optional[str]=None,
                 database = None,
                 params: Union[str, Path, IOBase, dict] = None,
                 **kwargs: any):
        """
        Initializes a Calculation object for a given style.

        Parameters
        ----------
        model : str, file-like object or DataModelDict, optional
            Record content in data model format to read in.  Cannot be given
            with params.
        name : str, optional
            The name to use for saving the record.  By default, this should be
            the calculation's key.
        database : yabadaba.Database, optional
            A default Database to associate with the Record, typically the
            Database that the Record was obtained from.  Can allow for Record
            methods to perform Database operations without needing to specify
            which Database to use.
        params : str, file-like object or dict, optional
            Calculation input parameters or input parameter file.  Cannot be
            given with model.
        **kwargs : any
            Any other core Calculation record attributes to set.  Cannot be
            given with model.
        """
        # Initialize subsets used by the calculation
        self.__potential = LammpsPotential(self)
        self.__commands = LammpsCommands(self)
        self.__units = Units(self)
        self.__system = AtommanSystemLoad(self)
        self.__system_mods = AtommanSystemManipulate(self)
        subsets = (self.commands, self.potential, self.system,
                   self.system_mods, self.units)

        # Initialize unique calculation attributes
        self.pressure = 0.0
        self.temperature = None
        self.temperature_melt = 3000.0
        self.randomseed = None

        self.meltsteps = 50000
        self.coolsteps = 10000
        self.equilvolumesteps = 50000
        self.equilenergysteps = 10000
        self.runsteps = 50000
        self.dumpsteps = None
        self.restartsteps = None

        self.equilvolumesamples = 300
        self.equilenergysamples = 100
        self.equilenergystyle = 'pe'

        self.rdfcutoff = None

        self.__final_dump = None
        self.__volume = None
        self.__volume_stderr = None
        self.__E_total = None
        self.__E_total_stderr = None
        self.__E_pot = None
        self.__E_pot_stderr = None
        self.__measured_temperature = None
        self.__measured_temperature_stderr = None
        self.__measured_pressure = None
        self.__measured_pressure_stderr = None
        self.__time_values = None
        self.__msd_x_values = None
        self.__msd_y_values = None
        self.__msd_z_values = None
        self.__msd_values = None
        self.__lammps_output = None

        # Define calc shortcut
        self.calc = relax_liquid

        # Call parent constructor
        super().__init__(model=model, name=name, database=database, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""
        return [
            'relax_liquid.py',
            'liquid.template'
        ]

############################## Class attributes ################################

    @property
    def commands(self) -> LammpsCommands:
        """LammpsCommands subset"""
        return self.__commands

    @property
    def potential(self) -> LammpsPotential:
        """LammpsPotential subset"""
        return self.__potential

    @property
    def units(self) -> Units:
        """Units subset"""
        return self.__units

    @property
    def system(self) -> AtommanSystemLoad:
        """AtommanSystemLoad subset"""
        return self.__system

    @property
    def system_mods(self) -> AtommanSystemManipulate:
        """AtommanSystemManipulate subset"""
        return self.__system_mods

    @property
    def pressure(self) -> float:
        """float: Target relaxation pressure"""
        return self.__pressure

    @pressure.setter
    def pressure(self, val: float):
        self.__pressure = float(val)

    @property
    def temperature(self) -> float:
        """float: Target relaxation temperature"""
        if self.__temperature is None:
            raise ValueError('temperature not set!')
        return self.__temperature

    @temperature.setter
    def temperature(self, val: Optional[float]):
        if val is None:
            self.__temperature = None
        else:
            val = float(val)
            assert val >= 0.0
            self.__temperature = val

    @property
    def rdfcutoff(self) -> float:
        """float: The cutoff distance for the RDF calculation."""
        if self.__rdfcutoff is None:
            try:
                ucell = self.system.ucell
            except:
                #raise ValueError('rdfcutoff not set and no ucell found to compute the default value')
                return None
            self.__rdfcutoff = 4 * ucell.r0()
        return self.__rdfcutoff

    @rdfcutoff.setter
    def rdfcutoff(self, val: Optional[float]):
        if val is not None:
            val = float(val)
        self.__rdfcutoff = val

    @property
    def dumpsteps(self) -> int:
        """int: How often to dump configuration during the final run."""
        if self.__dumpsteps is None:
            return self.meltsteps + self.coolsteps + self.equilvolumesteps + self.equilenergysteps + self.runsteps
        else:
            return self.__dumpsteps

    @dumpsteps.setter
    def dumpsteps(self, val: Optional[int]):
        if val is None:
            self.__dumpsteps = None
        else:
            val = int(val)
            assert val >= 0
            self.__dumpsteps = val

    @property
    def restartsteps(self) -> int:
        """int: How often to dump restart files during the final run."""
        if self.__restartsteps is None:
            return self.meltsteps + self.coolsteps + self.equilvolumesteps + self.equilenergysteps + self.runsteps
        else:
            return self.__restartsteps

    @restartsteps.setter
    def restartsteps(self, val: Optional[int]):
        if val is None:
            self.__restartsteps = None
        else:
            val = int(val)
            assert val >= 0
            self.__restartsteps = val

    @property
    def meltsteps(self) -> int:
        """int: Number of MD steps during the melting stage"""
        return self.__meltsteps

    @meltsteps.setter
    def meltsteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__meltsteps = val

    @property
    def coolsteps(self) -> int:
        """int: Number of MD steps during the cooling stage"""
        return self.__coolsteps

    @coolsteps.setter
    def coolsteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__coolsteps = val

    @property
    def equilvolumesteps(self) -> int:
        """int: Number of MD steps during the volume equilibration stage"""
        return self.__equilvolumesteps

    @equilvolumesteps.setter
    def equilvolumesteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__equilvolumesteps = val

    @property
    def equilenergysteps(self) -> int:
        """int: Number of MD steps during the energy equilibration stage"""
        return self.__equilenergysteps

    @equilenergysteps.setter
    def equilenergysteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__equilenergysteps = val

    @property
    def runsteps(self) -> int:
        """int: Number of MD steps during the nve analysis stage"""
        return self.__runsteps

    @runsteps.setter
    def runsteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__runsteps = val

    @property
    def equilvolumesamples(self) -> int:
        """
        int: Number of thermo samples from the volume equilibration run to
        use for averaging volume
        """
        return self.__equilvolumesamples

    @equilvolumesamples.setter
    def equilvolumesamples(self, val: int):
        val = int(val)
        assert val >= 0
        self.__equilvolumesamples = val

    @property
    def equilenergysamples(self) -> int:
        """
        int: Number of thermo samples from the energy equilibration run to use
        for averaging energies
        """
        return self.__equilenergysamples

    @equilenergysamples.setter
    def equilenergysamples(self, val: int):
        val = int(val)
        assert val >= 0
        self.__equilenergysamples = val

    @property
    def equilenergystyle(self) -> str:
        """
        str: Specifies the option to use for computing the target total energy
        during the energy equilibration run
        """
        return self.__equilenergystyle

    @equilenergystyle.setter
    def equilenergystyle(self, val: str):
        assert val in ['pe', 'te']
        self.__equilenergystyle = val

    @property
    def randomseed(self) -> int:
        """int: Random number seed."""
        return self.__randomseed

    @randomseed.setter
    def randomseed(self, val: int):
        if val is None:
            val = random.randint(1, 900000000)
        else:
            val = int(val)
            assert val > 0 and val <= 900000000
        self.__randomseed = val

    @property
    def final_dump(self) -> dict:
        """dict: Info about the final dump file"""
        if self.__final_dump is None:
            raise ValueError('No results yet!')
        return self.__final_dump

    @property
    def volume(self) -> float:
        """float: Mean volume identified from the volume equilibration stage"""
        if self.__volume is None:
            raise ValueError('No results yet!')
        return self.__volume

    @property
    def volume_stderr(self) -> float:
        """float: Standard error for the mean volume value"""
        if self.__volume_stderr is None:
            raise ValueError('No results yet!')
        return self.__volume_stderr

    @property
    def E_total(self) -> float:
        """float: Total energy per atom during the nve stage"""
        if self.__E_total is None:
            raise ValueError('No results yet!')
        return self.__E_total

    @property
    def E_total_stderr(self) -> float:
        """float: Standard error for the mean total energy during the energy equilibration stage"""
        if self.__E_total_stderr is None:
            raise ValueError('No results yet!')
        return self.__E_total_stderr

    @property
    def E_pot(self) -> float:
        """float: Mean potential energy during the energy equilibration stage"""
        if self.__E_pot is None:
            raise ValueError('No results yet!')
        return self.__E_pot

    @property
    def E_pot_stderr(self) -> float:
        """
        float: Standard error for the mean potential energy during the energy
        equilibration stage
        """
        if self.__E_pot_stderr is None:
            raise ValueError('No results yet!')
        return self.__E_pot_stderr

    @property
    def measured_pressure(self) -> float:
        """float: Mean measured pressure during the nve run"""
        if self.__measured_pressure is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure

    @property
    def measured_pressure_stderr(self) -> float:
        """float: Standard error of the measured mean pressure"""
        if self.__measured_pressure_stderr is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_stderr

    @property
    def measured_temperature(self) -> float:
        """float: Mean measured temperature during the nve run"""
        if self.__measured_temperature is None:
            raise ValueError('No results yet!')
        return self.__measured_temperature

    @property
    def measured_temperature_stderr(self) -> float:
        """float: Standard error of the mean measured temperature"""
        if self.__measured_temperature_stderr is None:
            raise ValueError('No results yet!')
        return self.__measured_temperature_stderr

    @property
    def time_values(self) -> np.ndarray:
        """numpy.array: Time values associated with the msd values"""
        if self.__time_values is None:
            raise ValueError('No results yet!')
        return self.__time_values

    @property
    def msd_x_values(self) -> np.ndarray:
        """numpy.array: Mean squared displacements along the x direction"""
        if self.__msd_x_values is None:
            raise ValueError('No results yet!')
        return self.__msd_x_values

    @property
    def msd_y_values(self) -> np.ndarray:
        """numpy.array: Mean squared displacements along the y direction"""
        if self.__msd_y_values is None:
            raise ValueError('No results yet!')
        return self.__msd_y_values

    @property
    def msd_z_values(self) -> np.ndarray:
        """numpy.array: Mean squared displacements along the z direction"""
        if self.__msd_z_values is None:
            raise ValueError('No results yet!')
        return self.__msd_z_values

    @property
    def msd_values(self) -> np.ndarray:
        """numpy.array: Total mean squared displacements"""
        if self.__msd_values is None:
            raise ValueError('No results yet!')
        return self.__msd_values

    @property
    def lammps_output(self) -> am.lammps.Log:
        """atomman.lammps.Log: The simulation output"""
        if self.__lammps_output is None:
            raise ValueError('No results! Does not get loaded from records!')
        return self.__lammps_output

    def set_values(self,
                   name: Optional[str] = None,
                   **kwargs: any):
        """
        Set calculation values directly.  Any terms not given will be set
        or reset to the calculation's default values.

        Parameters
        ----------
        name : str, optional
            The name to assign to the calculation.  By default, this is set as
            the calculation's key.
        pressure : float, optional
            The hydrostatic pressure to relax the system to.
        temperature : float
            The target temperature to relax to.
        temperature_melt : float, optional
            The elevated temperature to first use to hopefully melt the initial
            configuration.
        rdfcutoff : float, optional
            The cutoff distance to use for the RDF cutoff.
        meltsteps : int, optional
            The number of npt integration steps to perform during the melting
            stage at the melt temperature to create an amorphous liquid structure.
        coolsteps : int, optional
            The number of npt integration steps to perform during the cooling
            stage where the temperature is reduced from the melt temperature
            to the target temperature.
        equilvolumesteps : int, optional
            The number of npt integration steps to perform during the volume
            equilibration stage where the system is held at the target temperature
            and pressure to obtain an estimate for the relaxed volume.
        equilvolumesamples : int, optional
            The number of thermo samples from the end of the volume equilibration
            stage to use in computing the average volume.  Cannot be larger than
            equilvolumesteps / 100.  It is recommended to set smaller than the max
            to allow for some convergence time.
        equilenergysteps : int, optional
            The number of nvt integration steps to perform during the energy
            equilibration stage where the system is held at the target temperature
            to obtain an estimate for the total energy.
        equilenergysamples : int, optional
            The number of thermo samples from the end of the energy equilibrium
            stage to use in computing the target total energy.  Cannot be
            larger than equilenergysteps / 100.
        equilenergystyle : str, optional
            Indicates which scheme to use for computing the target total energy.
            Allowed values are 'pe' or 'te'.  For 'te', the average total energy
            from the equilenergysamples is used as the target energy.  For 'pe',
            the average potential energy plus 3/2 N kB T is used as the target
            energy.
        runsteps : int or None, optional
            The number of nve integration steps to perform on the system to
            obtain measurements of MSD and RDF of the liquid.
        dumpsteps : int or None, optional
            Dump files will be saved every this many steps during the runsteps
            simulation.
        restartsteps : int or None, optional
            Dump files will be saved every this many steps during the runsteps
            simulation.
        randomseed : int or None, optional
            Random number seed used by LAMMPS in creating velocities and with
            the Langevin thermostat.
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=name, **kwargs)

        # Set calculation-specific values
        if 'pressure' in kwargs:
            self.pressure = kwargs['pressure']
        if 'temperature' in kwargs:
            self.temperature = kwargs['temperature']
        if 'temperature_melt' in kwargs:
            self.temperature_melt = kwargs['temperature_melt']
        if 'rdfcutoff' in kwargs:
            self.rdfcutoff = kwargs['rdfcutoff']
        if 'randomseed' in kwargs:
            self.randomseed = kwargs['randomseed']
        if 'meltsteps' in kwargs:
            self.meltsteps = kwargs['meltsteps']
        if 'coolsteps' in kwargs:
            self.coolsteps = kwargs['coolsteps']
        if 'equilvolumesteps' in kwargs:
            self.equilvolumesteps = kwargs['equilvolumesteps']
        if 'equilenergysteps' in kwargs:
            self.equilenergysteps = kwargs['equilenergysteps']
        if 'thermosteps' in kwargs:
            self.thermosteps = kwargs['thermosteps']
        if 'runsteps' in kwargs:
            self.runsteps = kwargs['runsteps']
        if 'dumpsteps' in kwargs:
            self.dumpsteps = kwargs['dumpsteps']
        if 'restartsteps' in kwargs:
            self.restartsteps = kwargs['restartsteps']
        if 'equilvolumesamples' in kwargs:
            self.equilvolumesamples = kwargs['equilvolumesamples']
        if 'equilenergysamples' in kwargs:
            self.equilenergysamples = kwargs['equilenergysamples']
        if 'equilenergystyle' in kwargs:
            self.equilenergystyle = kwargs['equilenergystyle']

####################### Parameter file interactions ###########################

    def load_parameters(self,
                        params: Union[dict, str, IOBase],
                        key: Optional[str] = None):
        """
        Reads in and sets calculation parameters.

        Parameters
        ----------
        params : dict, str or file-like object
            The parameters or parameter file to read in.
        key : str, optional
            A new key value to assign to the object.  If not given, will use
            calc_key field in params if it exists, or leave the key value
            unchanged.
        """
        # Load universal content
        input_dict = super().load_parameters(params, key=key)

        # Load input/output units
        self.units.load_parameters(input_dict)

        # Change default values for subset terms
        input_dict['sizemults'] = input_dict.get('sizemults', '10 10 10')

        # Load calculation-specific strings
        self.equilenergystyle = input_dict.get('equilenergystyle', 'pe')

        # Load calculation-specific booleans

        # Load calculation-specific integers
        self.meltsteps = int(input_dict.get('meltsteps', 50000))
        self.coolsteps = int(input_dict.get('coolsteps', 10000))
        self.equilvolumesteps = int(input_dict.get('equilvolumesteps', 50000))
        self.equilvolumesamples = int(input_dict.get('equilvolumesamples', 300))
        self.equilenergysteps = int(input_dict.get('equilenergysteps', 10000))
        self.equilenergysamples = int(input_dict.get('equilenergysamples', 100))
        self.runsteps = int(input_dict.get('runsteps', 50000))
        self.dumpsteps = input_dict.get('dumpsteps', None)
        self.restartsteps = input_dict.get('restartsteps', None)
        self.randomseed = input_dict.get('randomseed', None)

        # Load calculation-specific unitless floats
        self.temperature = float(input_dict['temperature'])
        self.temperature_melt = float(input_dict.get('temperature_melt', 3000.0))

        # Load calculation-specific floats with units
        self.pressure = value(input_dict, 'pressure',
                              default_unit=self.units.pressure_unit,
                              default_term='0.0 GPa')
        if 'rdfcutoff' in input_dict:
            self.rdfcutoff = value(input_dict, 'rdfcutoff',
                              default_unit=self.units.length_unit)
        else:
            self.rdfcutoff = None

        # Load LAMMPS commands
        self.commands.load_parameters(input_dict)

        # Load LAMMPS potential
        self.potential.load_parameters(input_dict)

        # Load initial system
        self.system.load_parameters(input_dict)

        # Manipulate system
        self.system_mods.load_parameters(input_dict)

    def master_prepare_inputs(self,
                              branch: str = 'main',
                              **kwargs: any) -> dict:
        """
        Utility method that build input parameters for prepare according to the
        workflows used by the NIST Interatomic Potentials Repository.  In other
        words, transforms inputs from master_prepare into inputs for prepare.

        Parameters
        ----------
        branch : str, optional
            Indicates the workflow branch to prepare calculations for.  Default
            value is 'main'.
        **kwargs : any
            Any parameter modifications to make to the standard workflow
            prepare scripts.

        Returns
        -------
        params : dict
            The full set of prepare parameters based on the workflow branch
        """
        # Initialize params and copy over branch
        params = {}
        params['branch'] = branch

        # main branch
        if branch == 'main':

            # Check for required kwargs
            assert 'lammps_command' in kwargs

            # Set default workflow settings
            params['buildcombos'] = 'atomicparent load_file parent'
            params['parent_record'] = 'relaxed_crystal'
            params['parent_method'] = 'dynamic'
            params['parent_standing'] = 'good'
            params['parent_family'] = 'A1--Cu--fcc'
            params['sizemults'] = '10 10 10'
            params['atomshift'] = '0.05 0.05 0.05'
            params['temperature'] = [str(i) for i in np.arange(50, 3050, 50)]

            # Copy kwargs to params
            for key in kwargs:

                # Rename potential-related terms for buildcombos
                if key[:10] == 'potential_':
                    params[f'parent_{key}'] = kwargs[key]

                # Copy/overwrite other terms
                else:
                    params[key] = kwargs[key]

        elif branch == 'melt':

            # Check for required kwargs
            assert 'lammps_command' in kwargs
            assert 'temperature_melt' not in kwargs, 'temperature_melt == temperature for this branch'

            # Set default workflow settings
            params['buildcombos'] = 'atomicparent load_file parent'
            params['parent_record'] = 'relaxed_crystal'
            params['parent_method'] = 'dynamic'
            params['parent_standing'] = 'good'
            params['parent_family'] = 'A1--Cu--fcc'
            params['sizemults'] = '10 10 10'
            params['atomshift'] = '0.05 0.05 0.05'
            params['runsteps'] = '1000000'
            params['temperature'] = '3000'

            # Copy kwargs to params
            for key in kwargs:

                # Rename potential-related terms for buildcombos
                if key[:10] == 'potential_':
                    params[f'parent_{key}'] = kwargs[key]

                # Copy/overwrite other terms
                else:
                    params[key] = kwargs[key]

            # Set temperature_melt to temperature
            params['temperature_melt'] = params['temperature']

        elif branch == 'change_temp':

            # Check for required kwargs
            assert 'lammps_command' in kwargs
            assert 'temperature' in kwargs, 'temperature must be specified for this branch'
            assert 'temperature_melt' in kwargs, 'temperature_melt (previous temperature) must be specified for this branch'

            # Set default workflow settings
            params['buildcombos'] = 'atomicarchive load_file archive'
            params['archive_record'] = 'calculation_relax_liquid'
            params['archive_load_key'] = 'final-system'
            params['archive_status'] = 'finished'
            params['archive_temperature'] = kwargs['temperature_melt']
            params['sizemults'] = '1 1 1'
            params['atomshift'] = '0.0 0.0 0.0'
            params['runsteps'] = '1000000'
            params['temperature'] = kwargs['temperature']
            params['temperature_melt'] = kwargs['temperature_melt']
            params['meltsteps'] = '0'

            # Copy kwargs to params
            for key in kwargs:

                # Rename potential-related terms for buildcombos
                if key[:10] == 'potential_':
                    params[f'archive_{key}'] = kwargs[key]

                # Copy/overwrite other terms
                else:
                    params[key] = kwargs[key]

        else:
            raise ValueError(f'Unknown branch {branch}')

        return params

    @property
    def templatekeys(self) -> dict:
        """dict : The calculation-specific input keys and their descriptions."""

        return {
            'temperature': ' '.join([
                "The target temperature to relax to.  Required."]),
            'pressure': ' '.join([
                "The target hydrostatic pressure to relax to. Default value is 0.0 GPa"]),
            'temperature_melt': ' '.join([
                "The elevated temperature to first use to hopefully melt the initial",
                "configuration."]),
            'rdfcutoff': ' '.join([
                "The cutoff distance to use for the RDF cutoff.  If not given then",
                "will use 4 * r0, where r0 is the shortest atomic distance found in",
                "the given system configuration."]),
            'meltsteps': ' '.join([
                "The number of npt integration steps to perform during the melting",
                "stage at the melt temperature to create an amorphous liquid structure.",
                "Default value is 50000."]),
            'coolsteps': ' '.join([
                "The number of npt integration steps to perform during the cooling",
                "stage where the temperature is reduced from the melt temperature",
                "to the target temperature.  Default value is 10000."]),
            'equilvolumesteps': ' '.join([
                "The number of npt integration steps to perform during the volume",
                "equilibration stage where the system is held at the target temperature",
                "and pressure to obtain an estimate for the relaxed volume.  Default",
                "value is 50000."]),
            'equilvolumesamples': ' '.join([
                "The number of thermo samples from the end of the volume equilibration",
                "stage to use in computing the average volume.  Cannot be larger than",
                "equilvolumesteps / 100.  It is recommended to set smaller than the max",
                "to allow for some convergence time.  Default value is 300. "]),
            'equilenergysteps': ' '.join([
                "The number of nvt integration steps to perform during the energy",
                "equilibration stage where the system is held at the target temperature",
                "to obtain an estimate for the total energy.  Default value is 10000."]),
            'equilenergysamples': ' '.join([
                "The number of thermo samples from the end of the energy equilibrium",
                "stage to use in computing the target total energy.  Cannot be",
                "larger than equilenergysteps / 100.  Default value is 100."]),
            'equilenergystyle': ' '.join([
                "Indicates which scheme to use for computing the target total energy.",
                "Allowed values are 'pe' or 'te'.  For 'te', the average total energy",
                "from the equilenergysamples is used as the target energy.  For 'pe',",
                "the average potential energy plus 3/2 N kB T is used as the target",
                "energy.  Default value is 'pe'."]),
            'runsteps': ' '.join([
                "The number of nve integration steps to perform on the system to",
                "obtain measurements of MSD and RDF of the liquid. Default value is",
                "50000."]),
            'dumpsteps': ' '.join([
                "Dump files will be saved every this many steps during the runsteps",
                "simulation. Default is None, which sets dumpsteps equal to the sum",
                "of all other steps values so only the final configuration is saved."]),
            'restartsteps': ' '.join([
                "Restart files will be saved every this many steps. Default is None",
                "which sets restartsteps equal to the sum",
                "of all other steps values so only the final configuration is saved."]),
            'randomseed': ' '.join([
                "Random number seed used by LAMMPS in creating velocities and with",
                "the Langevin thermostat.  Default is None which will select a",
                "random int between 1 and 900000000."]),
        }

    @property
    def singularkeys(self) -> list:
        """list: Calculation keys that can have single values during prepare."""

        keys = (
            # Universal keys
            super().singularkeys

            # Subset keys
            + self.commands.keyset
            + self.units.keyset

            # Calculation-specific keys
        )
        return keys

    @property
    def multikeys(self) -> list:
        """list: Calculation key sets that can have multiple values during prepare."""

        keys = (
            # Universal multikeys
            super().multikeys +

            # Combination of potential and system keys
            [
                self.potential.keyset +
                self.system.keyset +
                [
                    "rdfcutoff"
                ]
            ] +

            # System mods keys
            [
                self.system_mods.keyset
            ] +

            # Pressure
            [
                [
                    'pressure',
                ]
            ] +

            # Temperature
            [
                [
                    'temperature',
                ]
            ] +

            # Run parameters
            [
                [
                    'temperature_melt',
                    'meltsteps',
                    'coolsteps',
                    'equilvolumesteps',
                    'equilvolumesamples',
                    'equilenergysteps',
                    'equilenergysamples',
                    'equilenergystyle',
                    'runsteps',
                    'dumpsteps',
                    'restartsteps',
                    'randomseed',
                ]
            ]
        )
        return keys

########################### Data model interactions ###########################

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'calculation-relax-liquid'

    def build_model(self) -> DM:
        """
        Generates and returns model content based on the values set to object.
        """
        # Build universal content
        model = super().build_model()
        calc = model[self.modelroot]

        # Build subset content
        self.commands.build_model(calc, after='atomman-version')
        self.potential.build_model(calc, after='calculation')
        self.system.build_model(calc, after='potential-LAMMPS')
        self.system_mods.build_model(calc)

        # Build calculation-specific content
        if 'calculation' not in calc:
            calc['calculation'] = DM()
        if 'run-parameter' not in calc['calculation']:
            calc['calculation']['run-parameter'] = DM()
        run_params = calc['calculation']['run-parameter']

        run_params['temperature_melt'] = self.temperature_melt
        run_params['rdfcutoff'] = self.rdfcutoff
        run_params['meltsteps'] = self.meltsteps
        run_params['coolsteps'] = self.coolsteps
        run_params['equilvolumesteps'] = self.equilvolumesteps
        run_params['equilvolumesamples'] = self.equilvolumesamples
        run_params['equilenergysteps'] = self.equilenergysteps
        run_params['equilenergysamples'] = self.equilenergysamples
        run_params['equilenergystyle'] = self.equilenergystyle
        run_params['runsteps'] = self.runsteps
        run_params['dumpsteps'] = self.dumpsteps
        run_params['randomseed'] = self.randomseed

        # Save phase-state info
        calc['phase-state'] = DM()
        calc['phase-state']['temperature'] = uc.model(self.temperature, 'K')
        calc['phase-state']['pressure'] = uc.model(self.pressure,
                                                   self.units.pressure_unit)

        # Build results
        if self.status == 'finished':

            # Save info on final configuration file
            calc['final-system'] = DM()
            calc['final-system']['artifact'] = DM()
            calc['final-system']['artifact']['file'] = self.final_dump['filename']
            calc['final-system']['artifact']['format'] = 'atom_dump'
            calc['final-system']['symbols'] = self.final_dump['symbols']

            # Save measured phase-state info
            calc['measured-phase-state'] = mps = DM()
            mps['volume'] = uc.model(self.volume, f'{self.units.length_unit}^3',
                                     self.volume_stderr)
            mps['temperature'] = uc.model(self.measured_temperature, 'K',
                                          self.measured_temperature_stderr)
            mps['pressure'] = uc.model(self.measured_pressure,
                                          self.units.pressure_unit,
                                          self.measured_pressure_stderr)

            calc['total-energy-per-atom'] = uc.model(self.E_total, self.units.energy_unit,
                                                     self.E_total_stderr)
            calc['potential-energy-per-atom'] = uc.model(self.E_pot, self.units.energy_unit,
                                                         self.E_pot_stderr)

            # Save mean squared displacements
            calc['mean-squared-displacements-relation'] = scan = DM()
            scan['t'] = uc.model(self.time_values, 'ps')
            scan['msd_x'] = uc.model(self.msd_x_values, f'{self.units.length_unit}^2')
            scan['msd_y'] = uc.model(self.msd_y_values, f'{self.units.length_unit}^2')
            scan['msd_z'] = uc.model(self.msd_z_values, f'{self.units.length_unit}^2')
            scan['msd'] = uc.model(self.msd_values, f'{self.units.length_unit}^2')

        self._set_model(model)
        return model

    def load_model(self,
                   model: Union[str, DM],
                   name: Optional[str] = None):
        """
        Loads record contents from a given model.

        Parameters
        ----------
        model : str or DataModelDict
            The model contents of the record to load.
        name : str, optional
            The name to assign to the record.  Often inferred from other
            attributes if not given.
        """
        # Load universal and subset content
        super().load_model(model, name=name)
        calc = self.model[self.modelroot]

        # Load calculation-specific content
        run_params = calc['calculation']['run-parameter']
        self.temperature_melt = run_params['temperature_melt']
        self.rdfcutoff = run_params['rdfcutoff']
        self.meltsteps = run_params['meltsteps']
        self.coolsteps = run_params['coolsteps']
        self.equilvolumesteps = run_params['equilvolumesteps']
        self.equilvolumesamples = run_params['equilvolumesamples']
        self.equilenergysteps = run_params['equilenergysteps']
        self.equilenergysamples = run_params['equilenergysamples']
        self.equilenergystyle = run_params['equilenergystyle']
        self.runsteps = run_params['runsteps']
        self.dumpsteps = run_params['dumpsteps']
        self.randomseed = run_params['randomseed']

        # Load phase-state info
        self.temperature = uc.value_unit(calc['phase-state']['temperature'])
        self.pressure = uc.value_unit(calc['phase-state']['pressure'])

        # Load results
        if self.status == 'finished':

            self.__final_dump = {
                'filename': calc['final-system']['artifact']['file'],
                'symbols': calc['final-system']['symbols']
            }

            mps = calc['measured-phase-state']
            self.__volume = uc.value_unit(mps['volume'])
            self.__volume_stderr = uc.error_unit(mps['volume'])
            self.__measured_temperature = uc.value_unit(mps['temperature'])
            self.__measured_temperature_stderr = uc.error_unit(mps['temperature'])
            self.__measured_pressure = uc.value_unit(mps['pressure'])
            self.__measured_pressure_stderr = uc.error_unit(mps['pressure'])

            self.__E_total = uc.value_unit(calc['total-energy-per-atom'])
            self.__E_total_stderr = uc.error_unit(calc['total-energy-per-atom'])
            self.__E_pot = uc.value_unit(calc['potential-energy-per-atom'])
            self.__E_pot_stderr = uc.error_unit(calc['potential-energy-per-atom'])

            scan = calc['mean-squared-displacements-relation']
            self.__time_values = uc.value_unit(scan['t'])
            self.__msd_x_values = uc.value_unit(scan['msd_x'])
            self.__msd_y_values = uc.value_unit(scan['msd_y'])
            self.__msd_z_values = uc.value_unit(scan['msd_z'])
            self.__msd_values = uc.value_unit(scan['msd'])

    @property
    def queries(self) -> dict:
        queries = deepcopy(super().queries)
        queries.update({
            'temperature': load_query(
                style='float_match',
                name='temperature',
                path=f'{self.modelroot}.phase-state.temperature.value',
                description='search by temperature in Kelvin'),
            'pressure': load_query(
                style='float_match',
                name='pressure',
                path=f'{self.modelroot}.phase-state.pressure.value',
                description='search by pressure in GPa',
                unit='GPa')
        })
        return queries

########################## Metadata interactions ##############################

    def metadata(self) -> dict:
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """
        # Call super to extract universal and subset content
        meta = super().metadata()

        # Extract calculation-specific content
        meta['temperature'] = self.temperature
        meta['pressure'] = self.pressure
        meta['rdfcutoff'] = self.rdfcutoff

        # Extract results
        if self.status == 'finished':
            meta['volume'] = self.volume
            meta['volume_stderr'] = self.volume_stderr
            meta['measured_temperature'] = self.measured_temperature
            meta['measured_temperature_stderr'] = self.measured_temperature_stderr
            meta['measured_pressure'] = self.measured_pressure
            meta['measured_pressure_stderr'] = self.measured_pressure_stderr

            meta['E_total'] = self.E_total
            meta['E_total_stderr'] = self.E_total_stderr
            meta['E_pot'] = self.E_pot
            meta['E_pot_stderr'] = self.E_pot_stderr

            meta['time_values'] = self.time_values.tolist()
            meta['msd_x_values'] = self.msd_x_values.tolist()
            meta['msd_y_values'] = self.msd_y_values.tolist()
            meta['msd_z_values'] = self.msd_z_values.tolist()
            meta['msd_values'] = self.msd_values.tolist()

        return meta

    @property
    def compare_terms(self) -> list:
        """list: The terms to compare metadata values absolutely."""
        return [
            'script',

            'parent_key',
            'load_options',
            'symbols',

            'potential_LAMMPS_key',
            'potential_key',
        ]

    @property
    def compare_fterms(self) -> dict:
        """dict: The terms to compare metadata values using a tolerance."""
        return {
            'temperature':1e-2,
            'pressure':1e-12,
        }

########################### Calculation interactions ##########################

    def calc_inputs(self) -> dict:
        """Builds calculation inputs from the class's attributes"""

        # Initialize input_dict
        input_dict = {}

        # Add subset inputs
        for subset in self.subsets:
            subset.calc_inputs(input_dict)

        # Remove unused subset inputs
        del input_dict['transform']
        del input_dict['ucell']

        # Add calculation-specific inputs
        input_dict['pressure'] = self.pressure
        input_dict['temperature'] = self.temperature
        input_dict['temperature_melt'] = self.temperature_melt
        input_dict['rdfcutoff'] = self.rdfcutoff
        input_dict['meltsteps'] = self.meltsteps
        input_dict['coolsteps'] = self.coolsteps
        input_dict['equilvolumesteps'] = self.equilvolumesteps
        input_dict['equilvolumesamples'] = self.equilvolumesamples
        input_dict['equilenergysteps'] = self.equilenergysteps
        input_dict['equilenergysamples'] = self.equilenergysamples
        input_dict['equilenergystyle'] = self.equilenergystyle
        input_dict['runsteps'] = self.runsteps
        input_dict['dumpsteps'] = self.dumpsteps
        input_dict['restartsteps'] = self.restartsteps
        input_dict['randomseed'] = self.randomseed

        # Return input_dict
        return input_dict

    def process_results(self, results_dict: dict):
        """
        Processes calculation results and saves them to the object's results
        attributes.

        Parameters
        ----------
        results_dict: dict
            The dictionary returned by the calc() method.
        """
        self.__final_dump = {
            'filename': results_dict['dumpfile_final'],
            'symbols': results_dict['symbols_final']
        }

        self.__volume = results_dict['volume']
        self.__volume_stderr = results_dict['volume_stderr']
        self.__measured_temperature = results_dict['measured_temp']
        self.__measured_temperature_stderr = results_dict['measured_temp_stderr']
        self.__measured_pressure = results_dict['measured_press']
        self.__measured_pressure_stderr = results_dict['measured_press_stderr']

        self.__E_total = results_dict['E_total']
        self.__E_total_stderr = results_dict['E_total_stderr']
        self.__E_pot = results_dict['E_pot']
        self.__E_pot_stderr = results_dict['E_pot_stderr']

        self.__time_values = results_dict['time_values']
        self.__msd_x_values = results_dict['msd_x_values']
        self.__msd_y_values = results_dict['msd_y_values']
        self.__msd_z_values = results_dict['msd_z_values']
        self.__msd_values = results_dict['msd_values']
        self.__lammps_output = results_dict['lammps_output']
