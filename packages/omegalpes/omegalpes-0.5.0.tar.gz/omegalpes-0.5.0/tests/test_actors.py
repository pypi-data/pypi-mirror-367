#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Unit tests for actor module.

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
    limitations under the License .
"""

import unittest
from omegalpes.actor.actor import Actor
from omegalpes.general.optimisation.model import OptimisationModel
from omegalpes.energy.units.energy_units import EnergyUnit
from omegalpes.energy.energy_nodes import EnergyNode
from omegalpes.general.time import TimeUnit


class TestActor(unittest.TestCase):
    """ Test of the actor class"""

    def setUp(self):
        self.actor = Actor(name='ACT0')
        self.act_operator = Actor(name='operator')
        self.act_regulator = Actor(name='regulator')
        self.time = TimeUnit(periods=1, dt=1)
        self.unit0 = EnergyUnit(time=self.time, name='unit0')
        self.unit1 = EnergyUnit(time=self.time, name='unit1')
        self.model = OptimisationModel(time=self.time, name='model')
        self.node = EnergyNode(name='node', time=self.time)

    def test_init(self):
        """ Test the name and the description """

        self.assertEqual(self.actor.name, 'ACT0')
        self.assertEqual(self.actor.description, 'Actor OptObject')

    def test_add_actor_constraint_operator(self):
        """ Test the add_actor_constraint method associated to an
        actor operating energy unit"""
        self.act_operator.add_actor_constraint(
            cst_name="add_ext_cst_test_1", exp="{}_p <= 10 ".format(
                self.unit0.name, parent=self.act_operator))
        self.node.connect_units(self.unit0)
        self.model.add_nodes_and_actors(self.node, self.act_operator)
        self.model.solve()

    def test_add_actor_constraint_regulator(self):
        """ Test the add_actor_constraint method  associated to an
        actor non operating energy unit"""
        self.act_regulator.add_actor_constraint(
            cst_name="add_ext_cst_test_2", exp="{}_p <= 10 ".format(
                self.unit1.name, parent=self.act_operator))
        self.node.connect_units(self.unit1)
        self.model.add_nodes_and_actors(self.node, self.act_regulator)
        self.model.solve()
        self.assertEqual(self.act_regulator.get_constraints_name_list(),
                         ['add_ext_cst_test_2'])

    def test_add_actor_dynamic_constraint_operator(self):
        """ Test the add_actor_dynamic_constraint method associated to an
        actor operating energy unit"""
        self.act_operator.add_actor_dynamic_constraint(
            cst_name="add_ext_cst_test_1", exp_t="{}_p[t] <= 10 ".format(
                self.unit0.name))
        self.node.connect_units(self.unit0)
        self.model.add_nodes_and_actors(self.node, self.act_operator)
        self.model.solve()
        self.assertEqual(self.act_operator.get_constraints_name_list(),
                         ['add_ext_cst_test_1'])

    def test_add_actor_dynamic_constraint_regulator(self):
        """ Test the add_actor_dynamic_constraint method associated to an
        actor non operating energy unit"""
        self.act_regulator.add_actor_dynamic_constraint(
            cst_name="add_ext_cst_test_2", exp_t="{}_p[t] <= 10 ".format(
                self.unit1.name))
        self.node.connect_units(self.unit1)
        self.model.add_nodes_and_actors(self.node, self.act_regulator)
        self.model.solve()
        self.assertEqual(self.act_regulator.get_constraints_name_list(),
                         ['add_ext_cst_test_2'])

    def test_add_objective_operator(self):
        """ Test the add_objective method associated to an
        actor operating energy unit"""
        self.act_operator.add_objective(obj_name="add_obj_test_1",
                                        exp='lpSum({}_p)'.format(
                                            self.unit0.name))
        self.node.connect_units(self.unit0)
        self.model.add_nodes_and_actors(self.node, self.act_operator)
        self.model.solve()
        self.assertEqual(self.act_operator.get_objectives_name_list(),
                         ['add_obj_test_1'])

    def test_add_objective_regulator(self):
        """ Test the add_objective method  associated to an
        actor non operating energy unit"""
        self.act_regulator.add_objective(obj_name="add_obj_test_2",
                                         exp='lpSum({}_p)'.format(
                                             self.unit0.name))
        self.node.connect_units(self.unit1)
        self.model.add_nodes_and_actors(self.node, self.act_regulator)
        self.model.solve()
        self.assertEqual(self.act_regulator.get_objectives_name_list(),
                         ['add_obj_test_2'])
