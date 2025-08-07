#! usr/bin/env python3
#  -*- coding: utf-8 -*-

""" Unit tests for exergy analysis module

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
from omegalpes.general.time import TimeUnit
from omegalpes.energy.exergy import *


class TestExergyAnalysis(unittest.TestCase):
    """ Test exergy analysis class """

    def test_electrical_exergy_but_no_energy_unit(self):
        """Asserting TypeError whenever electrical exergy analysis is attempted
        on an object that is not an EnergyUnit"""
        with self.assertRaises(TypeError):
            definitely_not_an_energy_unit = TimeUnit(periods=24, dt=1)
            ElectricalExergy(energy_unit=definitely_not_an_energy_unit)

    def test_electrical_exergy_list_but_no_energy_unit(self):
        """Asserting TypeError whenever electrical exergy analysis is attempted
        on a list of units that contains at least one object that is not an
        EnergyUnit"""
        with self.assertRaises(TypeError):
            time = TimeUnit(periods=24, dt=1)
            energy_unit = ProductionUnit(name='this one ok',
                                         energy_type='Electrical', time=time)
            definitely_not_an_energy_unit = TimeUnit(periods=12, dt=1)
            suspicious_list = [energy_unit, definitely_not_an_energy_unit]
            ElectricalExergy(energy_unit=suspicious_list)

    def test_electrical_exergy_but_already_assessed(self):
        """Asserting AttributeError whenever exergy analysis is attempted on a
        unit on which exergy analysis has already been applied"""
        with self.assertRaises(AttributeError):
            stop_applying_exergy_on_me = ProductionUnit(name='preexisting',
                                                        energy_type='Electrical',
                                                        time=TimeUnit(
                                                            periods=24, dt=1))
            ElectricalExergy(energy_unit=stop_applying_exergy_on_me)
            ElectricalExergy(energy_unit=stop_applying_exergy_on_me)

    def test_electrical_exergy_list_but_already_assessed(self):
        """Asserting AttributeError whenever exergy analysis is attempted on a
        list containing at least one unit where exergy is already assessed"""
        with self.assertRaises(AttributeError):
            time = TimeUnit(periods=24, dt=1)
            it_was_funny_the_first_time = ProductionUnit(name='preexisting',
                                          energy_type='Electrical',
                                          time=time)
            you_only_exergy_once = StorageUnit(name='you only exergy once',
                                               energy_type='Electrical',
                                               time=time)
            ElectricalExergy(energy_unit=it_was_funny_the_first_time)
            suspicious_list = [you_only_exergy_once,
                               it_was_funny_the_first_time]
            ElectricalExergy(energy_unit=suspicious_list)

    def test_electrical_exergy_but_non_electrical_unit(self):
        """Asserting TypeError whenever electrical exergy analysis is
        attempted on a thermal unit"""
        with self.assertRaises(TypeError):
            you_not_my_type = ConsumptionUnit(name='wrong energy type',
                                              energy_type='Thermal',
                                              time=TimeUnit(periods=24, dt=1))
            ElectricalExergy(energy_unit=you_not_my_type)

    def test_electrical_exergy_list_but_non_electrical_unit(self):
        """Asserting TypeError whenever electrical exergy analysis is
           attempted on a list of units where at least one is not an
           electrical unit."""
        with self.assertRaises(TypeError):
            time = TimeUnit(periods=24, dt=1)
            you_are_my_type = ConsumptionUnit(name='right energy type',
                                              energy_type='Electrical',
                                              time=time)
            you_are_not = ProductionUnit(name='wrong energy type',
                                         energy_type='Thermal', time=time)
            suspicious_list = [you_are_my_type, you_are_not]
            ElectricalExergy(energy_unit=suspicious_list)

    def test_thermal_exergy_but_not_an_energy_unit(self):
        """Asserting TypeError whenever thermal exergy analysis is attempted on
        an object that is not an EnergyUnit"""
        with self.assertRaises(TypeError):
            definitely_not_an_energy_unit = TimeUnit(periods=24, dt=1)
            ThermalExergy(energy_unit=definitely_not_an_energy_unit,
                          temp_heat=32)

    def test_thermal_exergy_list_but_non_energy_unit(self):
        """Asserting TypeError whenever thermal exergy analysis is attempted
        on a list of units which contains at least one object that is not an
        EnergyUnit"""
        with self.assertRaises(TypeError):
            time = TimeUnit(periods=18, dt=1)
            energy_unit = ConsumptionUnit(name='this one ok',
                                          energy_type='Thermal', time=time)
            definitely_not_an_energy_unit = TimeUnit(periods=18, dt=1)
            suspicious_list = [energy_unit, definitely_not_an_energy_unit]
            ThermalExergy(energy_unit=suspicious_list, temp_heat=55)

    def test_thermal_exergy_but_already_assessed(self):
        """Asserting AttributeError whenever exergy analysis is attempted on a
        unit on which exergy analysis has already been applied"""
        with self.assertRaises(AttributeError):
            stop_the_exergy_please = ProductionUnit(name='preexisting',
                                                        energy_type='Thermal',
                                                        time=TimeUnit(
                                                            periods=24, dt=1))
            ThermalExergy(energy_unit=stop_the_exergy_please, temp_heat=99)
            ThermalExergy(energy_unit=stop_the_exergy_please, temp_heat=99)

    def test_thermal_exergy_list_but_already_assessed(self):
        """Asserting AttributeError whenever exergy analysis is attempted on a
        list of units containing at least one on which exergy analysis has
        already been applied"""
        with self.assertRaises(AttributeError):
            time = TimeUnit(periods=24, dt=1)
            not_funny_anymore = StorageUnit(name='preexisting',
                                                      energy_type='Thermal',
                                                      time=time)
            you_only_exergy_once = ConsumptionUnit(name='you only exergy once',
                                                   energy_type='Thermal',
                                                   time=time)
            ThermalExergy(energy_unit=not_funny_anymore, temp_heat=9)
            suspicious_list = [you_only_exergy_once,
                               not_funny_anymore]
            ThermalExergy(energy_unit=suspicious_list, temp_heat=9)

    def test_thermal_exergy_but_non_thermal_unit(self):
        """Asserting TypeError whenever thermal exergy analysis is attempted
        on a unit whose energy type is not Thermal"""
        with self.assertRaises(TypeError):
            you_are_not_my_type = StorageUnit(name='you_are_not_my_type',
                                              energy_type='Gas',
                                              time=TimeUnit(periods=24, dt=1))
            ThermalExergy(energy_unit=you_are_not_my_type, temp_heat=99)

    def test_thermal_exergy_list_but_non_thermal_unit(self):
        """Asserting TypeError whenever thermal exergy analysis is attempted
        on a unit whose energy type is not Thermal"""
        with self.assertRaises(TypeError):
            time = TimeUnit(periods=24, dt=1)
            you_are_my_type = StorageUnit(name='you_are_my_type',
                                          energy_type='Thermal', time=time)
            you_are_not_my_type = StorageUnit(name='you_are_not_my_type',
                                              energy_type='Gas', time=time)
            suspicious_unit_list = [you_are_my_type, you_are_not_my_type]
            ThermalExergy(energy_unit=suspicious_unit_list, temp_heat=[15, 25])

    def test_thermal_exergy_but_no_temp(self):
        """Asserting ValueError whenever thermal exergy analysis is attempted
        without providing a temperature"""
        with self.assertRaises(ValueError):
            what_temp_is_it = ConsumptionUnit(name='what_temp_is_it',
                                              energy_type='Thermal',
                                              time=TimeUnit(periods=24, dt=1))
            ThermalExergy(energy_unit=what_temp_is_it, temp_heat=None)

    def test_thermal_exergy_but_no_temp_within_a_list(self):
        """Asserting TypeError whenever ThermalExergy is attempted with a list
        that contains at least one temperature in a wrong format"""
        with self.assertRaises(TypeError):
            what_temp_is_it = ConsumptionUnit(name='what_temp_is_it',
                                              energy_type='Thermal',
                                              time=TimeUnit(periods=3, dt=1))
            suspicious_temp_list = [10, None, 30]
            ThermalExergy(energy_unit=what_temp_is_it,
                          temp_heat=suspicious_temp_list)

    def test_thermal_exergy_but_temp_wrong_format(self):
        """ Asserting TypeError when energy type is Thermal but the temperature is
        not an int, nor a float, nor a list"""
        with self.assertRaises(TypeError):
            hot_or_not = ConsumptionUnit(name='hot_or_not',
                                         energy_type='Thermal',
                                         time=TimeUnit(periods=24, dt=1))
            ThermalExergy(energy_unit=hot_or_not, temp_heat='Wrong')

    def test_thermal_exergy_but_temp_list_wrong_format(self):
        """Asserting TypeError whenever Thermal exergy assessment is
        attempted with at least one temperature in the wrong format"""
        with self.assertRaises(TypeError):
            suspicious_temp = [10, 'twenty', 30]
            bring_the_heat = ConsumptionUnit(name='bring the heat',
                                             energy_type='Thermal',
                                             time=TimeUnit(periods=3, dt=1))
            ThermalExergy(energy_unit=bring_the_heat,
                          temp_heat=suspicious_temp)

    def test_thermal_exergy_but_temp_list_different_length(self):
        """Asserting IndexError whenever thermal exergy analysis is attempted
        on a unit that has a temperature vector with different length than the
        time vector"""
        with self.assertRaises(IndexError):
            never_ending_summer = ProductionUnit(name='never_ending_summer',
                                                 energy_type='Thermal',
                                                 time=TimeUnit(periods=2,
                                                               dt=1))
            ThermalExergy(energy_unit=never_ending_summer, temp_heat=[1, 2, 3])

    def test_thermal_exergy_multiple_but_temp_list_different_length(self):
        """Asserting IndexError whenever thermal exergy analysis is attempted
        on a unit that has a temperature vector with different length than the
        time vector"""
        with self.assertRaises(IndexError):
            time = TimeUnit(periods=24, dt=1)
            winter_is_coming = ProductionUnit(name='and_it_is_cold',
                                              energy_type='Thermal',
                                              time=time)
            but_after_winter = ConsumptionUnit(name='spring comes',
                                               energy_type='Thermal',
                                               time=time)
            ThermalExergy(energy_unit=[winter_is_coming, but_after_winter],
                          temp_heat=[1, 2, 3])

    def test_exergy_destruction_but_already_assessed(self):
        with self.assertRaises(AttributeError):
            conan = ConsumptionUnit(name='the barbarian',
                                    energy_type='Thermal',
                                    time=TimeUnit(periods=24, dt=24))
            ThermalExergy(energy_unit=conan, temp_ref=20, temp_heat=999)
            ExergyDestruction(energy_unit=conan, exergy_eff=0.01)
            ExergyDestruction(energy_unit=conan, exergy_eff=0.01)

    def test_exergy_destruction_but_exergy_not_assessed(self):
        with self.assertRaises(AttributeError):
            time = TimeUnit(periods=24, dt=24)
            conan_2 = HeatPump(name='the destroyer', time=time)
            ThermalExergy(energy_unit=conan_2.thermal_consumption_unit,
                          temp_heat=50)
            # ElectricalExergy(energy_unit=conan.elec_consumption_unit)
            """If this line is uncommented, exergy destruction is assessed
            correctly and the unittest does not pass"""
            ThermalExergy(energy_unit=conan_2.thermal_production_unit,
                          temp_heat=85)
            ExergyDestruction(energy_unit=conan_2, exergy_eff=0.99)

    def test_exergy_destruction_but_efficiency_not_defined(self):
        with self.assertRaises(ValueError):
            time = TimeUnit(periods=24, dt=2)
            how_good_are_you = ProductionUnit(name='i do not know',
                                              energy_type='Electrical',
                                              time=time)
            ElectricalExergy(energy_unit=how_good_are_you)
            ExergyDestruction(energy_unit=how_good_are_you, exergy_eff=None)
            """ If any value (greater than zero) is given to exergy_eff, 
            exergy dest is assessed correctly and the test does not pass"""

    def test_exergy_destruction_but_efficiency_not_defined_list(self):
        with self.assertRaises(ValueError):
            time = TimeUnit(periods=3, dt=2)
            how_good_are_you = ProductionUnit(name='i do not know',
                                              energy_type='Electrical',
                                              time=time)
            ElectricalExergy(energy_unit=how_good_are_you)
            ExergyDestruction(energy_unit=how_good_are_you,
                              exergy_eff=[0.5, 0.3, None])
            """ If any value (greater than zero) is given to exergy_eff, 
            exergy dest is assessed correctly and the test does not pass"""

    def test_exergy_destruction_but_efficiency_is_zero(self):
        with self.assertRaises(ValueError):
            time = TimeUnit(periods=24, dt=2)
            you_can_do_better = ProductionUnit(name='way better than that',
                                               energy_type='Electrical',
                                               time=time)
            ElectricalExergy(energy_unit=you_can_do_better)
            ExergyDestruction(energy_unit=you_can_do_better, exergy_eff=0)
            "If a value greater than zero is given to exergy_eff, exergy " \
                "destruction is assessed correctly and the test does not pass"

    def test_exergy_destruction_but_efficiency_is_zero_list(self):
        with self.assertRaises(ValueError):
            time = TimeUnit(periods=3, dt=2)
            how_good_are_you_then = ProductionUnit(name='how good am i',
                                                   energy_type='Electrical',
                                                   time=time)
            ElectricalExergy(energy_unit=how_good_are_you_then)
            ExergyDestruction(energy_unit=how_good_are_you_then,
                              exergy_eff=[0.5, 0.3, 0])
            """ If any value (greater than zero) is given to exergy_eff, 
            exergy dest is assessed correctly and the test does not pass"""

    def test_exergy_destruction_but_efficiency_list_different_length(self):
        with self.assertRaises(IndexError):
            time = TimeUnit(periods=1, dt=24)
            you_worked = ProductionUnit(name='for too long today',
                                        energy_type='Electrical',
                                        time=time)
            ElectricalExergy(energy_unit=you_worked)
            ExergyDestruction(energy_unit=you_worked, exergy_eff=[0.25, 0.5])
            "If the exergy efficiency list contains only one value, exergy" \
            "destruction is assessed correctly and the test does not pass"

    def test_exergy_destruction_but_efficiency_wrong_type(self):
        with self.assertRaises(TypeError):
            time = TimeUnit(periods=24, dt=1)
            stop_speaking_namekian = ProductionUnit(name='please',
                                                    energy_type='Electrical',
                                                    time=time)
            ElectricalExergy(energy_unit=stop_speaking_namekian)
            ExergyDestruction(energy_unit=stop_speaking_namekian,
                              exergy_eff='wtf')
            """If exergy eff is an int, a float or a list, exergy destruction 
            is assessed correctly and the test does not pass"""

    def test_exergy_destruction_but_efficiency_wrong_type_list(self):
        with self.assertRaises(ValueError):
            time = TimeUnit(periods=3, dt=2)
            i_cannot_speak_namekian = ProductionUnit(name='no namekian',
                                                     energy_type='Electrical',
                                                     time=time)
            ElectricalExergy(energy_unit=i_cannot_speak_namekian)
            ExergyDestruction(energy_unit=i_cannot_speak_namekian,
                              exergy_eff=[0.5, 0.3, 'wtf'])
            """ If any value (greater than zero) is given to exergy_eff, 
            exergy dest is assessed correctly and the test does not pass"""


if __name__ == "__main__":
    unittest.main()
