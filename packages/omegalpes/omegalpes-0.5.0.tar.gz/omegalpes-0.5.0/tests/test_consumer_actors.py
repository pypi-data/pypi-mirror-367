#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Unit tests for the module consumer_actors.py, defining constraints and
objectives for consumer actor type.

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
from omegalpes.actor.operator_actors.consumer_actors import Consumer
from omegalpes.energy.units.consumption_units import ConsumptionUnit
from omegalpes.general.time import TimeUnit
from omegalpes.general.optimisation.model import OptimisationModel
from omegalpes.energy.energy_nodes import EnergyNode


class TestConsumerActorObjectives(unittest.TestCase):
    """Test of ConsumerActor objectives"""

    def setUp(self):
        self.time = TimeUnit(periods=2, dt=1)
        self.conso0 = ConsumptionUnit(time=self.time, name='conso0')
        self.conso1 = ConsumptionUnit(time=self.time, name='conso1')
        self.ca = Consumer(name='ca', operated_unit_list=[self.conso0,
                                                          self.conso1])
        self.node = EnergyNode(time=self.time, name='node')
        self.model = OptimisationModel(time=self.time, name='OM')

    def test_minimize_consumption(self):
        """ Test the minimize_consumption objective on two consumption units"""
        self.ca.minimize_consumption()
        self.node.connect_units(self.conso0, self.conso1)
        self.model.add_nodes_and_actors(self.node, self.ca)
        self.model.solve_and_update()
        self.assertEqual(self.conso0.get_objectives_name_list(),
                         ['min_consumption'])
        self.assertEqual(self.conso1.get_objectives_name_list(),
                         ['min_consumption'])
        self.assertEqual(self.model.get_model_objectives_name_list(),
                         ['conso0_min_consumption', 'conso1_min_consumption'])

    def test_maximize_consumption(self):
        """ Test the maximize_consumption objective on two consumption units"""
        self.ca.maximize_consumption()
        self.node.connect_units(self.conso0, self.conso1)
        self.model.add_nodes_and_actors(self.node, self.ca)
        self.model.solve_and_update()
        self.assertEqual(self.conso0.get_objectives_name_list(),
                         ['max_consumption'])
        self.assertEqual(self.conso1.get_objectives_name_list(),
                         ['max_consumption'])
        self.assertEqual(self.model.get_model_objectives_name_list(),
                         ['conso0_max_consumption', 'conso1_max_consumption'])

    def test_minimize_consumption_cost(self):
        """ Test the minimize_consumption_cost objective on two consumption
        units"""
        self.conso0._add_operating_cost([1, 1])
        self.conso1._add_operating_cost([2, 2])
        self.ca.minimize_consumption_cost()
        self.node.connect_units(self.conso0, self.conso1)
        self.model.add_nodes_and_actors(self.node, self.ca)
        self.model.solve_and_update()
        self.assertEqual(self.conso0.get_objectives_name_list(),
                         ['min_consumption_cost'])
        self.assertEqual(self.conso1.get_objectives_name_list(),
                         ['min_consumption_cost'])
        self.assertEqual(self.model.get_model_objectives_name_list(),
                         ['conso0_min_consumption_cost',
                          'conso1_min_consumption_cost'])

    def test_minimize_co2_consumption(self):
        """ Test the minimize_co2_consumption objective on two consumption
        units"""
        self.conso0._add_co2_emissions([1, 1])
        self.conso1._add_co2_emissions([2, 2])
        self.ca.minimize_co2_consumption()
        self.node.connect_units(self.conso0, self.conso1)
        self.model.add_nodes_and_actors(self.node, self.ca)
        self.model.solve_and_update()
        self.assertEqual(self.conso0.get_objectives_name_list(),
                         ['min_CO2_emissions'])
        self.assertEqual(self.conso1.get_objectives_name_list(),
                         ['min_CO2_emissions'])
        self.assertEqual(self.model.get_model_objectives_name_list(),
                         ['conso0_min_CO2_emissions',
                          'conso1_min_CO2_emissions'])


class TestConsumerActorConstraints(unittest.TestCase):
    """Test of ConsumerActor constraints"""

    def setUp(self):
        self.time = TimeUnit(periods=2, dt=1)
        self.conso0 = ConsumptionUnit(time=self.time, name='conso0')
        self.conso1 = ConsumptionUnit(time=self.time, name='conso1')
        self.ca = Consumer(name='ca', operated_unit_list=[self.conso0,
                                                          self.conso1])
        self.node = EnergyNode(time=self.time, name='node')
        self.model = OptimisationModel(time=self.time, name='OM')

    def test_energy_consumption_minimum(self):
        """ Test the energy_consumption_minimum constraint on two consumption
        units """
        self.ca.add_energy_consumption_minimum(min_e_tot=10)
        self.node.connect_units(self.conso0, self.conso1)
        self.model.add_nodes_and_actors(self.node, self.ca)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'conso0_calc_e_tot',
                          'conso1_calc_e_tot',
                          'ca_min_energy_conso_conso0_conso1'])
        self.assertEqual(self.model._model_constraints_list[3].exp,
                         'lpSum(conso0_p[t] + conso1_p[t]  for t in time.I) '
                         '>= '
                         '10')

    def test_energy_consumption_minimum_without_int_or_float(self):
        """ Test it raises an error if min_e_tot is a list"""
        with self.assertRaises(TypeError):
            self.ca.add_energy_consumption_minimum(min_e_tot=[10, 10])

    def test_energy_consumption_maximum(self):
        """ Test the energy_consumption_maximum constraint on two consumption
        units """
        self.ca.add_energy_consumption_maximum(max_e_tot=10)
        self.node.connect_units(self.conso0, self.conso1)
        self.model.add_nodes_and_actors(self.node, self.ca)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'conso0_calc_e_tot',
                          'conso1_calc_e_tot',
                          'ca_max_energy_conso_conso0_conso1'])
        self.assertEqual(self.model._model_constraints_list[3].exp,
                         'lpSum(conso0_p[t] + conso1_p[t]  for t in time.I) '
                         '<= 10')

    def test_energy_consumption_maximum_without_int_or_float(self):
        """ Test it raises an error if max_e_tot is a list"""
        with self.assertRaises(TypeError):
            self.ca.add_energy_consumption_maximum(max_e_tot=[10, 10])

    def test_power_consumption_total_minimum(self):
        """ Test the add_power_consumption_minimum constraint on two
        consumption units """
        self.ca.add_power_consumption_total_minimum(time=self.time, min_p=10)
        self.node.connect_units(self.conso0, self.conso1)
        self.model.add_nodes_and_actors(self.node, self.ca)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'conso0_calc_e_tot',
                          'conso1_calc_e_tot',
                          'ca_min_total_power_conso_conso0_conso1'])
        self.assertEqual(self.model._model_constraints_list[3].exp,
                         'conso0_p[t] + conso1_p[t] >= 10')

    def test_power_consumption_total_minimum_with_list(self):
        """ Test the add_power_consumption_total_minimum constraint on two
        consumption units if min_p is a list"""
        self.ca.add_power_consumption_total_minimum(time=self.time,
                                                    min_p=[10, 10])
        self.node.connect_units(self.conso0, self.conso1)
        self.model.add_nodes_and_actors(self.node, self.ca)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'conso0_calc_e_tot',
                          'conso1_calc_e_tot',
                          'ca_min_total_power_conso_conso0_conso1'])
        self.assertEqual(self.model._model_constraints_list[3].exp,
                         'conso0_p[t] + conso1_p[t] >= [10, 10][t] for t in '
                         'time.I')

    def test_power_consumption_total_minimum_with_wrong_list(self):
        """ Test it raises an error if min_p is a list with a wrong
        dimension considering the unit time"""
        with self.assertRaises(IndexError):
            self.ca.add_power_consumption_total_minimum(time=self.time,
                                                        min_p=[10])

    def test_power_consumption_total_minimum_with_dic(self):
        """ Test it raises an error if min_p is a dictionary"""
        with self.assertRaises(TypeError):
            self.ca.add_power_consumption_total_minimum(time=self.time,
                                                        min_p={10})

    def test_power_consumption_by_unit_minimum(self):
        """ Test the add_power_consumption_by_unit_minimum constraint on two
        consumption units """
        self.ca.add_power_consumption_by_unit_minimum(time=self.time, min_p=10)
        self.node.connect_units(self.conso0, self.conso1)
        self.model.add_nodes_and_actors(self.node, self.ca)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'conso0_calc_e_tot',
                          'conso1_calc_e_tot',
                          'ca_min_by_unit_power_conso_conso0',
                          'ca_min_by_unit_power_conso_conso1'])
        self.assertEqual(self.model._model_constraints_list[3].exp,
                         'conso0_p[t] >= 10 for t in time.I')
        self.assertEqual(self.model._model_constraints_list[4].exp,
                         'conso1_p[t] >= 10 for t in time.I')

    def test_power_consumption_by_unit_minimum_with_list(self):
        """ Test the add_power_consumption_by_unit_minimum constraint on two
        consumption units if min_p is a list"""
        self.ca.add_power_consumption_by_unit_minimum(time=self.time,
                                                      min_p=[10, 10])
        self.node.connect_units(self.conso0, self.conso1)
        self.model.add_nodes_and_actors(self.node, self.ca)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'conso0_calc_e_tot',
                          'conso1_calc_e_tot',
                          'ca_min_by_unit_power_conso_conso0',
                          'ca_min_by_unit_power_conso_conso1'])
        self.assertEqual(self.model._model_constraints_list[3].exp,
                         'conso0_p[t] >= [10, 10][t] for t in time.I')
        self.assertEqual(self.model._model_constraints_list[4].exp,
                         'conso1_p[t] >= [10, 10][t] for t in time.I')

    def test_power_consumption_by_unit_minimum_with_wrong_list(self):
        """ Test it raises an error if min_p is a list with a wrong
        dimension considering the unit time"""
        with self.assertRaises(IndexError):
            self.ca.add_power_consumption_by_unit_minimum(time=self.time,
                                                          min_p=[10])

    def test_power_consumption_by_unit_minimum_with_dic(self):
        """ Test it raises an error if min_p is a dictionary"""
        with self.assertRaises(TypeError):
            self.ca.add_power_consumption_by_unit_minimum(time=self.time,
                                                          min_p={10})

    def test_power_consumption_total_maximum(self):
        """ Test the power_consumption_maximum constraint on two consumption
        units"""
        self.ca.add_power_consumption_total_maximum(time=self.time, max_p=10)
        self.node.connect_units(self.conso0, self.conso1)
        self.model.add_nodes_and_actors(self.node, self.ca)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'conso0_calc_e_tot',
                          'conso1_calc_e_tot',
                          'ca_max_total_power_conso_conso0_conso1'])
        self.assertEqual(self.model._model_constraints_list[3].exp,
                         'conso0_p[t] + conso1_p[t] <= 10')

    def test_power_consumption_total_maximum_with_list(self):
        """ Test the power_consumption_maximum constraint on two consumption
        units if max_p is a list"""
        self.ca.add_power_consumption_total_maximum(time=self.time, max_p=[10,
                                                                           11])
        self.node.connect_units(self.conso0, self.conso1)
        self.model.add_nodes_and_actors(self.node, self.ca)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'conso0_calc_e_tot',
                          'conso1_calc_e_tot',
                          'ca_max_total_power_conso_conso0_conso1'])
        self.assertEqual(self.model._model_constraints_list[3].exp,
                         'conso0_p[t] + conso1_p[t] <= [10, 11][t] for t in '
                         'time.I')

    def test_power_consumption_total_maximum_with_wrong_list(self):
        """ Test it raises an error if max_p is a list with a wrong
        dimension considering the unit time"""
        with self.assertRaises(IndexError):
            self.ca.add_power_consumption_total_maximum(time=self.time, max_p=[
                10])

    def test_power_consumption_total_maximum_with_dic(self):
        """ Test it raises an error if max_p is a list with dictionary"""
        with self.assertRaises(TypeError):
            self.ca.add_power_consumption_total_maximum(time=self.time, max_p={
                10})

    def test_power_consumption_by_unit_maximum(self):
        """ Test the power_consumption_by_unit_maximum constraint on two
        consumption units"""
        self.ca.add_power_consumption_by_unit_maximum(time=self.time, max_p=10)
        self.node.connect_units(self.conso0, self.conso1)
        self.model.add_nodes_and_actors(self.node, self.ca)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'conso0_calc_e_tot',
                          'conso1_calc_e_tot',
                          'ca_max_by_unit_power_conso_conso0',
                          'ca_max_by_unit_power_conso_conso1'])
        self.assertEqual(self.model._model_constraints_list[3].exp,
                         'conso0_p[t] <= 10 for t in '
                         'time.I')
        self.assertEqual(self.model._model_constraints_list[4].exp,
                         'conso1_p[t] <= 10 for t in '
                         'time.I')

    def test_power_consumption_by_unit_maximum_with_list(self):
        """ Test the power_consumption_by_unit_maximum constraint on two
        consumption units if max_p is a list"""
        self.ca.add_power_consumption_by_unit_maximum(time=self.time,
                                                      max_p=[10, 11])
        self.node.connect_units(self.conso0, self.conso1)
        self.model.add_nodes_and_actors(self.node, self.ca)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'conso0_calc_e_tot',
                          'conso1_calc_e_tot',
                          'ca_max_by_unit_power_conso_conso0',
                          'ca_max_by_unit_power_conso_conso1'])
        self.assertEqual(self.model._model_constraints_list[3].exp,
                         'conso0_p[t] <= [10, 11][t] for t in '
                         'time.I')
        self.assertEqual(self.model._model_constraints_list[4].exp,
                         'conso1_p[t] <= [10, 11][t] for t in '
                         'time.I')

    def test_power_consumption_by_unit_maximum_with_wrong_list(self):
        """ Test it raises an error if max_p is a list with a wrong
        dimension considering the unit time"""
        with self.assertRaises(IndexError):
            self.ca.add_power_consumption_by_unit_maximum(time=self.time,
                                                          max_p=[
                                                              10])

    def test_power_consumption_by_unit_maximum_with_dic(self):
        """ Test it raises an error if max_p is a list with dictionary"""
        with self.assertRaises(TypeError):
            self.ca.add_power_consumption_by_unit_maximum(time=self.time,
                                                          max_p={
                                                              10})
