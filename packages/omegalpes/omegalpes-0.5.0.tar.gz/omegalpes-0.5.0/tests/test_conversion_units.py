#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Unit tests for the module conversion_units.py, defining the conversion units
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
from omegalpes.energy.units.conversion_units import *
from omegalpes.general.time import TimeUnit
from omegalpes.energy.units.consumption_units import ConsumptionUnit
from omegalpes.energy.units.production_units import ProductionUnit
import pandas as pd
from omegalpes.general.optimisation.elements import Quantity, DynamicConstraint


class TestConversionUnit(unittest.TestCase):
    def test_conversion_unit(self):
        time = TimeUnit(periods=4, dt=1)
        conv_u = ConversionUnit(time=time, name='conv_u',
                                prod_units=[ProductionUnit(time=time,
                                                           name='pu')],
                                cons_units=[ConsumptionUnit(time=time,
                                                            name='cu')],
                                rev_units=None)
        self.assertIsInstance(conv_u, AssemblyUnit)


class TestSingleConvUnit(unittest.TestCase):
    def setUp(self):
        self.tu = TimeUnit(periods=4, dt=1)
        self.sing = SingleConversionUnit(time=self.tu, name='sing',
                                         energy_type_in=elec,
                                         energy_type_out=thermal)

    def test_prod_unit(self):
        """Checking the production_unit is properly defined"""
        self.assertIsInstance(self.sing.production_unit, ProductionUnit)
        self.assertEqual(self.sing.production_unit.time.DT, self.tu.DT)
        pd.testing.assert_index_equal(
            self.sing.production_unit.time.DATES,
            self.tu.DATES)
        self.assertEqual(self.sing.production_unit.name,
                         'sing_prod')
        self.assertEqual(self.sing.production_unit.p.value, {0: 0,
                                                                    1: 0, 2: 0,
                                                                    3: 0})
        self.assertEqual(self.sing.production_unit.energy_type,
                         'Thermal')

    def test_cons_unit(self):
        """Checking the consumption_unit is properly defined"""
        self.assertIsInstance(self.sing.consumption_unit, ConsumptionUnit)
        self.assertEqual(self.sing.consumption_unit.time.DT, self.tu.DT)
        pd.testing.assert_index_equal(
            self.sing.consumption_unit.time.DATES,
            self.tu.DATES)
        self.assertEqual(self.sing.consumption_unit.name, 'sing_cons')
        self.assertEqual(self.sing.consumption_unit.p.value, {0: 0,
                                                                  1: 0, 2: 0,
                                                                  3: 0})
        self.assertEqual(self.sing.consumption_unit.energy_type,
                         'Electrical')


class TestEfficiencyRatioFloat(unittest.TestCase):
    def setUp(self):
        self.sing = SingleConversionUnit(time=TimeUnit(periods=4, dt=1),
                                         name='eff_inf',
                                         efficiency_ratio=0.5)

    def test_conversion_constraint(self):
        """Checking the conversion constraint"""
        self.assertIsInstance(self.sing.conversion, DynamicConstraint)
        self.assertEqual(self.sing.conversion.name, 'conversion')
        self.assertEqual(self.sing.conversion.t_range, 'for t in time.I')
        self.assertEqual(self.sing.conversion.exp_t,
                         '{0}_p[t] == {1} * {2}_p[t]'
                         .format('eff_inf_prod', 0.5,
                                 'eff_inf_cons'))

    def test_eff_ratio_sup(self):
        """Asserting an error is raised when the efficiency ratio value is
        over 1"""
        with self.assertRaises(ValueError):
            eff_sup = SingleConversionUnit(
                time=TimeUnit(periods=4, dt=1), name='eff_sup',
                efficiency_ratio=4)


class TestEffRatioList(unittest.TestCase):
    def setUp(self):
        self.eff_r_list = [0.8, 0.5, 0.5, 1]
        self.sing = \
            SingleConversionUnit(time=TimeUnit(periods=4, dt=1),
                                 name='eff_inf',
                                 efficiency_ratio=self.eff_r_list)

    def test_conversion_constraint(self):
        """Checking the conversion constraint with a list
        efficiency_ratio"""
        self.assertIsInstance(self.sing.conversion, DynamicConstraint)
        self.assertEqual(self.sing.conversion.name, 'conversion')
        self.assertEqual(self.sing.conversion.t_range, 'for t in time.I')
        self.assertEqual(self.sing.conversion.exp_t,
                         '{0}_p[t] == {1}[t] * {2}_p[t]'
                         .format('eff_inf_prod', self.eff_r_list,
                                 'eff_inf_cons'))

    def test_eff_r_sup(self):
        """Asserting an error is raised when at least one element of the
        efficiency_ratio list is over 1"""
        with self.assertRaises(ValueError):
            sing_sup = SingleConversionUnit(
                time=TimeUnit(periods=4, dt=1), name='sing_sup',
                efficiency_ratio=[0.5, 0.8, 1.2, 1])

    def test_eff_r_sup_dict(self):
        """Asserting an error is raised when at least one element of the
        efficiency_ratio dict is over 1"""
        with self.assertRaises(ValueError):
            sing_sup = \
                SingleConversionUnit(time=TimeUnit(periods=4,
                                                                dt=1),
                                                  name='eff_sup',
                                                  efficiency_ratio={1: 0.5,
                                                                       2: 0.8,
                                                                       3: 1.2,
                                                                       4: 1})

    def test_eff_r_too_long(self):
        """Asserting an error is raised when the efficiency_ratio list is
        longer than the studied time period"""
        with self.assertRaises(IndexError):
            sing_long = SingleConversionUnit(time=TimeUnit(
                periods=4, dt=1), name='eff_long',
                efficiency_ratio=[0.5, 0.8, 1, 0.2, 1])

    def test_eff_r_wrong_type(self):
        """Asserting an error is raised when the efficiency_ratio is a
        string"""
        with self.assertRaises(TypeError):
            eff_wrong = SingleConversionUnit(
                time=TimeUnit(periods=4,
                              dt=1),
                name='eff_wrong',
                efficiency_ratio='lala')


class TestElec2ThermalConvUnit(unittest.TestCase):
    def setUp(self):
        self.tu = TimeUnit(periods=4, dt=1)
        self.e2h = ElectricalToThermalConversionUnit(time=self.tu, name='e2h')

    def test_h_prod_unit(self):
        """Checking the thermal_production_unit is properly defined"""
        self.assertIsInstance(self.e2h.thermal_production_unit, ProductionUnit)
        self.assertEqual(self.e2h.thermal_production_unit.time.DT, self.tu.DT)
        pd.testing.assert_index_equal(
            self.e2h.thermal_production_unit.time.DATES,
            self.tu.DATES)
        self.assertEqual(self.e2h.thermal_production_unit.name,
                         'e2h_therm_prod')
        self.assertEqual(self.e2h.thermal_production_unit.p.value, {0: 0,
                                                                    1: 0, 2: 0,
                                                                    3: 0})
        self.assertEqual(self.e2h.thermal_production_unit.energy_type,
                         'Thermal')

    def test_e_cons_unit(self):
        """Checking the elec_consumption_unit is properly defined"""
        self.assertIsInstance(self.e2h.elec_consumption_unit, ConsumptionUnit)
        self.assertEqual(self.e2h.elec_consumption_unit.time.DT, self.tu.DT)
        pd.testing.assert_index_equal(
            self.e2h.elec_consumption_unit.time.DATES,
            self.tu.DATES)
        self.assertEqual(self.e2h.elec_consumption_unit.name, 'e2h_elec_cons')
        self.assertEqual(self.e2h.elec_consumption_unit.p.value, {0: 0,
                                                                  1: 0, 2: 0,
                                                                  3: 0})
        self.assertEqual(self.e2h.elec_consumption_unit.energy_type,
                         'Electrical')


class TestE2HRatioFloat(unittest.TestCase):
    def setUp(self):
        self.e2h = ElectricalToThermalConversionUnit(time=TimeUnit(periods=4,
                                                                   dt=1),
                                                     name='e2h_inf',
                                                     elec_to_therm_ratio=0.5)

    def test_conversion_constraint(self):
        """Checking the conversion constraint"""
        self.assertIsInstance(self.e2h.conversion, DynamicConstraint)
        self.assertEqual(self.e2h.conversion.name, 'conversion')
        self.assertEqual(self.e2h.conversion.t_range, 'for t in time.I')
        self.assertEqual(self.e2h.conversion.exp_t,
                         '{0}_p[t] == {1} * {2}_p[t]'
                         .format('e2h_inf_therm_prod', 0.5,
                                 'e2h_inf_elec_cons'))

    def test_e2hr_sup(self):
        """Asserting an error is raised when the elec_to_therm ratio value is
        over 1"""
        with self.assertRaises(ValueError):
            e2h_sup = ElectricalToThermalConversionUnit(
                time=TimeUnit(periods=4, dt=1), name='e2h_sup',
                elec_to_therm_ratio=4)


class TestE2HRatioList(unittest.TestCase):
    def setUp(self):
        self.e2hr_list = [0.8, 0.5, 0.5, 1]
        self.e2h = \
            ElectricalToThermalConversionUnit(time=TimeUnit(periods=4, dt=1),
                                              name='e2h_inf',
                                              elec_to_therm_ratio=
                                              self.e2hr_list)

    def test_conversion_constraint(self):
        """Checking the conversion constraint with a list
        elec_to_therm_ratio"""
        self.assertIsInstance(self.e2h.conversion, DynamicConstraint)
        self.assertEqual(self.e2h.conversion.name, 'conversion')
        self.assertEqual(self.e2h.conversion.t_range, 'for t in time.I')
        self.assertEqual(self.e2h.conversion.exp_t,
                         '{0}_p[t] == {1}[t] * {2}_p[t]'
                         .format('e2h_inf_therm_prod', self.e2hr_list,
                                 'e2h_inf_elec_cons'))

    def test_e2hr_sup(self):
        """Asserting an error is raised when at least one element of the
        elec_to_therm_ratio list is over 1"""
        with self.assertRaises(ValueError):
            e2h_sup = ElectricalToThermalConversionUnit(
                time=TimeUnit(periods=4, dt=1), name='e2h_sup',
                elec_to_therm_ratio=[0.5, 0.8, 1.2, 1])

    def test_e2hr_sup_dict(self):
        """Asserting an error is raised when at least one element of the
        elec_to_therm_ratio dict is over 1"""
        with self.assertRaises(ValueError):
            e2h_sup = \
                ElectricalToThermalConversionUnit(time=TimeUnit(periods=4,
                                                                dt=1),
                                                  name='e2h_sup',
                                                  elec_to_therm_ratio={1: 0.5,
                                                                       2: 0.8,
                                                                       3: 1.2,
                                                                       4: 1})

    def test_e2hr_too_long(self):
        """Asserting an error is raised when the elec_to_therm_ratio list is
        longer than the studied time period"""
        with self.assertRaises(IndexError):
            e2h_long = ElectricalToThermalConversionUnit(time=TimeUnit(
                periods=4, dt=1), name='e2h_long',
                elec_to_therm_ratio=[0.5, 0.8, 1, 0.2, 1])

    def test_e2hr_wrong_type(self):
        """Asserting an error is raised when the elec_to_therm_ratio is a
        string"""
        with self.assertRaises(TypeError):
            e2h_wrong = ElectricalToThermalConversionUnit(
                time=TimeUnit(periods=4,
                              dt=1),
                name='e2h_wrong',
                elec_to_therm_ratio='lala')


class TestReversibleConversionUnitCreation(unittest.TestCase):
    def setUp(self):
        self.time = TimeUnit(periods=4, dt=1)
        self.rev_conv = ReversibleConversionUnit(time=self.time,
                                                 name='rev_conv',
                                                 pmin_up=1e-4, pmax_up=1e4,
                                                 pmin_down=2e-4,
                                                 pmax_down=2e4,
                                                 up2down_eff=0.9,
                                                 down2up_eff=0.7,
                                                 energy_type_up='Electrical',
                                                 energy_type_down='Thermal')

    def test_rev_units_up(self):
        """Testing the reversible units upstream is created"""
        self.assertIsInstance(self.rev_conv.rev_unit_upstream, ReversibleUnit)
        self.assertEqual(self.rev_conv.rev_unit_upstream.name,
                         'rev_conv_upstream')
        self.assertEqual(self.rev_conv.rev_unit_upstream.consumption_unit
                         .energy_type, 'Electrical')

    def test_rev_units_down(self):
        """Testing the reversible units downstream is created"""
        self.assertIsInstance(self.rev_conv.rev_unit_downstream,
                              ReversibleUnit)
        self.assertEqual(self.rev_conv.rev_unit_downstream.name,
                         'rev_conv_downstream')
        self.assertEqual(self.rev_conv.rev_unit_downstream.consumption_unit
                         .energy_type, 'Thermal')


class TestReversibleConversionUnitEff(unittest.TestCase):
    def setUp(self):
        self.time = TimeUnit(periods=4, dt=1)
        self.rev_conv = ReversibleConversionUnit(time=self.time,
                                                 name='rev_conv',
                                                 pmin_up=1e-4, pmax_up=1e4,
                                                 pmin_down=2e-4,
                                                 pmax_down=2e4,
                                                 up2down_eff=0.9,
                                                 down2up_eff=0.7,
                                                 energy_type_up='Electrical',
                                                 energy_type_down='Thermal')

        self.rev_conv_list = \
            ReversibleConversionUnit(time=self.time, name='rev_conv_list',
                                     pmin_up=1e-4, pmax_up=1e4, pmin_down=2e-4,
                                     pmax_down=2e4, up2down_eff=[0.9, 0.2, 0.8,
                                                                 0.7],
                                     down2up_eff=[0.4, 0.6, 0.5, 0.6])

        self.rev_conv_dict = \
            ReversibleConversionUnit(time=self.time, name='rev_conv_dict',
                                     pmin_up=1e-4, pmax_up=1e4, pmin_down=2e-4,
                                     pmax_down=2e4,
                                     up2down_eff={0: 0.9, 1: 0.2, 2: 0.8,
                                                  3: 0.7},
                                     down2up_eff={0: 0.4, 1: 0.6, 2: 0.5,
                                                  3: 0.6})

    def test_up2down_eff_float(self):
        """Testing the up2down_eff for float"""
        self.assertIsInstance(self.rev_conv.conversion_up2down,
                              DynamicConstraint)
        self.assertEqual(self.rev_conv.conversion_up2down.exp_t,
                         '{0}_p[t] == {1} * {2}_p[t]'.format(
                             'rev_conv_downstream_prod', 0.9,
                             'rev_conv_upstream_cons'))
        self.assertEqual(self.rev_conv.conversion_up2down.t_range,
                         'for t in time.I')
        self.assertEqual(self.rev_conv.conversion_up2down.name,
                         'conversion_up2down')

    def test_down2up_eff_float(self):
        """Testing the down2up_eff for float"""
        self.assertIsInstance(self.rev_conv.conversion_down2up,
                              DynamicConstraint)
        self.assertEqual(self.rev_conv.conversion_down2up.exp_t,
                         '{0}_p[t] == {1} * {2}_p[t]'.format(
                             'rev_conv_upstream_prod', 0.7,
                             'rev_conv_downstream_cons'))
        self.assertEqual(self.rev_conv.conversion_down2up.t_range,
                         'for t in time.I')
        self.assertEqual(self.rev_conv.conversion_down2up.name,
                         'conversion_down2up')

    def test_wrong_eff_float(self):
        with self.assertRaises(ValueError):
            rev_conv_w = ReversibleConversionUnit(time=self.time,
                                                  name='rev_conv_w',
                                                  pmin_up=1e-4, pmax_up=1e4,
                                                  pmin_down=2e-4,
                                                  pmax_down=2e4,
                                                  up2down_eff=9,
                                                  down2up_eff=7)

    def test_up2down_eff_list(self):
        """Testing the up2down_eff for lists"""
        self.assertIsInstance(self.rev_conv_list.conversion_up2down,
                              DynamicConstraint)
        self.assertEqual(self.rev_conv_list.conversion_up2down.exp_t,
                         '{0}_p[t] == {1}[t] * {2}_p[t]'.format(
                             'rev_conv_list_downstream_prod', [0.9, 0.2, 0.8,
                                                               0.7],
                             'rev_conv_list_upstream_cons'))
        self.assertEqual(self.rev_conv_list.conversion_up2down.t_range,
                         'for t in time.I')
        self.assertEqual(self.rev_conv_list.conversion_up2down.name,
                         'conversion_up2down')

    def test_down2up_eff_list(self):
        """Testing the down2up_eff for lists"""
        self.assertIsInstance(self.rev_conv_list.conversion_down2up,
                              DynamicConstraint)
        self.assertEqual(self.rev_conv_list.conversion_down2up.exp_t,
                         '{0}_p[t] == {1}[t] * {2}_p[t]'.format(
                             'rev_conv_list_upstream_prod',
                             [0.4, 0.6, 0.5, 0.6],
                             'rev_conv_list_downstream_cons'))
        self.assertEqual(self.rev_conv_list.conversion_down2up.t_range,
                         'for t in time.I')
        self.assertEqual(self.rev_conv_list.conversion_down2up.name,
                         'conversion_down2up')

    def test_wrong_eff_list(self):
        with self.assertRaises(ValueError):
            rev_conv_list_wrong = \
                ReversibleConversionUnit(time=self.time,
                                         name='rev_conv_list_w',
                                         pmin_up=1e-4, pmax_up=1e4,
                                         pmin_down=2e-4,
                                         pmax_down=2e4,
                                         up2down_eff=[0.9, 4, 0.8,
                                                      0.7],
                                         down2up_eff=[0.4, 0.6, 0.5, 6])

    def test_up2down_eff_dict(self):
        """Testing the up2down_eff for dicts"""
        self.assertIsInstance(self.rev_conv_dict.conversion_up2down,
                              DynamicConstraint)
        self.assertEqual(self.rev_conv_dict.conversion_up2down.exp_t,
                         '{0}_p[t] == {1}[t] * {2}_p[t]'.format(
                             'rev_conv_dict_downstream_prod',
                             {0: 0.9, 1: 0.2, 2: 0.8, 3: 0.7}.values(),
                             'rev_conv_dict_upstream_cons'))
        self.assertEqual(self.rev_conv_dict.conversion_up2down.t_range,
                         'for t in time.I')
        self.assertEqual(self.rev_conv_dict.conversion_up2down.name,
                         'conversion_up2down')

    def test_down2up_eff_dict(self):
        """Testing the down2up_eff for dicts"""
        self.assertIsInstance(self.rev_conv_dict.conversion_down2up,
                              DynamicConstraint)
        self.assertEqual(self.rev_conv_dict.conversion_down2up.exp_t,
                         '{0}_p[t] == {1}[t] * {2}_p[t]'.format(
                             'rev_conv_dict_upstream_prod',
                             {0: 0.4, 1: 0.6, 2: 0.5, 3: 0.6}.values(),
                             'rev_conv_dict_downstream_cons'))
        self.assertEqual(self.rev_conv_dict.conversion_down2up.t_range,
                         'for t in time.I')
        self.assertEqual(self.rev_conv_dict.conversion_down2up.name,
                         'conversion_down2up')

    def test_wrong_eff_dict(self):
        with self.assertRaises(ValueError):
            self.rev_conv_dict_wrong = \
                ReversibleConversionUnit(time=self.time,
                                         name='rev_conv_list_w',
                                         pmin_up=1e-4, pmax_up=1e4,
                                         pmin_down=2e-4,
                                         pmax_down=2e4,
                                         up2down_eff={0: 0.9, 1: 0.2, 2: 8,
                                                      3: 0.7},
                                         down2up_eff={0: 0.4, 1: 0.6, 2: 0.5,
                                                      3: 6})


class TestHeatPump(unittest.TestCase):
    def setUp(self):
        self.tu = TimeUnit(periods=4, dt=1)
        self.hp = HeatPump(time=self.tu, name='hp')

    def test_h_prod_unit(self):
        """Checking the thermal_production_unit of the heat pump is properly
        set"""
        self.assertIsInstance(self.hp.thermal_production_unit, ProductionUnit)
        self.assertEqual(self.hp.thermal_production_unit.time.DT, self.tu.DT)
        pd.testing.assert_index_equal(
            self.hp.thermal_production_unit.time.DATES,
            self.tu.DATES)
        self.assertEqual(self.hp.thermal_production_unit.name,
                         'hp_therm_prod')
        self.assertEqual(self.hp.thermal_production_unit.p.value, {0: 0,
                                                                   1: 0, 2: 0,
                                                                   3: 0})
        self.assertEqual(self.hp.thermal_production_unit.energy_type,
                         'Thermal')

    def test_h_cons_unit(self):
        """Checking the thermal_consumption_unit of the heat pump is properly
        set"""
        self.assertIsInstance(self.hp.thermal_consumption_unit,
                              ConsumptionUnit)
        self.assertEqual(self.hp.thermal_consumption_unit.time.DT, self.tu.DT)
        pd.testing.assert_index_equal(
            self.hp.thermal_consumption_unit.time.DATES,
            self.tu.DATES)
        self.assertEqual(self.hp.thermal_consumption_unit.name,
                         'hp_therm_cons')
        self.assertEqual(self.hp.thermal_consumption_unit.p.value, {0: 0,
                                                                    1: 0, 2: 0,
                                                                    3: 0})
        self.assertEqual(self.hp.thermal_consumption_unit.energy_type,
                         'Thermal')

    def test_e_cons_unit(self):
        """Checking the elec_consumption_unit of the heat pump is properly
        set"""
        self.assertIsInstance(self.hp.elec_consumption_unit, ConsumptionUnit)
        self.assertEqual(self.hp.elec_consumption_unit.time.DT, self.tu.DT)
        pd.testing.assert_index_equal(
            self.hp.elec_consumption_unit.time.DATES,
            self.tu.DATES)
        self.assertEqual(self.hp.elec_consumption_unit.name, 'hp_elec_cons')
        self.assertEqual(self.hp.elec_consumption_unit.p.value, {0: 0,
                                                                 1: 0, 2: 0,
                                                                 3: 0})
        self.assertEqual(self.hp.elec_consumption_unit.energy_type,
                         'Electrical')

    def test_hp_COP(self):
        """Checking the heat pump COP Quantity is properly set"""
        self.assertIsInstance(self.hp.COP, Quantity)
        self.assertEqual(self.hp.COP.value, 3.)
        self.assertEqual(self.hp.COP.name, 'COP')
        self.assertEqual(self.hp.COP.opt, False)


class TestCOPFloat(unittest.TestCase):
    def setUp(self):
        self.hp_sup = HeatPump(time=TimeUnit(periods=4, dt=1), name='hp_sup',
                               cop=4)

    def test_conversion_constraint(self):
        """Checking the conversion constraint of the heat pump is properly
        set"""
        self.assertIsInstance(self.hp_sup.conversion, DynamicConstraint)
        self.assertEqual(self.hp_sup.conversion.name, 'conversion')
        self.assertEqual(self.hp_sup.conversion.t_range, 'for t in time.I')
        self.assertEqual(self.hp_sup.conversion.exp_t,
                         '{0}_p[t] == {1} * {2}_p[t]'
                         .format('hp_sup_therm_prod', 4,
                                 'hp_sup_elec_cons'))

    def test_wrong_cop_value(self):
        """Asserting an error is raised when the COP value is below 1"""
        with self.assertRaises(ValueError):
            hp_inf = HeatPump(time=TimeUnit(periods=4, dt=1), name='hp_inf',
                              cop=0.5)

    def test_power_flow_constraint(self):
        """Checking the power flow constraint is properly set in the heat
        pump"""
        self.assertIsInstance(self.hp_sup.power_flow, DynamicConstraint)
        self.assertEqual(self.hp_sup.power_flow.name, 'power_flow')
        self.assertEqual(self.hp_sup.power_flow.t_range, 'for t in time.I')
        self.assertEqual(self.hp_sup.power_flow.exp_t, '{0}_p[t]*(1+{1}) =='
                                                       ' {2}_p[t] + {3}_p[t]'
                         .format('hp_sup_therm_prod', 0,
                                 'hp_sup_therm_cons',
                                 'hp_sup_elec_cons'))


class TestCOPList(unittest.TestCase):
    def setUp(self):
        self.cop_list = [4, 3.5, 3.2, 3]
        self.hp = HeatPump(time=TimeUnit(periods=4, dt=1), name='hp',
                           cop=self.cop_list)

    def test_conversion_constraint(self):
        """Checking the conversion constraint is properly set with a COP
        list"""
        self.assertIsInstance(self.hp.conversion, DynamicConstraint)
        self.assertEqual(self.hp.conversion.name, 'conversion')
        self.assertEqual(self.hp.conversion.t_range, 'for t in time.I')
        self.assertEqual(self.hp.conversion.exp_t,
                         '{0}_p[t] == {1}[t] * {2}_p[t]'
                         .format('hp_therm_prod', self.cop_list,
                                 'hp_elec_cons'))

    def test_cop_inf(self):
        """Asserting an error is raised when at least one value of the COP
        list is below 1"""
        with self.assertRaises(ValueError):
            hp_inf = HeatPump(time=TimeUnit(periods=4, dt=1), name='hp_inf',
                              cop=[4, 0.5, 3, 1])

    def test_cop_inf_dict(self):
        """Asserting an error is raised when at least one value of the COP
        dict is below 1"""
        with self.assertRaises(ValueError):
            hp_inf = HeatPump(time=TimeUnit(periods=4, dt=1), name='hp_inf',
                              cop={1: 4, 2: 0.5, 3: 1.2, 4: 1})

    def test_cop_too_long(self):
        """Asserting an error is raised when the cop list is too long
        compared to the studied period"""
        with self.assertRaises(IndexError):
            hp_long = HeatPump(time=TimeUnit(periods=4, dt=1), name='hp_long',
                               cop=[4.5, 1.8, 1, 8, 1])

    def test_cop_wrong_type(self):
        """Asserting an error is raised when the cop value is set to a
        string"""
        with self.assertRaises(TypeError):
            hp_wrong = HeatPump(time=TimeUnit(periods=4, dt=1),
                                name='hp_wrong', cop='lala')
