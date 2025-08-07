#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Unit tests for the module storage_units.py, defining the storage units
attributes, constraints and functions.

..

    Copyright 2018 G2ELab / MAGE

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import unittest
from omegalpes.energy.units.storage_units import *
from omegalpes.general.time import TimeUnit
from pulp import LpBinary
from omegalpes.general.optimisation.elements import DynamicConstraint, \
    TechnicalConstraint, Constraint
from omegalpes.general.optimisation.elements import Objective

# Todo: change the test for minimize capacity

class TestStorageUnitInit(unittest.TestCase):
    """Checking the initialisation of the StorageUnit class"""

    def setUp(self):
        self.su0 = StorageUnit(time=TimeUnit(periods=4, dt=1), name='STU',
                               capacity=10)
        self.su1 = StorageUnit(time=TimeUnit(periods=4, dt=1), name='STU1',
                               capacity=10, pc_max=1e4, pd_max=1e4)

    def test_SOC_error(self):
        """Asserting an error is raised when SOCmin > SOCmax"""
        with self.assertRaises(ValueError):
            suErr = StorageUnit(time=TimeUnit(periods=24, dt=1), name='STU',
                                soc_min=1e+3, soc_max=5e+2)
    def test_SOC_error_list(self):
        """Asserting an error is raised when SOCmin > SOCmax for all time instants"""
        with self.assertRaises(ValueError):
            suErr_1 = StorageUnit(time=TimeUnit(periods=2, dt=1), name='STU1',
                                soc_min=[0, 1, 0.3], soc_max=[1, 0.5, 0.8])
        with self.assertRaises(ValueError):
            suErr_2 = StorageUnit(time=TimeUnit(periods=2, dt=1), name='STU2',
                                soc_min=[0, 5, 0.3], soc_max=[1, 48, 0.8])
                    
    def test_SOC_error_list_length(self):
        """Asserting an error is raised when the lengths of SOCmin and socmax \
             != len(time.I) + 1"""
        with self.assertRaises(ValueError):
            suErr = StorageUnit(time=TimeUnit(periods=3, dt=1), name='STU',
                                soc_min=[0, 0.5, 0.3], soc_max=[1, 1, 0.8])

    def test_default_values_capacity(self):
        """Checking the default values for the capacity Quantity"""
        self.assertEqual(self.su0.capacity.name, 'capacity')
        self.assertEqual(self.su0.capacity.unit, 'kWh')
        self.assertEqual(self.su0.capacity.value, 10)  # set to 0 in Quantity
        self.assertEqual(self.su0.capacity.lb, 0)
        self.assertEqual(self.su0.capacity.vlen, 1)

    def test_default_values_energy(self):
        """Checking the default values for the energy Quantity"""
        self.assertEqual(self.su0.e.name, 'e')
        self.assertEqual(self.su0.e.opt, {0: True, 1: True, 2: True, 3: True})
        self.assertEqual(self.su0.e.description, 'energy at t in the storage')
        self.assertEqual(self.su0.e.unit, 'kWh')
        self.assertEqual(self.su0.e.vlen, 4)
        self.assertEqual(self.su0.e.lb, 0)
        self.assertEqual(self.su0.e.ub, 10)

    def test_default_values_pc(self):
        """Checking the default values for the pc Quantity"""
        self.assertEqual(self.su0.charge.p.name, 'p')
        self.assertEqual(self.su0.charge.p.opt, {0: True, 1: True, 2: True, 3: True})
        self.assertEqual(self.su0.charge.p.unit, 'kW')
        self.assertEqual(self.su0.charge.p.vlen, 4)
        self.assertEqual(self.su0.charge.p.lb, 0)
        self.assertEqual(self.su0.charge.p.ub, self.su0.capacity.value)
        self.assertEqual(self.su1.charge.p.ub, 1e+4)

    def test_quantity_pc_max(self):
        """Checking the quantity pc_max parameters"""
        self.assertEqual(self.su0.pc_max.name, 'pc_max')
        self.assertEqual(self.su0.pc_max.opt, False)
        self.assertEqual(self.su1.pc_max.opt, False)
        self.assertEqual(self.su0.pc_max.unit, 'kW')
        self.assertEqual(self.su0.pc_max.vlen, 1)
        self.assertEqual(self.su0.pc_max.lb, 0)
        self.assertIsNone(self.su0.pc_max.ub)

    def test_default_values_pd(self):
        """Checking the default values for the pd Quantity"""
        self.assertEqual(self.su0.discharge.p.name, 'p')
        self.assertEqual(self.su0.discharge.p.opt, {0: True, 1: True, 2: True,
                                            3: True})
        self.assertEqual(self.su0.discharge.p.unit, 'kW')
        self.assertEqual(self.su0.discharge.p.vlen, 4)
        self.assertEqual(self.su0.discharge.p.lb, 0)
        self.assertEqual(self.su0.discharge.p.ub, self.su0.capacity.value)
        self.assertEqual(self.su1.discharge.p.ub, 1e+4)

    def test_quantity_pd_max(self):
        """Checking the quantity pc_max parameters"""
        self.assertEqual(self.su0.pd_max.name, 'pd_max')
        self.assertEqual(self.su0.pd_max.opt, False)
        self.assertEqual(self.su1.pd_max.opt, False)
        self.assertEqual(self.su0.pd_max.unit, 'kW')
        self.assertEqual(self.su0.pd_max.vlen, 1)
        self.assertEqual(self.su0.pd_max.lb, 0)
        self.assertIsNone(self.su0.pd_max.ub)


class TestSOCStorageUnits(unittest.TestCase):
    def setUp(self):
        self.suFloat = StorageUnit(name='suf', time=TimeUnit(periods=3, dt=1),
                                   soc_min=0.2, soc_max=0.9)
        self.suList = StorageUnit(name='sul', time=TimeUnit(periods=2, dt=1),
                                  soc_min=[0, 0.5, 0.3], soc_max=[1, 1, 0.8])

    def test_SOC_float(self):
        """Checking the SOC is properly set when it is float"""
        self.assertEqual(self.suFloat.set_soc_min.exp_t, '{0}_e[t] >= {1} * '
                                                         '{0}_capacity'.format(
            'suf', 0.2))
        self.assertEqual(self.suFloat.set_soc_max.exp_t, '{0}_e[t] <= {1} * '
                                                         '{0}_capacity'.format(
            'suf', 0.9))

    def test_SOC_list(self):
        """Checking the SOC is properly set when it is float"""
        self.assertEqual(self.suList.set_soc_min.exp_t, '{0}_e[t] >= {1}[t] '
                                                        '* {0}_capacity'
                         .format('sul', [0, 0.5, 0.3]))
        self.assertEqual(self.suList.set_soc_max.exp_t, '{0}_e[t] <= {1}[t] * '
                                                        '{0}_capacity'.format(
            'sul', [1, 1, 0.8]))


class TestSelfDisch(unittest.TestCase):
    def setUp(self):
        self.suSelf = StorageUnit(name='su_self', time=TimeUnit(periods=4,
                                                                dt=1),
                                  capacity=10, self_disch=1e-3,
                                  self_disch_t=2e-3)

    def test_calc_e(self):
        """Checking the energy calculation is properly set"""
        self.assertEqual(self.suSelf.calc_e.name, 'calc_e')
        self.assertEqual(self.suSelf.calc_e.t_range, 'for t in time.I[:-1]')
        self.assertEqual(self.suSelf.calc_e.exp_t,
                         '{0}_e[t+1] - {0}_e[t]*(1-{1}*time.DT)'
                         ' - time.DT * ({0}_charge_p[t]*{3}- '
                         '{0}_discharge_p[t]*1/{4}- {2}*'
                         '{0}_capacity) == 0'
                         .format('su_self', 2e-3,
                                 1e-3, 1, 1))

    def test_wrong_self_disch_value(self):
        """Asserting an error is raised when the self_disch value is over 1"""
        with self.assertRaises(ValueError):
            suWrongSelf = StorageUnit(time=TimeUnit(periods=4, dt=1),
                                      name='STU',
                                      capacity=10, self_disch=1e+2)

    def test_wrong_self_disch_t_value(self):
        """Asserting an error is raised when the self_disch_t value is over
        1"""
        with self.assertRaises(ValueError):
            suWrongSelf = StorageUnit(time=TimeUnit(periods=4, dt=1),
                                      name='STU',
                                      capacity=10, self_disch_t=1e+2)


class TestCalcP(unittest.TestCase):
    def setUp(self):
        self.suCalcP = StorageUnit(name='su_calcP', time=TimeUnit(periods=4,
                                                                  dt=1))

    def test_calc_p(self):
        """Checking the power calculation is properly set"""
        self.assertEqual(self.suCalcP.calc_p.exp_t, '{0}_p[t] == {0}_charge_p[t] - '
                                                    '{0}_discharge_p[t]'
                         .format('su_calcP'))
        self.assertEqual(self.suCalcP.calc_p.name, 'calc_p')
        self.assertEqual(self.suCalcP.calc_p.t_range, 'for t in time.I')


class TestOnOffStor(unittest.TestCase):
    def setUp(self):
        self.suoos = StorageUnit(name='su_oos', time=TimeUnit(periods=4, dt=1))

    def test_on_off_stor(self):
        """Checking the on_off_stor is properly set"""
        self.assertEqual(self.suoos.on_off_stor.name, 'on_off_stor')
        self.assertEqual(self.suoos.on_off_stor.t_range, 'for t in time.I')
        self.assertEqual(self.suoos.on_off_stor.exp_t, '{1}_u[t] + {2}_u['
                                                        't] - {0}_u[t]'
                                                        ' <= 0'
                         .format('su_oos','su_oos_charge',
                                 'su_oos_discharge' ))

class Teste0eFNone(unittest.TestCase):
    def setUp(self):
        self.sueNone = StorageUnit(name='su_e_none', time=TimeUnit(periods=4,
                                                                   dt=1))

    def test_none_e0(self):
        """Asserting an error is raised when the set_e_0 method is used
        while e_0 is set to None"""
        with self.assertRaises(AttributeError):
            self.sueNone.set_e_0

    def test_none_eF(self):
        """Asserting an error is raised when the set_e_f method is used
        while e_f is set to None"""
        with self.assertRaises(AttributeError):
            self.sueNone.set_e_f


class Test_e_f(unittest.TestCase):
    def setUp(self):
        self.time =TimeUnit(periods=2, dt=1)
        self.suFloat_ef = StorageUnit(name='sueff', e_f=5, capacity=10,
                                      time=TimeUnit(periods=2, dt=1),
                                      soc_min=0.2, soc_max=0.9)
        self.suList_ef = StorageUnit(name='suefl', e_f=5, capacity=10,
                                     time=TimeUnit(periods=2, dt=1),
                                    soc_min=[0, 0.5, 0.3], soc_max=[1, 1, 0.8])
        self.suFloat_no_ef = StorageUnit(name='sunoeff', capacity=10,
                                      time=TimeUnit(periods=2, dt=1),
                                      soc_min=0.2, soc_max=0.9)
        self.suList_no_ef = StorageUnit(name='sunoefl', capacity=10,
                                     time=TimeUnit(periods=2, dt=1),
                                    soc_min=[0, 0.5, 0.3], soc_max=[1, 1, 0.8])

    def test_e_f_SOC_float(self):
        """Checking e_f boundary constraints are properly set when floats
        and deactivate it when ef is not none"""
        self.assertIsInstance(self.suFloat_ef.e_f_min, Constraint)
        self.assertEqual(self.suFloat_ef.e_f_min.active, False)
        self.assertEqual(self.suFloat_ef.e_f_min.exp, '{0}_e_f >= {1} * '
                                                         '{0}_capacity'.format(
            'sueff', 0.2))
        
        self.assertIsInstance(self.suFloat_ef.e_f_max, Constraint)
        self.assertEqual(self.suFloat_ef.e_f_max.active, False)
        self.assertEqual(self.suFloat_ef.e_f_max.exp, '{0}_e_f <= {1} * '
                                                         '{0}_capacity'.format(
            'sueff', 0.9))

    def test_e_f_SOC_list(self):
        """Checking boundary constraints are properly set when lists
        and deactivate it when ef is not none"""
        self.assertIsInstance(self.suList_ef.e_f_min, Constraint)
        self.assertEqual(self.suList_ef.e_f_min.active, False)
        self.assertEqual(self.suList_ef.e_f_min.exp, '{0}_e_f >= {1}[{2}] '
                                                        '* {0}_capacity'
                         .format('suefl', [0, 0.5, 0.3], self.time.I[-1]+1))
        
        self.assertIsInstance(self.suList_ef.e_f_max, Constraint)
        self.assertEqual(self.suList_ef.e_f_max.active, False)
        self.assertEqual(self.suList_ef.e_f_max.exp, '{0}_e_f <= {1}[{2}] * '
                                                        '{0}_capacity'.format(
            'suefl', [1, 1, 0.8], self.time.I[-1]+1))

    def test_set_e_f(self):
        """Checking the set_e_f is properly set"""
        self.assertEqual(self.suFloat_ef.set_e_f.name, 'set_e_f')
        self.assertEqual(self.suFloat_ef.set_e_f.exp, '{0}_e_f-{0}_e[{1}] == '
                                                      '{2}*({0}_charge_p[{1}]*{3}-'
                     '{0}_discharge_p[{1}]*1/{4}-{5}*{0}_e[{1}]-{6}*{0}_capacity)'
                 .format('sueff', self.time.I[-1], 1, 1, 1, 0, 0))

    def test_no_e_f_SOC_float(self):
        """Checking e_f boundary constraints are properly set when floats"""
        self.assertIsInstance(self.suFloat_no_ef.e_f_min, Constraint)
        self.assertEqual(self.suFloat_no_ef.e_f_min.active, True)
        self.assertEqual(self.suFloat_no_ef.e_f_min.exp, '{0}_e_f >= {1} * '
                                                         '{0}_capacity'.format(
            'sunoeff', 0.2))
        
        self.assertIsInstance(self.suFloat_no_ef.e_f_max, Constraint)
        self.assertEqual(self.suFloat_no_ef.e_f_max.active, True)
        self.assertEqual(self.suFloat_no_ef.e_f_max.exp, '{0}_e_f <= {1} * '
                                                         '{0}_capacity'.format(
            'sunoeff', 0.9))

    def test_no_e_f_SOC_list(self):
        """Checking boundary constraints are properly set when lists"""
        self.assertIsInstance(self.suList_no_ef.e_f_min, Constraint)
        self.assertEqual(self.suList_no_ef.e_f_min.active, True)
        self.assertEqual(self.suList_no_ef.e_f_min.exp, '{0}_e_f >= {1}[{2}] '
                                                        '* {0}_capacity'
                         .format('sunoefl', [0, 0.5, 0.3], self.time.I[-1]+1))
        
        self.assertIsInstance(self.suList_no_ef.e_f_max, Constraint)
        self.assertEqual(self.suList_no_ef.e_f_max.active, True)
        self.assertEqual(self.suList_no_ef.e_f_max.exp, '{0}_e_f <= {1}[{2}] * '
                                                        '{0}_capacity'.format(
            'sunoefl', [1, 1, 0.8], self.time.I[-1]+1))

    def test_calc_e_f(self):
        """Checking the calc_e_f is properly set"""
        self.assertEqual(self.suFloat_no_ef.calc_e_f.name, 'calc_e_f')
        self.assertEqual(self.suFloat_no_ef.calc_e_f.exp, '{0}_e_f-{0}_e[{1}] '
                                                        '== {2}*({0}_charge_p[{1}]*'
                                                         '{3}-{0}_discharge_p[{1}]*1/'
                                                         '{4}-{5}*{0}_e[{1}]-'
                                                         '{6}*{0}_capacity)'
                 .format('sunoeff', self.time.I[-1], 1, 1, 1, 0, 0))

class Teste0eF(unittest.TestCase):
    def setUp(self):
        self.time = TimeUnit(periods=4, dt=1)
        self.sue = StorageUnit(time=TimeUnit(periods=4, dt=1),
                                      name='su_e',
                                      capacity=100, soc_max=0.9, 
                                      soc_min=0.2,
                                      e_0=50, e_f = 50)
        
    def test_e0_valid(self):
        """Checking e_0 is within the defined valid soc range"""
        with self.assertRaises(ValueError):
            sue0valid = StorageUnit(time=TimeUnit(periods=4, dt=1),
                                      name='su_eovalid',
                                      capacity=100, soc_max=0.9, 
                                      soc_min=0.2, e_0=1)
            
    def test_ef_valid(self):
        """Checking e_f is within the defined valid soc range"""
        with self.assertRaises(ValueError):
            suefvalid = StorageUnit(time=TimeUnit(periods=4, dt=1),
                                      name='su_efvalid',
                                      capacity=100, self_disch_t=1,
                                      soc_max=0.9, soc_min=0.2,
                                      e_f=1, e_0=50)

    def test_e0(self):
        """Checking set_e_0 is properly set"""
        self.assertIsInstance(self.sue.set_e_0, ActorConstraint)
        self.assertEqual(self.sue.set_e_0.name, 'set_e_0')
        self.assertEqual(self.sue.set_e_0.exp, '{0}_e[0] == {1}'
                         .format('su_e', 50))

    def test_ef(self):
        """Checking set_e_f is properly set"""
        self.assertIsInstance(self.sue.set_e_f, Constraint)
        self.assertEqual(self.sue.set_e_f.name, 'set_e_f')
        self.assertEqual(self.sue.set_e_f.exp, '{0}_e_f-{0}_e[{1}] == {3}*('
                                               '{0}_charge_p[{1}]*{4}-{0}_discharge_p[{1}]*'
                                               '1/{5}-{6}*{0}_e[{1}]-{7}*'
                                               '{0}_capacity)'
                         .format('su_e', self.time.I[-1], 0, 1, 1, 1, 0, 0))


class TestE0equalEf(unittest.TestCase):
    def test_e0_eq_ef(self):
        """Checking ef_is_e0 is properly set"""
        sue0eq = StorageUnit(name='su_e0eq', time=TimeUnit(periods=4, dt=1),
                             e_f=5e+2, ef_is_e0=True)
        self.assertIsInstance(sue0eq.ef_is_e0, ActorConstraint)
        self.assertEqual(sue0eq.ef_is_e0.name, 'ef_is_e0')
        self.assertEqual(sue0eq.ef_is_e0.exp, '{0}_e[0] == {0}_e_f'
                         .format('su_e0eq'))

    def test_e0_eq_ef_error(self):
        """Asserting e0_is_e0 raises an error when e_0 and e_f are set to
        different values"""
        with self.assertRaises(ValueError):
            sue0eqerror = StorageUnit(name='su_e0eq', time=TimeUnit(periods=4,
                                                                    dt=1),
                                      e_0=1e+2, e_f=5e+2, ef_is_e0=True)

class TestE0greatequalEf(unittest.TestCase):
    def test_ef_geq_e0(self):
        """Checking ef_geq_e0 is properly set"""
        suefgeq = StorageUnit(name='su_efgeq', time=TimeUnit(periods=4, dt=1),
                              e_0=1e+2, ef_geq_e0=True)
        self.assertIsInstance(suefgeq.ef_geq_e0, ActorConstraint)
        self.assertEqual(suefgeq.ef_geq_e0.name, 'ef_geq_e0')
        self.assertEqual(suefgeq.ef_geq_e0.exp, '{0}_e_f >= {0}_e[0]'
                         .format('su_efgeq'))

    def test_ef_geq_e0_error(self):
        """Asserting e0_geq_ef raises an error when e_f are set to
        a constant value"""
        with self.assertRaises(ValueError):
            suefgeqerror = StorageUnit(name='su_efgeq', time=TimeUnit(periods=4,
                                                                    dt=1),
                                      e_0=1e+2, e_f=5e+2, 
                                      ef_geq_e0=True)
        with self.assertRaises(ValueError):
            suefgeqerror = StorageUnit(name='su_efgeq', time=TimeUnit(periods=4,
                                                                    dt=1),
                                      e_0=1e+2, 
                                      ef_geq_e0=True, ef_is_e0=True)
            

class TestCyclesNone(unittest.TestCase):
    def test_cycles_none(self):
        """Asserting an error is raised when set_cycles is used while cycles
        is not defined"""
        sucyclesNone = StorageUnit(name='su_cyclesNone', time=TimeUnit(
            periods=4, dt=1))
        with self.assertRaises(AttributeError):
            self.sucyclesNone.set_cycles


class TestCyclesWrong(unittest.TestCase):
    """Asserting an error is raised when cycles is not an int"""

    def test_cycles_wrong(self):
        with self.assertRaises(TypeError):
            sucyclesWrong = StorageUnit(name='su_cyclesWrong', time=TimeUnit(
                periods=4, dt=1), cycles=True)


class TestCycles(unittest.TestCase):
    def setUp(self):
        self.sucycles = StorageUnit(name='su_cycles', time=TimeUnit(
            periods=25, dt=1), cycles=12)

    def test_cycles(self):
        """Checking the cycles constraint is properly set"""
        self.assertIsInstance(self.sucycles.set_cycles,
                              TechnicalDynamicConstraint)
        self.assertEqual(self.sucycles.set_cycles.name, 'set_cycles')
        self.assertEqual(self.sucycles.set_cycles.t_range, 'for t in time.I['
                                                           ':-12]')
        self.assertEqual(self.sucycles.set_cycles.exp_t, '{0}_e[t] == {0}_e['
                                                         't+{1}]'.format(
            'su_cycles', 12))


class TestMinCapacity(unittest.TestCase):
    def setUp(self):
        self.suMinCapa = StorageUnit(name='su_min_capa', time=TimeUnit(
            periods=4, dt=1))
        self.suMinCapa.minimize_capacity()
        self.sucMinCapa = StorageUnit(name='suc_min_capa', time=TimeUnit(
            periods=4, dt=1))
        self.sucMinCapa.minimize_capacity(pc_max_ratio=1/4)
        self.sudMinCapa = StorageUnit(name='sud_min_capa', time=TimeUnit(
            periods=4, dt=1))
        self.sudMinCapa.minimize_capacity(pd_max_ratio=1/3)

    def test_def_capacity(self):
        """Checking the def_capacity constraint is properly defined"""
        self.assertIsInstance(self.suMinCapa.def_capacity, DynamicConstraint)
        self.assertEqual(self.suMinCapa.def_capacity.name, 'def_capacity')
        self.assertEqual(self.suMinCapa.def_capacity.t_range, 'for t in '
                                                              'time.I')
        self.assertEqual(self.suMinCapa.def_capacity.exp_t, '{0}_e[t] <= {0}'
                                                            '_capacity'
                         .format('su_min_capa'))

    def test_min_capacity(self):
        """Checking the min_capacity objective is properly defined"""
        self.assertIsInstance(self.suMinCapa.min_capacity, Objective)
        self.assertEqual(self.suMinCapa.min_capacity.name, 'min_capacity')
        self.assertEqual(self.suMinCapa.min_capacity.weight, 1)
        self.assertEqual(self.suMinCapa.min_capacity.exp,
                         '{0}_capacity'.format('su_min_capa'))

    def test_pc_max_ratio(self):
        """Checking the pc_max_ratio works properly"""
        self.assertIsInstance(self.sucMinCapa.def_pc_max_calc, Constraint)
        self.assertEqual(self.sucMinCapa.def_pc_max_calc.exp,
                         '{0}_pc_max == {0}_capacity*{1}'.format(
                        self.sucMinCapa.name, 1/4))
        self.assertEqual(self.sucMinCapa.def_pc_max_calc.name,
                         'def_pc_max_calc')
        self.assertIsInstance(self.sucMinCapa.def_pc_max, DynamicConstraint)
        self.assertEqual(self.sucMinCapa.def_pc_max.exp_t,
                         '{0}_charge_p[t] <= {0}_pc_max'.format(
                             self.sucMinCapa.name))
        self.assertEqual(self.sucMinCapa.def_pc_max.t_range,'for t in time.I')
        self.assertEqual(self.sucMinCapa.def_pc_max.name, 'def_pc_max')

    def test_pd_max_ratio(self):
        """Checking the pc_max_ratio works properly"""
        self.assertIsInstance(self.sudMinCapa.def_pd_max_calc, Constraint)
        self.assertEqual(self.sudMinCapa.def_pd_max_calc.exp,
                         '{0}_pd_max == {0}_capacity*{1}'.format(
                        self.sudMinCapa.name, 1/3))
        self.assertEqual(self.sudMinCapa.def_pd_max_calc.name,
                         'def_pd_max_calc')
        self.assertIsInstance(self.sudMinCapa.def_pd_max, DynamicConstraint)
        self.assertEqual(self.sudMinCapa.def_pd_max.exp_t,
                         '{0}_discharge_p[t] <= {0}_pd_max'.format(
                             self.sudMinCapa.name))
        self.assertEqual(self.sudMinCapa.def_pd_max.t_range,'for t in time.I')
        self.assertEqual(self.sudMinCapa.def_pd_max.name, 'def_pd_max')

    def test_float_pmax_ratio_error(self):
        """Asserting an error is raised when pmax ratio is not a float"""
        with self.assertRaises(ValueError):
            self.suMinCapa.minimize_capacity(pc_max_ratio='one')


class TestThermoclineStorageSocMax(unittest.TestCase):
    def setUp(self):
        self.ts = ThermoclineStorage(name='ts', time=TimeUnit(
            periods=250, dt=1))
        self.dict_opt = {}
        for i in range(0, 250):
            self.dict_opt[i] = True

    def test_is_soc_max(self):
        """Checking is_soc_max is properly defined"""
        self.assertEqual(self.ts.is_soc_max.name, 'is_soc_max')
        self.assertEqual(self.ts.is_soc_max.opt, self.dict_opt)
        self.assertEqual(self.ts.is_soc_max.vlen, 250)
        self.assertEqual(self.ts.is_soc_max.vtype, LpBinary)
        self.assertEqual(self.ts.is_soc_max.description, 'indicates if the '
                                                         'storage is fully '
                                                         'charged 0:No 1:Yes')

    def test_is_soc_max_inf(self):
        """Checking is_soc_max_inf constraint is properly defined"""
        self.assertIsInstance(self.ts.def_is_soc_max_inf, DynamicConstraint)
        self.assertEqual(self.ts.def_is_soc_max_inf.name, 'def_is_soc_max_inf')
        self.assertEqual(self.ts.def_is_soc_max_inf.t_range, 'for t in time.I')
        self.assertEqual(self.ts.def_is_soc_max_inf.exp_t, '{0}_capacity * {'
                                                           '0}_is_soc_max[t] '
                                                           '>= ({0}_e[t] - '
                                                           '{0}_capacity + {1})'.format(
            'ts', 0.1))

    def test_is_soc_max_sup(self):
        """Checking is_soc_max_sup constraint is properly defined"""
        self.assertIsInstance(self.ts.def_is_soc_max_sup, DynamicConstraint)
        self.assertEqual(self.ts.def_is_soc_max_sup.name, 'def_is_soc_max_sup')
        self.assertEqual(self.ts.def_is_soc_max_sup.t_range, 'for t in time.I')
        self.assertEqual(self.ts.def_is_soc_max_sup.exp_t, '{0}_capacity * {'
                                                           '0}_is_soc_max[t] '
                                                           '<= {0}_e[t]'
                         .format('ts'))

    def test_force_soc_max(self):
        """Checking the force_soc_max constraint is properly defined"""
        self.assertIsInstance(self.ts.force_soc_max, DynamicConstraint)
        self.assertEqual(self.ts.force_soc_max.name, 'force_soc_max')
        self.assertEqual(self.ts.force_soc_max.t_range, 'for t in time.I['
                                                        '120:]')
        self.assertEqual(self.ts.force_soc_max.exp_t, 'lpSum({0}_is_soc_max['
                                                      'k] for k in range(t-{'
                                                      '1}+1, t)) >= 1'
                         .format('ts', 120))

