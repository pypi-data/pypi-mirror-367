#! usr/bin/env python3
#  -*- coding: utf-8 -*-

""""
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
import random
from omegalpes.general.time import TimeUnit
from omegalpes.energy.units.energy_units import *
from omegalpes.energy.units.production_units import ProductionUnit
from omegalpes.energy.units.consumption_units import ConsumptionUnit
from omegalpes.energy.units.reversible_units import ReversibleUnit


class TestInitEnergyUnit(unittest.TestCase):
    def setUp(self):
        self.time = TimeUnit(periods=5)
        self.p_min = random.randint(1, 1000)
        self.p_max = random.randint(self.p_min, 2000)

    def test_p_lb_int_float(self):
        """
            Test if the expected lower bound is created for p with an int
            or a float
        """
        p_min = random.choice([self.p_min, self.p_min / 1])

        energy_unit = EnergyUnit(self.time, 'energy_unit', p_min=p_min)
        self.assertEqual(energy_unit.p.lb, 0)

    def test_p_lb_list(self):
        """
            Test if the expected lower bound is created for p with a list
        """
        p_min = [0, 5, -3, -9.0, 10]
        energy_unit = EnergyUnit(self.time, 'energy_unit', p_min=p_min)
        self.assertListEqual(energy_unit.p.lb, [0, 0, -3, -9.0, 0])

    def test_p_ub_int_float(self):
        """
            Test if the expected upper bound is created for p with an int
            or a float
        """
        p_max = random.choice([self.p_max, self.p_max / 1])

        energy_unit = EnergyUnit(self.time, 'energy_unit', p_max=p_max)
        self.assertEqual(energy_unit.p.ub, p_max)

    def test_p_ub_list(self):
        """
            Test if the expected upper bound is created for p with a list
        """
        p_max = [0, 5, -3, -9.0, 10]
        energy_unit = EnergyUnit(self.time, 'energy_unit', p_max=p_max)
        self.assertListEqual(energy_unit.p.ub, [0, 5, 0, 0, 10])


class TestEnergyMinMaxValues(unittest.TestCase):
    def setUp(self):
        self.eu_no_pmax = EnergyUnit(time=TimeUnit(periods=24, dt=1),
                              name='energy_unit_no_pmax', p_min=10)
        self.eu_pmax_int = EnergyUnit(time=TimeUnit(periods=24, dt=1),
                              name='energy_unit_pmax_int', p_min=-1e6,
                                      p_max=1e2)
        self.pmax_list = 12*[1e6] + 12*[1e4]
        self.pmin_list = 12*[1e2] + 12*[-1e4]
        self.eu_pmax_list = EnergyUnit(time=TimeUnit(periods=24, dt=1),
                              name='energy_unit_pmax_list',
                                       p_min=self.pmin_list,
                                       p_max=self.pmax_list)

    def test_e_tot_ub(self):
        self.assertEqual(self.eu_no_pmax.e_tot.ub, 1e4*24)
        self.assertEqual(self.eu_pmax_int.e_tot.ub, 1e2*24)
        self.assertEqual(self.eu_pmax_list.e_tot.ub, sum(self.pmax_list))

    def test_e_tot_lb(self):
        self.assertEqual(self.eu_no_pmax.e_tot.lb, 0)
        self.assertEqual(self.eu_pmax_int.e_tot.lb, -1e6*24)
        plb_list = [min(0,p) for p in self.pmin_list]
        self.assertEqual(self.eu_pmax_list.e_tot.lb, sum(plb_list))


class TestEminEmax(unittest.TestCase):
    def setUp(self):
        self.eu_no_emax = EnergyUnit(time=TimeUnit(periods=24, dt=1),
                                     name='eu_no_emax')
        self.eu_emax = EnergyUnit(time=TimeUnit(periods=24, dt=1),
                                  name='eu_emax', e_min=1e2, e_max=1e7)

    def test_no_emax(self):
        self.assertIs(self.eu_no_emax.set_e_max, None)
        self.assertIs(self.eu_no_emax.set_e_min, None)

    def test_e_max(self):
        self.assertIsInstance(self.eu_emax.set_e_max, TechnicalConstraint)
        exp_emax = 'eu_emax_e_tot <= {0}'.format(1e7)
        self.assertEqual(self.eu_emax.set_e_max.exp, exp_emax)
        self.assertEqual(self.eu_emax.set_e_max.name, 'set_e_max')

    def test_e_min(self):
        self.assertIsInstance(self.eu_emax.set_e_min, TechnicalConstraint)
        exp_emin = 'eu_emax_e_tot >= {0}'.format(1e2)
        self.assertEqual(self.eu_emax.set_e_min.exp, exp_emin)
        self.assertEqual(self.eu_emax.set_e_min.name, 'set_e_min')

class TestSetOperatingTimeRange(unittest.TestCase):
    def setUp(self):
        self.prod_u = ProductionUnit(name='prod_u', time=TimeUnit(
            periods=24*2*2+8, dt=1/2))
        self.prod_u.set_operating_time_range([["08:00", "12:30"],
                                              ["14:30", "22:30"]])

    def test_beg_time_range(self):
        """Asserting the set_start_time_range is properly created for the 3
        days"""
        self.assertIsInstance(self.prod_u.set_start_time_range_16,
                              DailyDynamicConstraint)
        self.assertEqual(self.prod_u.set_start_time_range_16.exp_t,
                         'prod_u_u[t] == 0')
        start_range = list(range(0, 8*2))+list(range(24*2, 24*2+8*2))+list(
            range(24*4, 24*4+8))
        self.assertEqual(self.prod_u.set_start_time_range_16.t_range,
                         'for t ''in {0}'.format(start_range))

    def test_mid_time_range(self):
        """Asserting the set_time_range are properly created"""
        self.assertIsInstance(self.prod_u.set_time_range_25_29,
                              DailyDynamicConstraint)
        self.assertEqual(self.prod_u.set_time_range_25_29.exp_t,
                         'prod_u_u[t] == 0')
        mid_range = list(range(25, 29))+list(range(24*2+25, 24*2+29))
        self.assertEqual(self.prod_u.set_time_range_25_29.t_range,
                         'for t ''in {0}'.format(mid_range))

    def test_end_time_range(self):
        """Asserting the set_end_time_range is properly created"""
        self.assertIsInstance(self.prod_u.set_end_time_range_45,
                              DailyDynamicConstraint)
        self.assertEqual(self.prod_u.set_end_time_range_45.exp_t,
                         'prod_u_u[t] == 0')
        end_range = list(range(45, 24*2))+list(range(24*2+45, 24*2*2))
        self.assertEqual(self.prod_u.set_end_time_range_45.t_range,
                         'for t ''in {0}'.format(end_range))


class TestAddEnergyLimitsOnTimePeriod(unittest.TestCase):
    def setUp(self):
        periods = random.randint(24, 6000)
        self.time = TimeUnit(periods=periods)
        self.emin = random.randint(1, 1000)
        self.emax = random.randint(self.emin, 2000)
        self.energy_unit = EnergyUnit(self.time, 'energy_unit')
        self.start = '2018-01-01 3:00:00'
        self.end = '2018-01-01 8:00:00'

    def test_empty_start(self):
        """
            Test if the period_index is time.I[0:end] when no empty start
        """
        self.energy_unit.add_energy_limits_on_time_period(e_min=self.emin,
                                                          e_max=self.emax,
                                                          end=self.end)
        time = self.time
        period_index = [0, 1, 2, 3, 4, 5, 6, 7]

        self.assertListEqual(list(eval(self.energy_unit.set_e_max_period.exp[
                                       42:52])),
                             period_index)

    def test_empty_end(self):
        """
            Test if the period_index is time.I[start:] when no empty end
        """
        self.energy_unit.add_energy_limits_on_time_period(e_min=self.emin,
                                                          e_max=self.emax,
                                                          start=self.start)
        time = self.time
        end = self.time.I[-1]
        period_index = list(range(3, end + 1))

        self.assertListEqual(list(eval(self.energy_unit.set_e_max_period.exp[
                                       42:52])),
                             period_index)

    def test_e_min_0(self):
        """
            Test if there is no min constraint added with e_min equals to 0
        """
        self.energy_unit.add_energy_limits_on_time_period(e_min=0)

        set_e_min_period = getattr(self.energy_unit, 'set_e_min_period')
        self.assertIsNone(set_e_min_period)

    def test_no_e_max(self):
        """
            Test if there is no max constraint added with e_max = None
        """
        self.energy_unit.add_energy_limits_on_time_period(e_max=None)

        set_e_max_period = getattr(self.energy_unit, 'set_e_max_period')
        self.assertIsNone(set_e_max_period)


class TestWrongAssemblyUnit(unittest.TestCase):
    def setUp(self):
        self.prod_u = ProductionUnit(name='prod_u', time=TimeUnit(periods=4,
                                                                  dt=1))
        self.cons_u = ConsumptionUnit(name='cons_u', time=TimeUnit(periods=4,
                                                                   dt=1))
        self.rev_u = ReversibleUnit(name='rev_u', time=TimeUnit(periods=4,
                                                                   dt=1))

    def test_no_defined_prod_units(self):
        """Asserting an error is raised when no production unit is defined"""
        with self.assertRaises(IndexError):
            au_p_index = AssemblyUnit(name='au_p_index',
                                      time=TimeUnit(periods=4, dt=1),
                                      cons_units=[self.cons_u])

    def test_no_list_prod_units(self):
        """Asserting an error is raised when no list of production unit is
        defined"""
        with self.assertRaises(TypeError):
            au_p_type = AssemblyUnit(name='au_p_type',
                                       time=TimeUnit(periods=4, dt=1),
                                       prod_units=self.prod_u,
                                       cons_units=[self.cons_u])

    def test_wrong_prod_units(self):
        """Asserting an error is raised when the objects in the list of
        production units are not production units"""
        with self.assertRaises(TypeError):
            au_wpu = AssemblyUnit(time=TimeUnit(periods=4, dt=1),
                                    name='au_wrong_pu',
                                    prod_units=[self.cons_u],
                                    cons_units=[self.cons_u])

    def test_no_defined_cons_units(self):
        """Asserting an error is raised when no consumption unit is defined"""
        with self.assertRaises(IndexError):
            au_c_index = AssemblyUnit(name='au_c_index',
                                        time=TimeUnit(periods=4, dt=1),
                                        prod_units=[self.prod_u])

    def test_no_list_cons_units(self):
        """Asserting an error is raised when no list of consumption unit is
        defined"""
        with self.assertRaises(TypeError):
            au_c_type = AssemblyUnit(name='au_c_type',
                                       time=TimeUnit(periods=4, dt=1),
                                       prod_units=[self.prod_u],
                                       cons_units=self.cons_u)

    def test_wrong_cons_units(self):
        """Asserting an error is raised when the objects in the list of
        consumption units are not consumption units"""
        with self.assertRaises(TypeError):
            au_wcu = AssemblyUnit(time=TimeUnit(periods=4, dt=1),
                                  name='au_wrong_cu',
                                  prod_units=[self.prod_u],
                                  cons_units=[self.prod_u])

    def test_no_list_rev_units(self):
        """Asserting an error is raised when no list of reversible unit is
        defined"""
        with self.assertRaises(TypeError):
            au_r_type = AssemblyUnit(name='au_r_type',
                                     time=TimeUnit(periods=4, dt=1),
                                     rev_units=self.rev_u)

    def test_wrong_rev_units(self):
        """Asserting an error is raised when the objects in the list of
        reversible units are not reversible units"""
        with self.assertRaises(TypeError):
            au_wru = AssemblyUnit(time=TimeUnit(periods=4, dt=1),
                                  name='au_wrong_ru', rev_units=[self.prod_u])


class TestAssemblyUnitAttributes(unittest.TestCase):
    def setUp(self):
        self.prod_u = ProductionUnit(name='prod_u', time=TimeUnit(periods=4,
                                                               dt=1))
        self.cons_u = ConsumptionUnit(name='cons_u',
                                      time=TimeUnit(periods=4, dt=1))
        self.au = AssemblyUnit(time=TimeUnit(periods=4, dt=1), name='au',
                               prod_units=[self.prod_u],
                               cons_units=[self.cons_u])

    def test_attributes(self):
        """Checking the attributes of the Assembly unit are properly set :
        - operator,
        - prod_units
        - cons_units
        - poles
        """
        self.assertEqual(self.au.prod_units, [self.prod_u])
        self.assertEqual(self.au.cons_units, [self.cons_u])
        poles_dict = {}
        poles_dict[1] = self.prod_u.poles[1]
        poles_dict[2] = self.cons_u.poles[1]
        self.assertDictEqual(self.au.poles, poles_dict)


class TestAddProdUnit(unittest.TestCase):
    def setUp(self):
        self.pu = ProductionUnit(name='pu', time=TimeUnit(periods=4, dt=1))
        self.pu2 = ProductionUnit(name='pu2', time=TimeUnit(periods=4, dt=1))

        self.cons_u = ConsumptionUnit(name='cons_u',
                                      time=TimeUnit(periods=4, dt=1))
        self.au = AssemblyUnit(time=TimeUnit(periods=4, dt=1), name='au',
                               prod_units=[self.pu], cons_units=[self.cons_u])

    def test_add_prod_unit(self):
        """Checking the method add_prod_unit"""
        self.au._add_production_unit(self.pu2)
        poles_dict = dict()
        poles_dict[1] = self.pu.poles[1]
        poles_dict[2] = self.cons_u.poles[1]
        poles_dict[3] = self.pu2.poles[1]
        self.assertEqual(self.au.poles, poles_dict)
        self.assertEqual(self.au.prod_units, [self.pu, self.pu2])


class TestAddConsUnit(unittest.TestCase):
    def setUp(self):
        self.pu = ProductionUnit(name='pu', time=TimeUnit(periods=4, dt=1))
        self.cons_u = ConsumptionUnit(name='cons_u',
                                      time=TimeUnit(periods=4, dt=1))
        self.cons_u2 = ConsumptionUnit(name='cons_u2',
                                       time=TimeUnit(periods=4, dt=1))
        self.au = AssemblyUnit(time=TimeUnit(periods=4, dt=1), name='au',
                               prod_units=[self.pu], cons_units=[self.cons_u])

    def test_add_cons_unit(self):
        """Checking the method add_cons_unit"""
        self.au._add_consumption_unit(self.cons_u2)
        poles_dict = dict()
        poles_dict[1] = self.pu.poles[1]
        poles_dict[2] = self.cons_u.poles[1]
        poles_dict[3] = self.cons_u2.poles[1]
        self.assertEqual(self.au.poles, poles_dict)
        self.assertEqual(self.au.cons_units, [self.cons_u, self.cons_u2])


class TestAddRevUnit(unittest.TestCase):
    def setUp(self):
        self.time = TimeUnit(periods=4, dt=1)
        self.ru = ReversibleUnit(name='ru', time=self.time)
        self.ru2 = ReversibleUnit(name='ru', time=self.time)
        self.au = AssemblyUnit(time=self.time, name='au', rev_units=[self.ru])

    def test_add_rev_unit(self):
        """Checking the method add_rev_unit"""
        self.au._add_reversible_unit(self.ru2)
        poles_dict = dict()
        poles_dict[1] = self.ru.poles[1]
        poles_dict[2] = self.ru.poles[2]
        poles_dict[3] = self.ru2.poles[1]
        poles_dict[4] = self.ru2.poles[2]
        self.assertEqual(self.au.poles, poles_dict)
        self.assertEqual(self.au.rev_units, [self.ru, self.ru2])


class TestAddRevProdConsUnit(unittest.TestCase):
    def setUp(self):
        self.time = TimeUnit(periods=4, dt=1)
        self.pu = ProductionUnit(name='pu', time=self.time)
        self.cu = ConsumptionUnit(name='cons_u', time=self.time)
        self.ru = ReversibleUnit(name='ru', time=self.time)
        self.au = AssemblyUnit(time=self.time, name='au',
                               prod_units=[self.pu], cons_units=[self.cu],
                               rev_units=[self.ru])

    def test_assembly_units_poles(self):
        """Checking the poles of assembly unit"""
        poles_dict = dict()
        poles_dict[1] = self.ru.poles[1]
        poles_dict[2] = self.ru.poles[2]
        poles_dict[3] = self.pu.poles[1]
        poles_dict[4] = self.cu.poles[1]
        self.assertEqual(self.au.poles, poles_dict)

    def test_assembly_units_types(self):
        """Checking the types of the unit in AssemblyUnit"""
        self.assertIsInstance(self.au.rev_units[0], ReversibleUnit)
        self.assertIsInstance(self.au.prod_units[0], ProductionUnit)
        self.assertIsInstance(self.au.cons_units[0], ConsumptionUnit)
