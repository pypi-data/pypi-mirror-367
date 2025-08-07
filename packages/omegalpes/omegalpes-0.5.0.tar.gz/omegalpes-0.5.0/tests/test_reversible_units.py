#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Unit tests for the module reversible_units.py, defining the reversible units
attributes, constraints and functions.

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
from omegalpes.energy.units.reversible_units import *
from omegalpes.general.time import TimeUnit
from omegalpes.energy.units.consumption_units import ConsumptionUnit, \
    FixedConsumptionUnit, VariableConsumptionUnit
from omegalpes.energy.units.production_units import ProductionUnit, \
    FixedProductionUnit, VariableProductionUnit
import datetime
import pandas as pd
import numpy as np
from omegalpes.general.optimisation.elements import Quantity, DynamicConstraint


class TestRevUnit(unittest.TestCase):
    def setUp(self):
        self.time = TimeUnit(periods=4, dt=1)
        self.var_rev = ReversibleUnit(time=self.time, name='_var_rev',
                                      pmax_prod=1e4)
        self.fixed_cons_rev = ReversibleUnit(time=self.time,
                                             name='fixed_c_rev',
                                             p_cons=[1, 2, 3, 4],
                                             pmax_prod=2e4)
        self.fixed_prod_rev = ReversibleUnit(time=self.time,
                                             name='fixed_p_rev',
                                             p_prod=[4, 3, 0, 2],
                                             pmax_cons=3e4)
        # Assert no error is raised with this "right" fixed reversible unit
        # (compared to test_def_fixed_rev where a "wrong" one is tested).
        self.fixed_rev = ReversibleUnit(time=self.time, name='fixed_rev',
                                        p_cons=[0, 0, 3, 0],
                                        p_prod=[4, 3, 0, 2])

    def test_fixed_var_rev(self):
        """Asserting fixed units are created when power values are given as
        parameters of the ReversibleUnit"""
        self.assertIsInstance(self.fixed_prod_rev.production_unit,
                              FixedProductionUnit)
        self.assertIsInstance(self.fixed_cons_rev.consumption_unit,
                              FixedConsumptionUnit)
        self.assertIsInstance(self.var_rev.production_unit,
                              VariableProductionUnit)
        self.assertIsInstance(self.var_rev.consumption_unit,
                              VariableConsumptionUnit)

    def test_def_rev_var(self):
        """Asserting the def_rev constraint (non-simultaneity constraint) is
        properly defined with variable energy units"""
        self.assertIsInstance(self.var_rev.def_rev,
                              DynamicConstraint)
        self.assertEqual(self.var_rev.def_rev.name,
                         'def_rev')
        self.assertEqual(self.var_rev.def_rev.t_range,
                         'for t in time.I')
        self.assertEqual(self.var_rev.def_rev.exp_t,
                         '{0}_p[t] - (1 - {1}_u[t]) * {2} <= 0'
                         .format(self.var_rev.production_unit.name,
                                 self.var_rev.consumption_unit.name, 1e4))

    def test_def_rev_cons(self):
        """Asserting the def_rev constraint (non-simultaneity constraint) is
        properly defined with fixed consumption unit"""
        self.assertIsInstance(self.fixed_cons_rev.def_rev_c,
                              DynamicConstraint)
        self.assertEqual(self.fixed_cons_rev.def_rev_c.name,
                         'def_rev_c')
        self.assertEqual(self.fixed_cons_rev.def_rev_c.t_range,
                         'for t in time.I')
        self.assertEqual(self.fixed_cons_rev.def_rev_c.exp_t,
                         '{0}_p[t] - (1 - {1}_u[t]) * {2} <= 0'
                         .format(self.fixed_cons_rev.consumption_unit.name,
                                 self.fixed_cons_rev.production_unit.name,
                                 1e5))

    def test_def_rev_prod(self):
        """Asserting the def_rev constraint (non-simultaneity constraint) is
        properly defined with fixed production unit"""
        self.assertIsInstance(self.fixed_prod_rev.def_rev_p,
                              DynamicConstraint)
        self.assertEqual(self.fixed_prod_rev.def_rev_p.name,
                         'def_rev_p')
        self.assertEqual(self.fixed_prod_rev.def_rev_p.t_range,
                         'for t in time.I')
        self.assertEqual(self.fixed_prod_rev.def_rev_p.exp_t,
                         '{0}_p[t] - (1 - {1}_u[t]) * {2} <= 0'
                         .format(self.fixed_prod_rev.production_unit.name,
                                 self.fixed_prod_rev.consumption_unit.name,
                                 1e5))

    def test_def_fixed_rev(self):
        """Asserting the inputs checking is properly led with fixed units"""
        with self.assertRaises(TypeError):
            wrong_fixed_rev = ReversibleUnit(time=self.time,
                                             name='w_fixed_rev',
                                             p_cons=[1, 2, 3, 4],
                                             p_prod=[4, 3, 0, 2])
        with self.assertRaises(TypeError):
            wrong_fixed_rev_dict = ReversibleUnit(time=self.time,
                                                  name='w_fixed_rev_dict',
                                                  p_cons={0: 1, 1: 2, 2: 3,
                                                          3: 4},
                                                  p_prod={0: 0, 1: 1, 2: 2,
                                                          3: 3})

        with self.assertRaises(TypeError):
            columns = ['Values']
            data1 = np.array([np.arange(4)]).T
            data2 = np.array([np.arange(4)]).T
            df1 = pd.DataFrame(data1, index=self.time.DATES, columns=columns)
            df2 = pd.DataFrame(data2, index=self.time.DATES, columns=columns)
            # with df3, no error is raised
            df3 = pd.DataFrame(index=self.time.DATES, columns=columns)
            df3 = df3.fillna(0)

            wrong_fixed_rev_df = ReversibleUnit(time=self.time,
                                                name='w_fixed_rev_dict',
                                                p_cons=df1,
                                                p_prod=df2)

