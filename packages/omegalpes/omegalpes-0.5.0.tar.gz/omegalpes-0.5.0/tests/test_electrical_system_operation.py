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
from examples.electrical_system_operation import main
from omegalpes.general.optimisation.model import OptimisationModel
from omegalpes.general.time import TimeUnit
from omegalpes.energy.units.consumption_units import FixedConsumptionUnit
from omegalpes.energy.units.production_units import VariableProductionUnit


class TestElectricalSystemOperation(unittest.TestCase):
    """ Unittests for the example electrical_system_operation.py """

    def setUp(self):
        # Hourly operating costs for the first production unit
        self.work_path = os.getcwd()[:-5] + 'examples'
        self.consumption_file = self.work_path + \
                                "/data/building_consumption_day.txt"
        self.operating_costs_a = [41.1, 41.295, 43.125, 51.96, 58.275, 62.955,
                                  58.08, 57.705, 59.94, 52.8, 53.865, 46.545,
                                  41.4, 39, 36.87, 36.6, 39.15, 43.71, 45.195,
                                  47.04, 44.28, 39.975, 34.815, 28.38]
        # Hourly operating costs for the second production unit
        self.operating_costs_b = [58.82, 58.23, 51.95, 47.27, 45.49, 44.5, 44.5,
                                  44.72, 44.22, 42.06, 45.7, 47.91, 49.57,
                                  48.69, 46.91, 46.51, 46.52, 51.59, 59.07,
                                  62.1, 56.26, 55, 56.02, 52]

    def test_load_creation(self):
        """ Check the name for the load creation """
        self.assertIsInstance(self.consumption_file, str)

        self.assertEqual(self.consumption_file,
                         self.work_path + "/data/building_consumption_day.txt")

    def test_return_first_model(self):
        """ Check if the first value of return is an OptimisationModel """
        model, _, _, _, _ = main(work_path=self.work_path,
                                 op_cost_a=self.operating_costs_a,
                                 op_cost_b=self.operating_costs_b,
                                 consumption_file=self.consumption_file)

        self.assertIsInstance(model, OptimisationModel)

    def test_return_second_time(self):
        """ Check if the second value of return is a TimeUnit """
        _, time, _, _, _ = main(work_path=self.work_path,
                                op_cost_a=self.operating_costs_a,
                                op_cost_b=self.operating_costs_b,
                                consumption_file=self.consumption_file)

        self.assertIsInstance(time, TimeUnit)

    def test_return_third_load(self):
        """
        Check if the third value of return is a FixedConsumptionUnit
        Check  the result of the third value
        """
        _, _, fcu, _, _ = main(work_path=self.work_path,
                               op_cost_a=self.operating_costs_a,
                               op_cost_b=self.operating_costs_b,
                               consumption_file=self.consumption_file)

        self.assertIsInstance(fcu, FixedConsumptionUnit)

        self.assertListEqual(getattr(fcu.p, 'value'), [162.0, 138.0, 91.0,
                                                       171.0, 154.0, 94.0,
                                                       155.0, 88.0, 161.0,
                                                       148.0, 155.0, 93.0, 91.0,
                                                       135.0, 94.0, 225.0, 96.0,
                                                       97.0, 150.0, 182.0,
                                                       195.0, 143.0, 198.0,
                                                       137.0])

    def test_return_fourth_fifth_production(self):
        """
        Check if the fourth and fifth values of return is a
        VariableProductionUnit type
        Check  the result of the fourth and fifth values
        """
        _, _, _, vpu, vpu2 = main(work_path=self.work_path,
                                  op_cost_a=self.operating_costs_a,
                                  op_cost_b=self.operating_costs_b,
                                  consumption_file=self.consumption_file)

        self.assertIsInstance(vpu, VariableProductionUnit)
        self.assertIsInstance(vpu2, VariableProductionUnit)

    def test_power_calculation_variable_production(self):
        """
            Check the power calculated for the variable production unit
            """
        _, _, _, vpu, _ = main(work_path=self.work_path,
                               op_cost_a=self.operating_costs_a,
                               op_cost_b=self.operating_costs_b,
                               consumption_file=self.consumption_file)

        self.assertDictEqual(getattr(vpu.p, 'value'), {0: 162.0,
                                                       1: 138.0,
                                                       2: 91,
                                                       3: 0.0, 4: 0.0, 5: 0.0,
                                                       6: 0.0, 7: 0.0, 8: 0.0,
                                                       9: 0.0, 10: 0.0,
                                                       11: 93.0, 12: 91.0,
                                                       13: 135.0, 14: 94.0,
                                                       15: 225.0, 16: 96.0,
                                                       17: 97.0, 18: 150.0,
                                                       19: 182.0, 20: 195.0,
                                                       21: 143.0, 22: 198.0,
                                                       23: 137.0})

    def test_total_energy_calculation_variable_production(self):
        """
            Check the operating cost calculated for the variable production unit
        """
        _, _, _, vpu, _ = main(work_path=self.work_path,
                               op_cost_a=self.operating_costs_a,
                               op_cost_b=self.operating_costs_b,
                               consumption_file=self.consumption_file)

        self.assertAlmostEqual(getattr(vpu.e_tot, 'value'), 2227.0)

    def test_operating_cost_calculation_variable_production(self):
        """
            Check the operating cost calculated for the variable production unit
            """
        _, _, _, vpu, _ = main(work_path=self.work_path,
                               op_cost_a=self.operating_costs_a,
                               op_cost_b=self.operating_costs_b,
                               consumption_file=self.consumption_file)

        self.assertDictEqual(getattr(vpu.operating_cost, 'value'),
                             {0: 6658.2, 1: 5698.71, 2: 3924.375,
                              3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0,
                              8: 0.0, 9: 0.0, 10: 0.0, 11: 4328.685,
                              12: 3767.4, 13: 5265.0, 14: 3465.78,
                              15: 8235.0, 16: 3758.4, 17: 4239.87,
                              18: 6779.25, 19: 8561.28, 20: 8634.6,
                              21: 5716.425, 22: 6893.37, 23: 3888.06})
