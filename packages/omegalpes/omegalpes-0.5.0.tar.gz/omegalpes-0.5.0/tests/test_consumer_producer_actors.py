#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Unit tests for the module consumer_producer_actors.py, defining constraints and
objectives for consumer_producer actor type.

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
from omegalpes.actor.operator_actors.prosumer_actors import Prosumer
from omegalpes.energy.units.consumption_units import ConsumptionUnit
from omegalpes.energy.units.production_units import ProductionUnit
from omegalpes.energy.units.storage_units import StorageUnit
from omegalpes.general.time import TimeUnit
from omegalpes.general.optimisation.model import OptimisationModel
from omegalpes.energy.energy_nodes import EnergyNode
from omegalpes.general.optimisation.elements import Quantity, \
    DynamicConstraint, Objective

#TODO: Add to test for minimize capacity

class TestProsumerActor(unittest.TestCase):
    """Test of ProsumerActor definition"""

    def setUp(self):
        self.time = TimeUnit(periods=2, dt=1)
        self.conso0 = ConsumptionUnit(time=self.time, name='conso0')
        self.prod0 = ProductionUnit(time=self.time, name='prod0')
        self.stor0 = StorageUnit(time = self.time, name = "stor0")
        self.pa = Prosumer(name='pa', operated_consumption_unit_list=[
            self.conso0], operated_production_unit_list=[self.prod0],
                           operated_storage_unit_list = [self.stor0])
        self.node = EnergyNode(time=self.time, name='node')
        self.model = OptimisationModel(time=self.time, name='OM')

    def test_unit_list(self):
        """ Test operator unit lists """
        self.assertEqual(self.pa.operated_consumption_unit_list, [self.conso0])
        self.assertEqual(self.pa.operated_production_unit_list, [self.prod0])
        self.assertEqual(self.pa.operated_storage_unit_list, [self.stor0])
        self.assertEqual(self.pa.operated_unit_list, [self.conso0, self.prod0, self.stor0])


class TestCheckOperatedList(unittest.TestCase):
    """Test of _check_operated_list method dedicated to production or
    consumption"""

    def setUp(self):
        self.time = TimeUnit(periods=2, dt=1)
        self.conso0 = ConsumptionUnit(time=self.time, name='conso0')
        self.prod0 = ProductionUnit(time=self.time, name='prod0')
        self.stor0 = StorageUnit(time = self.time, name = "stor0")
        self.pa = Prosumer(name='pa', operated_consumption_unit_list=[
            self.conso0], operated_production_unit_list=[self.prod0],
                           operated_storage_unit_list = [self.stor0])
        self.pa.maximize_conso_prod_match(time=self.time)
        self.node = EnergyNode(time=self.time, name='node')
        self.model = OptimisationModel(time=self.time, name='OM')

    def test_check_operated_consumption_list(self):
        """ Test _check_operated_consumption_list method """
        operated_conso_list = self.pa._check_operated_consumption_list(
            obj_operated_unit_list=None)
        self.assertEqual(operated_conso_list,
                         self.pa.operated_consumption_unit_list)

    def test_check_operated_production_list(self):
        """ Test _check_operated_production_list method """
        operated_prod_list = self.pa._check_operated_production_list(
            obj_operated_unit_list=None)
        self.assertEqual(operated_prod_list,
                         self.pa.operated_production_unit_list)

    def test_check_operated_storage_list(self):
        """ Test _check_operated_production_list method """
        operated_stor_list = self.pa._check_operated_storage_list(
            obj_operated_unit_list=None)
        self.assertEqual(operated_stor_list,
                         self.pa.operated_storage_unit_list)


class TestMaximizeConsoProdMatch(unittest.TestCase):
    """Test of maximize_conso_prod_match method"""

    def setUp(self):
        self.time = TimeUnit(periods=2, dt=1)
        self.conso0 = ConsumptionUnit(time=self.time, name='conso0')
        self.prod0 = ProductionUnit(time=self.time, name='prod0')
        self.stor0 = StorageUnit(time = self.time, name = "stor0")
        self.pa = Prosumer(name='pa', operated_consumption_unit_list=[
            self.conso0], operated_production_unit_list=[self.prod0],
                           operated_storage_unit_list = [self.stor0])
        self.pa.maximize_conso_prod_match(time=self.time)
        self.node = EnergyNode(time=self.time, name='node')
        self.model = OptimisationModel(time=self.time, name='OM')

    def test_conso_prod_match(self):
        """ Test conso_prod_match is a Quantity """
        self.assertIsInstance(self.pa.conso_prod_match, Quantity)

    def test_calc_conso_prod_match(self):
        """ Test the conso_prod_match DynamicConstraint """
        self.assertIsInstance(self.pa.calc_conso_prod_match,
                              DynamicConstraint)
        self.assertEqual(self.pa.calc_conso_prod_match.name,
                         'calc_conso_prod_match')
        self.assertEqual(self.pa.calc_conso_prod_match.exp_t,
                         'pa_conso_prod_match[t] == (prod0_p[t] - ( conso0_p['
                         't] )) * time.DT')


class TestMaximizeSelfconsumptionRate(unittest.TestCase):
    """Test of maximize_selfconsumption_rate method"""

    def setUp(self):
        self.time = TimeUnit(periods=2, dt=1)
        self.conso0 = ConsumptionUnit(time=self.time, name='conso0')
        self.prod0 = ProductionUnit(time=self.time, name='prod0')
        self.stor0 = StorageUnit(time = self.time, name = "stor0")
        self.pa = Prosumer(name='pa', operated_consumption_unit_list=[
            self.conso0], operated_production_unit_list=[self.prod0],
                           operated_storage_unit_list = [self.stor0])
        self.pa.maximize_selfconsumption_rate(time=self.time)
        self.pa.maximize_conso_prod_match(time=self.time)
        self.node = EnergyNode(time=self.time, name='node')
        self.model = OptimisationModel(time=self.time, name='OM')

    def test_maximize_conso_prod_match(self):
        """ Test maximize_conso_prod_match is activated """
        self.assertIsInstance(self.pa.conso_prod_match, Quantity)

    def test_selfconsumption_rate(self):
        """ Test selfconsumption_rate is Quantity """
        self.assertIsInstance(self.pa.selfconsumption_rate, Quantity)

    def test_calc_selfconsumption_rate(self):
        """ Test the calc_selfconsumption_rate DynamicConstraint """
        self.assertIsInstance(self.pa.calc_selfconsumption_rate,
                              DynamicConstraint)
        self.assertEqual(self.pa.calc_selfconsumption_rate.name,
                         'calc_selfconsumption_rate')
        # TODO check + with exports
        self.assertEqual(self.pa.calc_selfconsumption_rate.exp_t,
                         'pa_selfconsumption_rate[t] == ( +  - ( prod0_p['
                         't] )) * time.DT')


class TestMaximizeSelfproductionRate(unittest.TestCase):
    """Test of maximize_selfproduction_rate method"""

    def setUp(self):
        self.time = TimeUnit(periods=2, dt=1)
        self.conso0 = ConsumptionUnit(time=self.time, name='conso0')
        self.prod0 = ProductionUnit(time=self.time, name='prod0')
        self.stor0 = StorageUnit(time = self.time, name = "stor0")
        self.pa = Prosumer(name='pa', operated_consumption_unit_list=[
            self.conso0], operated_production_unit_list=[self.prod0],
                           operated_storage_unit_list = [self.stor0])
        self.pa.maximize_conso_prod_match(time=self.time)
        self.pa.maximize_selfproduction_rate(time=self.time)
        self.node = EnergyNode(time=self.time, name='node')
        self.model = OptimisationModel(time=self.time, name='OM')

    def test_maximize_conso_prod_match(self):
        """ Test maximize_conso_prod_match is activated """
        self.assertIsInstance(self.pa.conso_prod_match, Quantity)

    def test_selfproduction_rate(self):
        """ Test selfproduction_rate is Quantity """
        self.assertIsInstance(self.pa.selfproduction_rate, Quantity)

    def test_calc_selfproduction_rate(self):
        """ Test the calc_selproduction_rate DynamicConstraint """
        self.assertIsInstance(self.pa.calc_selfproduction_rate,
                              DynamicConstraint)
        self.assertEqual(self.pa.calc_selfproduction_rate.name,
                         'calc_selfproduction_rate')
        # TODO check + with exports
        self.assertEqual(self.pa.calc_selfproduction_rate.exp_t,
                         'pa_selfproduction_rate[t] == ( +  - ( conso0_p['
                         't] )) * time.DT')
