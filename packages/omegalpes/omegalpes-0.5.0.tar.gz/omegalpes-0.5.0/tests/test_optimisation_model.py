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

from pulp import LpBinary, LpContinuous, LpInteger, LpVariable
from omegalpes.general.optimisation.model import OptimisationModel
from omegalpes.general.optimisation.model import check_if_unit_could_have_parent
from omegalpes.general.optimisation.elements import Constraint, \
    DynamicConstraint, Quantity, Objective
from omegalpes.general.optimisation.core import OptObject
from omegalpes.general.time import TimeUnit
from omegalpes.energy.energy_nodes import EnergyNode
from omegalpes.energy.units.energy_units import EnergyUnit, VariableEnergyUnit


class TestAddUnitParent(unittest.TestCase):

    def setUp(self):
        self.time = TimeUnit(periods=2, dt=1)
        self.model = OptimisationModel(time=self.time)
        self.unit_1 = OptObject('U1')
        self.unit_2 = OptObject('U2')

    def test_parent_unit_added(self):
        """
        Check if the parent of the unit is added to the _model_units_list
        when the
        parent of the unit is a OptObject.
        """

        setattr(self.unit_1, 'parent', self.unit_2)
        self.model._add_unit_parent(self.unit_1)

        self.assertIn(self.unit_2, self.model._model_units_list)

    def test_if_no_parent(self):
        """ Check if the list is still empty when the unit gets no parent """

        self.model._add_unit_parent(self.unit_1)

        self.assertListEqual(self.model._model_units_list, [])

    def test_parent_not_added_if_not_unit(self):
        """ Check if the parent is not added to the _model_units_list when the
        parent is not a OptObject. """

        parent = object()
        setattr(self.unit_1, 'parent', parent)
        self.model._add_unit_parent(self.unit_1)

        self.assertNotIn(parent, self.model._model_units_list)


class TestAddQuantity(unittest.TestCase):

    def setUp(self):
        self.time = TimeUnit(periods=2, dt=1)
        self.model = OptimisationModel(time=self.time)
        self.parent = OptObject(name='unit_parent')
        self.q_name = 'ex_name'
        self.q_type = random.choice([LpContinuous, LpInteger, LpBinary])

    def test_ub_list(self):
        """ Check that an dynamic constraint 'set_ub' is added to the parent """

        q_val = random.choice([0, [0, 0], {0: 0}])
        q_lb = None
        q_ub = [1, 2]
        if isinstance(q_val, int):
            q_opt = False
        elif isinstance(q_val, list):
            q_opt = [False, False]
        else:
            q_opt = {0: False}
        parent = OptObject(name='unit_parent')

        self.model._add_quantity(q_name=self.q_name, q_val=q_val,
                                 q_type=self.q_type, q_lb=q_lb, q_ub=q_ub,
                                 q_opt=q_opt, parent=self.parent)

        self.assertIsInstance(self.parent.set_ub, DynamicConstraint)

    def test_lb_list(self):
        """ Check that an dynamic constraint 'set_lb' is added to the parent """

        q_val = random.choice([0, [0, 0], {0: 0}])
        q_lb = [1, 2]
        q_ub = None
        if isinstance(q_val, int):
            q_opt = False
        elif isinstance(q_val, list):
            q_opt = [False, False]
        else:
            q_opt = {0: False}
        parent = OptObject(name='unit_parent')

        self.model._add_quantity(q_name=self.q_name, q_val=q_val,
                                 q_type=self.q_type, q_lb=q_lb, q_ub=q_ub,
                                 q_opt=q_opt, parent=self.parent)

        self.assertIsInstance(self.parent.set_lb, DynamicConstraint)

    def test_dict_qval_with_opt(self):
        """ Check that the quantity is created and is a LpVariable when
        opt=True """

        q_val = {'first': None, 'second': None, 'third': None}
        q_lb = None
        q_ub = None
        q_opt = {0: True, 1: True, 2: True}

        self.model._add_quantity(q_name=self.q_name, q_val=q_val,
                                 q_type=self.q_type, q_lb=q_lb, q_ub=q_ub,
                                 q_opt=q_opt, parent=self.parent)

        # Import the model module in order to get the global variables
        import omegalpes.general.optimisation.model as mod
        q_var = eval('mod.' + self.q_name)

        for key in q_val.keys():
            self.assertIsInstance(q_var[key], LpVariable)

    def test_dict_qval_without_opt(self):
        """ Check that the quantity is created and is equals the value of the
        dictionary when opt=False """

        q_val = {'first': 1, 'second': 2, 'third': 3}
        q_lb = None
        q_ub = None
        q_opt = {0: False, 1: False, 2: False}

        self.model._add_quantity(q_name=self.q_name, q_val=q_val,
                                 q_type=self.q_type, q_lb=q_lb, q_ub=q_ub,
                                 q_opt=q_opt, parent=self.parent)

        # Import the model module in order to get the global variables
        import omegalpes.general.optimisation.model as mod

        q_var = eval('mod.' + self.q_name)
        self.assertDictEqual(q_var, q_val)

    def test_list_qval_with_opt(self):
        """ Check that the quantity is created and is a LpVariable when
        opt=True """

        q_val = [1, 2, 3]
        q_lb = None
        q_ub = None
        q_opt = [True] * 3

        self.model._add_quantity(q_name=self.q_name, q_val=q_val,
                                 q_type=self.q_type, q_lb=q_lb, q_ub=q_ub,
                                 q_opt=q_opt, parent=self.parent)

        # Import the model module in order to get the global variables
        import omegalpes.general.optimisation.model as mod

        for ind, _ in enumerate(q_val):
            q_var = eval('mod.' + self.q_name + '_{}'.format(ind))
            self.assertIsInstance(q_var, LpVariable)

    def test_list_qval_without_opt(self):
        """ Check that the quantity is created and is equals the value of the
        list when opt=False """

        q_val = [1, 2, 3]
        q_lb = None
        q_ub = None
        q_opt = [False] * 3

        self.model._add_quantity(q_name=self.q_name, q_val=q_val,
                                 q_type=self.q_type, q_lb=q_lb, q_ub=q_ub,
                                 q_opt=q_opt, parent=self.parent)

        # Import the model module in order to get the global variables
        import omegalpes.general.optimisation.model as mod

        q_var = eval('mod.' + self.q_name)
        self.assertListEqual(q_var, q_val)

    def test_int_float_qval_with_opt(self):
        """ Check that the quantity is created as LpVariable when opt=True"""

        q_int = random.randint(1, 50000)
        q_float = float(q_int)
        q_val = random.choice([q_int, q_float])
        q_lb = None
        q_ub = None
        q_opt = True

        self.model._add_quantity(q_name=self.q_name, q_val=q_val,
                                 q_type=self.q_type, q_lb=q_lb, q_ub=q_ub,
                                 q_opt=q_opt, parent=self.parent)

        # Import the model module in order to get the global variables
        import omegalpes.general.optimisation.model as mod
        q_var = eval('mod.' + self.q_name)

        self.assertIsInstance(q_var, LpVariable)

    def test_int_float_qval_without_opt(self):
        """ Check that the quantity is created and equals the q_val when
        opt=False """

        q_int = random.randint(1, 50000)
        q_float = float(q_int)
        q_val = random.choice([q_int, q_float])
        q_lb = None
        q_ub = None
        q_opt = False

        self.model._add_quantity(q_name=self.q_name, q_val=q_val,
                                 q_type=self.q_type, q_lb=q_lb, q_ub=q_ub,
                                 q_opt=q_opt, parent=self.parent)

        # Import the model module in order to get the global variables
        import omegalpes.general.optimisation.model as mod
        q_var = eval('mod.' + self.q_name)

        self.assertEqual(q_val, q_var)

    def test_wrong_type_qval(self):
        """ Check if TypeError is raised when q_val is not an int, a float,
        a list or a dictionary """

        q_val = object()
        q_lb = None
        q_ub = None
        q_opt = None

        with self.assertRaises(TypeError):
            self.model._add_quantity(q_name=self.q_name, q_val=q_val,
                                     q_type=self.q_type, q_lb=q_lb, q_ub=q_ub,
                                     q_opt=q_opt, parent=self.parent)


class TestAddQuantities(unittest.TestCase):

    def setUp(self):
        self.time = TimeUnit(periods=2, dt=1)
        self.model = OptimisationModel(self.time)

    def test_no_parent_for_quantity(self):
        """ Check that ValueError is raised when there is a try to add a
        quantity with parent=None to the _model_quantities_list through
        model._add_quantities() """

        self.model._model_quantities_list = [Quantity(parent=None)]

        with self.assertRaises(ValueError):
            self.model._add_quantities()


class TestAddUnitAttributes(unittest.TestCase):

    def setUp(self):
        self.time = TimeUnit(periods=2, dt=1)
        self.model = OptimisationModel(self.time)
        self.unit = OptObject()

    def test_add_all_children(self):
        """ Check if all OptObject objects contained as attributes in a OptObject are
        added to the _model_units_list of the model """

        unit_1 = OptObject('U1')
        unit_2 = OptObject('U2')
        unit_3 = OptObject('U3')
        setattr(unit_1, 'U2', unit_2)
        setattr(unit_1, 'U3', unit_3)

        self.model._add_unit_attributes(unit_1)

        self.assertListEqual([unit_2, unit_3], self.model._model_units_list)

    def test_add_all_quantities(self):
        """ Check if all Quantity objects contained as attributes in a OptObject
        are added to the _model_quantities_list of the model """

        unit = OptObject()
        quantity_1 = Quantity('Q1')
        quantity_2 = Quantity('Q2')
        setattr(unit, 'Q1', quantity_1)
        setattr(unit, 'Q2', quantity_2)

        self.model._add_unit_attributes(unit)

        self.assertListEqual([quantity_1, quantity_2],
                             self.model._model_quantities_list)

    def test_add_all_constraints(self):
        """ Check if all Constraint objects contained as attributes in a OptObject
        are added to the cosntraints_list of the model """

        constraint_1 = Constraint(exp='exp1', parent=None)
        constraint_2 = Constraint(exp='exp2', parent=None)
        setattr(self.unit, 'C1', constraint_1)
        setattr(self.unit, 'C2', constraint_2)

        self.model._add_unit_attributes(self.unit)

        self.assertListEqual([constraint_1, constraint_2],
                             self.model._model_constraints_list)

    def test_add_all_objectives(self):
        """ Check if all Objective objects contained as attributes in a OptObject
        are added to the objective_list of the model """

        objective_1 = Objective('O1')
        objective_2 = Objective('O2')
        setattr(self.unit, 'O1', objective_1)
        setattr(self.unit, 'O2', objective_2)

        self.model._add_unit_attributes(self.unit)

        self.assertListEqual([objective_1, objective_2],
                             self.model._model_objectives_list)

    def test_quantity_parent(self):
        """ Check if the parent of the Quantity object contained as attribute
        in a OptObject is this OptObject """

        quantity = Quantity('Q')
        setattr(self.unit, 'Q', quantity)

        self.model._add_unit_attributes(self.unit)

        self.assertEqual(self.unit, quantity.parent)

    def test_constraint_parent(self):
        """ Check if the parent of the Constraint object contained as
        attribute in a OptObject is this OptObject """

        constraint = Constraint(exp='exp', parent=None)
        setattr(self.unit, 'Cst', constraint)

        self.model._add_unit_attributes(self.unit)

        self.assertEqual(self.unit, constraint.parent)

    def test_objective_parent(self):
        """ Check if the parent of the Objective object contained as attribute
        in a OptObject is this OptObject """

        objective = Objective(exp='exp')
        setattr(self.unit, 'Obj', objective)

        self.model._add_unit_attributes(self.unit)

        self.assertEqual(self.unit, objective.parent)


class TestGetAllUnits(unittest.TestCase):
    def setUp(self):
        self.time = TimeUnit(periods=2, dt=1)
        self.model = OptimisationModel(self.time)

        self.unit_1 = OptObject('U1')
        self.unit_2 = OptObject('U2')
        self.unit_3 = OptObject('U3')
        self.unit_4 = OptObject('U4')
        self.unit_5 = OptObject('U5')
        self.unit_6 = OptObject('U6')
        self.unit_7 = OptObject('U7')

        self.all_units = [self.unit_1, self.unit_2, self.unit_3, self.unit_4,
                          self.unit_5, self.unit_6, self.unit_7]

        # The unit 4 is the parent of units 1, 2 and 3
        setattr(self.unit_4, 'U1', self.unit_1)
        setattr(self.unit_4, 'U2', self.unit_2)
        setattr(self.unit_4, 'U3', self.unit_3)

        # The unit 1 is the parent of the unit 5, which is parent of the unit 7
        setattr(self.unit_1, 'U5', self.unit_5)
        setattr(self.unit_5, 'U7', self.unit_7)

        # The unit 2 is the parent of the unit 6
        setattr(self.unit_2, 'U6', self.unit_6)

    def test_all_units_in_list_no_parent(self):
        """ Check if all units are in self._model_units_list when the unit with no
        parent is added first when parent are not explicitly defined """
        # Initialize the units list with the higher unit in possession : unit4
        self.model._model_units_list = [self.unit_4]

        for unit in self.model._model_units_list:
            self.model._add_unit_parent(unit)
            self.model._add_unit_attributes(unit)

        for unit in self.all_units:
            self.assertIn(unit, self.model._model_units_list)

    def test_all_units_in_list_with_parents(self):
        """ Check if all units are in self._model_units_list when the unit when the
        parents are correctly defined for each unit """

        # The unit 4 is the parent of units 1, 2 and 3
        setattr(self.unit_1, 'parent', self.unit_4)
        setattr(self.unit_2, 'parent', self.unit_4)
        setattr(self.unit_3, 'parent', self.unit_4)

        # The unit 1 is the parent of the unit 5, which is parent of the unit 7
        setattr(self.unit_5, 'parent', self.unit_1)
        setattr(self.unit_7, 'parent', self.unit_5)

        # The unit 2 is the parent of the unit 6
        setattr(self.unit_6, 'parent', self.unit_2)

        # Initialize the units list with any unit
        self.model._model_units_list = [random.choice(self.all_units)]

        for unit in self.model._model_units_list:
            self.model._add_unit_parent(unit)
            self.model._add_unit_attributes(unit)

        for unit in self.all_units:
            self.assertIn(unit, self.model._model_units_list)


class TestCheckIfUnitCouldHaveParent(unittest.TestCase):

    def setUp(self):
        self.unit_1 = OptObject('U1')
        self.unit_2 = OptObject('U2')

        # The unit 1 is the child of the unit 2
        setattr(self.unit_2, 'U1', self.unit_1)

    def test_warning(self):
        """ Check if a Warning is raised when there is a suspicion that a
        OptObject with no parent as attribute is contained in an other OptObject """

        with self.assertWarns(Warning):
            check_if_unit_could_have_parent(self.unit_1)

    def test_no_warning(self):
        """ Check if no Warning is raised when there is no suspicion that a
        OptObject with no parent as attribute is contained in an other OptObject """

        check_if_unit_could_have_parent(self.unit_1)


class TestAddConstraints(unittest.TestCase):
    def setUp(self):
        self.periods = random.randint(1, 6000)
        self.time = TimeUnit(periods=self.periods)
        self.model = OptimisationModel(self.time)

        self.unit = OptObject(name='unit')

    def test_add_constraint(self):
        """ Check if the Constraint is added to the dictionary of
        constraints by looking at the key. """

        constraint = random.choice([Constraint(name='cst_name',
                                               exp='x <= 4',
                                               parent=self.unit),
                                    DynamicConstraint(name='cst_name',
                                                      exp_t='x <= 4',
                                                      parent=self.unit)])

        self.model._add_quantity(q_name='x', q_val=0, q_type=LpContinuous,
                                 q_lb=None, q_ub=None, q_opt=True,
                                 parent=self.unit)

        self.model._model_constraints_list = [constraint]
        self.model._add_constraints(self.time)

        if isinstance(constraint, DynamicConstraint):
            for t in range(self.periods):
                self.assertIn('unit_cst_name_' + str(t),
                              self.model.constraints.keys())

        else:
            self.assertIn('unit_cst_name', self.model.constraints.keys())


class TestAddObjectives(unittest.TestCase):
    """ Test add_objectives method"""

    def setUp(self):
        periods = random.randint(1, 6000)
        self.time = TimeUnit(periods=periods)
        self.model = OptimisationModel(self.time)

        self.unit = OptObject(name='unit')

    def test_add_objective(self):
        """ Check that all objective are added to the model with their
        weights taken into account to create the optimisation expression """

        obj_1 = Objective(exp='2.50 * x', weight=3, parent=self.unit)
        obj_2 = Objective(exp='3 * x - 5', weight=2, parent=self.unit)

        self.model._add_quantity(q_name='x', q_val=0, q_type=LpContinuous,
                                 q_lb=None, q_ub=None, q_opt=True,
                                 parent=self.unit)

        self.model._model_objectives_list = [obj_1, obj_2]
        self.model._add_objectives(self.time)

        self.assertEqual('13.5*x - 10.0', str(self.model.objective))


class TestGetLists(unittest.TestCase):
    """ Test quantity, constraint and objective get methods"""

    def setUp(self):
        self.time = TimeUnit(periods=1, dt=1)
        self.model = OptimisationModel(name='model', time=self.time)
        self.unit0 = EnergyUnit(time=self.time, name='unit0')
        self.unit1 = VariableEnergyUnit(time=self.time, name='unit1')
        self.node = EnergyNode(name='node', time=self.time)

    def test_add_and_get_constraints(self):
        """ Test if the constraint is added into the model is available with
        get_constraints_name_list()
        """
        self.unit1.constraint = Constraint(exp="unit1_p==1", name='cst_test')
        self.node.connect_units(self.unit1)
        self.model.add_nodes(self.node)
        self.model.solve()
        self.assertEqual(self.model.get_model_constraints_name_list(), [
            'node_power_balance', 'unit1_calc_e_tot', 'unit1_on_off_max',
            'unit1_on_off_min', 'unit1_cst_test'])

    def test_add_and_get_objectives(self):
        """ Test if the objective is added into the model is available with
        get_objectives_name_list() """
        self.unit0.objectives = Objective(exp="lpSum(unit0_p)",
                                          name='obj_test')
        self.node.connect_units(self.unit0)
        self.model.add_nodes(self.node)
        self.model.solve()
        self.assertEqual(self.model.get_model_objectives_name_list(),
                         ['unit0_obj_test'])

    def test_add_and_get_quantities(self):
        """ Test if the quantity is added into the model is available with
        get_quantities_name_list() """
        self.unit1.quantity = Quantity(name='quantity_test')
        self.node.connect_units(self.unit1)
        self.model.add_nodes(self.node)
        self.model.solve()
        self.assertEqual(self.model.get_model_quantities_name_list(),
                         ['unit1_p', 'unit1_e_tot', 'unit1_u',
                          'unit1_quantity_test'])


class TestAddNode(unittest.TestCase):
    """ Test add_nodes method"""

    def setUp(self):
        self.model_time = TimeUnit(periods=2, dt=1)
        self.model = OptimisationModel(time=self.model_time)
        self.other_time = TimeUnit(periods=4, dt=1)

    def test_adding_unit_instead_of_node(self):
        """
        Check that it raises an error if an energyunit is added instead of a
        node

        """
        self.unit = EnergyUnit(time=self.model_time, name='U')
        self.node = EnergyNode(time=self.model_time, name='N')
        self.node.connect_units(self.unit)

        with self.assertRaises(TypeError):
            self.model.add_nodes(self.unit)

    def test_node_with_different_model_time(self):
        """
        Check that it raises an error if the time of a node is different of
        the model time

        """
        self.node = EnergyNode(time=self.other_time, name='N')

        with self.assertRaises(ValueError):
            self.model.add_nodes(self.node)

    def test_unit_with_different_model_time(self):
        """
        Check that it raises an error if the time of a unit is different of
        the model time

        """
        self.unit = EnergyUnit(time=self.other_time, name='U')
        self.node = EnergyNode(time=self.model_time, name='N')
        self.node.connect_units(self.unit)

        with self.assertRaises(ValueError):
            self.model.add_nodes(self.node)


class TestAddNodeAndActors(unittest.TestCase):
    """ Test add_nodes_and_actors method"""

    def setUp(self):
        self.model_time = TimeUnit(periods=2, dt=1)
        self.model = OptimisationModel(time=self.model_time)
        self.other_time = TimeUnit(periods=4, dt=1)

    def test_adding_unit_instead_of_node(self):
        """
        Check that it raises an error if an energyunit is added instead of a
        node

        """
        self.unit = EnergyUnit(time=self.model_time, name='U')
        self.node = EnergyNode(time=self.model_time, name='N')
        self.node.connect_units(self.unit)

        with self.assertRaises(TypeError):
            self.model.add_nodes(self.unit)

    def test_node_with_different_model_time(self):
        """
        Check that it raises an error if the time of a node is different of
        the model time

        """
        self.node = EnergyNode(time=self.other_time, name='N')

        with self.assertRaises(ValueError):
            self.model.add_nodes(self.node)

    def test_unit_with_different_model_time(self):
        """
        Check that it raises an error if the time of a unit is different of
        the model time

        """
        self.unit = EnergyUnit(time=self.other_time, name='U')
        self.node = EnergyNode(time=self.model_time, name='N')
        self.node.connect_units(self.unit)

        with self.assertRaises(ValueError):
            self.model.add_nodes(self.node)
