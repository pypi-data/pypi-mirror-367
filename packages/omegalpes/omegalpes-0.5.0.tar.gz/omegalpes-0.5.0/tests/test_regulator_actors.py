#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Unit tests for the module regulator_actors.py, defining regulator
actor classes and constraints for regulator actors.

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
from omegalpes.actor.regulator_actors.regulator_actors import RegulatorActor
from omegalpes.energy.units.production_units import ProductionUnit
from omegalpes.general.time import TimeUnit
from omegalpes.general.optimisation.model import OptimisationModel
from omegalpes.energy.energy_nodes import EnergyNode


class TestRegulatorActor(unittest.TestCase):
    """Test of RegulatorActor constraint"""

    def setUp(self):
        self.time = TimeUnit(periods=2, dt=1)
        self.prod0 = ProductionUnit(time=self.time, name='prod0', co2_out=[1,
                                                                           1])
        self.prod1 = ProductionUnit(time=self.time, name='prod1', co2_out=[2,
                                                                           2])
        self.ra = RegulatorActor(name='ra')
        self.node = EnergyNode(time=self.time, name='node')
        self.model = OptimisationModel(time=self.time, name='OM')

    def test_co2_emission_maximum(self):
        """ Test the co2_emission_maximum constraint on two production
        units"""
        self.ra.add_co2_emission_maximum(co2_max=10, time=self.time,
                                         cst_production_list=[self.prod0,
                                                          self.prod1])
        self.node.connect_units(self.prod0, self.prod1)
        self.model.add_nodes_and_actors(self.node, self.ra)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'prod0_calc_e_tot',
                          'prod0_calc_co2_emissions', 'prod1_calc_e_tot',
                          'prod1_calc_co2_emissions',
                          'ra_max_co2_emission_prod0_prod1'])
        self.assertEqual(self.model._model_constraints_list[5].exp,
                         'prod0_co2_emissions[t] + prod1_co2_emissions[t] <= '
                         '10')

    def test_co2_emission_maximum_with_list(self):
        """ Test the co2_emission_maximum constraint on two production
        units if max_co2 is a list"""
        self.ra.add_co2_emission_maximum(co2_max=[10, 10], time=self.time,
                                         cst_production_list=[self.prod0,
                                                          self.prod1])
        self.node.connect_units(self.prod0, self.prod1)
        self.model.add_nodes_and_actors(self.node, self.ra)
        self.model.solve_and_update()
        self.assertEqual(self.model.get_model_constraints_name_list(),
                         ['node_power_balance', 'prod0_calc_e_tot',
                          'prod0_calc_co2_emissions',
                          'prod1_calc_e_tot', 'prod1_calc_co2_emissions',
                          'ra_max_co2_emission_prod0_prod1'])
        self.assertEqual(self.model._model_constraints_list[5].exp,
                         'prod0_co2_emissions[t] + prod1_co2_emissions[t] <= '
                         '[10, 10][t] '
                         'for t in '
                         'time.I')

    def test_power_production_maximum_with_wrong_list(self):
        """ Test it raises an error if max_co2 is a list with a wrong
        dimension considering the unit time"""
        with self.assertRaises(IndexError):
            self.ra.add_co2_emission_maximum(co2_max=[10], time=self.time,
                                             cst_production_list=[self.prod0,
                                                              self.prod1])

    def test_power_production_maximum_with_dic(self):
        """ Test it raises an error if max_co2 is a list with dictionary"""
        with self.assertRaises(TypeError):
            self.ra.add_co2_emission_maximum(co2_max={10}, time=self.time,
                                             cst_production_list=[self.prod0,
                                                              self.prod1])
