# coding: utf-8
# Standard Python libraries
from io import IOBase
from pathlib import Path
from copy import deepcopy
from typing import Optional, Union
import random

import numpy as np
import numpy.typing as npt

from yabadaba import load_query

# https://github.com/usnistgov/atomman
import atomman.unitconvert as uc

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Calculation
from .free_energy import free_energy
from ...calculation_subset import (LammpsPotential, LammpsCommands, Units,
                                   AtommanSystemLoad, AtommanSystemManipulate)
from ...input import value
from ...tools import aslist

class FreeEnergy(Calculation):
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
        self.temperature = None
        self.spring_constants = None
        self.equilsteps = 25000
        self.switchsteps = 50000
        self.springsteps = 50000
        self.pressure = 0.0
        self.randomseed = None

        self.__volume = None
        self.__natoms = None
        self.__work_forward = None
        self.__work_reverse = None
        self.__work = None
        self.__helmholtz_reference = None
        self.__helmholtz = None
        self.__gibbs = None

        # Define calc shortcut
        self.calc = free_energy

        # Call parent constructor
        super().__init__(model=model, name=name, database=database, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""
        return [
            'free_energy.py',
            'msd.template',
            'free_energy.template'
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
    def temperature(self) -> float:
        """float: Target temperature"""
        return self.__temperature

    @temperature.setter
    def temperature(self, val: float):
        if val is not None:
            val = float(val)
            assert val >= 0.0
        self.__temperature = val

    @property
    def spring_constants(self) -> Optional[np.ndarray]:
        """numpy.ndarray or None: The Einstein spring constants for each temperature"""
        return self.__spring_constants

    @spring_constants.setter
    def spring_constants(self, val: Optional[npt.ArrayLike]):
        if val is not None:
            val = np.asarray(aslist(val))
        self.__spring_constants = val

    @property
    def equilsteps(self) -> int:
        """int: The number of ignored equilibration steps at the beginning of simulations"""
        return self.__equilsteps

    @equilsteps.setter
    def equilsteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__equilsteps = val

    @property
    def switchsteps(self) -> int:
        """int: The number of steps to perform during the two switch runs."""
        return self.__switchsteps

    @switchsteps.setter
    def switchsteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__switchsteps = val

    @property
    def springsteps(self) -> int:
        """int: The number of steps to perform to evaluate the spring constants."""
        return self.__springsteps

    @springsteps.setter
    def springsteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__springsteps = val

    @property
    def randomseed(self) -> int:
        """int: Random number seed used by LAMMPS."""
        return self.__randomseed

    @randomseed.setter
    def randomseed(self, val: Optional[int]):
        if val is None:
            val = random.randint(1, 900000000)
        else:
            val = int(val)
            assert val > 0 and val <= 900000000
        self.__randomseed = val

    @property
    def volume(self) -> float:
        """float: The total volume of the system."""
        if self.__volume is None:
            return self.system_mods.system.box.volume
        else:
            return self.__volume

    @property
    def natoms(self) -> float:
        """int: The total number of atoms in the system."""
        if self.__natoms is None:
            return self.system_mods.system.natoms
        else:
            return self.__natoms

    @property
    def work_forward(self) -> float:
        """float: The work/atom during the forward switching step."""
        if self.__work_forward is None:
            raise ValueError('No results yet!')
        return self.__work_forward

    @property
    def work_reverse(self) -> float:
        """float: The work/atom during the reverse switching step."""
        if self.__work_reverse is None:
            raise ValueError('No results yet!')
        return self.__work_reverse

    @property
    def work(self) -> float:
        """float: The reversible work/atom."""
        if self.__work is None:
            raise ValueError('No results yet!')
        return self.__work

    @property
    def helmholtz_reference(self) -> float:
        """float: The Helmholtz free energy/atom for the reference Einstein solid."""
        if self.__helmholtz_reference is None:
            raise ValueError('No results yet!')
        return self.__helmholtz_reference

    @property
    def helmholtz(self) -> float:
        """float: The Helmholtz free energy/atom."""
        if self.__helmholtz is None:
            raise ValueError('No results yet!')
        return self.__helmholtz

    @property
    def gibbs(self) -> float:
        """float: The Gibbs free energy/atom."""
        if self.__gibbs is None:
            raise ValueError('No results yet!')
        return self.__gibbs

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
        temperature : float, optional
            The temperature to run at.
        spring_constants : float, array-like object or None, optional
            The Einstein solid spring constants to assign to each atom type.  If
            None (default), then a separate simulation will estimate them using
            mean squared displacements.
        equilsteps : int, optional
            The number of equilibration timesteps at the beginning of simulations
            to ignore before evaluations.  This is used at the beginning of both
            the spring constant estimate and before each thermo switch run.
        switchsteps : int, optional
            The number of integration steps to perform during the two switch runs.
        springsteps : int, optional
            The number of integration steps to perform for the spring constants
            estimation, which is only done if spring_constants is None.
        pressure : float, optional
            A value of pressure to use for computing the Gibbs free energy from
            the Helmholtz free energy.  NOTE: this is not used to equilibrate the
            system during this calculation!
        randomseed : int, optional
            Random number seed used by LAMMPS.
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=name, **kwargs)

        # Set calculation-specific values
        if 'temperature' in kwargs:
            self.temperature = kwargs['temperature']
        if 'spring_constants' in kwargs:
            self.spring_constants = kwargs['spring_constants']
        if 'equilsteps' in kwargs:
            self.equilsteps = kwargs['equilsteps']
        if 'switchsteps' in kwargs:
            self.switchsteps = kwargs['switchsteps']
        if 'springsteps' in kwargs:
            self.springsteps = kwargs['springsteps']
        if 'pressure' in kwargs:
            self.pressure = kwargs['pressure']
        if 'randomseed' in kwargs:
            self.randomseed = kwargs['randomseed']

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

        # Load calculation-specific booleans

        # Load calculation-specific integers
        self.equilsteps = int(input_dict.get('equilsteps', 25000))
        self.switchsteps = int(input_dict.get('switchsteps', 50000))
        self.springsteps = int(input_dict.get('springsteps', 50000))
        self.randomseed = input_dict.get('randomseed', None)

        # Load calculation-specific unitless floats
        self.temperature = float(input_dict['temperature'])

        # Load calculation-specific floats with units
        self.pressure = value(input_dict, 'pressure',
                              default_unit=self.units.pressure_unit,
                              default_term='0.0 GPa')

        # Load and split spring constants - None, or float(s) with units energy/area
        spring_constants = input_dict.get('spring_constants', None)
        if spring_constants is not None:
            spring_constants = spring_constants.split()
            for i in range(len(spring_constants)-1):
                spring_constants[i] = float(spring_constants[i])
            try:
                spring_constants[-1] = float(spring_constants[-1])
                unit = f'{self.units.energy_unit}/{self.units.length_unit}^2'
            except:
                unit = spring_constants.pop(-1)
            spring_constants = uc.set_in_units(spring_constants, unit)
        self.spring_constants = spring_constants

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
            assert 'temperature' in kwargs, 'temperature must be specified for this branch'

            # Set default workflow settings
            params['buildcombos'] = 'atomicarchive load_file archive'

            params['archive_record'] = 'calculation_relax_dynamic'
            params['archive_load_key'] = 'final-system'
            params['archive_status'] = 'finished'
            params['archive_temperature'] = kwargs['temperature']
            params['sizemults'] = '1 1 1'
            params['temperature'] = kwargs['temperature']

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
                "Target temperature for the simulations.  Required."]),
            'spring_constants': ' '.join([
                "The Einstein solid spring constants (in energy/area) to assign",
                "to each atom type, given as space-delimited floats with optional",
                "units.  If not given, then a separate simulation will be",
                "performed to estimate the constants from mean squared displacements"]),
            'equilsteps': ' '.join([
                "The number of equilibration timesteps at the beginning of",
                "simulations to ignore before evaluations.  This is used at",
                "the beginning of both the spring constant estimate and before",
                "each thermo switch run.  Default value is 25000."]),
            'switchsteps': ' '.join([
                "The number of integration steps to perform during each of the two",
                "switch runs.  Default value is 50000."]),
            'springsteps': ' '.join([
                "The number of integration steps to perform for the spring",
                "constants estimation, which is only done if spring_constants are",
                "not given.  Default value is 50000."]),
            'pressure': ' '.join([
                "A value of pressure to use for computing the Gibbs free energy",
                "from the Helmholtz free energy.  NOTE: this is not used to",
                "equilibrate the system during this calculation!  Default value",
                "is 0.0."]),
            'randomseed': ' '.join([
                "An int random number seed to use for generating initial velocities.",
                "A random int will be selected if not given."]),
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
                self.system.keyset
            ] +

            # System mods keys
            [
                self.system_mods.keyset
            ] +

            # Run parameters
            [
                [
                    'equilsteps',
                    'switchsteps',
                    'springsteps',
                    'randomseed',
                    'temperature',
                    'pressure',
                    'spring_constants',
                ]
            ]
        )
        return keys

########################### Data model interactions ###########################

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'calculation-free-energy'

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

        run_params['equilsteps'] = self.equilsteps
        run_params['switchsteps'] = self.switchsteps
        run_params['springsteps'] = self.springsteps
        run_params['randomseed'] = self.randomseed

        # Save phase-state info
        calc['phase-state'] = DM()
        calc['phase-state']['temperature'] = uc.model(self.temperature, 'K')
        calc['phase-state']['pressure'] = uc.model(self.pressure,
                                                   self.units.pressure_unit)

        # Build results
        if self.status == 'finished':

            # Save the total system volume and number of atoms
            calc['volume'] = uc.model(self.volume,
                                      f'{self.units.length_unit}^3')
            calc['natoms'] = self.natoms

            # Save the spring constants used
            calc['spring-constants'] = uc.model(self.spring_constants,
                                                f'{self.units.energy_unit}/{self.units.length_unit}^2')

            # Save the computed energy terms
            calc['work-forward'] = uc.model(self.work_forward,
                                            self.units.energy_unit)
            calc['work-reverse'] = uc.model(self.work_reverse,
                                            self.units.energy_unit)
            calc['work'] = uc.model(self.work, self.units.energy_unit)
            calc['Helmholtz-energy-reference'] = uc.model(self.helmholtz_reference,
                                                          self.units.energy_unit)
            calc['Helmholtz-energy'] = uc.model(self.helmholtz,
                                                self.units.energy_unit)
            calc['Gibbs-energy'] = uc.model(self.gibbs,
                                            self.units.energy_unit)

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
        self.equilsteps = run_params['equilsteps']
        self.switchsteps = run_params['switchsteps']
        self.springsteps = run_params['springsteps']
        self.randomseed = run_params['randomseed']

        # Load phase-state info
        self.temperature = uc.value_unit(calc['phase-state']['temperature'])
        self.pressure = uc.value_unit(calc['phase-state']['pressure'])

        # Load results
        if self.status == 'finished':
            self.__volume = uc.value_unit(calc['volume'])
            self.__natoms = calc['natoms']
            self.__spring_constants = uc.value_unit(calc['spring-constants'])
            self.__work_forward = uc.value_unit(calc['work-forward'])
            self.__work_reverse = uc.value_unit(calc['work-reverse'])
            self.__work = uc.value_unit(calc['work'])
            self.__helmholtz_reference = uc.value_unit(calc['Helmholtz-energy-reference'])
            self.__helmholtz = uc.value_unit(calc['Helmholtz-energy'])
            self.__gibbs = uc.value_unit(calc['Gibbs-energy'])

    @property
    def queries(self) -> dict:
        queries = deepcopy(super().queries)
        queries.update({
            'temperature': load_query(
                style='float_match',
                name='temperature',
                path=f'{self.modelroot}.phase-state.temperature.value',
                description='search by temperature in Kelvin'),
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

        # Extract results
        if self.status == 'finished':
            meta['spring_constants'] = self.spring_constants.tolist()
            meta['volume'] = self.volume
            meta['natoms'] = self.natoms
            meta['work_forward'] = self.work_forward
            meta['work_reverse'] = self.work_reverse
            meta['work'] = self.work
            meta['Helmholtz_reference'] = self.helmholtz_reference
            meta['Helmholtz'] = self.helmholtz
            meta['Gibbs'] = self.gibbs

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
            'pressure':1e-2,
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
        input_dict['temperature'] = self.temperature
        input_dict['spring_constants'] = self.spring_constants
        input_dict['pressure'] = self.pressure

        input_dict['equilsteps'] = self.equilsteps
        input_dict['switchsteps'] = self.switchsteps
        input_dict['springsteps'] = self.springsteps
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
        self.spring_constants = results_dict['spring_constants']
        self.__work_forward = results_dict['work_forward']
        self.__work_reverse = results_dict['work_reverse']
        self.__work = results_dict['work']
        self.__helmholtz_reference = results_dict['Helmholtz_reference']
        self.__helmholtz = results_dict['Helmholtz']
        self.__gibbs = results_dict['Gibbs']
