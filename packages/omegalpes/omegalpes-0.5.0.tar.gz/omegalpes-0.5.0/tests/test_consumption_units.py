#! usr/bin/env python3
#  -*- coding: utf-8 -*-

""" Unit tests for consumption_units module

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
from omegalpes.general.time import TimeUnit
from omegalpes.energy.units.consumption_units import ConsumptionUnit, \
    FixedConsumptionUnit, VariableConsumptionUnit, ShiftableConsumptionUnit


class TestInitConsumptionUnit(unittest.TestCase):
    """ Check the initialisation of the ConsumptionUnit class"""

    def test_none_definition(self):
        """ Check if the external constraints are none at the initialisation """
        cu0 = ConsumptionUnit(time=TimeUnit(periods=24, dt=1), name='CU0')

        self.assertIsNone(cu0.set_max_ramp_up)
        self.assertIsNone(cu0.set_max_ramp_down)
        self.assertIsNone(cu0.set_min_up_time)
        self.assertIsNone(cu0.set_min_down_time)
        self.assertIsNone(cu0.set_availability)


class TestDefConsumptionCostCalc(unittest.TestCase):
    """ Check the _def_consumption_cost_calc method """

    def test_none_consumption_cost_calc(self):
        """ check if the consumption_cost is none """
        cu0 = ConsumptionUnit(time=TimeUnit(periods=24, dt=1), name='CU0')
        self.assertIsNone(cu0.operating_cost)

    def test_int_consumption_cost_calc(self):
        """ check the cost calculation if consumption_cost is an int """
        cu_cost_int = ConsumptionUnit(time=TimeUnit(periods=24, dt=1),
                                      consumption_cost=3, name='CU0')
        self.assertEqual(cu_cost_int.calc_operating_cost.exp,
                         'CU0_operating_cost[t] == 3 * CU0_p[t] * time.DT '
                         'for t in time.I')

    def test_float_consumption_cost_calc(self):
        """ check the cost calculation if consumption_cost is a float """
        cu_cost_float = ConsumptionUnit(time=TimeUnit(periods=24, dt=1),
                                        consumption_cost=3.5, name='CU0')
        self.assertEqual(cu_cost_float.calc_operating_cost.exp,
                         'CU0_operating_cost[t] == 3.5 * CU0_p[t] * time.DT '
                         'for t in time.I')

    def test_list_consumption_cost_calc(self):
        """ check the cost calculation if consumption_cost is a list
        First an incomplete list considering the time of the study
        Then a complete list
        """
        with self.assertRaises(IndexError):
            ConsumptionUnit(time=TimeUnit(periods=24, dt=1), name='CU0',
                            consumption_cost=[1, 2])

        cu_cost_float = ConsumptionUnit(time=TimeUnit(periods=2, dt=1),
                                        consumption_cost=[0, 1], name='CU0')
        self.assertEqual(cu_cost_float.calc_operating_cost.exp,
                         'CU0_operating_cost[t] == [0, 1][t] * CU0_p[t] * '
                         'time.DT for t in time.I')

    def test_dict_consumption_cost_calc(self):
        """ check no cost calculation if consumption_cost is a dictionary """
        with self.assertRaises(TypeError):
            ConsumptionUnit(time=TimeUnit(periods=24, dt=1), name='CU0',
                            consumption_cost={0: 1})


class TestMinimizeConsumption(unittest.TestCase):
    """ Check the minimize_consumption method """

    def setUp(self):
        self.cu0 = ConsumptionUnit(TimeUnit(periods=24, dt=1), name='CU0')
        self.cu0.minimize_consumption()

    def test_minimize_consumption_name(self):
        """ Check the name of the min_consumption objective """
        self.assertIs(self.cu0.min_energy.name,
                      'min_consumption')

    def test_minimize_consumption_expression(self):
        """ Check the expression of the min_consumption objective """
        self.assertEqual(self.cu0.min_energy.exp,
                         'lpSum(CU0_p[t] for t in time.I)')


class TestMaximizeConsumption(unittest.TestCase):
    """ Check the maximize_consumption method """

    def setUp(self):
        self.cu0 = ConsumptionUnit(TimeUnit(periods=24, dt=1), name='CU0')
        self.cu0.maximize_consumption()

    def test_minimize_consumption_name(self):
        """ Check the name of the max_consumption objective """
        self.assertIs(self.cu0.min_energy.name,
                      'max_consumption')

    def test_minimize_consumption_expression(self):
        """ Check the expression of the max_consumption objective """
        self.assertEqual(self.cu0.min_energy.exp,
                         'lpSum(CU0_p[t] for t in time.I)')
        self.assertEqual(self.cu0.min_energy.weight, -1)


class TestMinimizeConsumptionCost(unittest.TestCase):
    """ Check the minimize_consumption_cost method """

    def setUp(self):
        self.cu0 = VariableConsumptionUnit(TimeUnit(periods=24, dt=1),
                                           name='CU0')
        self.cu0._add_operating_cost(3)
        self.cu0.minimize_consumption_cost()

    def test_minimize_consumption_name(self):
        """ Check the name of the min_consumption_cost objective """
        self.assertIs(self.cu0.min_operating_cost.name,
                      'min_consumption_cost')

    def test_minimize_consumption_expression(self):
        """ Check the expression of the min_consumption_cost objective """
        self.assertEqual(self.cu0.min_operating_cost.exp,
                         'lpSum(CU0_operating_cost[t] for t in time.I)')


class TestFixedConsumptionUnit(unittest.TestCase):
    """ Check the FixedConsumptionUnit class """

    def test_variable_consumption_none_p(self):
        """ Check if it raises an error if no energy profile is done for a
        FixedConsumptionUnit """
        with self.assertRaises(TypeError):
            FixedConsumptionUnit(TimeUnit(periods=24, dt=1))


class TestShiftableConsumptionUnit(unittest.TestCase):
    """check the ShiftableConsumptionUnit class"""

    def setUp(self):
        self.pv =  [0,0,0,0,0,0,0,0,0,0,24,]
        self.shu0 = ShiftableConsumptionUnit(time=TimeUnit(periods=11, dt=1), name = "demand1",\
                                             power_values=[10,1,10,0,0,0,3,0,0,0,0,], \
                                                mandatory=True)
        self.shu1 = ShiftableConsumptionUnit(time=TimeUnit(periods=11, dt=1), name = "demand2",\
                                             power_values=[0,1,10,0,0,0,3,0,0,0,5,], \
                                                mandatory=False)
        
    def test_power_values_cropping_and_epsilon(self):
        expected_cropped_0 = [10,1,10,0,0,0,3]
        self.assertEqual(len(self.shu0.power_values.value), len(expected_cropped_0))
        self.assertEqual(self.shu0.power_values.value, expected_cropped_0)
        expected_cropped_1 = [1,10,0,0,0,3,0,0,0,5]
        self.assertEqual(len(self.shu1.power_values.value), len(expected_cropped_1))
        self.assertEqual(self.shu1.power_values.value, expected_cropped_1)
    
    def test_energy_bounds_mandatory_and_nonmandatory(self):
        # e_max = sum(power_profile) * dt
        self.assertAlmostEqual(self.shu0._e_max_value, 24)
        self.assertAlmostEqual(self.shu1._e_max_value, 19)
        self.assertAlmostEqual(self.shu0._e_min_value, 24)
        self.assertAlmostEqual(self.shu1._e_min_value, 0)

    def test_no_overshoot_constraint(self):
        """checking no overshoot constraint is properly set"""

        self.assertEqual(self.shu0.set_no_overshoot.name, "no_overshoot_constraint")
        self.assertEqual(self.shu0.set_no_overshoot.exp, "lpSum({0}_start_up[t] for \
                                    t in range({1}-{2},{1}, 1) ) == 0".format(self.shu0.name,11,7))
        
        self.assertEqual(self.shu1.set_no_overshoot.name, "no_overshoot_constraint")
        self.assertEqual(self.shu1.set_no_overshoot.exp, "lpSum({0}_start_up[t] for \
                                    t in range({1}-{2},{1}, 1) ) == 0".format(self.shu1.name,11,10))
        
    def test_shiftable_constraint(self):
        self.assertEqual(self.shu0.def_0_power_value.name, 'def_0_power_value')
        self.assertEqual(self.shu0.def_0_power_value.exp_t, "{0}_p[t] >= {0}_power_values[{1}] * " \
                    "{0}_start_up[t-{1}]".format(self.shu0.name, 0))
        self.assertEqual(self.shu0.def_6_power_value.name, 'def_6_power_value')
        self.assertEqual(self.shu0.def_6_power_value.exp_t, "{0}_p[t] >= {0}_power_values[{1}] * " \
                    "{0}_start_up[t-{1}]".format(self.shu0.name, 6))
        
        self.assertEqual(self.shu1.def_5_power_value.name, 'def_5_power_value')
        self.assertEqual(self.shu1.def_5_power_value.exp_t, "{0}_p[t] >= {0}_power_values[{1}] * " \
                    "{0}_start_up[t-{1}]".format(self.shu1.name, 5))
        
        self.assertEqual(self.shu1.def_9_power_value.name, 'def_9_power_value')
        self.assertEqual(self.shu1.def_9_power_value.exp_t, "{0}_p[t] >= {0}_power_values[{1}] * " \
                    "{0}_start_up[t-{1}]".format(self.shu1.name, 9))
        
        # the test should generate error since there is no constraint beyond the length\
        # cropped boundary
        with self.assertRaises(AttributeError):
            self.shu0.def_9_power_value

        with self.assertRaises(AttributeError):
            self.shu1.def_10_power_value

    def test_shiftable_startup(self):
        """checking add start up constraint is properly set"""
        self.assertEqual(self.shu0.def_start_up.name, 'def_start_up')
        self.assertEqual(self.shu1.def_no_start_up.exp_t, '{0}_start_up[t+1] <= ({0}_u[t+1] - {0}_u[t]'
                  ' + 1)/2'.format('demand2'))
        self.assertEqual(self.shu0.start_up.vlen, 11)
        self.assertEqual(self.shu1.def_init_start_up.exp, '{0}_start_up[0] == {0}_u[0]'.format(self.shu1.name))
        
