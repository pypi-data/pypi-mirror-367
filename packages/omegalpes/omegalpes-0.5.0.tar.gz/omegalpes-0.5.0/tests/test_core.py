#! usr/bin/env python3
#  -*- coding: utf-8 -*-

""""
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
from omegalpes.general.optimisation.core import OptObject
from omegalpes.general.optimisation.elements import Quantity, Constraint, \
    Objective
from omegalpes.general.optimisation.model import OptimisationModel
from omegalpes.energy.units.energy_units import VariableEnergyUnit
from omegalpes.energy.energy_nodes import EnergyNode
from omegalpes.general.time import TimeUnit


class TestUnit(unittest.TestCase):
    """ Test the OptObject class"""
    def test_init(self):
        """ Test the initialisation with empty quantities, constraints and
        objectives """
        unit0 = OptObject('test_name', 'test_description')

        self.assertIsInstance(unit0, OptObject)

        self.assertIs('test_name', unit0.name)
        self.assertIs('test_description', unit0.description)

        self.assertListEqual(unit0._quantities_list, [])
        self.assertListEqual(unit0._constraints_list, [])
        self.assertListEqual(unit0._objectives_list, [])


class Teststr(unittest.TestCase):
    """ Test the __str__ method"""

    def test_return_empty_name(self):
        """ Test the return considering a unit with empty name and
        description """
        unit0 = OptObject()
        self.assertEqual(unit0.__str__(), '<OMEGALPES.general.units.OptObject: '
                                          '\nname: {0} \ndescription: {1}\n\n'
                                          'Optimization '
                                          'variables:\n\nConstants:'
                                          '\n\nConstraints:\n\nObjective:\n'
                         .format('U0', 'Optimization object'))

    def test_return(self):
        """ Test the return considering the name and the description """
        unit0 = OptObject('test_name', 'test_description')
        self.assertEqual(unit0.__str__(), '<OMEGALPES.general.units.OptObject: '
                                          '\nname: {0} \ndescription: {1}\n\n'
                                          'Optimization '
                                          'variables:\n\nConstants:'
                                          '\n\nConstraints:\n\nObjective:\n'
                         .format('test_name', 'test_description'))

    def test_optimised_quantity(self):
        """ Test the return considering a unit with a quantity which can be
        optimised """
        unit0 = OptObject('N', 'D')
        unit0.optimised_quantity = Quantity(name="var0", opt=True)
        self.assertEqual(unit0.__str__(), '<OMEGALPES.general.units.OptObject: '
                                          '\nname: N \ndescription: D\n\n'
                                          'Optimization variables:\nname: '
                                          'var0\n\nConstants:\n\n'
                                          'Constraints:\n\nObjective:\n')

    def test_constant_quantity(self):
        """ Test the return considering a unit with a quantity which is
        constant """
        unit0 = OptObject('N', 'D')
        unit0.constant_quantity = Quantity(name="cst0", value=1)
        self.assertEqual(unit0.__str__(),
                         '<OMEGALPES.general.units.OptObject: \nname: N '
                         '\ndescription: D\n\nOptimization '
                         'variables:\n\nConstants:\nname: cst0,'
                         '  value: 1\n\nConstraints:'
                         '\n\nObjective:\n')

    def test_dict_quantity(self):
        """ Test the return considering a unit with a quantity which is a
        dictionary """
        unit0 = OptObject('N', 'D')
        unit0.constant_quantity = Quantity(name="cst0", value={1: 2})
        self.assertEqual(unit0.__str__(),
                         '<OMEGALPES.general.units.OptObject: \nname: N '
                         '\ndescription: D\n\nOptimization '
                         'variables:\n\nConstants:\nname: cst0,'
                         '  value: {1: 2}\n\nConstraints:'
                         '\n\nObjective:\n')

    def test_constraint(self):
        """ Test the return considering a unit with a constraint """
        unit0 = OptObject('N', 'D')
        unit0.constraint = Constraint(exp='p=1')
        self.assertEqual(unit0.__str__(),
                         '<OMEGALPES.general.units.OptObject: \nname: N '
                         '\ndescription: D\n\nOptimization '
                         'variables:\n\nConstants:\n\nConstraints:\n[True] '
                         'name: CST0 exp: p=1'
                         '\n\nObjective:\n')

    def test_objective(self):
        """ Test the return considering a unit with an objective """
        unit0 = OptObject('N', 'D')
        unit0.objective = Objective(exp='p')
        self.assertEqual(unit0.__str__(),
                         '<OMEGALPES.general.units.OptObject: \nname: N '
                         '\ndescription: D\n\nOptimization '
                         'variables:\n\nConstants:\n\nConstraints:'
                         '\n\nObjective:\n[True]name: OBJ0 exp: p\n')


class Testrepr(unittest.TestCase):
    """ Test the __repr__ method"""

    def test_return(self):
        """ Test the return for a unit with a name """
        unit0 = OptObject('test_name')
        self.assertEqual(unit0.__repr__(),
                         "<OMEGALPES.general.optimisation.units.OptObject: "
                         "name:\'test_name\'>")

    def test_return_empty_name(self):
        """ Test the return for a unit without name """
        unit0 = OptObject()
        self.assertEqual(unit0.__repr__(),
                         "<OMEGALPES.general.optimisation.units.OptObject: "
                         "name:\'U0\'>")


class TestLists(unittest.TestCase):
    """ Test add_unit_attributes_in_lists and associated quantity,
    constraint and objective methods"""

    def setUp(self):
        self.time = TimeUnit(periods=1, dt=1)
        self.model = OptimisationModel(name='model', time=self.time)
        self.unit0 = VariableEnergyUnit(time=self.time, name='unit0')
        self.node = EnergyNode(name='node', time=self.time)

    def test_add_and_get_constraints(self):
        """ Test if the constraint is added into the _model_constraints_list
        and that
        the list of constraints is available with get_constraints_name_list()
        """
        self.unit0.constraint = Constraint(exp="unit0_p==1", name='cst_test',
                                           parent=self.unit0)
        self.node.connect_units(self.unit0)
        self.model.add_nodes(self.node)
        self.model.solve()
        self.assertEqual(self.unit0.get_constraints_name_list(), ['calc_e_tot',
                                                                  'on_off_max',
                                                                  'on_off_min',
                                                                  'cst_test'])

    def test_add_and_get_objectives(self):
        """ Test if the objective is added into the _model_objectives_list
        and that
        the list of objective is available with get_objectives_name_list() """
        self.unit0.objectives = Objective(exp="lpSum(unit0_p)",
                                          name='obj_test', parent=self.unit0)
        self.node.connect_units(self.unit0)
        self.model.add_nodes(self.node)
        self.model.solve()
        self.assertEqual(self.unit0.get_objectives_name_list(), ['obj_test'])

    def test_add_and_get_quantities(self):
        """ Test if the quantity is added into the _model_quantities_list and
        that
        the list of quantities is available with get_quantities_name_list() """
        self.unit0.quantity = Quantity(name='quantity_test', parent=self.unit0)
        self.node.connect_units(self.unit0)
        self.model.add_nodes(self.node)
        self.model.solve()
        self.assertEqual(self.unit0.get_quantities_name_list(),
                         ['p', 'e_tot', 'u', 'quantity_test'])
