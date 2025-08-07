#! usr/bin/env python3
#  -*- coding: utf-8 -*-

""""
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

import os
import unittest
import random

from omegalpes.general.optimisation.model import OptimisationModel
from omegalpes.general.time import TimeUnit
from omegalpes.energy.units.consumption_units import FixedConsumptionUnit
from omegalpes.energy.units.production_units import VariableProductionUnit
from omegalpes.energy.units.storage_units import StorageUnit
from omegalpes.energy.energy_nodes import EnergyNode

from examples.storage_design import main


class TestStorageDesign(unittest.TestCase):
    """ Unittests for the example storage_design.py """
    def setUp(self):
        self.load_profile = [4, 5, 6, 2, 3, 4, 7, 8, 13, 24, 18, 16, 17, 12,
                             20, 15, 17, 21, 25, 23, 18, 16, 13, 4]
        self.production_p_max = 15
        self.storage_pcharge_max = 20
        self.storage_pdischarge_max = 20
        self.work_path = os.getcwd()[:-5] + 'examples'

    def test_load_profile_creation(self):
        """
            Check if the load profile is taken into account for power values
        """
        load_profile = []
        while len(load_profile) < 24:
            load_profile.append(random.randrange(0, 50000))

        _, _, load, _, _, _ = main(work_path=self.work_path,
                                   load_profile=load_profile,
                                   production_pmax=self.production_p_max,
                                   storage_pcharge_max=self.storage_pcharge_max,
                                   storage_pdischarge_max=self.storage_pdischarge_max)

        self.assertListEqual(load_profile, load.p.value)

    def test_p_max_prod(self):
        """ Check if the p_max constraint is respected for the production. """
        production_p_max = random.randrange(15, 50000)

        _, _, _, prod, _, _ = main(work_path=self.work_path,
                                   load_profile=self.load_profile,
                                   production_pmax=production_p_max,
                                   storage_pcharge_max=self.storage_pcharge_max,
                                   storage_pdischarge_max=
                                   self.storage_pdischarge_max)

        for power in prod.p.value.values():
            self.assertLessEqual(power, production_p_max)

    def test_p_min_storage(self):
        """ Check if the p_max constraint is respected for the storage. """
        storage_p_min = random.randrange(0, 20)

        _, _, _, _, stor, _ = main(work_path=self.work_path,
                                   load_profile=self.load_profile,
                                   production_pmax=self.production_p_max,
                                   storage_pcharge_max=self.storage_pcharge_max,
                                   storage_pdischarge_max=storage_p_min)

        for power in stor.p.value.values():
            self.assertGreaterEqual(power, -storage_p_min)

    def test_p_max_storage(self):
        """ Check if the p_max constraint is respected for the storage. """
        storage_p_max = random.randrange(20, 5000)

        _, _, _, _, stor, _ = main(work_path=self.work_path,
                                   load_profile=self.load_profile,
                                   production_pmax=self.production_p_max,
                                   storage_pcharge_max=storage_p_max,
                                   storage_pdischarge_max=
                                   self.storage_pdischarge_max)

        for power in stor.p.value.values():
            self.assertLessEqual(power, storage_p_max)

    def test_cycling(self):
        """ Check if the storage is cycling """
        _, _, _, _, stor, _ = main(work_path=self.work_path,
                                   load_profile=self.load_profile,
                                   production_pmax=self.production_p_max,
                                   storage_pcharge_max=self.storage_pcharge_max,
                                   storage_pdischarge_max=
                                   self.storage_pdischarge_max)
        e_init = list(stor.e.value.values())[0]
        e_final = stor.e_f.value

        self.assertEqual(e_init, e_final)

    def test_soc_min(self):
        """ Check if the minimal value of state of charge is respected """
        _, _, _, _, stor, _ = main(work_path=self.work_path,
                                   load_profile=self.load_profile,
                                   production_pmax=self.production_p_max,
                                   storage_pcharge_max=self.storage_pcharge_max,
                                   storage_pdischarge_max=
                                   self.storage_pdischarge_max)

        e_min = stor.capacity.value * 0.1

        for soc in stor.e.value.values():
            self.assertGreaterEqual(soc, e_min)

    def test_soc_max(self):
        """ Check if the maximal value of state of charge is respected """
        _, _, _, _, stor, _ = main(work_path=self.work_path,
                                   load_profile=self.load_profile,
                                   production_pmax=self.production_p_max,
                                   storage_pcharge_max=self.storage_pcharge_max,
                                   storage_pdischarge_max=
                                   self.storage_pdischarge_max)

        e_max = stor.capacity.value * 0.9

        for soc in stor.e.value.values():
            self.assertLessEqual(soc, e_max)

    def test_capacity_result(self):
        """ Check if the capacity results with the defined parameters is the
        right solution """
        _, _, _, _, stor, _ = main(work_path=self.work_path,
                                   load_profile=self.load_profile,
                                   production_pmax=self.production_p_max,
                                   storage_pcharge_max=self.storage_pcharge_max,
                                   storage_pdischarge_max=
                                   self.storage_pdischarge_max)

        self.assertAlmostEqual(stor.capacity.value, 70.149254)

    def test_return_first_model(self):
        """ Check if the first value of return is an OptimisationModel """
        mod, _, _, _, _, _ = main(work_path=self.work_path,
                                  load_profile=self.load_profile,
                                  production_pmax=self.production_p_max,
                                  storage_pcharge_max=self.storage_pcharge_max,
                                  storage_pdischarge_max=
                                  self.storage_pdischarge_max)

        self.assertIsInstance(mod, OptimisationModel)

    def test_return_second_time(self):
        """ Check if the second value of return is a TimeUnit """
        _, time, _, _, _, _ = main(work_path=self.work_path,
                                   load_profile=self.load_profile,
                                   production_pmax=self.production_p_max,
                                   storage_pcharge_max=self.storage_pcharge_max,
                                   storage_pdischarge_max=
                                   self.storage_pdischarge_max)

        self.assertIsInstance(time, TimeUnit)

    def test_return_third_load(self):
        """ Check if the third value of return is a FixedConsumptionUnit """
        _, _, load, _, _, _ = main(work_path=self.work_path,
                                   load_profile=self.load_profile,
                                   production_pmax=self.production_p_max,
                                   storage_pcharge_max=self.storage_pcharge_max,
                                   storage_pdischarge_max=
                                   self.storage_pdischarge_max)

        self.assertIsInstance(load, FixedConsumptionUnit)

    def test_return_fourth_production(self):
        """ Check if the fourth value of return is a VariableProductionUnit """
        _, _, _, prod, _, _ = main(work_path=self.work_path,
                                   load_profile=self.load_profile,
                                   production_pmax=self.production_p_max,
                                   storage_pcharge_max=self.storage_pcharge_max,
                                   storage_pdischarge_max=
                                   self.storage_pdischarge_max)

        self.assertIsInstance(prod, VariableProductionUnit)

    def test_return_fifth_storage(self):
        """ Check if the fifth value of return is a StorageUnit """
        _, _, _, _, stor, _ = main(work_path=self.work_path,
                                   load_profile=self.load_profile,
                                   production_pmax=self.production_p_max,
                                   storage_pcharge_max=self.storage_pcharge_max,
                                   storage_pdischarge_max=
                                   self.storage_pdischarge_max)

        self.assertIsInstance(stor, StorageUnit)

    def test_return_sixth_node(self):
        """ Check if the sixth value of return is an EnergyNode """
        _, _, _, _, _, node = main(work_path=self.work_path,
                                   load_profile=self.load_profile,
                                   production_pmax=self.production_p_max,
                                   storage_pcharge_max=self.storage_pcharge_max,
                                   storage_pdischarge_max=
                                   self.storage_pdischarge_max)

        self.assertIsInstance(node, EnergyNode)
