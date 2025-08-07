#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
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
import os
import random

from examples.electric_vehicle import main
from omegalpes.general.optimisation.model import OptimisationModel
from omegalpes.general.time import TimeUnit
from omegalpes.energy.units.consumption_units import FixedConsumptionUnit
from omegalpes.energy.units.production_units import VariableProductionUnit
from omegalpes.energy.units.storage_units import StorageUnit
from omegalpes.energy.energy_nodes import EnergyNode


class TestElectricVehicle(unittest.TestCase):
    """ Unittests for the example electrical_system_operation.py """

    def setUp(self):
        self.work_path = os.getcwd()[:-5] + 'examples'

        # Load dynamic profile - one value per hour during a day
        self.load_profile = [4, 5, 6, 2, 3, 4, 7, 8, 13,
                             24, 18, 16, 17, 12, 20, 15, 17,
                             21, 25, 23, 18, 16, 13, 4]

        # Production cost dynamic profile - one value per hour during a day
        self.production_cost_profile = [20, 20, 20, 20, 20, 20, 20, 20, 40,
                                        40, 40, 40, 20, 20, 20, 20, 40,
                                        40, 40, 40, 40, 20, 20, 20]

        # EV load dynamic profile - one value per hour during a day
        self.EV_load_profile = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 10, 0, 10, 10, 0,
                                0, 0, 0, 0, 0, 0, 0]

        # EV disconnection dynamic profile - one value per hour during a day
        self.EV_connection_profile = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1,
                                      1, 1, 1, 1, 1, 1, 1]

        # EV storage maximal charging and discharging powers
        self.EV_pcharge_max = 20
        self.EV_pdischarge_max = 20

        # EV storage capacity
        self.EV_capacity = 50

    def test_load_profile_creation(self):
        """
        Check if the load profile is taken into account for power values
        """
        load_profile = []
        while len(load_profile) < 24:
            load_profile.append(random.randrange(0, 100))

        _, _, load, _, _, _, _, _ = main(work_path=self.work_path,
                                         load_profile=load_profile,
                                         EV_load_profile=self.EV_load_profile,
                                         EV_connection_profile=self.EV_connection_profile,
                                         EV_pcharge_max=self.EV_pcharge_max,
                                         EV_pdischarge_max=self.EV_pdischarge_max,
                                         EV_capacity=self.EV_capacity,
                                         production_cost_profile=self.production_cost_profile)

        self.assertListEqual(load_profile, load.p.value)

    def test_return_first_model(self):
        """ Check if the first value of return is an OptimisationModel """
        model, _, _, _, _, _, _, _ = main(work_path=self.work_path,
                                          load_profile=self.load_profile,
                                          EV_load_profile=self.EV_load_profile,
                                          EV_connection_profile=self.EV_connection_profile,
                                          EV_pcharge_max=self.EV_pcharge_max,
                                          EV_pdischarge_max=self.EV_pdischarge_max,
                                          EV_capacity=self.EV_capacity,
                                          production_cost_profile=self.production_cost_profile)

        self.assertIsInstance(model, OptimisationModel)

    def test_return_second_time(self):
        """ Check if the second value of return is a TimeUnit """
        _, time, _, _, _, _, _, _ = main(work_path=self.work_path,
                                         load_profile=self.load_profile,
                                         EV_load_profile=self.EV_load_profile,
                                         EV_connection_profile=self.EV_connection_profile,
                                         EV_pcharge_max=self.EV_pcharge_max,
                                         EV_pdischarge_max=self.EV_pdischarge_max,
                                         EV_capacity=self.EV_capacity,
                                         production_cost_profile=self.production_cost_profile)

        self.assertIsInstance(time, TimeUnit)

    def test_return_third_load(self):
        """
        Check if the third value of return is a FixedConsumptionUnit
        Check  the result of the third value
        """
        _, _, fcu, _, _, _, _, _ = main(work_path=self.work_path,
                                        load_profile=self.load_profile,
                                        EV_load_profile=self.EV_load_profile,
                                        EV_connection_profile=self.EV_connection_profile,
                                        EV_pcharge_max=self.EV_pcharge_max,
                                        EV_pdischarge_max=self.EV_pdischarge_max,
                                        EV_capacity=self.EV_capacity,
                                        production_cost_profile=self.production_cost_profile)

        self.assertIsInstance(fcu, FixedConsumptionUnit)

        self.assertListEqual(getattr(fcu.p, 'value'), [4, 5, 6, 2, 3, 4, 7, 8, 13,
                                                       24, 18, 16, 17, 12, 20, 15, 17,
                                                       21, 25, 23, 18, 16, 13, 4]
                             )

    def test_return_fourth_fifth_production(self):
        """
        Check if the fourth value of return is a
        VariableProductionUnit type
        """
        _, _, _, vpu, _, _, _, _ = main(work_path=self.work_path,
                                        load_profile=self.load_profile,
                                        EV_load_profile=self.EV_load_profile,
                                        EV_connection_profile=self.EV_connection_profile,
                                        EV_pcharge_max=self.EV_pcharge_max,
                                        EV_pdischarge_max=self.EV_pdischarge_max,
                                        EV_capacity=self.EV_capacity,
                                        production_cost_profile=self.production_cost_profile)

        self.assertIsInstance(vpu, VariableProductionUnit)

    def test_power_calculation_variable_production(self):
        """
        Check the power calculated for the variable production unit
        """
        _, _, _, vpu, _, _, _, _ = main(work_path=self.work_path,
                                        load_profile=self.load_profile,
                                        EV_load_profile=self.EV_load_profile,
                                        EV_connection_profile=self.EV_connection_profile,
                                        EV_pcharge_max=self.EV_pcharge_max,
                                        EV_pdischarge_max=self.EV_pdischarge_max,
                                        EV_capacity=self.EV_capacity,
                                        production_cost_profile=self.production_cost_profile)

        self.assertDictEqual(getattr(vpu.p, 'value'), {0: 4.0, 1: 5.0,
                                                       2: 6.0, 3: 2.0,
                                                       4: 13.0, 5: 4.0,
                                                       6: 27.0, 7: 28.0,
                                                       8: 3.0, 9: 24.0,
                                                       10: 18.0, 11: 16.0,
                                                       12: 17.0, 13: 12.0,
                                                       14: 20.0, 15: 15.0,
                                                       16: 17.0, 17: 21.0,
                                                       18: 25.0, 19: 23.0,
                                                       20: 18.0, 21: 16.0,
                                                       22: 13.0, 23: 4.0})

    def test_total_energy_calculation_variable_production(self):
        """
        Check the total energy produced calculated for the variable production unit
        """
        _, _, _, vpu, _, _, _, _ = main(work_path=self.work_path,
                                        load_profile=self.load_profile,
                                        EV_load_profile=self.EV_load_profile,
                                        EV_connection_profile=self.EV_connection_profile,
                                        EV_pcharge_max=self.EV_pcharge_max,
                                        EV_pdischarge_max=self.EV_pdischarge_max,
                                        EV_capacity=self.EV_capacity,
                                        production_cost_profile=self.production_cost_profile)

        self.assertAlmostEqual(getattr(vpu.e_tot, 'value'), 351.0)

    def test_operating_cost_calculation_variable_production(self):
        """
        Check the operating cost calculated for the variable production unit
        """
        _, _, _, vpu, _, _, _, _ = main(work_path=self.work_path,
                                        load_profile=self.load_profile,
                                        EV_load_profile=self.EV_load_profile,
                                        EV_connection_profile=self.EV_connection_profile,
                                        EV_pcharge_max=self.EV_pcharge_max,
                                        EV_pdischarge_max=self.EV_pdischarge_max,
                                        EV_capacity=self.EV_capacity,
                                        production_cost_profile=self.production_cost_profile)

        self.assertDictEqual(getattr(vpu.operating_cost, 'value'),
                             {0: 80.0, 1: 100.0, 2: 120.0, 3: 40.0,
                              4: 260.0, 5: 80.0, 6: 540.0, 7: 560.0, 8: 120.0,
                              9: 960.0, 10: 720.0, 11: 640.0, 12: 340.0,
                              13: 240.0, 14: 400.0, 15: 300.0, 16: 680.0,
                              17: 840.0, 18: 1000.0, 19: 920.0, 20: 720.0,
                              21: 320.0, 22: 260.0, 23: 80.0})

    def test_return_fith_load(self):
        """
        Check if the fith value of return is a FixedConsumptionUnit
        Check  the result of the fith value
        """
        _, _, _, _, fcu, _, _, _ = main(work_path=self.work_path,
                                        load_profile=self.load_profile,
                                        EV_load_profile=self.EV_load_profile,
                                        EV_connection_profile=self.EV_connection_profile,
                                        EV_pcharge_max=self.EV_pcharge_max,
                                        EV_pdischarge_max=self.EV_pdischarge_max,
                                        EV_capacity=self.EV_capacity,
                                        production_cost_profile=self.production_cost_profile)

        self.assertIsInstance(fcu, FixedConsumptionUnit)

        self.assertListEqual(getattr(fcu.p, 'value'), [0, 0, 0, 0, 0, 0, 0, 0,
                                                       0, 0, 0, 10, 10, 0, 10, 10, 0,
                                                       0, 0, 0, 0, 0, 0, 0])

    def test_return_sixth_storage(self):
        """
        Check if the sixth value of return is a StorageUnit
        """
        _, _, _, _, _, sto, _, _ = main(work_path=self.work_path,
                                        load_profile=self.load_profile,
                                        EV_load_profile=self.EV_load_profile,
                                        EV_connection_profile=self.EV_connection_profile,
                                        EV_pcharge_max=self.EV_pcharge_max,
                                        EV_pdischarge_max=self.EV_pdischarge_max,
                                        EV_capacity=self.EV_capacity,
                                        production_cost_profile=self.production_cost_profile)

        self.assertIsInstance(sto, StorageUnit)

    def test_energy_calculation_storage(self):
        """
        Check the energy calculated for the storage unit
        """
        _, _, _, _, _, sto, _, _ = main(work_path=self.work_path,
                                        load_profile=self.load_profile,
                                        EV_load_profile=self.EV_load_profile,
                                        EV_connection_profile=self.EV_connection_profile,
                                        EV_pcharge_max=self.EV_pcharge_max,
                                        EV_pdischarge_max=self.EV_pdischarge_max,
                                        EV_capacity=self.EV_capacity,
                                        production_cost_profile=self.production_cost_profile)

        self.assertDictEqual(getattr(sto.e, 'value'), {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0,
                                                       4: 0.0, 5: 10.0, 6: 10.0, 7: 30.0,
                                                       8: 50.0, 9: 40.0, 10: 40.0, 11: 40.0,
                                                       12: 30.0, 13: 20.0, 14: 20.0, 15: 10.0,
                                                       16: 0.0, 17: 0.0, 18: 0.0, 19: 0.0, 20: 0.0,
                                                       21: 0.0, 22: 0.0, 23: 0.0})

    def test_seventh_node(self):
        """Checking the 7th return is a node"""
        _, _, _, _, _, _, EV_node, _ = main(work_path=self.work_path,
                                            load_profile=self.load_profile,
                                            EV_load_profile=self.EV_load_profile,
                                            EV_connection_profile=self.EV_connection_profile,
                                            EV_pcharge_max=self.EV_pcharge_max,
                                            EV_pdischarge_max=self.EV_pdischarge_max,
                                            EV_capacity=self.EV_capacity,
                                            production_cost_profile=self.production_cost_profile)
        self.assertIsInstance(EV_node, EnergyNode)

    def test_seventh_node(self):
        """Checking the 8th return is a node"""
        _, _, _, _, _, _, _, main_node = main(work_path=self.work_path,
                                              load_profile=self.load_profile,
                                              EV_load_profile=self.EV_load_profile,
                                              EV_connection_profile=self.EV_connection_profile,
                                              EV_pcharge_max=self.EV_pcharge_max,
                                              EV_pdischarge_max=self.EV_pdischarge_max,
                                              EV_capacity=self.EV_capacity,
                                              production_cost_profile=self.production_cost_profile)
        self.assertIsInstance(main_node, EnergyNode)
