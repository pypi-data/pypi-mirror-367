#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Unit tests for the module operator_actors.py, defining an operator actor.

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
from omegalpes.general.time import TimeUnit
from omegalpes.actor.operator_actors.operator_actors import OperatorActor
from omegalpes.energy.units.production_units import ProductionUnit
from omegalpes.energy.units.consumption_units import ConsumptionUnit
from omegalpes.energy.energy_nodes import EnergyNode


class TestOperatorActor(unittest.TestCase):
    """ Test OperatorActor class """

    def setUp(self):
        self.pu0 = ProductionUnit(time=TimeUnit(periods=24, dt=1), name='PU0')
        self.opa0 = OperatorActor(name='OPA0',
                                  operated_unit_type_tuple=(ProductionUnit,
                                                            EnergyNode))
        self.opa_op_list = OperatorActor(name='OPA0',
                                         operated_unit_type_tuple=(
                                             ProductionUnit,
                                             EnergyNode),
                                         operated_unit_list=[self.pu0])

    def test_name_description(self):
        """ Test the name and the description associated to an operator_actor
        object """
        self.assertIs(self.opa0.name, 'OPA0')
        self.assertEqual(self.opa0.description, 'Operator Actor OptObject')

    def test_operated_unit_list_none(self):
        """ Test the operated unit list associated to an
        operator_actor object if it is none"""
        self.assertEqual(self.opa0.operated_unit_list, [])

    def test_operated_unit_list_not_none(self):
        """ Test the operated unit list associated to an
        operator_actor object if it is not none"""
        self.assertEqual(self.opa_op_list.operated_unit_list, [self.pu0])


class TestCheckOperatedUnitList(unittest.TestCase):
    """ Test the _check_operated_unit_list method"""

    def setUp(self):
        self.pu0 = ProductionUnit(time=TimeUnit(periods=24, dt=1), name='PU1')
        self.pu1 = ProductionUnit(time=TimeUnit(periods=24, dt=1), name='PU1')
        self.opa0 = OperatorActor(name='OPA0',
                                  operated_unit_type_tuple=(ProductionUnit,
                                                            EnergyNode))
        self.opa_op_list = OperatorActor(name='OPA0',
                                         operated_unit_type_tuple=(
                                             ProductionUnit,
                                             EnergyNode),
                                         operated_unit_list=[self.pu0])

    def test_obj_operated_unit_list_none(self):
        """ Test if obj_operated_unit_list is none"""
        test_op_list = self.opa_op_list._check_operated_unit_list(
            obj_operated_unit_list=None)
        self.assertEqual(self.opa_op_list.operated_unit_list, test_op_list)

    def test_obj_operated_unit_list_empty(self):
        """ Test if obj_operated_unit_list is empty"""
        test_op_list = self.opa_op_list._check_operated_unit_list(
            obj_operated_unit_list=[])
        self.assertEqual(self.opa_op_list.operated_unit_list, test_op_list)

    def test_obj_operated_unit_list_with_operated_unit(self):
        """ Test obj_operated_unit_list with operated unit"""
        test_op_list = self.opa_op_list._check_operated_unit_list(
            obj_operated_unit_list=[self.pu0])
        self.assertEqual(self.opa_op_list.operated_unit_list, test_op_list)

    def test_obj_operated_unit_list_without_operated_unit(self):
        """ Test obj_operated_unit_list with operated unit"""
        with self.assertRaises(ValueError):
            test_op_list = self.opa_op_list._check_operated_unit_list(
                obj_operated_unit_list=[self.pu1])
            self.assertEqual(self.opa_op_list.operated_unit_list, test_op_list)

    def test_error_if_not_list(self):
        """ Test obj_operated_unit_list raise an error if
        obj_operated_unit_list is not a list"""
        with self.assertRaises(TypeError):
            self.opa_op_list._check_operated_unit_list(
                obj_operated_unit_list=self.pu0)


class TestCheckOperatedUnitType(unittest.TestCase):
    """ Test the _check_unit_type method"""

    def setUp(self):
        self.pu0 = ProductionUnit(time=TimeUnit(periods=24, dt=1), name='PU1')
        self.pu1 = ProductionUnit(time=TimeUnit(periods=24, dt=1), name='PU1')

    def test_error_if_wrong_unit_type(self):
        """ Test _check_unit_type raise an error if the operator operates a
        unit from another type """
        with self.assertRaises(TypeError):
            OperatorActor(name='OPA0',
                          operated_unit_type_tuple=(ConsumptionUnit,
                                                    EnergyNode),
                          operated_unit_list=[self.pu0])
