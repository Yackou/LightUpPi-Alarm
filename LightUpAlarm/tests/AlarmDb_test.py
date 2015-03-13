#!/usr/bin/env python2
#
# Unit test for the AlarmDb class.
#
# Copyright (c) 2015 carlosperate https://github.com/carlosperate/
# Licensed under The MIT License (MIT), a copy can be found in the LICENSE file
#
from __future__ import unicode_literals, absolute_import
import unittest
import os.path
from LightUpAlarm.AlarmDb import AlarmDb
from LightUpAlarm.AlarmItem import AlarmItem


class AlarmDbTestCase(unittest.TestCase):
    """ Tests for AlarmDb class. """

    # Database name to be used for the unit test
    db_name = 'AlarmDb_test_db'

    # just random repeat days to use for tests
    random_days = (False, False, True, False, False, True, False)

    def only_five_entries(self, alarm_db):
        """
        Removes all rows and adds 5 entries into the input alarm database.
        :param alarm_db: AlarmDb instance to add entries
        No return as the mutable argument changes remain after exit
        """
        alarm_db.delete_all_alarms()
        alarm_db.add_alarm(AlarmItem(13, 35, self.random_days, False))  # id 1
        alarm_db.add_alarm(AlarmItem(14, 36, self.random_days, False))  # id 2
        alarm_db.add_alarm(AlarmItem(15, 37, self.random_days, False))  # id 3
        alarm_db.add_alarm(AlarmItem(16, 38, self.random_days, False))  # id 4
        alarm_db.add_alarm(AlarmItem(17, 39, self.random_days, False))  # id 5

    def test_create_instance(self):
        """
        Simply creates an instance with an input file and checks the database
        file has been created.
        """
        db_file = '%s.db' % self.db_name
        # Ensure the file is not there
        if os.path.isfile(db_file):
            os.remove(db_file)
        self.assertFalse(os.path.isfile(db_file))
        adh = AlarmDb(self.db_name)
        adh._AlarmDb__connect()
        self.assertTrue(os.path.isfile(db_file))

    def test_entry(self):
        """ Adds an entry to the database and deletes it. """
        hour = 13
        minute = 35
        days = (False, False, True, False, False, True, False)
        active = False

        adh = AlarmDb(self.db_name)
        test_alarm = AlarmItem(hour, minute, days, active)
        test_alarm.id_ = adh.add_alarm(test_alarm)
        retrieved_alarm = adh.get_alarm(test_alarm.id_)
        self.assertEqual(hour, retrieved_alarm.hour)
        self.assertEqual(minute, retrieved_alarm.minute)
        self.assertEqual(days[0], retrieved_alarm.monday)
        self.assertEqual(days[1], retrieved_alarm.tuesday)
        self.assertEqual(days[2], retrieved_alarm.wednesday)
        self.assertEqual(days[3], retrieved_alarm.thursday)
        self.assertEqual(days[4], retrieved_alarm.friday)
        self.assertEqual(days[5], retrieved_alarm.saturday)
        self.assertEqual(days[6], retrieved_alarm.sunday)
        self.assertEqual(active, retrieved_alarm.active)
        #print(retrieved_alarm)

    def test_entry_error(self):
        """ Tries to add an entry with an incorrect number of arguments. """
        adh = AlarmDb(self.db_name)
        self.assertRaises(TypeError, adh.add_alarm, AlarmItem(0, 0), 0)
        self.assertRaises(TypeError, adh.add_alarm)

    def test_get_wrong_entry(self):
        """ Loads 5 alarms and then tries to access an invalid alarm. """
        adh = AlarmDb(self.db_name)
        self.only_five_entries(adh)
        # ID 7 does not exists
        alarm = adh.get_alarm(7)
        self.assertIsNone(alarm)

    def test_get_all_alarms(self):
        """
        Adds 5 alarms to the db, then checks all are retrieved.
        Also test the get_number_of_alarms method.
        """
        adh = AlarmDb(self.db_name)
        self.only_five_entries(adh)
        number_of_alarms = adh.get_number_of_alarms()
        all_alarms = adh.get_all_alarms()
        self.assertEqual(number_of_alarms, 5)
        self.assertEqual(number_of_alarms, len(all_alarms))
        hour = 13
        minute = 35
        for alarm in all_alarms:
            self.assertEqual(hour, alarm.hour)
            self.assertEqual(minute, alarm.minute)
            hour += 1
            minute += 1

    def test_get_alarm_and_delete(self):
        """
        Adds 5 alarms into the database, then it removes one, and then all the
        rest.
        """
        adh = AlarmDb(self.db_name)
        self.only_five_entries(adh)
        retrieved_alarm = adh.get_alarm(3)  # AlarmItem(15, 37) id=3
        self.assertEqual(retrieved_alarm.hour, 15)
        self.assertEqual(retrieved_alarm.minute, 37)
        delete_success = adh.delete_alarm(3)
        self.assertTrue(delete_success)
        retrieved_alarm = adh.get_alarm(3)  # AlarmItem(15, 37) id=3
        self.assertIsNone(retrieved_alarm)
        delete_success = adh.delete_all_alarms()
        self.assertTrue(delete_success)

    def test_empty_table_zero_alarms(self):
        """ Check that an empty table returns a 0 length list of items """
        adh = AlarmDb(self.db_name)
        adh.delete_all_alarms()
        number_of_alarms = adh.get_number_of_alarms()
        all_alarms = adh.get_all_alarms()
        self.assertEqual(number_of_alarms, 0)
        self.assertEqual(len(all_alarms), 0)

    def test_get_actives(self):
        """
        Adds 5 alarms into the database, 3 active and 2 inactive. Checks the
        active and inactive getters are working.
        """
        adh = AlarmDb(self.db_name)
        adh.delete_all_alarms()
        adh.add_alarm(AlarmItem(13, 35, self.random_days, True))   # id 1
        adh.add_alarm(AlarmItem(14, 36, self.random_days, False))  # id 2
        adh.add_alarm(AlarmItem(15, 37, self.random_days, True))   # id 3
        adh.add_alarm(AlarmItem(16, 38, self.random_days, False))  # id 4
        adh.add_alarm(AlarmItem(17, 39, self.random_days, True))   # id 5
        active_alarms = adh.get_all_active_alarms()
        inactive_alarms = adh.get_all_inactive_alarms()
        self.assertEqual(len(active_alarms), 3)
        self.assertEqual(len(inactive_alarms), 2)

    def test_edit_alarm(self):
        """ Creates an alarm and edits it. """
        adh = AlarmDb(self.db_name)
        adh.delete_all_alarms()
        alarm_test = AlarmItem(
            13, 35, (False, False, False, False, False, False, False), True)
        alarm_test.id_ = adh.add_alarm(alarm_test)
        edit_success = adh.edit_alarm(
            alarm_test.id_, 11, 22, (True, True, True, True, True, True, True),
            False)
        self.assertEqual(edit_success, True)
        edited_alarm = adh.get_alarm(alarm_test.id_)
        self.assertEqual(edited_alarm.hour, 11)
        self.assertEqual(edited_alarm.minute, 22)
        self.assertTrue(edited_alarm.monday)
        self.assertTrue(edited_alarm.tuesday)
        self.assertTrue(edited_alarm.wednesday)
        self.assertTrue(edited_alarm.thursday)
        self.assertTrue(edited_alarm.friday)
        self.assertTrue(edited_alarm.saturday)
        self.assertTrue(edited_alarm.sunday)
        self.assertFalse(edited_alarm.active)

    def test_edit_alarm_single(self):
        """
        Adds an alarm, edits a single value and checks all the others remain the
        same.
        """
        adh = AlarmDb(self.db_name)
        alarm_test = AlarmItem(
            13, 35, (True, False, True, False, True, False, True), True)
        alarm_test.id_ = adh.add_alarm(alarm_test)
        edit_success = adh.edit_alarm(alarm_test.id_, minute=0)
        self.assertTrue(edit_success)
        edited_alarm = adh.get_alarm(alarm_test.id_)
        self.assertEqual(edited_alarm.hour, 13)
        self.assertEqual(edited_alarm.minute, 0)
        self.assertTrue(edited_alarm.monday)
        self.assertFalse(edited_alarm.tuesday)
        self.assertTrue(edited_alarm.wednesday)
        self.assertFalse(edited_alarm.thursday)
        self.assertTrue(edited_alarm.friday)
        self.assertFalse(edited_alarm.saturday)
        self.assertTrue(edited_alarm.sunday)
        self.assertTrue(edited_alarm.active)
        # Test with opposite initial values
        alarm_test = AlarmItem(
            10, 20, (False, True, False, True, False, True, False), False)
        alarm_test.id_ = adh.add_alarm(alarm_test)
        edit_success = adh.edit_alarm(alarm_test.id_, hour=0)
        self.assertTrue(edit_success)
        edited_alarm = adh.get_alarm(alarm_test.id_)
        self.assertEqual(edited_alarm.hour, 0)
        self.assertEqual(edited_alarm.minute, 20)
        self.assertFalse(edited_alarm.monday)
        self.assertTrue(edited_alarm.tuesday)
        self.assertFalse(edited_alarm.wednesday)
        self.assertTrue(edited_alarm.thursday)
        self.assertFalse(edited_alarm.friday)
        self.assertTrue(edited_alarm.saturday)
        self.assertFalse(edited_alarm.sunday)
        self.assertFalse(edited_alarm.active)


if __name__ == '__main__':
    unittest.main()