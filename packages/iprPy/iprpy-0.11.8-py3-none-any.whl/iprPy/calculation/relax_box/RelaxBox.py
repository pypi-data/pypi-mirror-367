# coding: utf-8
# Standard Python libraries
from io import IOBase
from pathlib import Path
from typing import Optional, Union

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Calculation
from .relax_box import relax_box
from ...calculation_subset import (LammpsPotential, LammpsCommands, Units,
                                   AtommanSystemLoad, AtommanSystemManipulate)
from ...input import value

class RelaxBox(Calculation):
    """Class for managing box-only relaxations"""

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
        self.pressure_xx = 0.0
        self.pressure_yy = 0.0
        self.pressure_zz = 0.0
        self.pressure_xy = 0.0
        self.pressure_xz = 0.0
        self.pressure_yz = 0.0
        self.strainrange = 1e-6
        self.__initial_dump = None
        self.__final_dump = None
        self.__final_box = None
        self.__potential_energy = None
        self.__measured_pressure_xx = None
        self.__measured_pressure_yy = None
        self.__measured_pressure_zz = None
        self.__measured_pressure_xy = None
        self.__measured_pressure_xz = None
        self.__measured_pressure_yz = None

        # Define calc shortcut
        self.calc = relax_box

        # Call parent constructor
        super().__init__(model=model, name=name, database=database, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""
        return [
            'relax_box.py',
            'cij.template'
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
    def pressure_xx(self) -> float:
        """float: Target relaxation pressure component xx"""
        return self.__pressure_xx

    @pressure_xx.setter
    def pressure_xx(self, val: float):
        self.__pressure_xx = float(val)

    @property
    def pressure_yy(self) -> float:
        """float: Target relaxation pressure component yy"""
        return self.__pressure_yy

    @pressure_yy.setter
    def pressure_yy(self, val: float):
        self.__pressure_yy = float(val)

    @property
    def pressure_zz(self) -> float:
        """float: Target relaxation pressure component zz"""
        return self.__pressure_zz

    @pressure_zz.setter
    def pressure_zz(self, val: float):
        self.__pressure_zz = float(val)

    @property
    def pressure_xy(self) -> float:
        """float: Target relaxation pressure component xy"""
        return self.__pressure_xy

    @pressure_xy.setter
    def pressure_xy(self, val: float):
        self.__pressure_xy = float(val)

    @property
    def pressure_xz(self) -> float:
        """float: Target relaxation pressure component xz"""
        return self.__pressure_xz

    @pressure_xz.setter
    def pressure_xz(self, val: float):
        self.__pressure_xz = float(val)

    @property
    def pressure_yz(self) -> float:
        """float: Target relaxation pressure component yz"""
        return self.__pressure_yz

    @pressure_yz.setter
    def pressure_yz(self, val: float):
        self.__pressure_yz = float(val)

    @property
    def strainrange(self) -> float:
        """float: Strain range size used during box relaxation"""
        return self.__strainrange

    @strainrange.setter
    def strainrange(self, val: float):
        val = float(val)
        assert val >= 0.0
        self.__strainrange = val

    @property
    def initial_dump(self) -> dict:
        """dict: Info about the initial dump file"""
        if self.__initial_dump is None:
            raise ValueError('No results yet!')
        return self.__initial_dump

    @property
    def final_dump(self) -> dict:
        """dict: Info about the final dump file"""
        if self.__final_dump is None:
            raise ValueError('No results yet!')
        return self.__final_dump

    @property
    def final_box(self) -> am.Box:
        """atomman.Box: Relaxed unit cell box"""
        if self.__final_box is None:
            raise ValueError('No results yet!')
        return self.__final_box

    @property
    def potential_energy(self) -> float:
        """float: Potential energy per atom for the relaxed system"""
        if self.__potential_energy is None:
            raise ValueError('No results yet!')
        return self.__potential_energy

    @property
    def measured_pressure_xx(self) -> float:
        """float: Measured relaxation pressure component xx"""
        if self.__measured_pressure_xx is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_xx

    @property
    def measured_pressure_yy(self) -> float:
        """float: Measured relaxation pressure component yy"""
        if self.__measured_pressure_yy is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_yy

    @property
    def measured_pressure_zz(self) -> float:
        """float: Measured relaxation pressure component zz"""
        if self.__measured_pressure_zz is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_zz

    @property
    def measured_pressure_xy(self) -> float:
        """float: Measured relaxation pressure component xy"""
        if self.__measured_pressure_xy is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_xy

    @property
    def measured_pressure_xz(self) -> float:
        """float: Measured relaxation pressure component xz"""
        if self.__measured_pressure_xz is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_xz

    @property
    def measured_pressure_yz(self) -> float:
        """float: Measured relaxation pressure component yz"""
        if self.__measured_pressure_yz is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_yz

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
        pressure_xx : float, optional
            The target Pxx pressure component for the relaxation.
        pressure_yy : float, optional
            The target Pyy pressure component for the relaxation.
        pressure_zz : float, optional
            The target Pzz pressure component for the relaxation.
        pressure_xy : float, optional
            The target Pxy pressure component for the relaxation.
        pressure_xz : float, optional
            The target Pxz pressure component for the relaxation.
        pressure_yz : float, optional
            The target Pyz pressure component for the relaxation.
        strainrange : float, optional
            The magnitide of the strain to use for evaluating the elastic
            constants, which are then used to relax the box dimensions.
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=name, **kwargs)

        # Set calculation-specific values
        if 'pressure_xx' in kwargs:
            self.pressure_xx = kwargs['pressure_xx']
        if 'pressure_yy' in kwargs:
            self.pressure_yy = kwargs['pressure_yy']
        if 'pressure_zz' in kwargs:
            self.pressure_zz = kwargs['pressure_zz']
        if 'pressure_xy' in kwargs:
            self.pressure_xy = kwargs['pressure_xy']
        if 'pressure_xz' in kwargs:
            self.pressure_xz = kwargs['pressure_xz']
        if 'pressure_yz' in kwargs:
            self.pressure_yz = kwargs['pressure_yz']
        if 'strainrange' in kwargs:
            self.strainrange = kwargs['strainrange']

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
        input_dict['sizemults'] = input_dict.get('sizemults', '1 1 1')

        # Load calculation-specific strings

        # Load calculation-specific booleans

        # Load calculation-specific integers
        self.number_of_steps_r = int(input_dict.get('number_of_steps_r', 201))

        # Load calculation-specific unitless floats
        self.strainrange = float(input_dict.get('strainrange', 1e-6))

        # Load calculation-specific floats with units
        self.pressure_xx = value(input_dict, 'pressure_xx',
                                 default_unit=self.units.pressure_unit,
                                 default_term='0.0 GPa')
        self.pressure_yy = value(input_dict, 'pressure_yy',
                                 default_unit=self.units.pressure_unit,
                                 default_term='0.0 GPa')
        self.pressure_zz = value(input_dict, 'pressure_zz',
                                 default_unit=self.units.pressure_unit,
                                 default_term='0.0 GPa')
        self.pressure_xy = value(input_dict, 'pressure_xy',
                                 default_unit=self.units.pressure_unit,
                                 default_term='0.0 GPa')
        self.pressure_xz = value(input_dict, 'pressure_xz',
                                 default_unit=self.units.pressure_unit,
                                 default_term='0.0 GPa')
        self.pressure_yz = value(input_dict, 'pressure_yz',
                                 default_unit=self.units.pressure_unit,
                                 default_term='0.0 GPa')

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
            params['buildcombos'] = [
                'atomicreference load_file reference',
                'atomicparent load_file parent'
            ]
            params['parent_record'] = 'calculation_E_vs_r_scan'
            params['parent_load_key'] = 'minimum-atomic-system'
            params['parent_status'] = 'finished'
            params['sizemults'] = '10 10 10'
            params['atomshift'] = '0.05 0.05 0.05'
            params['strainrange'] = '1e-6'

            # Copy kwargs to params
            for key in kwargs:

                # Rename potential-related terms for buildcombos
                if key[:10] == 'potential_':
                    params[f'reference_{key}'] = kwargs[key]
                    params[f'parent_{key}'] = kwargs[key]

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
            'pressure_xx': ' '.join([
                "The Pxx normal pressure component to relax the box to.",
                "Default value is 0.0 GPa."]),
            'pressure_yy': ' '.join([
                "The Pyy normal pressure component to relax the box to.",
                "Default value is 0.0 GPa."]),
            'pressure_zz': ' '.join([
                "The Pzz normal pressure component to relax the box to.",
                "Default value is 0.0 GPa."]),
            'pressure_xy': ' '.join([
                "The Pxy normal pressure component to relax the box to.",
                "Default value is 0.0 GPa."]),
            'pressure_xz': ' '.join([
                "The Pxz normal pressure component to relax the box to.",
                "Default value is 0.0 GPa."]),
            'pressure_yz': ' '.join([
                "The Pyz normal pressure component to relax the box to.",
                "Default value is 0.0 GPa."]),
            'strainrange': ' '.join([
                "The strain range to use when estimating the elastic constants",
                "used to relax the box dimensions.  Default value is 1e-6."]),
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

            # Pressure parameters
            [
                [
                    'pressure_xx',
                    'pressure_yy',
                    'pressure_zz',
                    'pressure_xy',
                    'pressure_xz',
                    'pressure_yz',
                ]
            ] +

            # Strainrange
            [
                [
                    'strainrange',
                ]
            ]
        )
        return keys

########################### Data model interactions ###########################

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'calculation-relax-box'

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
        run_params['strain-range'] = self.strainrange

        # Save phase-state info
        calc['phase-state'] = DM()
        calc['phase-state']['temperature'] = uc.model(0.0, 'K')
        calc['phase-state']['pressure-xx'] = uc.model(self.pressure_xx,
                                                      self.units.pressure_unit)
        calc['phase-state']['pressure-yy'] = uc.model(self.pressure_yy,
                                                      self.units.pressure_unit)
        calc['phase-state']['pressure-zz'] = uc.model(self.pressure_zz,
                                                      self.units.pressure_unit)
        calc['phase-state']['pressure-xy'] = uc.model(self.pressure_xy,
                                                      self.units.pressure_unit)
        calc['phase-state']['pressure-xz'] = uc.model(self.pressure_xz,
                                                      self.units.pressure_unit)
        calc['phase-state']['pressure-yz'] = uc.model(self.pressure_yz,
                                                      self.units.pressure_unit)

        # Build results
        if self.status == 'finished':
            # Save info on initial and final configuration files
            calc['initial-system'] = DM()
            calc['initial-system']['artifact'] = DM()
            calc['initial-system']['artifact']['file'] = self.initial_dump['filename']
            calc['initial-system']['artifact']['format'] = 'atom_dump'
            calc['initial-system']['symbols'] = self.initial_dump['symbols']

            calc['final-system'] = DM()
            calc['final-system']['artifact'] = DM()
            calc['final-system']['artifact']['file'] = self.final_dump['filename']
            calc['final-system']['artifact']['format'] = 'atom_dump'
            calc['final-system']['symbols'] = self.final_dump['symbols']

            # Save measured box parameter info
            calc['measured-box-parameter'] = mbp = DM()
            mbp['lx'] = uc.model(self.final_box.lx, self.units.length_unit)
            mbp['ly'] = uc.model(self.final_box.ly, self.units.length_unit)
            mbp['lz'] = uc.model(self.final_box.lz, self.units.length_unit)
            mbp['xy'] = uc.model(self.final_box.xy, self.units.length_unit)
            mbp['xz'] = uc.model(self.final_box.xz, self.units.length_unit)
            mbp['yz'] = uc.model(self.final_box.yz, self.units.length_unit)

            # Save measured phase-state info
            calc['measured-phase-state'] = mps = DM()
            mps['temperature'] = uc.model(0.0, 'K')
            mps['pressure-xx'] = uc.model(self.measured_pressure_xx,
                                          self.units.pressure_unit)
            mps['pressure-yy'] = uc.model(self.measured_pressure_yy,
                                          self.units.pressure_unit)
            mps['pressure-zz'] = uc.model(self.measured_pressure_zz,
                                          self.units.pressure_unit)
            mps['pressure-xy'] = uc.model(self.measured_pressure_xy,
                                          self.units.pressure_unit)
            mps['pressure-xz'] = uc.model(self.measured_pressure_xz,
                                          self.units.pressure_unit)
            mps['pressure-yz'] = uc.model(self.measured_pressure_yz,
                                          self.units.pressure_unit)

            # Save the final cohesive energy
            calc['cohesive-energy'] = uc.model(self.potential_energy,
                                               self.units.energy_unit,
                                               None)

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
        self.strainrange = run_params['strain-range']

        # Load phase-state info
        self.pressure_xx = uc.value_unit(calc['phase-state']['pressure-xx'])
        self.pressure_yy = uc.value_unit(calc['phase-state']['pressure-yy'])
        self.pressure_zz = uc.value_unit(calc['phase-state']['pressure-zz'])

        # Load results
        if self.status == 'finished':
            self.__initial_dump = {
                'filename': calc['initial-system']['artifact']['file'],
                'symbols': calc['initial-system']['symbols']
            }

            self.__final_dump = {
                'filename': calc['final-system']['artifact']['file'],
                'symbols': calc['final-system']['symbols']
            }

            lx = uc.value_unit(calc['measured-box-parameter']['lx'])
            ly = uc.value_unit(calc['measured-box-parameter']['ly'])
            lz = uc.value_unit(calc['measured-box-parameter']['lz'])
            xy = uc.value_unit(calc['measured-box-parameter']['xy'])
            xz = uc.value_unit(calc['measured-box-parameter']['xz'])
            yz = uc.value_unit(calc['measured-box-parameter']['yz'])
            self.__final_box = am.Box(lx=lx, ly=ly, lz=lz, xy=xy, xz=xz, yz=yz)

            self.__potential_energy = uc.value_unit(calc['cohesive-energy'])

            mps = calc['measured-phase-state']
            self.__measured_pressure_xx = uc.value_unit(mps['pressure-xx'])
            self.__measured_pressure_yy = uc.value_unit(mps['pressure-yy'])
            self.__measured_pressure_zz = uc.value_unit(mps['pressure-zz'])
            self.__measured_pressure_xy = uc.value_unit(mps['pressure-xy'])
            self.__measured_pressure_xz = uc.value_unit(mps['pressure-xz'])
            self.__measured_pressure_yz = uc.value_unit(mps['pressure-yz'])

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
        meta['temperature'] = 0.0
        meta['pressure_xx'] = self.pressure_xx
        meta['pressure_yy'] = self.pressure_yy
        meta['pressure_zz'] = self.pressure_zz
        meta['pressure_xy'] = self.pressure_xy
        meta['pressure_xz'] = self.pressure_xz
        meta['pressure_yz'] = self.pressure_yz

        # Extract results
        if self.status == 'finished':
            meta['lx'] = self.final_box.lx
            meta['ly'] = self.final_box.ly
            meta['lz'] = self.final_box.lz
            meta['xy'] = self.final_box.xy
            meta['xz'] = self.final_box.xz
            meta['yz'] = self.final_box.yz

            meta['E_pot'] = self.potential_energy
            meta['measured_temperature'] = 0.0
            meta['measured_pressure_xx'] = self.measured_pressure_xx
            meta['measured_pressure_yy'] = self.measured_pressure_yy
            meta['measured_pressure_zz'] = self.measured_pressure_zz
            meta['measured_pressure_xy'] = self.measured_pressure_xy
            meta['measured_pressure_xz'] = self.measured_pressure_xz
            meta['measured_pressure_yz'] = self.measured_pressure_yz

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
            'pressure_xx':1e-2,
            'pressure_yy':1e-2,
            'pressure_zz':1e-2,
            'pressure_xy':1e-2,
            'pressure_xz':1e-2,
            'pressure_yz':1e-2,
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
        input_dict['strainrange'] = self.strainrange
        input_dict['p_xx'] = self.pressure_xx
        input_dict['p_yy'] = self.pressure_yy
        input_dict['p_zz'] = self.pressure_zz
        input_dict['p_xy'] = self.pressure_xy
        input_dict['p_xz'] = self.pressure_xz
        input_dict['p_yz'] = self.pressure_yz

        # Return input_dict
        return input_dict

    @property
    def calc_output_files(self) -> list:
        """list : Glob path strings for files generated by this calculation"""
        return [
            'init.dat',
            'initial.dump',
            'initial.restart',
            'final.dump',
            'cij-*-log.lammps',
            'cij_run0.in',
        ]

    def process_results(self, results_dict: dict):
        """
        Processes calculation results and saves them to the object's results
        attributes.

        Parameters
        ----------
        results_dict: dict
            The dictionary returned by the calc() method.
        """
        self.__initial_dump = {
            'filename': results_dict['dumpfile_initial'],
            'symbols': results_dict['symbols_initial']
        }
        self.__final_dump = {
            'filename': results_dict['dumpfile_final'],
            'symbols': results_dict['symbols_final']
        }
        lx = results_dict['lx'] / (self.system_mods.a_mults[1] - self.system_mods.a_mults[0])
        ly = results_dict['ly'] / (self.system_mods.b_mults[1] - self.system_mods.b_mults[0])
        lz = results_dict['lz'] / (self.system_mods.c_mults[1] - self.system_mods.c_mults[0])
        xy = results_dict['xy'] / (self.system_mods.b_mults[1] - self.system_mods.b_mults[0])
        xz = results_dict['xz'] / (self.system_mods.c_mults[1] - self.system_mods.c_mults[0])
        yz = results_dict['yz'] / (self.system_mods.c_mults[1] - self.system_mods.c_mults[0])
        self.__final_box = am.Box(lx=lx, ly=ly, lz=lz, xy=xy, xz=xz, yz=yz)
        self.__potential_energy = results_dict['E_pot']
        self.__measured_pressure_xx = results_dict['measured_pxx']
        self.__measured_pressure_yy = results_dict['measured_pyy']
        self.__measured_pressure_zz = results_dict['measured_pzz']
        self.__measured_pressure_xy = results_dict['measured_pxy']
        self.__measured_pressure_xz = results_dict['measured_pxz']
        self.__measured_pressure_yz = results_dict['measured_pyz']
