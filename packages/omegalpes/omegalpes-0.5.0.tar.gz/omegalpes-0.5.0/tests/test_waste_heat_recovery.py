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
import os
import random
from pulp import LpStatus
from omegalpes.energy.energy_nodes import EnergyNode
from omegalpes.energy.units.consumption_units import FixedConsumptionUnit, \
    VariableConsumptionUnit
from omegalpes.energy.units.conversion_units import \
    SingleConversionUnit, HeatPump
from omegalpes.energy.units.production_units import ProductionUnit
from omegalpes.energy.units.storage_units import StorageUnit
from omegalpes.general.optimisation.model import OptimisationModel
from omegalpes.general.time import TimeUnit
from examples.waste_heat_recovery import main


class TestWasteHeatRecoverySystem(unittest.TestCase):
    """ Unittests for the example waste_heat_recovery.py """

    def setUp(self):
        self.elec_to_therm_ratio = 0.9
        self.pc_max_sto = self.pd_max_sto = 5000
        self.pc_min_sto = self.pd_min_sto = 0.15 * self.pc_max_sto
        self.capa_sto = 20000
        self.soc_0 = 0.2
        self.cop = 3
        self.p_max_hp = 1000
        self.work_path = os.getcwd()[:-5] + 'examples'

    def test_file_indus(self):
        """Checking the text file for the indus consumption is properly
        taken into account"""
        indus_cons_file = open(self.work_path + "/data/indus_cons_week.txt",
                               "r")
        indus_cons = [c for c in map(float, indus_cons_file)]

        _, _, indus, _, _, _, _, _, _, _, _ = main(work_path=self.work_path,
                                                   elec2therm_ratio=
                                                   self.elec_to_therm_ratio,
                                                   pc_max=self.pc_max_sto,
                                                   pd_max=self.pd_max_sto,
                                                   pc_min=self.pc_min_sto,
                                                   pd_min=self.pd_min_sto,
                                                   capa=self.capa_sto,
                                                   cop_hp=self.cop,
                                                   pmax_elec_hp=self.p_max_hp,
                                                   storage_soc_0=self.soc_0)

        self.assertEqual(indus.consumption_unit.p.value, indus_cons)

    def test_file_cons(self):
        """Checking the text file for the district heat load consumption is
        properly taken into account"""
        heat_load_file = open(self.work_path +
                              "/data/District_heat_load_consumption.txt", "r")
        heat_load = [c for c in map(float, heat_load_file)]
        _, _, _, dhl, _, _, _, _, _, _, _ = main(work_path=self.work_path,
                                                 elec2therm_ratio=
                                                 self.elec_to_therm_ratio,
                                                 pc_max=self.pc_max_sto,
                                                 pd_max=self.pd_max_sto,
                                                 pc_min=self.pc_min_sto,
                                                 pd_min=self.pd_min_sto,
                                                 capa=self.capa_sto,
                                                 cop_hp=self.cop,
                                                 pmax_elec_hp=self.p_max_hp,
                                                 storage_soc_0=self.soc_0)
        self.assertEqual(dhl.p.value, heat_load)

    # def test_p_min_storage(self):
    #     """ Checking if the p_min constraint is respected for the storage. """
    #     storage_p_min = random.randrange(0, self.pc_min_sto)
    #
    #     _, _, _, _, _, _, _, sto, _, _, _ = main(work_path=self.work_path,
    #                                              elec2heat_ratio=
    #                                              self.elec_to_therm_ratio,
    #                                              pc_max=self.pc_max_sto,
    #                                              pd_max=self.pd_max_sto,
    #                                              pc_min=storage_p_min,
    #                                              pd_min=storage_p_min,
    #                                              capa=self.capa_sto,
    #                                              cop_hp=self.cop,
    #                                              pmax_elec_hp=self.p_max_hp,
    #                                              storage_soc_0=self.soc_0)
    #
    #     for i in range (0, sto.time.LEN):
    #         self.assertGreaterEqual(sto.p.value[i],
    #                                 storage_p_min*sto.u.value[i])
    # TODO: check pc and pd min & max thanks to uc and u (see constraints in
    #  storage unit)

    def test_p_max_storage(self):
        """ Checking if the p_max constraint is respected for the storage. """
        storage_p_max = random.randrange(self.pc_min_sto, self.pd_max_sto)

        _, _, _, _, _, _, _, sto, _, _, _ = main(work_path=self.work_path,
                                                 elec2therm_ratio=
                                                 self.elec_to_therm_ratio,
                                                 pc_max=storage_p_max,
                                                 pd_max=storage_p_max,
                                                 pc_min=self.pc_min_sto,
                                                 pd_min=self.pd_min_sto,
                                                 capa=self.capa_sto,
                                                 cop_hp=self.cop,
                                                 pmax_elec_hp=self.p_max_hp,
                                                 storage_soc_0=self.soc_0)

        for power in sto.p.value.values():
            self.assertLessEqual(power, storage_p_max)

    def test_p_max_hp(self):
        """ Checking if the p_max constraint is respected for the heat pump."""
        hp_p_max = random.randrange(0, self.p_max_hp)

        _, _, _, _, hp, _, _, _, _, _, _ = main(work_path=self.work_path,
                                                elec2therm_ratio=
                                                self.elec_to_therm_ratio,
                                                pc_max=self.pc_max_sto,
                                                pd_max=self.pd_max_sto,
                                                pc_min=self.pc_min_sto,
                                                pd_min=self.pd_min_sto,
                                                capa=self.capa_sto,
                                                cop_hp=self.cop,
                                                pmax_elec_hp=hp_p_max,
                                                storage_soc_0=self.soc_0)

        for power in hp.elec_consumption_unit.p.value.values():
            self.assertLessEqual(power, hp_p_max)

    def test_minimise_heat_prod(self):
        """Checking the optimisation result"""
        _, _, _, _, _, h_prod, _, _, _, _, _ = main(work_path=self.work_path,
                                                    elec2therm_ratio=
                                                    self.elec_to_therm_ratio,
                                                    pc_max=self.pc_max_sto,
                                                    pd_max=self.pd_max_sto,
                                                    pc_min=self.pc_min_sto,
                                                    pd_min=self.pd_min_sto,
                                                    capa=self.capa_sto,
                                                    cop_hp=self.cop,
                                                    pmax_elec_hp=self.p_max_hp,
                                                    storage_soc_0=self.soc_0)
        self.assertEqual(h_prod.e_tot.value, 171563.17)

    def test_first_model(self):
        """Checking the first return is a model"""
        mod, _, _, _, _, _, _, _, _, _, _ = main(work_path=self.work_path,
                                                 elec2therm_ratio=self.elec_to_therm_ratio,
                                                 pc_max=self.pc_max_sto,
                                                 pd_max=self.pd_max_sto,
                                                 pc_min=self.pc_min_sto,
                                                 pd_min=self.pd_min_sto,
                                                 capa=self.capa_sto,
                                                 cop_hp=self.cop,
                                                 pmax_elec_hp=self.p_max_hp,
                                                 storage_soc_0=self.soc_0)
        self.assertIsInstance(mod, OptimisationModel)

    def test_second_time(self):
        """Checking the second return is a time unit"""
        _, time, _, _, _, _, _, _, _, _, _ = main(work_path=self.work_path,
                                                  elec2therm_ratio=
                                                  self.elec_to_therm_ratio,
                                                  pc_max=self.pc_max_sto,
                                                  pd_max=self.pd_max_sto,
                                                  pc_min=self.pc_min_sto,
                                                  pd_min=self.pd_min_sto,
                                                  capa=self.capa_sto,
                                                  cop_hp=self.cop,
                                                  pmax_elec_hp=self.p_max_hp,
                                                  storage_soc_0=self.soc_0)
        self.assertIsInstance(time, TimeUnit)

    def test_third_convers(self):
        """Checking the 3rd return is a conversion unit"""
        _, _, indus, _, _, _, _, _, _, _, _ = main(work_path=self.work_path,
                                                   elec2therm_ratio=self.elec_to_therm_ratio,
                                                   pc_max=self.pc_max_sto,
                                                   pd_max=self.pd_max_sto,
                                                   pc_min=self.pc_min_sto,
                                                   pd_min=self.pd_min_sto,
                                                   capa=self.capa_sto,
                                                   cop_hp=self.cop,
                                                   pmax_elec_hp=self.p_max_hp,
                                                   storage_soc_0=self.soc_0)
        self.assertIsInstance(indus, SingleConversionUnit)

    def test_fourth_cons(self):
        """Checking the 4th return is a consumption unit"""
        _, _, _, dhl, _, _, _, _, _, _, _ = main(work_path=self.work_path,
                                                 elec2therm_ratio=
                                                 self.elec_to_therm_ratio,
                                                 pc_max=self.pc_max_sto,
                                                 pd_max=self.pd_max_sto,
                                                 pc_min=self.pc_min_sto,
                                                 pd_min=self.pd_min_sto,
                                                 capa=self.capa_sto,
                                                 cop_hp=self.cop,
                                                 pmax_elec_hp=self.p_max_hp,
                                                 storage_soc_0=self.soc_0)
        self.assertIsInstance(dhl, FixedConsumptionUnit)

    def test_fifth_hp(self):
        """Checking the 5th return is a heat pump"""
        _, _, _, _, hp, _, _, _, _, _, _ = main(work_path=self.work_path,
                                                elec2therm_ratio=
                                                self.elec_to_therm_ratio,
                                                pc_max=self.pc_max_sto,
                                                pd_max=self.pd_max_sto,
                                                pc_min=self.pc_min_sto,
                                                pd_min=self.pd_min_sto,
                                                capa=self.capa_sto,
                                                cop_hp=self.cop,
                                                pmax_elec_hp=self.p_max_hp,
                                                storage_soc_0=self.soc_0)
        self.assertIsInstance(hp, HeatPump)

    def test_sixth_heat_prod(self):
        """Checking the 6th return is a heat prod"""
        _, _, _, _, _, h_prod, _, _, _, _, _ = main(work_path=self.work_path,
                                                    elec2therm_ratio=
                                                    self.elec_to_therm_ratio,
                                                    pc_max=self.pc_max_sto,
                                                    pd_max=self.pd_max_sto,
                                                    pc_min=self.pc_min_sto,
                                                    pd_min=self.pd_min_sto,
                                                    capa=self.capa_sto,
                                                    cop_hp=self.cop,
                                                    pmax_elec_hp=self.p_max_hp,
                                                    storage_soc_0=self.soc_0)
        self.assertIsInstance(h_prod, ProductionUnit)

    def test_seventh_dissip(self):
        """Checking the 7th return is a consumption unit"""
        _, _, _, _, _, _, dissip, _, _, _, _ = main(work_path=self.work_path,
                                                    elec2therm_ratio=
                                                    self.elec_to_therm_ratio,
                                                    pc_max=self.pc_max_sto,
                                                    pd_max=self.pd_max_sto,
                                                    pc_min=self.pc_min_sto,
                                                    pd_min=self.pd_min_sto,
                                                    capa=self.capa_sto,
                                                    cop_hp=self.cop,
                                                    pmax_elec_hp=self.p_max_hp,
                                                    storage_soc_0=self.soc_0)
        self.assertIsInstance(dissip, VariableConsumptionUnit)

    def test_eighth_sto(self):
        """Checking the 8th return is a consumption unit"""
        _, _, _, _, _, _, _, sto, _, _, _ = main(work_path=self.work_path,
                                                 elec2therm_ratio=
                                                 self.elec_to_therm_ratio,
                                                 pc_max=self.pc_max_sto,
                                                 pd_max=self.pd_max_sto,
                                                 pc_min=self.pc_min_sto,
                                                 pd_min=self.pd_min_sto,
                                                 capa=self.capa_sto,
                                                 cop_hp=self.cop,
                                                 pmax_elec_hp=self.p_max_hp,
                                                 storage_soc_0=self.soc_0)
        self.assertIsInstance(sto, StorageUnit)

    def test_ninth_node(self):
        """Checking the 9th return is a node"""
        _, _, _, _, _, _, _, _, hnb, _, _ = main(work_path=self.work_path,
                                                 elec2therm_ratio=
                                                 self.elec_to_therm_ratio,
                                                 pc_max=self.pc_max_sto,
                                                 pd_max=self.pd_max_sto,
                                                 pc_min=self.pc_min_sto,
                                                 pd_min=self.pd_min_sto,
                                                 capa=self.capa_sto,
                                                 cop_hp=self.cop,
                                                 pmax_elec_hp=self.p_max_hp,
                                                 storage_soc_0=self.soc_0)
        self.assertIsInstance(hnb, EnergyNode)

    def test_tenth_node(self):
        """Checking the 10th return is a node"""
        _, _, _, _, _, _, _, _, _, hna, _ = main(work_path=self.work_path,
                                                 elec2therm_ratio=
                                                 self.elec_to_therm_ratio,
                                                 pc_max=self.pc_max_sto,
                                                 pd_max=self.pd_max_sto,
                                                 pc_min=self.pc_min_sto,
                                                 pd_min=self.pd_min_sto,
                                                 capa=self.capa_sto,
                                                 cop_hp=self.cop,
                                                 pmax_elec_hp=self.p_max_hp,
                                                 storage_soc_0=self.soc_0)
        self.assertIsInstance(hna, EnergyNode)

    def test_eleventh_node(self):
        """Checking the 11th return is a node"""
        _, _, _, _, _, _, _, _, _, _, hna_hp = main(work_path=self.work_path,
                                                    elec2therm_ratio=
                                                    self.elec_to_therm_ratio,
                                                    pc_max=self.pc_max_sto,
                                                    pd_max=self.pd_max_sto,
                                                    pc_min=self.pc_min_sto,
                                                    pd_min=self.pd_min_sto,
                                                    capa=self.capa_sto,
                                                    cop_hp=self.cop,
                                                    pmax_elec_hp=self.p_max_hp,
                                                    storage_soc_0=self.soc_0)
        self.assertIsInstance(hna_hp, EnergyNode)
