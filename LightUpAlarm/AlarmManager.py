# -*- coding: utf-8 -*-
#
# General management class for the LightUp Alarm package.
#
# Copyright (c) 2015 carlosperate http://carlosperate.github.io
#
# Licensed under The MIT License (MIT), a copy can be found in the LICENSE file
#
# Alarm management system. It saves alarms into a database using the AlarmDb
# class and launches a running thread per active alarm using the AlarmThread
# class.
# It also provides access to the Alarm settings (snooze time, and alarm
# offset alert time).
#
from __future__ import unicode_literals, absolute_import, print_function
import sys
import time
try:
    from LightUpAlarm.AlarmDb import AlarmDb
    from LightUpAlarm.AlarmItem import AlarmItem
    from LightUpAlarm.StationItem import StationItem
    from LightUpAlarm.AlarmThread import AlarmThread
    from LightUpAlarm.Py23Compatibility import *
except ImportError:
    from AlarmDb import AlarmDb
    from AlarmItem import AlarmItem
    from StationItem import StationItem
    from AlarmThread import AlarmThread
    from Py23Compatibility import *


class AlarmManager(object):
    """
    General management system for the LightUp Alarm package.
    """
    alarmdb = AlarmDb()

    #
    # Instance initialiser
    #
    def __init__(self, alert_callback=None, offset_alert_callback=None):
        """
        On initialization we connect to the database and check if there are
        any alarms to load. If not, load a couple of dummy alarms.
        It also registers any alarms present in the database.
        :param alert_callback: Optional argument to register a callback function
                               to be executed on an alarm alert.
        :param offset_alert_callback: Optional argument to register a callback
                                      function to be executed on an offset time
                                      of the alarm.
        """
        # Save the alarm callback functions as a private member variable
        self.__alert_callback = alert_callback
        self.__offset_alert_callback = offset_alert_callback

        # Create a private member list for the alarm threads
        self.__alarm_threads = []

        # Set dummy alarms if database empty
        if AlarmManager.alarmdb.get_number_of_alarms() == 0:
            self.load_dummy_alarms()

        # Register and launch any active (enabled with repeat days) alarms
        # from the database
        alarms = AlarmManager.get_all_active_alarms()
        for alarm in alarms:
            self.__set_alarm_thread(alarm)

    #
    # Methods to get an edit settings
    #
    @staticmethod
    def get_snooze_time():
        """
        Static method, gets the current set snooze time interval.
        :return: Integer with the snooze time interval in minutes.
        """
        return AlarmManager.alarmdb.get_snooze_time()

    @staticmethod
    def set_snooze_time(snooze_time):
        """
        Static method, sets the current snooze time interval.
        :param snooze_time: Integer, new snooze time in minutes.
        :return: Boolean indicating the operation success.
        """
        return AlarmManager.alarmdb.set_snooze_time(snooze_time)

    @staticmethod
    def get_offset_alert_time():
        """
        Static method, gets the offset alert time (the time difference before or
        after the alarm alert is triggered), used to set some action.
        :return: Integer, the offset alert time in minutes.
        """
        return AlarmManager.alarmdb.get_offset_alert_time()

    @staticmethod
    def set__offset_alert_time(offset_alert_time):
        """
        Static method, sets the offset alert time (the time before or after the
        alarm alert is triggered), used to set some additional action to the
        alarm alert.
        :param offset_alert_time: Integer, offset alert time in minutes.
        :return: Boolean indicating the operation success.
        """
        return AlarmManager.alarmdb.set_offset_alert_time(offset_alert_time)

    #
    # static methods to retrieve alarms
    #
    @staticmethod
    def get_all_alarms():
        """
        Static method, gets all the alarms from the database.
        :return: List of AlarmItems containing all alarms. Returns an empty list
                 if there aren't any.
        """
        return AlarmManager.alarmdb.get_all_alarms()

    @staticmethod
    def get_number_of_alarms():
        """
        Gets the number of alarms stored in the database.
        :return: Integer indicating the number of alarms in the db.
        """
        return AlarmManager.alarmdb.get_number_of_alarms()

    @staticmethod
    def get_all_enabled_alarms():
        """
        Gets all the enabled alarms from the database.
        :return: List of AlarmItems containing all enabled alarms. Returns an
                 empty list if there aren't any.
        """
        return AlarmManager.alarmdb.get_all_enabled_alarms()

    @staticmethod
    def get_all_disabled_alarms():
        """
        Gets all the disabled alarms from the database.
        :return: List of AlarmItems containing all enabled alarms. Returns an
                 empty list if there aren't any.
        """
        return AlarmManager.alarmdb.get_all_disabled_alarms()

    @staticmethod
    def get_all_active_alarms():
        """
        Gets all the active alarms (enabled with at least one repeating day)
        from the database.
        :return: List of AlarmItems containing all enabled alarms. Returns an
                 empty list if there aren't any.
        """
        active_alarms = AlarmManager.get_all_enabled_alarms()
        # Need to iterate backwards in order to remove items safely
        if active_alarms:
            for i in xrange(len(active_alarms) - 1, -1, -1):
                if active_alarms[i].any_day_enabled() is False:
                    del active_alarms[i]
            return active_alarms
        else:
            return []

    @staticmethod
    def get_alarm(alarm_id):
        """
        Get the alarm with the given ID from the database.
        :param alarm_id: Integer to indicate the primary key of the Alarm to
                         get.
        :return: AlarmItem with the alarm data, or None if id could not be
                 found.
        """
        return AlarmManager.alarmdb.get_alarm(alarm_id)

    @staticmethod
    def get_next_alarm():
        """
        Gets the current time and all the active alarms. For each of these
        alarms it calculates the elapsed time that will pass for its next alert.
        Then it sorts the list based on this value and returns closes.
        :return: AlarmItem of the next alarm to alert.
        """
        # now_time[3] = tm_hour, now_time[4] = tm_minute, now_time[6] = tm_wday
        now_time = time.localtime(time.time())

        all_alarms = AlarmManager.get_all_active_alarms()
        if len(all_alarms) > 0:
            for alarm in all_alarms:
                alarm.next_alert = alarm.minutes_to_alert(
                    now_time[3], now_time[4], now_time[6])
            sorted_alarms = sorted(
                all_alarms, key=lambda a: a.next_alert)
            return sorted_alarms[0]
        else:
            return None

    #
    # member methods to add alarms
    #
    def add_alarm(self, hour, minute,
                  days=(False, False, False, False, False, False, False),
                  enabled=True, label='', timestamp=None, station_id=1):
        """
        Adds an alarm to the database with the input values.
        If saved successfully it is sent to __set_alarm_thread to see if it
        should be launched as an enabled alarm thread.
        :param hour: Integer to indicate the alarm hour.
        :param minute: Integer to indicate the alarm minute.
        :param days: 7-item list of booleans to indicate repeat weekdays.
        :param enabled: Boolean to indicate the alarm enabled state.
        :param label: Strong to contain the alarm label.
        :param timestamp: Time, in seconds since 1970, that this alarm was last
                          modified. This value can be added in order to be
                          able to synchronise alarms between different systems.
        :return: Integer indicating the newly created alarm ID, or None if fail.
        """
        alarm = AlarmItem(
            hour, minute, days=days, enabled=enabled, label=label,
            timestamp=timestamp, station_id=station_id)
        if alarm is not None:
            alarm.id_ = AlarmManager.alarmdb.add_alarm(alarm)
            if alarm.id_ is not None:
                self.__set_alarm_thread(alarm)
                return alarm.id_
        return None

    def load_dummy_alarms(self):
        """
        It loads 2 inactive dummy alarms into the database for demonstration
        purposes.
        """
        self.add_alarm(
            7, 10, days=(True, True, True, True, True, False, False),
            enabled=False, label='one')
        self.add_alarm(
            10, 30, days=(False, False, False, False, False, True, True),
            enabled=False, label='two')

    #
    # member methods to edit alarms
    #
    def edit_alarm(self, alarm_id, hour=None, minute=None, days=None,
                   enabled=None, label=None, station_id=None):
        """
        Edits an alarm from the database with the input data.
        A new timestamp is set by the AlarmDb class if the edit is successful.
        :param alarm_id: Integer to indicate the ID of the alarm to be edited.
        :param hour: Integer to indicate the alarm hour.
        :param minute: Integer to indicate the alarm minute.
        :param days: 7-item list of booleans to indicate repeat weekdays.
        :param enabled: Boolean to indicate alarm enabled state.
        :param label: Strong to contain the alarm label.
        :return: Boolean indicating the success of the 'edit' operation.
        """
        db = AlarmManager.alarmdb
        # As the default values for AlarmDb.edit_alarm are all None as well we
        # can send all through as is.
        success = db.edit_alarm(
            alarm_id,  hour=hour, minute=minute, days=days, enabled=enabled,
            label=label, station_id=station_id)

        # If a successful edit was carried, then make sure the alarm is launched
        if success is True:
            self.__set_alarm_thread(AlarmManager.get_alarm(alarm_id))

        return success

    @staticmethod
    def update_alarm(alarm):
        """
        Updates the alarm in the database with an AlarmItem input data.
        This method also updates the timestamp stored into the instance passed
        as an argument.
        :param alarm: AlarmItem instance with data to update the database.
        :return: Boolean indicating the success of the 'update' operation.
        """
        if isinstance(alarm, AlarmItem):
            success = AlarmManager.alarmdb.update_alarm(alarm)
        else:
            success = False
        return success

    def delete_alarm(self, alarm_id):
        """
        Remove the alarm with the given ID from the database and remove its
        alarm thread.
        :param alarm_id: Integer to indicate the primary key of the Alarm to be
                         removed.
        :return: Boolean indicating the success of the 'delete alarm' operation.
        """
        # First we need to ensure it there is no alarm thread running for it
        self.__stop_alarm_thread(alarm_id)
        # Remove it from the database
        return AlarmManager.alarmdb.delete_alarm(alarm_id)

    def delete_all_alarms(self):
        """
        Removes all alarm threads and alarms from the database.
        :return: Boolean indicating the success of the 'delete all' operation.
        """
        # Ensure there are no alarm threads running anymore
        thread_success = self.__stop_all_alarm_threads()
        # Remove from database
        db_success = AlarmManager.alarmdb.delete_all_alarms()

        if thread_success is True and db_success is True:
            return True
        else:
            return False

    @staticmethod
    def get_station(station_id):
        """
        Get the station with the given ID from the database.
        :param station_id: Integer to indicate the primary key of the Station to
                         get.
        :return: StationItem with the station data, or None if id could not be
                 found.
        """
        return AlarmManager.alarmdb.get_station(station_id)

    @staticmethod
    def get_all_stations():
        """
        Static method, gets all the stations from the database.
        :return: List of StationItems containing all stations. Returns an empty list
                 if there aren't any.
        """
        return AlarmManager.alarmdb.get_all_stations()

    #
    # member methods to add stations
    #
    def add_station(self, name, url):
        """
        Adds a station to the database with the input values.
        :param name: String containing the name of the station.
        :param url: String containing the URL of the station.
        :return: Integer indicating the newly created station ID, or None if fail.
        """
        station = StationItem(name, url)
        if station is not None:
            station.id_ = AlarmManager.alarmdb.add_station(station)
            if station.id_ is not None:
                return station.id_
        return None

    def delete_station(self, station_id):
        """
        Remove the station with the given ID from the database.
        :param station_id: Integer to indicate the primary key of the Station to be
                         removed.
        :return: Boolean indicating the success of the 'delete station' operation.
        """
        # Remove it from the database
        return AlarmManager.alarmdb.delete_station(station_id)

    def delete_all_stations(self):
        """
        Removes all stations from the database.
        :return: Boolean indicating the success of the 'delete all' operation.
        """
        # Remove from database
        return AlarmManager.alarmdb.delete_all_stations()


    #
    # member methods to launch, edit and stop alarm events
    #
    def __set_alarm_thread(self, alarm):
        """
        Takes an input alarm and determines if is active, in order to be
        launched as an alarm thread, or if a thread should be changed due to
        the new alarm data.
        Maintains the thread list updated with the running alarms.
        :param alarm: AlarmItem to launch, edited, or stop thread.
        :return: Boolean indicating if Alarm Thread is running.
        """
        thread_up = False
        # First check if the alarm to be register is already in the list
        for i, alarm_thread in enumerate(self.__alarm_threads):
            if alarm.id_ == alarm_thread.get_id():
                # Already set as launched, check if should be stopped or edited
                if alarm.is_active() is False:
                    self.__stop_alarm_thread(alarm.id_)
                else:
                    alarm_thread.edit_alarm(alarm)
                    # It is meant to be up and running, check that it is
                    if alarm_thread.isAlive() is False:
                        self.__alarm_threads[i] = AlarmThread(
                            alarm,
                            alarm_callback=self.__alert_callback,
                            offset_alarm_time=self.get_offset_alert_time(),
                            offset_callback=self.__offset_alert_callback)
                        self.__alarm_threads[i].start()
                    thread_up = alarm_thread.isAlive()
                break
        # Else only executes if no alarm with same ID was found
        else:
            # Before thread is launched, check if the alarm is active
            if alarm.is_active() is True:
                alarm_thread = AlarmThread(
                    alarm,
                    alarm_callback=self.__alert_callback,
                    offset_alarm_time=self.get_offset_alert_time(),
                    offset_callback=self.__offset_alert_callback)
                self.__alarm_threads.append(alarm_thread)
                alarm_thread.start()
                thread_up = alarm_thread.isAlive()

        return thread_up

    def __stop_alarm_thread(self, alarm_id):
        """
        Stops an AlarmThread and removes item from the threads list.
        This method can take up to 2 seconds to run.
        :param alarm_id: ID of the AlarmItem for the alarm thread to stop.
        :return: Boolean indicating if the operation was successful.
        """
        success = False
        for alarm_thread in self.__alarm_threads:
            if alarm_id == alarm_thread.get_id():
                alarm_thread.stop()
                # Check that it has really stopped for a maximum period of 3s
                milliseconds_passed = 0
                while alarm_thread.isAlive() and (milliseconds_passed < 3000):
                    time.sleep(0.01)
                    milliseconds_passed += 10
                # isAlive returns False if it has stopped
                success = not alarm_thread.isAlive()
                if success is True:
                    self.__alarm_threads.remove(alarm_thread)
        return success

    def __stop_all_alarm_threads(self):
        """
        Stops all AlarmThreads and removes items from the threads list.
        This method can take up to 15 seconds to run.
        :return: Boolean indicating if the operation was successful.
        """
        for alarm_thread in self.__alarm_threads:
            alarm_thread.stop()

        # Check, for a max time of 15s, that all threads have really stopped
        milliseconds_passed = 0
        continue_trying = True
        while continue_trying and (milliseconds_passed < 15000):
            continue_trying = False
            # Need to iterate backwards in order to remove items safely
            for i in xrange(len(self.__alarm_threads) - 1, -1, -1):
                if self.__alarm_threads[i].isAlive() is True:
                    continue_trying = True
                else:
                    del self.__alarm_threads[i]
            time.sleep(0.01)
            milliseconds_passed += 10

        if self.__alarm_threads:
            return False
        else:
            return True

    def is_alarm_running(self, alarm_id):
        """
        Checks if the given alarm ID is running as a thread.
        :param alarm_id: ID of the AlarmItem for the alarm thread to check.
        :return:
        """
        for alarm_thread in self.__alarm_threads:
            if alarm_thread.get_id() == alarm_id:
                return alarm_thread.isAlive()
        return False

    def get_running_alarms(self):
        """
        Returns a list of all the running alarms (active alarms verified to be
        running on their own thread).
        :return: List of AlarmItems that are currently running.
        """
        # self test and self recovery
        self.check_threads_state()
        alarm_list = []
        for alarm_thread in self.__alarm_threads:
            alarm_list.append(AlarmManager.get_alarm(alarm_thread.get_id()))
        return alarm_list

    def check_threads_state(self):
        """
        Retrieves all the alarms and checks if the are running or not as they
        should. Tries to correct any possible errors, and if it can't it prints
        an error into stderr.
        :return: Boolean indicating if everything was running correctly before
                 the method was called.
        """
        previously_correct = True
        running_counter = 0
        all_alarms = AlarmManager.get_all_alarms()
        for alarm in all_alarms:
            if alarm.is_active() is True:
                # This alarm should be running
                running_counter += 1
                if self.is_alarm_running(alarm.id_) is False:
                    self.__set_alarm_thread(alarm)
                    previously_correct = False
            else:
                # This alarm should not be running
                if self.is_alarm_running(alarm.id_) is True:
                    self.__stop_alarm_thread(alarm.id_)
                    previously_correct = False

        # Check we have as many threads as expected
        if len(self.__alarm_threads) != running_counter:
            previously_correct = False
            # We can only attempt to recover if there are extra threads not
            # meant to be running
            for alarm_thread in self.__alarm_threads:
                for alarm in all_alarms:
                    if alarm.id_ == alarm_thread.get_id():
                        break
                else:
                    self.__stop_alarm_thread(alarm_thread.get_id())

            if len(self.__alarm_threads) != running_counter:
                print('ERROR: Could not correct the alarm threads in' +
                      'self.check_threads_state !',
                      file=sys.stderr)

        return previously_correct
