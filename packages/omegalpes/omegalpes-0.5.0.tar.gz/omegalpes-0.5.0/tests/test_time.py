#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
Unittests for the module time.py, defining the time units class of the models

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
from omegalpes.general.time import TimeUnit, convert_european_format
import pandas as pd
import numpy as np


class TestTimeUnit(unittest.TestCase):
    """Checking the attributes of TimeUnit are properly set for european and
    dateTime formats"""
    def setUp(self):
        self.time_euro = TimeUnit(start='15/10/2017', end=None, periods=120,
                                  dt=1)
        self.time = TimeUnit(start='2017-10-15', end=None, periods=120,
                             dt=1)

    def test_time_unit_dt(self):
        self.assertEqual(self.time.DT, 1)
        self.assertEqual(self.time_euro.DT, 1)

    def test_time_unit_dates(self):
        pd.testing.assert_index_equal(self.time.DATES, pd.date_range(
            start='15/10/2017', end=None, periods=120, freq='1H'))
        pd.testing.assert_index_equal(self.time_euro.DATES, pd.date_range(
            start='15/10/2017', end=None, periods=120, freq='1H'))

    def test_time_unit_len(self):
        self.assertEqual(self.time.LEN, 120)
        self.assertEqual(self.time_euro.LEN, 120)

    def test_time_unit_i(self):
        self.assertEqual(self.time.I.all(), np.arange(120).all())
        self.assertEqual(self.time_euro.I.all(), np.arange(120).all())


class TestGetDays(unittest.TestCase):
    def setUp(self):
        self.time = TimeUnit(start='26/10/2018', periods=72)

    def test_get_days(self):
        """Asserting the get_days function returns the days as expected"""
        self.assertEqual(self.time.get_days, [pd.datetime(2018, 10, 26).date(),
                                              pd.datetime(2018, 10, 27).date(),
                                              pd.datetime(2018, 10,
                                                          28).date()])


class TestGetDateForIndex(unittest.TestCase):
    def setUp(self):
        self.time = TimeUnit(start='15/10/2017', periods=24)

    def test_get_date_for_index_int(self):
        """Checking the get_date_for index function return the right date"""
        index_int = 3
        self.assertEqual(self.time.get_date_for_index(index_int),
                         pd.date_range(start='2017-10-15 03:00:00',
                                       end='2017-10-15 04:00:00'))

    def test_get_date_for_index_out_of_range(self):
        """Checking the get_date_for index function raises an Error when
        asked an index out of range"""
        index_int_oor = 25
        with self.assertRaises(ValueError):
            self.time.get_date_for_index(index_int_oor)

    def test_get_date_for_index_float(self):
        """Checking the get_date_for index function raises an Error when
        asked a float index"""
        index_float = 4.
        with self.assertRaises(TypeError):
            self.time.get_date_for_index(index_float)

    def test_get_date_for_index_list(self):
        """Checking the get_date_for index function raises an Error when
        asked a list index"""
        index_list = [1, 10]
        with self.assertRaises(TypeError):
            self.time.get_date_for_index(index_list)

    def test_get_date_for_index_dict(self):
        """Checking the get_date_for index function raises an Error when
        asked a dict index"""
        index_dict = {1, 10}
        with self.assertRaises(TypeError):
            self.time.get_date_for_index(index_dict)

    def test_get_date_for_index_string(self):
        """Checking the get_date_for index function raises an Error when
        asked a string index"""
        index_string = 'test_string'
        with self.assertRaises(TypeError):
            self.time.get_date_for_index(index_string)


class TestGetIndexForDate(unittest.TestCase):
    def setUp(self):
        self.time = TimeUnit(start='15/10/2017', end=None, periods=120*6,
                             dt=1/6)
        self.date_tstp_test = pd.Timestamp('2017-10-16 10:30:00')

    def test_get_index_for_date(self):
        """Checking the right index is returned for a certain date"""
        self.assertEqual(self.time.get_index_for_date(self.date_tstp_test),
                         207)

    def test_get_index_for_date_error(self):
        """Checking an error is raised when asked for a timestamp more
        precise than the timestep"""
        with self.assertRaises(ValueError):
            self.time.get_index_for_date(pd.Timestamp('2017-10-16 10:30:05'))


class TestGetIndexForDateRange(unittest.TestCase):
    def setUp(self):
        self.time = TimeUnit(start='15/10/2017', end=None, periods=120, dt=1)
        self.index_list = list(range(34, 44))

    def test_get_index_for_date_range_periods(self):
        """Checking the right list of indexes is returned when using
        get_index_for_date_range with start and periods"""
        self.assertListEqual(self.time.get_index_for_date_range(
            starting_date='2017-10-16 10:00:00', periods=10), self.index_list)

    def test_get_index_for_date_range_end(self):
        """Checking the right list of indexes is returned when using
        get_index_for_date_range with start and end"""
        self.assertListEqual(self.time.get_index_for_date_range(
            starting_date='2017-10-16 10:00:00', end='2017-10-16 19:00:00'),
            self.index_list)


class TestConvertEuropeanFormat(unittest.TestCase):
    def setUp(self):
        self.dateEuro = '26/10/2018'
        self.dateTime = '2018-10-26'

    def test_convert_european_format_euro(self):
        """Testing the function convert_european_format with an european
        format date"""
        self.assertEqual(convert_european_format(self.dateEuro),
                         pd.to_datetime(self.dateEuro, dayfirst=True))

    def test_convert_european_format_dt(self):
        """Testing the function convert_european_format with a dateTime
         format date"""
        self.assertEqual(convert_european_format(self.dateTime),
                         self.dateTime)