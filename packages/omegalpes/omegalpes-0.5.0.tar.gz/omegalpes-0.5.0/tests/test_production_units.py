#! usr/bin/env python3
#  -*- coding: utf-8 -*-

""" Unit tests for production_units module

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
    limitations under the License."""

import unittest
from pulp import LpBinary, LpInteger, LpContinuous
from omegalpes.general.time import TimeUnit
from omegalpes.energy.units.production_units import ProductionUnit, \
    FixedProductionUnit, SeveralProductionUnit, \
    SquareProductionUnit, ShiftableProductionUnit
from omegalpes.general.optimisation.elements import *


class TestQuantitiesAndConstraints(unittest.TestCase):
    """ Check the initialisation of the ProductionUnit class"""

    def setUp(self):
        self.time = TimeUnit(periods=24, dt=1)
        self.pu0 = ProductionUnit(time=self.time, name='PU0',
                                  starting_cost=1)
        self.pu3 = ProductionUnit(time=self.time, name='PU0',
                                  co2_out=1, operating_cost=1)

    def test_none_definition(self):
        """ Check if the objectives are none at the initialisation """
        self.assertIsNotNone(self.pu0.start_up)
        self.assertIsNotNone(self.pu0.def_start_up)
        self.assertIsNotNone(self.pu0.def_no_start_up)
        self.assertIsNotNone(self.pu0.def_init_start_up)

        pu1 = ProductionUnit(time=self.time, name='PU1',
                             min_time_on=1)
        self.assertIsNotNone(pu1.start_up)

        pu2 = ProductionUnit(time=self.time, name='PU2',
                             min_time_off=1)
        self.assertIsNotNone(pu2.start_up)

    def test_start_up(self):
        """ Test the creation of the start_up quantity """
        self.assertIs(self.pu0.start_up.name, 'start_up')
        self.assertEqual(self.pu0.start_up.description, 'The EnergyUnit is '
                                                        'starting :1 or not :0')
        self.assertIs(self.pu0.start_up.vtype, LpBinary)
        self.assertIs(self.pu0.start_up.vlen, self.time.LEN)
        self.assertIs(self.pu0.start_up.parent, self.pu0)

    def test_switch_off(self):
        """ Test the creation of the switch_off quantity """
        self.pu0._add_switch_off()
        self.assertIs(self.pu0.switch_off.name, 'switch_off')
        self.assertEqual(self.pu0.switch_off.description,
                         'The EnergyUnit is '
                         'switching off :1 or '
                         'not :0')
        self.assertIs(self.pu0.switch_off.vtype, LpBinary)
        self.assertIs(self.pu0.switch_off.vlen, self.time.LEN)
        self.assertIs(self.pu0.switch_off.parent, self.pu0)

    def test_def_start_up(self):
        """ Test the creation of the def_start_up constraint """
        self.assertIs(self.pu0.def_start_up.__class__,
                      DefinitionDynamicConstraint)
        self.assertIs(self.pu0.def_start_up.name, 'def_start_up')
        self.assertEqual(self.pu0.def_start_up.exp_t,
                         '{0}_u[t+1] - {0}_u[t] <= '
                         '{0}_start_up[t+1]'.format(self.pu0.name))
        self.assertEqual(self.pu0.def_start_up.t_range, 'for t in time.I['
                                                        ':-1]')

    def test_def_no_start_up(self):
        """ Test the creation of the def_start_up constraint """
        self.assertIs(self.pu0.def_no_start_up.__class__,
                      DefinitionDynamicConstraint)
        self.assertIs(self.pu0.def_no_start_up.name, 'def_no_start_up')
        self.assertEqual(self.pu0.def_no_start_up.exp_t,
                         '{0}_start_up[t+1] <= ({0}_u[t+1] - {0}_u[t] + '
                         '1)/2'.format(self.pu0.name))
        self.assertEqual(self.pu0.def_no_start_up.t_range, 'for t in time.I['
                                                           ':-1]')

    def test_def_switch_off(self):
        """ Test the creation of the def_switch_off constraint """
        self.pu0._add_switch_off()
        self.assertIs(self.pu0.def_switch_off.__class__,
                      DefinitionDynamicConstraint)
        self.assertIs(self.pu0.def_switch_off.name, 'def_switch_off')
        self.assertEqual(self.pu0.def_switch_off.exp_t,
                         '{0}_switch_off[t+1] == {0}_start_up[t+1] '
                         '+ {0}_u[t] - {0}_u[t+1]'.format(self.pu0.name))
        self.assertEqual(self.pu0.def_switch_off.t_range, 'for t in time.I['
                                                          ':-1]')

    def test_def_init_start_up(self):
        """ Test the creation of the def_init_start_up constraint """
        self.assertIs(self.pu0.def_init_start_up.__class__,
                      DefinitionConstraint)
        self.assertIs(self.pu0.def_init_start_up.name, 'def_init_start_up')
        self.assertEqual(self.pu0.def_init_start_up.exp,
                         '{0}_start_up[0] == {0}_u[0]'.format(self.pu0.name))

    def test_def_init_switch_off(self):
        """ Test the creation of the def_init_switch_off constraint """
        self.pu0._add_switch_off()
        self.assertIs(self.pu0.def_init_switch_off.__class__,
                      DefinitionConstraint)
        self.assertIs(self.pu0.def_init_switch_off.name, 'def_init_switch_off')
        self.assertEqual(self.pu0.def_init_switch_off.exp,
                         '{0}_switch_off[0] == 0'.format(self.pu0.name))

    def test_co2_emissions(self):
        """ Test the creation of the co2_emissions quantity """
        self.assertIs(self.pu3.co2_emissions.name, 'co2_emissions')
        self.assertEqual(self.pu3.co2_emissions.description,
                         'Dynamic CO2 emissions generated by the '
                         'EnergyUnit')
        self.assertEqual(self.pu3.co2_emissions.lb, 0)
        self.assertIs(self.pu3.co2_emissions.vlen, self.time.LEN)
        self.assertEqual(self.pu3.co2_emissions.parent, self.pu3)

    def test_starting_cost(self):
        """ Test the creation of the starting_cost quantity """
        self.assertIs(self.pu0.starting_cost.name, 'starting_cost')
        self.assertEqual(self.pu0.starting_cost.description,
                         'Dynamic cost for the start of EnergyUnit')
        self.assertEqual(self.pu0.starting_cost.lb, 0)
        self.assertIs(self.pu0.starting_cost.vlen, self.time.LEN)
        self.assertIs(self.pu0.starting_cost.parent, self.pu0)

    def test_operating_cost(self):
        """ Test the creation of the operating_cost quantity """
        self.assertIs(self.pu3.operating_cost.name, 'operating_cost')
        self.assertEqual(self.pu3.operating_cost.description,
                         'Dynamic cost for the operation of the EnergyUnit')
        self.assertEqual(self.pu3.operating_cost.lb, 0)
        self.assertIs(self.pu3.operating_cost.vlen, self.time.LEN)
        self.assertIs(self.pu3.operating_cost.parent, self.pu3)


class TestTheConstraintsMethods(unittest.TestCase):
    """ Check the constraint methods of the ProductionUnit class"""

    def setUp(self):
        self.time = TimeUnit(periods=24, dt=1)
        self.pu0 = ProductionUnit(time=self.time, name='PU0')
        self.pu_av_hours = ProductionUnit(time=self.time, name='PU0',
                                          availability_hours=10)
        self.pu_min_time_on = ProductionUnit(time=self.time, name='PU0',
                                             min_time_on=10)
        self.pu_min_time_off = ProductionUnit(time=self.time, name='PU0',
                                              min_time_off=10)
        self.pu_max_ramp_up = ProductionUnit(time=self.time, name='PU0',
                                             max_ramp_up=10)
        self.pu_max_ramp_down = ProductionUnit(time=self.time, name='PU0',
                                               max_ramp_down=10)

    def test_def_availability_cst_none(self):
        """ Test the _def_availability_cst method if availability_hours is
        none """
        self.assertIsNone(self.pu0.set_availability)

    def test_def_availability_cst_not_none(self):
        """ Test the _def_availability_cst method if availability_hours is not
        none """
        self.assertIs(self.pu_av_hours.set_availability.__class__,
                      ActorConstraint)
        self.assertIs(self.pu_av_hours.set_availability.name,
                      'set_availability')
        self.assertEqual(self.pu_av_hours.set_availability.exp,
                         'lpSum({dt} * {name}_u[t] for t in time.I) <= '
                         '{av_h}'.format(dt=self.time.DT,
                                         name=self.pu_av_hours.name,
                                         av_h=10))
        self.assertIs(self.pu_av_hours.set_availability.parent,
                      self.pu_av_hours)

    def test_def_min_up_time_cst_none(self):
        """ Test the _def_min_up_time_cst method if set_min_up_time is
        none """
        self.assertIsNone(self.pu0.set_min_up_time)

    def test_def_min_up_time_cst_not_none(self):
        """ Test the _def_min_up_time_cst method if set_min_up_time is not
        none """
        self.assertIs(self.pu_min_time_on.set_min_up_time.__class__,
                      TechnicalDynamicConstraint)
        self.assertIs(self.pu_min_time_on.set_min_up_time.name,
                      'set_min_up_time')
        self.assertEqual(self.pu_min_time_on.set_min_up_time.exp_t,
                         '{0}_u[t] >= lpSum({0}_start_up[i] for i in range('
                         'max(t - {1} + 1, 0), t))'.format(
                             self.pu_min_time_on.name, 10))
        self.assertEqual(self.pu_min_time_on.set_min_up_time.t_range,
                         'for t in time.I')

    def test_def_min_down_time_cst_none(self):
        """ Test the _def_min_down_time_cst method if set_min_down_time is
        none """
        self.assertIsNone(self.pu0.set_min_down_time)

    def test_def_min_down_time_cst_not_none(self):
        """ Test the _def_min_down_time_cst method if set_min_down_time is not
        none """
        self.assertIs(self.pu_min_time_off.set_min_down_time.__class__,
                      TechnicalDynamicConstraint)
        self.assertIs(self.pu_min_time_off.set_min_down_time.name,
                      'set_min_down_time')
        self.assertEqual(self.pu_min_time_off.set_min_down_time.exp_t,
                         '1 - {0}_u[t] >= lpSum({0}_switch_off[i] for i in '
                         'range(max(t - {1} + 1, 0), t))'.format(
                             self.pu_min_time_off.name, 10))
        self.assertEqual(self.pu_min_time_off.set_min_down_time.t_range,
                         'for t in time.I')

    def test_def_max_ramp_up_cst_none(self):
        """ Test the _def_max_ramp_up_cst method if set_max_ramp_up is
        none """
        self.assertIsNone(self.pu0.set_max_ramp_up)

    def test_def_max_ramp_up_cst_not_none(self):
        """ Test the _def_max_ramp_up_cst method if set_max_ramp_up is not
        none """
        self.assertIs(self.pu_max_ramp_up.set_max_ramp_up.__class__,
                      TechnicalDynamicConstraint)
        self.assertIs(self.pu_max_ramp_up.set_max_ramp_up.name,
                      'set_max_ramp_up')
        self.assertEqual(self.pu_max_ramp_up.set_max_ramp_up.exp_t,
                         '{0}_p[t+1] - {0}_p[t] <= {1}'.format(
                             self.pu_max_ramp_up.name, 10))
        self.assertEqual(self.pu_max_ramp_up.set_max_ramp_up.t_range,
                         'for t in time.I[:-1]')

    def test_def_max_ramp_down_cst_none(self):
        """ Test the _def_max_ramp_down_cst method if set_max_ramp_down is
        none """
        self.assertIsNone(self.pu0.set_max_ramp_down)

    def test_def_max_ramp_down_cst_not_none(self):
        """ Test the _def_max_ramp_down_cst method if set_max_ramp_down is not
        none """
        self.assertIs(self.pu_max_ramp_down.set_max_ramp_down.__class__,
                      TechnicalDynamicConstraint)
        self.assertIs(self.pu_max_ramp_down.set_max_ramp_down.name,
                      'set_max_ramp_down')
        self.assertEqual(self.pu_max_ramp_down.set_max_ramp_down.exp_t,
                         '{0}_p[t] - {0}_p[t+1] <= {1}'.format(
                             self.pu_max_ramp_down.name, 10))
        self.assertEqual(self.pu_max_ramp_down.set_max_ramp_down.t_range,
                         'for t in time.I[:-1]')


class TestCalculationMethods(unittest.TestCase):
    """ Check the calculation methods of the ProductionUnit class"""

    def test_def_co2_emissions_calc_none(self):
        """ Test the _def_co2_emissions_calc method if co2_out is none """
        pu0 = ProductionUnit(time=TimeUnit(periods=24, dt=1), name='PU0')
        self.assertIsNone(pu0.co2_emissions)

    def test_def_co2_emissions_calc_int(self):
        """ Test the _def_co2_emissions_calc method if co2_out is an int """
        pu_co2_int = ProductionUnit(time=TimeUnit(periods=24, dt=1),
                                    name='PU0', co2_out=10)
        self.assertEqual(pu_co2_int.calc_co2_emissions.__class__,
                         DefinitionDynamicConstraint)
        self.assertEqual(pu_co2_int.calc_co2_emissions.name,
                         'calc_co2_emissions')
        self.assertEqual(pu_co2_int.calc_co2_emissions.exp_t,
                         '{0}_co2_emissions[t] == {1} * '
                         '{0}_p[t] * time.DT'.format(pu_co2_int.name, 10))
        self.assertEqual(pu_co2_int.calc_co2_emissions.parent, pu_co2_int)

    def test_def_co2_emissions_calc_float(self):
        """ Test the _def_co2_emissions_calc method if co2_out is a float """
        pu_co2_float = ProductionUnit(time=TimeUnit(periods=24, dt=1),
                                      name='PU0', co2_out=1.5)
        self.assertEqual(pu_co2_float.calc_co2_emissions.__class__,
                         DefinitionDynamicConstraint)
        self.assertEqual(pu_co2_float.calc_co2_emissions.name,
                         'calc_co2_emissions')
        self.assertEqual(pu_co2_float.calc_co2_emissions.exp_t,
                         '{0}_co2_emissions[t] == {1} * '
                         '{0}_p[t] * time.DT'.format(pu_co2_float.name, 1.5))
        self.assertEqual(pu_co2_float.calc_co2_emissions.parent,
                         pu_co2_float)

    def test_def_co2_emissions_calc_list(self):
        """ Test the _def_co2_emissions_calc method if co2_out is a
        incomplete and complete list """
        with self.assertRaises(IndexError):
            ProductionUnit(time=TimeUnit(periods=24, dt=1), name='PU0',
                           co2_out=[1])

        pu_co2_complete_list = ProductionUnit(time=TimeUnit(periods=2, dt=1),
                                              name='PU0', co2_out=[1, 2])
        self.assertEqual(pu_co2_complete_list.calc_co2_emissions.__class__,
                         DefinitionDynamicConstraint)
        self.assertEqual(pu_co2_complete_list.calc_co2_emissions.name,
                         'calc_co2_emissions')
        self.assertEqual(pu_co2_complete_list.calc_co2_emissions.exp_t,
                         '{0}_co2_emissions[t] == {1}[t] * '
                         '{0}_p[t] * time.DT'.format(pu_co2_complete_list.name,
                                                  [1, 2]))
        self.assertEqual(pu_co2_complete_list.calc_co2_emissions.parent,
                         pu_co2_complete_list)

    def test_def_co2_emissions_calc_other(self):
        """ Test the _def_co2_emissions_calc method if co2_out is a dictionary
        """
        with self.assertRaises(TypeError):
            ProductionUnit(time=TimeUnit(periods=24, dt=1), name='PU0',
                           co2_out={0: 1})

    def test_def_starting_cost_calc_none(self):
        """ Test the _def_starting_cost_cal method if start_cost is none """
        pu0 = ProductionUnit(time=TimeUnit(periods=24, dt=1), name='PU0')
        self.assertIsNone(pu0.starting_cost)

    def test_def_starting_cost_calc_not_none(self):
        """ Test the _def_starting_cost_cal method if start_cost is not none """
        pu_starting_cost = ProductionUnit(time=TimeUnit(periods=24, dt=1),
                                          name='PU0', starting_cost=1)
        self.assertIs(pu_starting_cost.calc_start_cost.name, 'calc_start_cost')
        self.assertIs(pu_starting_cost.calc_start_cost.__class__,
                      DefinitionDynamicConstraint)
        self.assertEqual(pu_starting_cost.calc_start_cost.exp_t,
                         '{0}_starting_cost[t] == {1} * {0}_start_up[t]'.format(
                             pu_starting_cost.name, 1))
        self.assertEqual(pu_starting_cost.calc_start_cost.t_range,
                         'for t in time.I[:-1]')

    def test_def_operating_cost_calc_none(self):
        """ Test the _def_operating_cost_calc method if operating_cost is
        none """
        pu0 = ProductionUnit(time=TimeUnit(periods=24, dt=1), name='PU0')
        self.assertIsNone(pu0.operating_cost)

    def test_def_operating_cost_calc_int(self):
        """ Test the _def_operating_cost_calc method if operating_cost is an
        int """
        pu_op_cost_int = ProductionUnit(time=TimeUnit(periods=24, dt=1),
                                        name='PU0', operating_cost=10)
        self.assertEqual(pu_op_cost_int.calc_operating_cost.__class__,
                         DefinitionDynamicConstraint)
        self.assertEqual(pu_op_cost_int.calc_operating_cost.name,
                         'calc_operating_cost')
        self.assertEqual(pu_op_cost_int.calc_operating_cost.exp_t,
                         '{0}_operating_cost[t] == {1} * {0}_p[t] * time.DT'
                         .format(pu_op_cost_int.name, 10))
        self.assertEqual(pu_op_cost_int.calc_operating_cost.parent,
                         pu_op_cost_int)

    def test_def_operating_cost_calc_float(self):
        """ Test the _def_operating_cost_calc method if operating_cost is a
        float """
        pu_operating_cost_float = ProductionUnit(
            time=TimeUnit(periods=24, dt=1),
            name='PU0', operating_cost=1.5)
        self.assertEqual(pu_operating_cost_float.calc_operating_cost.__class__,
                         DefinitionDynamicConstraint)
        self.assertEqual(pu_operating_cost_float.calc_operating_cost.name,
                         'calc_operating_cost')
        self.assertEqual(pu_operating_cost_float.calc_operating_cost.exp_t,
                         '{0}_operating_cost[t] == {1} * {0}_p[t] * time.DT'
                         .format(pu_operating_cost_float.name, 1.5))
        self.assertEqual(pu_operating_cost_float.calc_operating_cost.parent,
                         pu_operating_cost_float)

    def test_def_operating_cost_calc_list(self):
        """ Test the _def_operating_cost_calc method if operating_cost is a
        incomplete and complete list """
        with self.assertRaises(IndexError):
            ProductionUnit(time=TimeUnit(periods=24, dt=1), name='PU0',
                           operating_cost=[1])

        pu_op_cost_complete_list = ProductionUnit(time=TimeUnit(
            periods=2, dt=1), name='PU0', operating_cost=[1, 2])
        self.assertEqual(pu_op_cost_complete_list.calc_operating_cost.__class__,
                         DefinitionDynamicConstraint)
        self.assertEqual(pu_op_cost_complete_list.calc_operating_cost.name,
                         'calc_operating_cost')
        self.assertEqual(pu_op_cost_complete_list.calc_operating_cost.exp_t,
                         '{0}_operating_cost[t] == {1}[t] * {0}_p[t]'
                         ' * time.DT'.format(pu_op_cost_complete_list.name,
                                             [1, 2]))
        self.assertEqual(pu_op_cost_complete_list.calc_operating_cost.parent,
                         pu_op_cost_complete_list)

    def test_def_operating_cost_calc_other(self):
        """ Test the _def_operating_cost_calc method if operating_cost is a
        dictionary """
        with self.assertRaises(TypeError):
            ProductionUnit(time=TimeUnit(periods=24, dt=1), name='PU0',
                           co2_out={0: 1})


class TestObjectives(unittest.TestCase):
    """ Test the objective methods """

    def setUp(self):
        self.pu0 = ProductionUnit(TimeUnit(periods=24, dt=1), name='PU0',
                                  starting_cost=4)

    def test_minimize_starting_cost(self):
        """ Check min_start_cost objective
        """
        self.pu0.minimize_starting_cost(weight=2)
        self.assertIs(self.pu0.min_start_cost.name,
                      'min_start_cost')
        self.assertIs(self.pu0.min_start_cost.__class__, Objective)
        self.assertEqual(self.pu0.min_start_cost.exp,
                         'lpSum({0}_starting_cost[t] for t in time.I)'
                         .format(self.pu0.name))
        self.assertIs(self.pu0.min_start_cost.parent, self.pu0)
        self.assertIs(self.pu0.min_start_cost.weight, 2)

    def test_minimize_operating_cost(self):
        """ Check the min_operating_cost objective  """
        self.pu0._add_operating_cost(5)
        self.pu0.minimize_operating_cost(weight=2)
        self.assertIs(self.pu0.min_operating_cost.name, 'min_operating_cost')
        self.assertIs(self.pu0.min_operating_cost.__class__, Objective)
        self.assertEqual(self.pu0.min_operating_cost.exp,
                         'lpSum({0}_operating_cost[t] for t in time.I)'
                         .format(self.pu0.name))
        self.assertIs(self.pu0.min_operating_cost.parent, self.pu0)
        self.assertIs(self.pu0.min_operating_cost.weight, 2)

    def test_minimize_production(self):
        """ Check min_production objective """
        self.pu0.minimize_production(weight=2)
        self.assertIs(self.pu0.min_energy.name,
                      'min_production')
        self.assertIs(self.pu0.min_energy.__class__, Objective)
        self.assertEqual(self.pu0.min_energy.exp,
                         'lpSum({}_p[t] for t in time.I)'.format(self.pu0.name))
        self.assertIs(self.pu0.min_energy.weight, 2)

    def test_minimize_time_of_use(self):
        """ Check min_time_of_use objective """
        self.pu0.minimize_time_of_use(weight=2)
        self.assertIs(self.pu0.min_time_of_use.name,
                      'min_time_of_use')
        self.assertIs(self.pu0.min_time_of_use.__class__, Objective)
        self.assertEqual(self.pu0.min_time_of_use.exp,
                         'lpSum({}_u[t] for t in time.I)'.format(self.pu0.name))
        self.assertIs(self.pu0.min_time_of_use.weight, 2)


class TestFixedProductionUnit(unittest.TestCase):
    """ Check the FixedProductionUnit class """

    def test_variable_production_none_p(self):
        """ Check if it raises an error if no energy profile is done for a
        FixedProductionUnit """
        with self.assertRaises(TypeError):
            FixedProductionUnit(TimeUnit(periods=24, dt=1))


class TestSeveralProductionUnit(unittest.TestCase):
    """ Check the SeveralProductionUnit class """

    def test_production_curve_quantity(self):
        """ Test the creation of the production_curve quantity """
        spu = SeveralProductionUnit(TimeUnit(periods=2, dt=1), 'SPU',
                                    fixed_prod=[1, 2])
        self.assertIs(spu.power_curve.name, 'power_curve')
        self.assertEqual(spu.power_curve.opt, [False, False])
        self.assertEqual(spu.power_curve.value, [1, 2])
        self.assertEqual(spu.power_curve.vlen,
                         TimeUnit(periods=2, dt=1).LEN)

    def test_nb_unit_quantity(self):
        """ Test the creation of the nb_unit quantity """
        spu = SeveralProductionUnit(TimeUnit(periods=2, dt=1), 'SPU',
                                    fixed_prod=[1, 2])
        self.assertIs(spu.nb_unit.name, 'nb_unit')
        self.assertEqual(spu.nb_unit.opt, True)
        self.assertIs(spu.nb_unit.vtype, LpInteger)
        self.assertEqual(spu.nb_unit.vlen, 1)

    def test_nb_unit_constraint(self):
        """ Test the creation of the calc_prod_with_nb_unit_cst constraint """
        spu = SeveralProductionUnit(TimeUnit(periods=2, dt=1), 'SPU',
                                    fixed_prod=[1, 2])
        self.assertIs(spu.calc_power_with_nb_unit_cst.__class__,
                      DefinitionDynamicConstraint)
        self.assertIs(spu.calc_power_with_nb_unit_cst.name,
                      'calc_power_with_nb_unit')
        self.assertEqual(spu.calc_power_with_nb_unit_cst.exp_t,
                         '{0}_p[t] == {0}_nb_unit * {0}_power_curve[t]'.format(
                             spu.name))
        self.assertEqual(spu.calc_power_with_nb_unit_cst.t_range, 'for t in '
                                                                  'time.I')
        self.assertIs(spu.calc_power_with_nb_unit_cst.parent, spu)


class TestSquareProductionUnit(unittest.TestCase):
    """ Check the SquareProductionUnit class """

    def test_duration_error(self):
        """ Test if it raises an error if the duration is under 1"""
        with self.assertRaises(ValueError):
            SquareProductionUnit(TimeUnit(periods=24, dt=1), 'SPU',
                                 p_square=1, n_square=1, t_between_sq=0,
                                 duration=0)


class TestShiftableProductionUnit(unittest.TestCase):
    """ Check the ShiftableProductionUnit class """

    def setUp(self):
        self.shpu_mandatory = ShiftableProductionUnit(TimeUnit(periods=24,
                                                               dt=1),
                                                      'SHPU', [1, 2])
        self.shpu_not_mandatory = ShiftableProductionUnit(TimeUnit(periods=24,
                                                                   dt=1),
                                                          'SHPU', [1, 2],
                                                          mandatory=False)

    def test_mandatory_true(self):
        """ Test the duration constraint if mandatory is true """
        self.assertIs(self.shpu_mandatory.e_tot.lb,
                      self.shpu_mandatory.e_tot.lb)

    def test_mandatory_false(self):
        """ Test the duration constraint if mandatory is false """
        self.assertIs(self.shpu_not_mandatory.e_tot.lb, 0)

    def set_energy_limits_on_time_period_mandatory_true(self):
        """ Test the quantity created by the set_energy_limits_on_time_period
        method, and the emin definition"""
        self.assertEqual(self.shpu_not_mandatory.set_e_min.name,
                         'set_e_min')

    def set_energy_limits_on_time_period_mandatory_false(self):
        """ Test the quantity created by the set_energy_limits_on_time_period
        method, and the emin definition"""
        self.assertEqual(self.shpu_not_mandatory.set_e_min.name,
                         'set_e_max')

    def test_power_values_quantity(self):
        """ Test the creation of the power_values quantity """
        self.assertIs(self.shpu_not_mandatory.power_values.name, 'power_values')
        self.assertEqual(self.shpu_not_mandatory.power_values.opt,
                         [False, False])
        self.assertEqual(self.shpu_not_mandatory.power_values.value, [1, 2])
        self.assertIs(self.shpu_not_mandatory.power_values.parent,
                      self.shpu_not_mandatory)
