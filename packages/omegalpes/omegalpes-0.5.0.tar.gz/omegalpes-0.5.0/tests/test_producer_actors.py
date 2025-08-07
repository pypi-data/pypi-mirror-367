#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Unit tests for the module producer_actors.py, defining constraints and
objectives for producer actor type.

..

    Copyright 2018 G2Elab / MAGE

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
from omegalpes.actor.operator_actors.producer_actors import Producer
from omegalpes.energy.units.production_units import ProductionUnit, \
    VariableProductionUnit
from omegalpes.general.time import TimeUnit
from omegalpes.general.optimisation.model import OptimisationModel
from omegalpes.energy.energy_nodes import EnergyNode


class TestProducerActorObjectives(unittest.TestCase):
    """Test of ProducerActor objectives"""

    def setUp(self):
        self.time = TimeUnit(periods=2, dt=1)
        self.prod0 = VariableProductionUnit(time=self.time, name='prod0')
        self.prod1 = VariableProductionUnit(time=self.time, name='prod1')
        self.pa = Producer(name='pa', operated_unit_list=[self.prod0,
                                                          self.prod1])
        self.node = EnergyNode(time=self.time, name='node')
        self.model = OptimisationModel(time=self.time, name='OM')

    def test_maximize_production(self):
        """ Test the maximize_production objective on two production units"""
        self.pa.maximize_production()
        self.node.connect_units(self.prod0, self.prod1)
        self.model.add_nodes_and_actors(self.node, self.pa)
        self.model.solve_and_update()
        self.assertEqual(self.prod0.get_objectives_name_list(),
                         ['max_production'])
        self.assertEqual(self.prod1.get_objectives_name_list(),
                         ['max_production'])
        self.assertEqual(self.model.get_model_objectives_name_list(),
                         ['prod0_max_production', 'prod1_max_production'])

    def test_minimize_production(self):
        """ Test the minimize_production objective on two production units"""
        self.pa.minimize_production()
        self.node.connect_units(self.prod0, self.prod1)
        self.model.add_nodes_and_actors(self.node, self.pa)
        self.model.solve_and_update()
        self.assertEqual(self.prod0.get_objectives_name_list(),
                         ['min_production'])
        self.assertEqual(self.prod1.get_objectives_name_list(),
                         ['min_production'])
        self.assertEqual(self.model.get_model_objectives_name_list(),
                         ['prod0_min_production', 'prod1_min_production'])

    def test_minimize_time_of_use(self):
        """ Test the minimize_time_of_use objective on two production
        units"""
        self.pa.minimize_time_of_use()
        self.node.connect_units(self.prod0, self.prod1)
        self.model.add_nodes_and_actors(self.node, self.pa)
        self.model.solve_and_update()
        self.assertEqual(self.prod0.get_objectives_name_list(),
                         ['min_time_of_use'])
        self.assertEqual(self.prod1.get_objectives_name_list(),
                         ['min_time_of_use'])
        self.assertEqual(self.model.get_model_objectives_name_list(),
                         ['prod0_min_time_of_use',
                          'prod1_min_time_of_use'])

    def test_minimize_co2_emissions(self):
        """ Test the minimize_co2_production objective on two production
        units"""
        self.prod0._add_co2_emissions([1, 1])
        self.prod1._add_co2_emissions([2, 2])
        self.pa.minimize_co2_emissions()
        self.node.connect_units(self.prod0, self.prod1)
        self.model.add_nodes_and_actors(self.node, self.pa)
        self.model.solve_and_update()
        self.assertEqual(self.prod0.get_objectives_name_list(),
                         ['min_CO2_emissions'])
        self.assertEqual(self.prod1.get_objectives_name_list(),
                         ['min_CO2_emissions'])
        self.assertEqual(self.model.get_model_objectives_name_list(),
                         ['prod0_min_CO2_emissions',
                          'prod1_min_CO2_emissions'])

    def test_minimize_costs(self):
        """ Test the minimize_costs objective considering starting and
        operating costs on two production units"""
        self.prod0._add_operating_cost([1, 1])
        self.prod1._add_operating_cost([2, 2])
        self.prod0._add_starting_cost([3, 3])
        self.prod1._add_starting_cost([4, 4])
        self.pa.minimize_costs()
        self.node.connect_units(self.prod0, self.prod1)
        self.model.add_nodes_and_actors(self.node, self.pa)
        self.model.solve_and_update()
        self.assertEqual(self.prod0.get_objectives_name_list(),
                         ['min_start_cost', 'min_operating_cost'])
        self.assertEqual(self.prod1.get_objectives_name_list(),
                         ['min_start_cost', 'min_operating_cost'])
        self.assertEqual(self.model.get_model_objectives_name_list(),
                         ['prod0_min_start_cost',
                          'prod0_min_operating_cost',
                          'prod1_min_start_cost',
                          'prod1_min_operating_cost'])

    def test_minimize_operating_costs(self):
        """ Test the minimize_operating_cost objective on two production
        units"""
        self.prod0._add_operating_cost([1, 1])
        self.prod1._add_operating_cost([2, 2])
        self.pa.minimize_operating_cost()
        self.node.connect_units(self.prod0, self.prod1)
        self.model.add_nodes_and_actors(self.node, self.pa)
        self.model.solve_and_update()
        self.assertEqual(self.prod0.get_objectives_name_list(),
                         ['min_operating_cost'])
        self.assertEqual(self.prod1.get_objectives_name_list(),
                         ['min_operating_cost'])
        self.assertEqual(self.model.get_model_objectives_name_list(),
                         ['prod0_min_operating_cost',
                          'prod1_min_operating_cost'])

    def test_minimize_starting_costs(self):
        """ Test the minimize_starting_cost objective on two production
        units"""
        self.prod0._add_starting_cost([3, 3])
        self.prod1._add_starting_cost([4, 4])
        self.pa.minimize_starting_cost()
        self.node.connect_units(self.prod0, self.prod1)
        self.model.add_nodes_and_actors(self.node, self.pa)
        self.model.solve_and_update()
        self.assertEqual(self.prod0.get_objectives_name_list(),
                         ['min_start_cost'])
        self.assertEqual(self.prod1.get_objectives_name_list(),
                         ['min_start_cost'])
        self.assertEqual(self.model.get_model_objectives_name_list(),
                         ['prod0_min_start_cost',
                          'prod1_min_start_cost'])


class TestProducerActorConstraints(unittest.TestCase):
    """Test of ProducerActor constraints"""

    def setUp(self):
        self.time = TimeUnit(periods=2, dt=1)
        self.prod0 = VariableProductionUnit(time=self.time, name='prod0')
        self.prod1 = VariableProductionUnit(time=self.time, name='prod1')
        self.pa = Producer(name='pa', operated_unit_list=[self.prod0,
                                                          self.prod1])
        self.node = EnergyNode(time=self.time, name='node')
        self.model = OptimisationModel(time=self.time, name='OM')

    def test_energy_production_minimum(self):
        """ Test the energy_production_minimum constraint on two production
        units """
        self.pa.add_energy_production_minimum(min_e_tot=10)
        self.node.connect_units(self.prod0, self.prod1)
        self.model.add_nodes_and_actors(self.node, self.pa)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'prod0_calc_e_tot',
                          'prod0_on_off_max', 'prod0_on_off_min',
                          'prod1_calc_e_tot', 'prod1_on_off_max',
                          'prod1_on_off_min',
                          'pa_min_energy_prod_prod0_prod1'])
        self.assertEqual(self.model._model_constraints_list[7].exp,
                         'lpSum(prod0_p[t] + prod1_p[t] for t in time.I) >= '
                         '10')

    def test_energy_production_minimum_without_int_or_float(self):
        """ Test it raises an error if min_e_tot is a list"""
        with self.assertRaises(TypeError):
            self.pa.add_energy_production_minimum(min_e_tot=[10, 10])

    def test_energy_production_maximum(self):
        """ Test the energy_production_maximum constraint on two production
        units """
        self.pa.add_energy_production_maximum(max_e_tot=10)
        self.node.connect_units(self.prod0, self.prod1)
        self.model.add_nodes_and_actors(self.node, self.pa)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'prod0_calc_e_tot',
                          'prod0_on_off_max', 'prod0_on_off_min',
                          'prod1_calc_e_tot', 'prod1_on_off_max',
                          'prod1_on_off_min',
                          'pa_max_energy_prod_prod0_prod1'])
        self.assertEqual(self.model._model_constraints_list[7].exp,
                         'lpSum(prod0_p[t] + prod1_p[t]  for t in time.I) <= '
                         '10')

    def test_energy_production_maximum_without_int_or_float(self):
        """ Test it raises an error if max_e_tot is a list"""
        with self.assertRaises(TypeError):
            self.pa.add_energy_production_maximum(max_e_tot=[10, 10])

    def test_power_production_total_minimum(self):
        """ Test the add_power_production_minimum constraint on two
        production units """
        self.pa.add_power_production_total_minimum(time=self.time, min_p=10)
        self.node.connect_units(self.prod0, self.prod1)
        self.model.add_nodes_and_actors(self.node, self.pa)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'prod0_calc_e_tot',
                          'prod0_on_off_max', 'prod0_on_off_min',
                          'prod1_calc_e_tot', 'prod1_on_off_max',
                          'prod1_on_off_min',
                          'pa_min_total_power_prod_prod0_prod1'])
        self.assertEqual(self.model._model_constraints_list[7].exp,
                         'prod0_p[t] + prod1_p[t] >= 10')

    def test_power_production_total_minimum_with_list(self):
        """ Test the add_power_production_total_minimum constraint on two
        production units if min_p is a list"""
        self.pa.add_power_production_total_minimum(time=self.time,
                                                   min_p=[10, 10])
        self.node.connect_units(self.prod0, self.prod1)
        self.model.add_nodes_and_actors(self.node, self.pa)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'prod0_calc_e_tot',
                          'prod0_on_off_max', 'prod0_on_off_min',
                          'prod1_calc_e_tot', 'prod1_on_off_max',
                          'prod1_on_off_min',
                          'pa_min_total_power_prod_prod0_prod1'])
        self.assertEqual(self.model._model_constraints_list[7].exp,
                         'prod0_p[t] + prod1_p[t] >= [10, 10][t] for t in '
                         'time.I')

    def test_power_production_total_minimum_with_wrong_list(self):
        """ Test it raises an error if min_p is a list with a wrong
        dimension considering the unit time"""
        with self.assertRaises(IndexError):
            self.pa.add_power_production_total_minimum(time=self.time,
                                                       min_p=[10])

    def test_power_production_total_minimum_with_dic(self):
        """ Test it raises an error if min_p is a dictionary"""
        with self.assertRaises(TypeError):
            self.pa.add_power_production_total_minimum(time=self.time,
                                                       min_p={10})

    def test_power_production_by_unit_minimum(self):
        """ Test the add_power_production_by_unit_minimum constraint on two
        production units """
        self.pa.add_power_production_by_unit_minimum(time=self.time, min_p=10)
        self.node.connect_units(self.prod0, self.prod1)
        self.model.add_nodes_and_actors(self.node, self.pa)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'prod0_calc_e_tot',
                          'prod0_on_off_max', 'prod0_on_off_min',
                          'prod1_calc_e_tot', 'prod1_on_off_max',
                          'prod1_on_off_min',
                          'pa_min_by_unit_power_prod_prod0',
                          'pa_min_by_unit_power_prod_prod1'])
        self.assertEqual(self.model._model_constraints_list[7].exp,
                         'prod0_p[t] >= 10 for t in time.I')
        self.assertEqual(self.model._model_constraints_list[8].exp,
                         'prod1_p[t] >= 10 for t in time.I')

    def test_power_production_by_unit_minimum_with_list(self):
        """ Test the add_power_production_by_unit_minimum constraint on two
        production units if min_p is a list"""
        self.pa.add_power_production_by_unit_minimum(time=self.time,
                                                     min_p=[10, 10])
        self.node.connect_units(self.prod0, self.prod1)
        self.model.add_nodes_and_actors(self.node, self.pa)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'prod0_calc_e_tot',
                          'prod0_on_off_max', 'prod0_on_off_min',
                          'prod1_calc_e_tot', 'prod1_on_off_max',
                          'prod1_on_off_min',
                          'pa_min_by_unit_power_prod_prod0',
                          'pa_min_by_unit_power_prod_prod1'])
        self.assertEqual(self.model._model_constraints_list[7].exp,
                         'prod0_p[t] >= [10, 10][t] for t in time.I')
        self.assertEqual(self.model._model_constraints_list[8].exp,
                         'prod1_p[t] >= [10, 10][t] for t in time.I')

    def test_power_production_by_unit_minimum_with_wrong_list(self):
        """ Test it raises an error if min_p is a list with a wrong
        dimension considering the unit time"""
        with self.assertRaises(IndexError):
            self.pa.add_power_production_by_unit_minimum(time=self.time,
                                                         min_p=[10])

    def test_power_production_by_unit_minimum_with_dic(self):
        """ Test it raises an error if min_p is a dictionary"""
        with self.assertRaises(TypeError):
            self.pa.add_power_production_by_unit_minimum(time=self.time,
                                                         min_p={10})

    def test_power_production_total_maximum(self):
        """ Test the power_production_maximum constraint on two production
        units"""
        self.pa.add_power_production_total_maximum(time=self.time, max_p=10)
        self.node.connect_units(self.prod0, self.prod1)
        self.model.add_nodes_and_actors(self.node, self.pa)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'prod0_calc_e_tot',
                          'prod0_on_off_max', 'prod0_on_off_min',
                          'prod1_calc_e_tot', 'prod1_on_off_max',
                          'prod1_on_off_min',
                          'pa_max_total_power_prod_prod0_prod1'])
        self.assertEqual(self.model._model_constraints_list[7].exp,
                         'prod0_p[t] + prod1_p[t] <= 10')

    def test_power_production_total_maximum_with_list(self):
        """ Test the power_production_maximum constraint on two production
        units if max_p is a list"""
        self.pa.add_power_production_total_maximum(time=self.time, max_p=[10,
                                                                          11])
        self.node.connect_units(self.prod0, self.prod1)
        self.model.add_nodes_and_actors(self.node, self.pa)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'prod0_calc_e_tot',
                          'prod0_on_off_max', 'prod0_on_off_min',
                          'prod1_calc_e_tot', 'prod1_on_off_max',
                          'prod1_on_off_min',
                          'pa_max_total_power_prod_prod0_prod1'])
        self.assertEqual(self.model._model_constraints_list[7].exp,
                         'prod0_p[t] + prod1_p[t] <= [10, 11][t] for t in '
                         'time.I')

    def test_power_production_total_maximum_with_wrong_list(self):
        """ Test it raises an error if max_p is a list with a wrong
        dimension considering the unit time"""
        with self.assertRaises(IndexError):
            self.pa.add_power_production_total_maximum(time=self.time, max_p=[
                10])

    def test_power_producion_total_maximum_with_dic(self):
        """ Test it raises an error if max_p is a list with dictionary"""
        with self.assertRaises(TypeError):
            self.pa.add_power_production_total_maximum(time=self.time, max_p={
                10})

    def test_power_production_by_unit_maximum(self):
        """ Test the power_production_by_unit_maximum constraint on two
        production units"""
        self.pa.add_power_production_by_unit_maximum(time=self.time, max_p=10)
        self.node.connect_units(self.prod0, self.prod1)
        self.model.add_nodes_and_actors(self.node, self.pa)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'prod0_calc_e_tot',
                          'prod0_on_off_max', 'prod0_on_off_min',
                          'prod1_calc_e_tot', 'prod1_on_off_max',
                          'prod1_on_off_min',
                          'pa_max_by_unit_power_prod_prod0',
                          'pa_max_by_unit_power_prod_prod1'])
        self.assertEqual(self.model._model_constraints_list[7].exp,
                         'prod0_p[t] <= 10 for t in time.I')
        self.assertEqual(self.model._model_constraints_list[8].exp,
                         'prod1_p[t] <= 10 for t in time.I')

    def test_power_production_by_unit_maximum_with_list(self):
        """ Test the power_production_by_unit_maximum constraint on two
        production units if max_p is a list"""
        self.pa.add_power_production_by_unit_maximum(time=self.time,
                                                     max_p=[10, 11])
        self.node.connect_units(self.prod0, self.prod1)
        self.model.add_nodes_and_actors(self.node, self.pa)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'prod0_calc_e_tot',
                          'prod0_on_off_max', 'prod0_on_off_min',
                          'prod1_calc_e_tot', 'prod1_on_off_max',
                          'prod1_on_off_min',
                          'pa_max_by_unit_power_prod_prod0',
                          'pa_max_by_unit_power_prod_prod1'])
        self.assertEqual(self.model._model_constraints_list[7].exp,
                         'prod0_p[t] <= [10, 11][t] for t in time.I')
        self.assertEqual(self.model._model_constraints_list[8].exp,
                         'prod1_p[t] <= [10, 11][t] for t in time.I')

    def test_power_production_by_unit_maximum_with_wrong_list(self):
        """ Test it raises an error if max_p is a list with a wrong
        dimension considering the unit time"""
        with self.assertRaises(IndexError):
            self.pa.add_power_production_by_unit_maximum(time=self.time,
                                                         max_p=[10])

    def test_power_production_by_unit_maximum_with_dic(self):
        """ Test it raises an error if max_p is a list with dictionary"""
        with self.assertRaises(TypeError):
            self.pa.add_power_production_by_unit_maximum(time=self.time,
                                                         max_p={10})
