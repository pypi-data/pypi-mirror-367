#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Unit tests for the module elements.py, defining the quantity, constraint and
objective classes

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
from omegalpes.general.optimisation.elements import *
from pulp import LpContinuous
from omegalpes.general.time import TimeUnit
from omegalpes.energy.units.energy_units import EnergyUnit
from pandas.testing import assert_frame_equal


class TestQuantityFloatValue(unittest.TestCase):
    """Tests on the Quantity class when its value is a float"""

    def setUp(self):
        self.quant = Quantity(name="quant0", opt=True, unit="s.u", vlen=None,
                              value=54.6, description="",
                              vtype=LpContinuous, lb=None, ub=None,
                              parent=None)

    def test_elements_opt(self):
        """Checking the opt value"""
        self.assertEqual(self.quant.opt, False)

    def test_elements_vlen(self):
        """Checking the vlen value"""
        self.assertEqual(self.quant.vlen, 1)

    def test_elements_value(self):
        """Checking the quantity value"""
        self.assertEqual(self.quant.value, 54.6)

    def test_elements_vlen_error(self):
        """Checking error is raised when vlen is wrong"""
        with self.assertRaises(ValueError):
            quant_bis = Quantity(name="quant1", opt=True, unit="s.u", vlen=5,
                                 value=54.6, description="",
                                 vtype=LpContinuous, lb=None, ub=None,
                                 parent=None)


class TestQuantityListValues(unittest.TestCase):
    def setUp(self):
        self.quant = Quantity(name="quant0", opt=True, unit="s.u", vlen=None,
                              value=[1, 4, 8, 10], description="",
                              vtype=LpContinuous, lb=None, ub=None,
                              parent=None)

    def test_elements_opt(self):
        """Checking the opt value"""
        self.assertEqual(self.quant.opt, [False, False, False, False])

    def test_elements_vlen(self):
        """Checking the vlen value"""
        self.assertEqual(self.quant.vlen, 4)

    def test_elements_value(self):
        """Checking the quantity value"""
        self.assertEqual(self.quant.value, [1, 4, 8, 10])


class TestQuantityDictValue(unittest.TestCase):
    """Testing Quantity when the value is a dict"""

    def setUp(self):
        self.quant_val = Quantity(name="quant0", opt=True, unit="s.u",
                                  vlen=None, value={"p1": None, "p2": 8,
                                                    "p3": 4},
                                  description="", vtype=LpContinuous,
                                  lb=None, ub=None, parent=None)
        self.quant_none = Quantity(name="quant0", opt=True, unit="s.u",
                                   vlen=None, value={"p1": None, "p2": None,
                                                     "p3": None},
                                   description="", vtype=LpContinuous,
                                   lb=None, ub=None, parent=None)

    def test_elements_value(self):
        """Checking the dict values"""
        self.assertDictEqual(self.quant_val.value, {'p1': None, 'p2': 8,
                                                    'p3': 4})
        self.assertDictEqual(self.quant_none.value, {'p1': None, 'p2': None,
                                                     'p3': None})

    def test_elements_opt(self):
        """Checking the opt is set to False if at least one dict value is
        specified"""
        self.assertDictEqual(self.quant_val.opt, {'p1': False, 'p2': False,
                                                  'p3': False})

    def test_elements_opt_none(self):
        """Checking the opt remains the same if at no dict value is
        specified"""
        self.assertDictEqual(self.quant_none.opt, {'p1': True, 'p2': True,
                                                   'p3': True})

    def test_elements_wrong_vlen(self):
        """Checking if the error is raised when the vlen is wrong"""
        with self.assertRaises(ValueError):
            quant_bis = Quantity(name="quant0", opt=False, unit="s.u", vlen=8,
                                 value={"p1": 10, "p2": 12, "p3": 15},
                                 description="", vtype=LpContinuous, lb=None,
                                 ub=None, parent=None)


class TestQuantityNoneValue(unittest.TestCase):
    """Tests when the quantity has no value"""

    def setUp(self):
        self.quant = Quantity(name="quant0", opt=True, unit="s.u", vlen=3,
                              value=None, description="",
                              vtype=LpContinuous, lb=None, ub=None,
                              parent=None)
        self.quant_bis = Quantity(name="quant0", opt=True, unit="s.u", vlen=1,
                                  value=None, description="",
                                  vtype=LpContinuous, lb=None, ub=None,
                                  parent=None)

    def test_elements_none_value_false_opt(self):
        """Checking an exception is raised when value = None AND opt=False"""
        with self.assertRaises(Exception):
            quant_false = Quantity(name="quant0", opt=False, unit="s.u",
                                   vlen=3,
                                   value=None, description="",
                                   vtype=LpContinuous, lb=None, ub=None,
                                   parent=None)

    def test_elements_none_value_vlen_above_two(self):
        """Checking a dict of value is created when opt=True and vlen is
        set>2"""
        self.assertDictEqual(self.quant.value, {0: 0, 1: 0, 2: 0})

    def test_elements_none_opt_vlen_above_two(self):
        """Checking a dict of opt is created when opt=True and vlen is
        set>2"""
        self.assertDictEqual(self.quant.opt, {0: True, 1: True, 2: True})

    def test_element_none_value_below_two(self):
        """Checking the value is set to 0 when opt=True and vlen=1"""
        self.assertEqual(self.quant_bis.value, 0)


class TestQuantityWrongValue(unittest.TestCase):
    """Checking an error is raised if value has a wrong value"""

    def test_elements_wrong_value(self):
        with self.assertRaises(TypeError):
            quant_bis = Quantity(name="quant0", opt=False, unit="s.u",
                                 vlen=None, value="puissance",
                                 description="", vtype=LpContinuous, lb=None,
                                 ub=None, parent=None)


class TestQuantityOtherOptObjects(unittest.TestCase):
    """Checking an exception is raised if opt is a list or a dict"""

    def test_elements_other_opt_objects(self):
        with self.assertRaises(Exception):
            quant = Quantity(name="quant0", opt=[True, False], unit="s.u",
                             vlen=None, value="puissance",
                             description="", vtype=LpContinuous, lb=None,
                             ub=None, parent=None)


class TestQuantityWrongOptObjects(unittest.TestCase):
    """Checking an error is raised if opt has a wrong type"""

    def test_elements_other_opt_objects(self):
        with self.assertRaises(TypeError):
            quant = Quantity(name="quant0", opt="False", unit="s.u",
                             vlen=None, value="puissance",
                             description="", vtype=LpContinuous, lb=None,
                             ub=None, parent=None)


class TestQuantitySpecialMethodStr(unittest.TestCase):
    """Checking the Str special method works properly with floats,
      lists and dicts"""

    def setUp(self):
        self.quant_float = Quantity(name="quant0", opt=False, unit="s.u",
                                    vlen=None, value=4800.5,
                                    description="", vtype=LpContinuous, lb=None,
                                    ub=None, parent=None)
        self.quant_list = Quantity(name="quant1", opt=False, unit="s.u",
                                   vlen=None, value=[8, 12, 200],
                                   description="", vtype=LpContinuous, lb=None,
                                   ub=None, parent=None)
        self.quant_dict = Quantity(name="quant2", opt=False, unit="s.u",
                                   vlen=None, value={"p1": 54, "p2": 420},
                                   description="", vtype=LpContinuous, lb=None,
                                   ub=None, parent=None)

    def test_elements_str_float(self):
        self.assertEqual(str(self.quant_float), str(4800.5))

    def test_elements_str_list(self):
        self.assertEqual(str(self.quant_list), str([8, 12, 200]))

    def test_elements_str_dict(self):
        self.assertEqual(str(self.quant_dict), str({"p1": 54, "p2": 420}))


class TestQuantitySpecialMethodRepr(unittest.TestCase):
    """Checking the Repr special method works properly with floats,
      lists and dicts"""

    def setUp(self):
        self.quant_bool = Quantity(name="quant0", opt=False, unit="s.u",
                                   vlen=None, value=4800.5,
                                   description="", vtype=LpContinuous, lb=None,
                                   ub=None, parent=None)
        self.quant_list = Quantity(name="quant1", opt=False,
                                   unit="s.u", vlen=None, value=[8, 21],
                                   description="", vtype=LpContinuous, lb=None,
                                   ub=None, parent=None)
        self.quant_dict = Quantity(name="quant2", opt=False,
                                   unit="s.u", vlen=None,
                                   value={"p1": 54, "p2": 420},
                                   description="", vtype=LpContinuous, lb=None,
                                   ub=None, parent=None)

    def test_elements_repr_bool(self):
        self.assertEqual(repr(self.quant_bool),
                         '<OMEGALPES.general.optimisation.elements.Quantity '
                         ': (name:\'{0}\', ' 'opt:{1}, vlen:{1})> \n'.format(
                             "quant0", False, 1))

    def test_elements_repr_list(self):
        self.assertEqual(repr(self.quant_list),
                         '<OMEGALPES.general.optimisation.elements'
                         '.Quantity : (name:\'{0}\', opt[0]:{1}, '
                         'vlen:{2})> \n'.format("quant1", False, 2))

    def test_elements_repr_dict(self):
        self.assertEqual(repr(self.quant_dict),
                         '<OMEGALPES.general.optimisation.elements'
                         '.Quantity : (name:\'{0}\', opt:{1}, '
                         'vlen:{2})> \n'.format("quant2", [
                             False, False], 2))


class TestQuantitySpecialMethodFloat(unittest.TestCase):
    """Checking the Str special method works properly with floats,
    and raises an error for lists and dicts"""

    def setUp(self):
        self.quant_float = Quantity(name="quant0", opt=False, unit="s.u",
                                    vlen=None, value=4800.5,
                                    description="", vtype=LpContinuous,
                                    lb=None, ub=None, parent=None)
        self.quant_list = Quantity(name="quant1", opt=False, unit="s.u",
                                   vlen=None, value=[8, 12, 200],
                                   description="", vtype=LpContinuous, lb=None,
                                   ub=None, parent=None)
        self.quant_dict = Quantity(name="quant2", opt=False, unit="s.u",
                                   vlen=None, value={"p1": 54, "p2": 420},
                                   description="",
                                   vtype=LpContinuous, lb=None, ub=None,
                                   parent=None)

    def test_elements_str_float(self):
        self.assertEqual(float(self.quant_float), float(4800.5))

    def test_elements_str_list(self):
        with self.assertRaises(TypeError):
            float(self.quant_list)

    def test_elements_str_dict(self):
        with self.assertRaises(TypeError):
            float(self.quant_dict)


class TestGetValue(unittest.TestCase):
    """Checking the get_value() method"""

    def setUp(self):
        self.quant_int = Quantity(name="quant0", opt=False, unit="s.u",
                                  vlen=None, value=48,
                                  description="", vtype=LpContinuous,
                                  lb=None, ub=None, parent=None)
        self.quant_float = Quantity(name="quant1", opt=False, unit="s.u",
                                    vlen=None, value=4800.5,
                                    description="", vtype=LpContinuous,
                                    lb=None, ub=None, parent=None)
        self.quant_list = Quantity(name="quant2", opt=False, unit="s.u",
                                   vlen=None, value=[8, 12, 200],
                                   description="", vtype=LpContinuous, lb=None,
                                   ub=None, parent=None)
        self.quant_dict = Quantity(name="quant3", opt=False, unit="s.u",
                                   vlen=None, value={"p1": 54, "p2": 420},
                                   description="",
                                   vtype=LpContinuous, lb=None, ub=None,
                                   parent=None)

    def test_int_get_int(self):
        """Checking if get_value() on an int gives an int"""
        self.assertIsInstance(self.quant_int.get_value(), int)

    def test_int_get_correct_int(self):
        """Checking if get_value() on an int gives correct value"""
        self.assertEqual(self.quant_int.get_value(), 48)

    def test_float_get_float(self):
        """Checking if get_value() on a float gives a float"""
        self.assertIsInstance(self.quant_float.get_value(), float)

    def test_float_get_correct_float(self):
        """Checking if get_value() on an float gives correct value"""
        self.assertEqual(self.quant_float.get_value(), 4800.5)

    def test_list_get_list(self):
        """Checking if get_value() on a list gives a list"""
        self.assertIsInstance(self.quant_list.get_value(), list)

    def test_list_get_correct_list(self):
        """Checking if get_value() on an list gives correct value"""
        self.assertEqual(self.quant_list.get_value(), [8, 12, 200])

    def test_dict_get_list(self):
        """Checking if get_value() on a dict gives a list"""
        self.assertIsInstance(self.quant_dict.get_value(), list)

    def test_dict_get_correct_list(self):
        """Checking if get_value() on an dict gives correct value"""
        self.assertEqual(self.quant_dict.get_value(), [54, 420])


class TestGetValueWithDate(unittest.TestCase):
    """Checking the get_value_with_date() method"""

    def setUp(self):
        eu = EnergyUnit(time=TimeUnit(periods=2, dt=1), name='EU')
        self.quant_list = Quantity(name="quant0", opt=False, unit="s.u",
                                   vlen=None, value=[8, 12],
                                   description="", vtype=LpContinuous, lb=None,
                                   ub=None, parent=eu)
        self.quant_dict = Quantity(name="quant1", opt=False, unit="s.u",
                                   vlen=None, value={"p1": 54, "p2": 420},
                                   description="",
                                   vtype=LpContinuous, lb=None, ub=None,
                                   parent=eu)
        self.df_list = pd.DataFrame(data=[8, 12],
                                    index=TimeUnit(periods=2, dt=1).DATES,
                                    columns=['Value in s.u'])
        self.df_dict = pd.DataFrame(data=[54, 420],
                                    index=TimeUnit(periods=2, dt=1).DATES,
                                    columns=['Value in s.u'])

    def test_list_get_dataframe(self):
        """Checking if get_value_with_date() on a list gives a dataframe"""
        self.assertIsInstance(self.quant_list.get_value_with_date(),
                              pd.DataFrame)

    def test_list_get_correct_dataframe(self):
        """Checking if get_value_with_date() on a list gives a
        correct dataframe"""
        assert_frame_equal(self.quant_list.get_value_with_date(),
                           self.df_list)

    def test_dict_get_dataframe(self):
        """Checking if get_value_with_date() on a dict gives a dataframe"""
        self.assertIsInstance(self.quant_dict.get_value_with_date(),
                              pd.DataFrame)

    def test_dict_get_correct_dataframe(self):
        """Checking if get_value_with_date() on a dict gives a
        correct dataframe"""
        assert_frame_equal(self.quant_dict.get_value_with_date(),
                           self.df_dict)


class TestConstraint(unittest.TestCase):
    """Checking the attributes of Constraint are properly set"""

    def test_elements_constr(self):
        constr = Constraint(exp='p[t]>pmin', name='CST0', description='Test '
                                                                      'constraint',
                            active=True, parent=None)
        self.assertEqual(constr.name, 'CST0')
        self.assertEqual(constr.description, 'Test constraint')
        self.assertEqual(constr.exp, 'p[t]>pmin')
        self.assertEqual(constr.active, True)
        self.assertIsNone(constr.parent)


class TestDynamicConstraint(unittest.TestCase):
    """Checking the attributes of Dynamic Constraint are properly set"""

    def setUp(self):
        self.time = TimeUnit(periods=24, dt=1)
        self.dcons = DynamicConstraint('p[t]<pmax', t_range='for t in time.I['
                                                            ':-1]',
                                       name='DCST0',
                                       description='dynamic constraint',
                                       active=True, parent=None)

    # def test_time_dconstr(self):

    def test_dconstr(self):
        self.assertEqual(self.dcons.exp_t, 'p[t]<pmax')
        self.assertEqual(self.dcons.t_range, 'for t in time.I[:-1]')


class TestTechnicalConstraint(unittest.TestCase):
    """Checking the attributes of TechnicalConstraint are properly set"""

    def test_deactivate_tech_cons(self):
        techcons = TechnicalConstraint(exp="T<Tmax", name='TechCST0',
                                       description='Temp constraint',
                                       active=True,
                                       parent=None)
        techcons.deactivate_constraint()
        self.assertEqual(techcons.active, False)


class TestActorConstraint(unittest.TestCase):
    """Checking the attributes of ActorConstraint are properly set"""

    def test_deactivate_actor_cons(self):
        actorcons = ActorConstraint(exp="T<Tmax", name='ActorCST0',
                                    description='Temp constraint', active=True,
                                    parent=None)
        actorcons.deactivate_constraint()
        self.assertEqual(actorcons.active, False)


class TestHourlyDynamicConstraint(unittest.TestCase):
    """Testing Hourly Dynamic Constraint"""

    def setUp(self):
        self.time = TimeUnit(periods=48, dt=1)
        self.hdcons = HourlyDynamicConstraint(exp_t='p[t]<pmax',
                                              time=self.time, init_h=2,
                                              final_h=6, name='HDCST0',
                                              description='hd constraint',
                                              active=True, parent=None)
        self.hdconsfinal = HourlyDynamicConstraint(exp_t='p[t]<pmax',
                                                   time=self.time, init_h=2,
                                                   final_h=24, name='HDCST0',
                                                   description='hd constraint',
                                                   active=True, parent=None)

    def test_hd_cons_wrong_init_final_time(self):
        """Checking if the ValueError final_h<init_h is raised"""
        with self.assertRaises(ValueError):
            hdconswrong1 = HourlyDynamicConstraint(exp_t='p[t]<pmax',
                                                   time=self.time,
                                                   init_h=22,
                                                   final_h=6,
                                                   name='HDCSTW1',
                                                   description='hd constraint',
                                                   active=True, parent=None)

    def test_hd_cons_wrong_final_time(self):
        """Checking if the ValueError finak_h>24 is raised"""
        with self.assertRaises(ValueError):
            hdconswrong2 = HourlyDynamicConstraint(exp_t='p[t]<pmax',
                                                   time=self.time, init_h=2,
                                                   final_h=26,
                                                   name='HDCSTW2',
                                                   description='hd constraint',
                                                   active=True, parent=None)

    def test_hd_cons_final_24(self):
        """Checking t_range if final_h=24"""
        self.assertEqual(self.hdconsfinal.t_range, 'for t in {0}'.format(
            [*range(2, 25)]))

    def test_hd_cons_t_range(self):
        """Checking t_range values"""
        l1 = list(range(2, 7))
        l1.extend(list(range(26, 31)))
        self.assertEqual(self.hdcons.t_range, 'for t in {0}'.format(l1))


class TestDailyDynamicConstraint(unittest.TestCase):
    """Testing Daily Dynamic Constraint"""

    def setUp(self):
        self.time = TimeUnit(periods=96, dt=1/2)
        self.time_long = TimeUnit(periods=96 + 2*4, dt=1/2)
        self.ddcons = DailyDynamicConstraint(exp_t='p[t]<pmax',
                                             time=self.time, init_time='02:00',
                                             final_time='06:00', name='DDCST0',
                                             description='dd constraint',
                                             active=True, parent=None)
        self.ddcons_long = DailyDynamicConstraint(exp_t='p[t]<pmax',
                                                  time=self.time_long,
                                                  init_time='02:00',
                                                  final_time='06:00',
                                                  name='DDCST1',
                                                  description='dd constraint',
                                                  active=True, parent=None)
        self.ddcons_midnight = DailyDynamicConstraint(exp_t='p[t]<pmax',
                                                      time=self.time_long,
                                                      init_time='20:00',
                                                      final_time='00:00',
                                                      name='DDCST2',
                                                      description='dd '
                                                                  'constraint',
                                                      active=True, parent=None)


    def test_dd_cons_init_higher_than_final_time(self):
        """Checking if the ValueError is raised if init_time higher than
        final_time"""
        with self.assertRaises(ValueError):
            ddconswrong1 = DailyDynamicConstraint(exp_t='p[t]<pmax',
                                                  time=self.time,
                                                  init_time='22:00',
                                                  final_time='06:00',
                                                  name='DDCSTW1',
                                                  description='dd constraint',
                                                  active=True, parent=None)
        with self.assertRaises(ValueError):
            ddconswrong2 = DailyDynamicConstraint(exp_t='p[t]<pmax',
                                                  time=self.time,
                                                  init_time='22:30',
                                                  final_time='22:00',
                                                  name='DDCSTW2',
                                                  description='dd constraint',
                                                  active=True, parent=None)

    def test_dd_cons_wrong_final_time(self):
        """Checking if the ValueError finak_h>24 is raised"""
        with self.assertRaises(ValueError):
            ddconswrong3 = DailyDynamicConstraint(exp_t='p[t]<pmax',
                                                  time=self.time,
                                                  init_time='02:00',
                                                  final_time='26:30',
                                                  name='HDCSTW3',
                                                  description='dd constraint',
                                                  active=True, parent=None)

    def test_dd_cons_t_range(self):
        """Checking t_range values"""
        l1 = list(range(4, 13))
        l1.extend(list(range(52, 61)))
        self.assertEqual(self.ddcons.t_range, 'for t in {0}'.format(l1))

    def test_dd_cons_long_t_range(self):
        """Checking t_range values when the studied period ends between the
        the specified init and final time"""
        l1 = list(range(4, 13))
        l1.extend(list(range(52, 61)))
        l1.extend(list(range(96+4, 96 + 2*4)))
        self.assertEqual(self.ddcons_long.t_range, 'for t in {0}'.format(l1))

    def test_dd_cons_midnight_end(self):
        """Checking t_range values when the studied period ends at midnight"""
        l1 = list(range(40, 49))
        l1.extend(list(range(88, 97)))
        self.assertEqual(self.ddcons_midnight.t_range, 'for t in {0}'.format(
            l1))


class TestObjective(unittest.TestCase):
    """Checking the attributes of Objective are properly set"""

    def test_objective(self):
        obj = Objective(exp='e', name='OBJ0', description='Test objective',
                        active=True, weight=1, unit='s.u.', parent=None)
        self.assertEqual(obj.name, 'OBJ0')
        self.assertEqual(obj.exp, 'e')
        self.assertEqual(obj.description, 'Test objective')
        self.assertEqual(obj.active, True)
        self.assertEqual(obj.weight, 1)
        self.assertIsNone(obj.parent)
        self.assertEqual(obj.unit, 's.u.')
