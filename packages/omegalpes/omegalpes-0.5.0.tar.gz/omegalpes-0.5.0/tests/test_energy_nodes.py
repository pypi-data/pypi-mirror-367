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
from omegalpes.general.optimisation.elements import Quantity
from omegalpes.energy.units.energy_units import EnergyUnit, AssemblyUnit
from omegalpes.energy.units.production_units import ProductionUnit
from omegalpes.energy.units.consumption_units import ConsumptionUnit
from omegalpes.general.time import TimeUnit
from omegalpes.energy.energy_nodes import EnergyNode
from omegalpes.energy.io.poles import Epole, FlowPole


class TestAddConnectedEnergyUnits(unittest.TestCase):
    """

    """

    def setUp(self):
        periods = random.randint(1, 6000)
        self.time = TimeUnit(periods=periods)
        self.energy_node = EnergyNode(time=self.time, name='energy_node')
        self.energy_unit = EnergyUnit(time=self.time, name='energy_unit')

    def test_raise_type_error(self):
        """ Test if the proper TypeError is raised when the unit is not an
        EnergyUnit"""
        unit = object()
        with self.assertRaisesRegexp(TypeError, "The unit {0} to connect to "
                                                "an EnergyNode should be an "
                                                "EnergyUnit and is {1}"
                                                .format(unit, type(unit))):
            self.energy_node.add_connected_energy_unit(unit)

    def test_raise_type_error_assembly(self):
        """ Test if the proper TypeError is raised when the unit is an
        AssemblyUnit"""
        time = TimeUnit(periods=4, dt=1)
        unit = AssemblyUnit(time=time, name='au',
                            prod_units=[ProductionUnit(time, 'pu')],
                            cons_units=[ConsumptionUnit(time, 'cu')])
        with self.assertRaisesRegexp(TypeError, "The unit {0} is an "
                                                "AssemblyUnit: you should "
                                                "connect the Energy units "
                                                "within this assembly unit to"
                                                " the node, not the whole "
                                                "unit!".format(unit.name)):
            self.energy_node.add_connected_energy_unit(unit)

    def test_add_to_list(self):
        """ Test if the EnergyUnit is added to the connected_energy_units
        list. """
        self.energy_node.add_connected_energy_unit(self.energy_unit)

        self.assertIn(self.energy_unit,
                      self.energy_node._connected_energy_units)

    def test_add_only_once_to_list(self):
        """ Test if the EnergyUnit is not added into the
        connected_energy_units list when already in it."""
        self.energy_node._connected_energy_units = [self.energy_unit]
        self.energy_node.add_connected_energy_unit(self.energy_unit)

        self.assertListEqual([self.energy_unit],
                             self.energy_node._connected_energy_units)

    def test_no_energy_type_for_unit(self):
        """
            Test if the energy_type of the EnergyUnit becomes the energy_type
            of the EnergyNode connected to the unit, when there is no
            energy_type for the EnergyUnit.
        """
        self.energy_node.energy_type = 'node_energy_type'
        self.energy_node.add_connected_energy_unit(self.energy_unit)

        self.assertEqual('node_energy_type', self.energy_unit.energy_type)

    def test_no_energy_type_for_node(self):
        """
            Test if the energy_type of the EnergyNode becomes the energy_type
            of the EnergyUnit connected to the node, when there is no
            energy_type for the EnergyNode.
        """
        self.energy_unit.energy_type = 'unit_energy_type'
        self.energy_node.add_connected_energy_unit(self.energy_unit)

        self.assertEqual('unit_energy_type', self.energy_node.energy_type)

    def test_raise_energy_type_error(self):
        """
            Test if a TypeError is raised when the energy_type of the node
            is not the same as the energy_type of the unit to be connected.
        """
        self.energy_node.energy_type = 'node_energy_type'
        self.energy_unit.energy_type = 'unit_energy_type'

        with self.assertRaises(TypeError):
            self.energy_node.add_connected_energy_unit(self.energy_unit)


class TestAddPole(unittest.TestCase):

    def setUp(self):
        periods = random.randint(1, 6000)
        self.time = TimeUnit(periods=periods)
        self.energy_node = EnergyNode(time=self.time, name='energy_node')
        self.energy_unit = EnergyUnit(time=self.time, name='energy_unit')
        flow = Quantity()
        direction = random.choice(['in', 'out'])
        self.e_pole = Epole(p=flow, direction=direction)

    def test_raise_type_error(self):
        """ Test if a TypeError is raised when the pole is not an Epole """
        pole = object()
        with self.assertRaises(AssertionError):
            self.energy_node.add_pole(pole)

    def test_add_pole_to_list(self):
        """ Test if the pole is added to the list of poles """
        self.energy_node.add_pole(self.e_pole)
        self.assertIn(self.e_pole, self.energy_node._poles_list)

    def test_add_pole_only_once_to_list(self):
        """ Test if the pole is not added to the list of poles if it
        is already in it"""
        self.energy_node._poles_list = [self.e_pole]
        self.energy_node.add_pole(self.e_pole)
        self.assertListEqual([self.e_pole], self.energy_node._poles_list)


class TestIsImport(unittest.TestCase):
    def setUp(self):
        periods = random.randint(1, 6000)
        self.time = TimeUnit(periods=periods)
        self.energy_node = EnergyNode(time=self.time, name='energy_node')
        self.q_import = Quantity()

    def test_is_import_True(self):
        """
            Test if the method returns True when the quantity test is in the
            import list.
        """
        self.energy_node._imports = [self.q_import]

        is_import = self.energy_node.is_import_flow(self.q_import)
        self.assertTrue(is_import)

    def test_is_import_False(self):
        """
            Test if the method returns False when the quantity test is not in
            the import list.
        """
        q_not_import = Quantity()
        self.energy_node._imports = [self.q_import]

        is_import = self.energy_node.is_import_flow(q_not_import)
        self.assertFalse(is_import)


class TestIsExport(unittest.TestCase):
    def setUp(self):
        periods = random.randint(1, 6000)
        self.time = TimeUnit(periods=periods)
        self.energy_node = EnergyNode(time=self.time, name='energy_node')
        self.q_export = Quantity()

    def test_is_export_True(self):
        """
            Test if the method returns True when the quantity test is in the
            export list.
        """
        self.energy_node._exports = [self.q_export]

        is_export = self.energy_node.is_export_flow(self.q_export)
        self.assertTrue(is_export)

    def test_is_export_False(self):
        """
            Test if the method returns False when the quantity test is not in
            the export list.
        """
        q_not_export = Quantity()
        self.energy_node._exports = [self.q_export]

        is_export = self.energy_node.is_import_flow(q_not_export)
        self.assertFalse(is_export)


class TestExportToNode(unittest.TestCase):
    def setUp(self):
        periods = random.randint(1, 6000)
        self.time = TimeUnit(periods=periods)
        self.energy_node = EnergyNode(time=self.time, name='energy_node')
        self.energy_node_2 = EnergyNode(time=self.time, name='energy_node_2')

    def test_raise_error_if_not_EnergyNode(self):
        """
            Test if a TypeError is raised when the node is not an EnergyNode.
        """
        not_energy_node = object()

        with self.assertRaises(TypeError):
            self.energy_node.export_to_node(not_energy_node)

    def test_raise_error_if_wrong_energy_type(self):
        """
            Test if an AttributeError is raised when the node to whom we export
            is not the same energy type as the node from whom we export.
        """
        self.energy_node.energy_type = 'energy_type_1'
        self.energy_node_2.energy_type = 'energy_type_2'

        with self.assertRaises(AttributeError):
            self.energy_node.export_to_node(self.energy_node_2)


class TestCreateExport(unittest.TestCase):
    def setUp(self):
        periods = random.randint(1, 6000)
        self.time = TimeUnit(periods=periods)
        self.energy_node = EnergyNode(time=self.time, name='energy_node')
        self.energy_node_2 = EnergyNode(time=self.time, name='energy_node_2')
        self.export_min = random.randint(1, 6000)
        self.export_max = random.randint(self.export_min, 12000)

    def test_energy_export_to_node_is_added(self):
        """
            Test if the Quantity energy_export is added as attribute to the node
        """
        self.energy_node.create_export(self.energy_node_2,
                                       self.export_min, self.export_max)
        energy_node_attr = self.energy_node.__dict__.keys()

        self.assertIn("energy_export_to_{}".format(self.energy_node_2.name),
                      energy_node_attr)

    def test_is_exporting_to_node_is_added(self):
        """
            Test if the Quantity is_exporting is added as attribute to the node
        """
        self.energy_node.create_export(self.energy_node_2,
                                       self.export_min, self.export_max)
        energy_node_attr = self.energy_node.__dict__.keys()

        self.assertIn("is_exporting_to_{}".format(self.energy_node_2.name),
                      energy_node_attr)

    def test_set_export_min_to_node_is_added(self):
        """
            Test if the Constraint set_export_min is added as attribute to the
            node
        """
        self.energy_node.create_export(self.energy_node_2,
                                       self.export_min, self.export_max)
        energy_node_attr = self.energy_node.__dict__.keys()

        self.assertIn("set_export_to_energy_node_2_min", energy_node_attr)

    def test_set_export_max_to_node_is_added(self):
        """
            Test if the Constraint set_export_max is added as attribute to the
            node
        """
        self.energy_node.create_export(self.energy_node_2,
                                       self.export_min, self.export_max)
        energy_node_attr = self.energy_node.__dict__.keys()

        self.assertIn("set_export_to_energy_node_2_max", energy_node_attr)

    def test_add_to_export_list(self):
        """
            Test if the energy_export is added to the export list
        """
        self.energy_node.create_export(self.energy_node_2,
                                       self.export_min, self.export_max)

        energy_export = getattr(self.energy_node, 'energy_export_to_{0}'.format(
            self.energy_node_2.name))
        self.assertIn(energy_export, self.energy_node._exports)

    def test_add_to_import_list(self):
        """
            Test if the energy export is added to the import list of the
            other node
        """
        self.energy_node.create_export(self.energy_node_2,
                                       self.export_min, self.export_max)

        energy_export = getattr(self.energy_node, 'energy_export_to_{0}'.format(
            self.energy_node_2.name))
        self.assertIn(energy_export, self.energy_node_2._imports)


class TestSetPowerBalance(unittest.TestCase):
    def setUp(self):
        periods = random.randint(1, 6000)
        self.time = TimeUnit(periods=periods)
        self.energy_node = EnergyNode(time=self.time, name='energy_node')

        self.energy_unit_1 = EnergyUnit(time=self.time, name='energy_unit_1')
        self.energy_unit_2 = EnergyUnit(time=self.time, name='energy_unit_2')

        flow_in = Quantity(name='flow_in', parent=self.energy_unit_1)
        flow_out = Quantity(name='flow_out', parent=self.energy_unit_2)

        self.e_pole_in = Epole(p=flow_in, direction='in')
        self.e_pole_out = Epole(p=flow_out, direction='out')

        self.energy_node._poles_list = [self.e_pole_in, self.e_pole_out]

    def test_raise_TypeError_if_not_FlowPole(self):
        """
           Test if a TypeError is raised if there is an object that is not a
           FlowPole in the pole list
        """
        not_a_pole = object()
        self.energy_node._poles_list = [not_a_pole]
        with self.assertRaises(TypeError):
            self.energy_node.set_power_balance()

    def test_if_power_balance_is_added(self):
        """
             Test if the Constraint power_balance is added as attribute to the
             node
        """
        self.energy_node.set_power_balance()

        energy_node_attr = self.energy_node.__dict__.keys()
        self.assertIn("power_balance", energy_node_attr)

    def test_power_balance_expression(self):
        """
            Test if the power_balance expression is the expected expression
        """
        self.energy_node.set_power_balance()

        power_balance = getattr(self.energy_node, 'power_balance')
        exp_t = getattr(power_balance, 'exp_t')

        self.assertEqual(exp_t, '-energy_unit_1_flow_in[t]+'
                                'energy_unit_2_flow_out[t] == 0')