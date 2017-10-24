# -*- coding: utf-8 -*-
#
# Class to define Alarm data.
#
# Copyright (c) 2015 carlosperate http://carlosperate.github.io
#
# Licensed under The MIT License (MIT), a copy can be found in the LICENSE file
#
from __future__ import unicode_literals, absolute_import, print_function
import collections
try:
    from LightUpAlarm.Py23Compatibility import *
except ImportError:
    from Py23Compatibility import *


class AlarmItem(object):
    """
    This class defines an Alarm object, with the following data items.
        id: primary key ID from the alarm database.
        hour: Hour value for the alarm. Integer from 0 to 23.
        minute: Minute value for the alarm. Integer from 0 to 59.
        monday: Indicates if the alarm repeats every monday. Boolean.
        tuesday: Indicates if the alarm repeats every tuesday. Boolean.
        wednesday: Indicates if the alarm repeats every wednesday. Boolean.
        thursday: Indicates if the alarm repeats every thursday. Boolean.
        friday: Indicates if the alarm repeats every friday. Boolean.
        saturday: Indicates if the alarm repeats every saturday. Boolean.
        sunday: Indicates if the alarm repeats every sunday. Boolean.
        enabled: Indicates if the alarm is enabled (turned on). Boolean.
        label: Stores a string to accompany the alarm as a label.
        timestamp: Timestamp, in seconds since 1970, of the last time the alarm
                   was modified. This is stored and read from the storage
                   database, so this class does not set the value without an
                   input (stays as None).
    """

    #
    # metaclass methods: constructor, initialiser and print
    #
    def __new__(cls, hour, minute,
                days=(False, False, False, False, False, False, False),
                enabled=True, label='', timestamp=None, alarm_id=None, station_id=None):
        """
        This is the class constructor. We need to initialise the class instance
        here instead of in __init__ because the accessors input sanitation is
        used to determine the validity of the given inputs. If invalid data is
        inputted to the constructor it returns None instead of the instance.
        :param cls: Class type
        :param hour: Integer to indicate the alarm hour.
        :param minute: Integer to indicate the alarm minute.
        :param days: 7-item list of booleans to indicate repeat weekdays.
        :param enabled: Boolean to indicate alarm enabled state.
        :param timestamp: Time, in seconds since 1970, that this alarm was last
                          modified. This value can be added in order to be
                          able to synchronise alarms between different systems.
        :param alarm_id: Integer to indicate the Alarm ID
        :return: instance of the AlarmItem class. Returns None if input data is
                invalid.
        """
        instance = object.__new__(cls)
        # ID is only created at first save into db
        instance.__id = None
        # Alarm time
        instance.__minute = 0
        instance.__hour = 0
        # Indicates if the alarm is enabled or not
        instance.__enabled = False
        # Contains the days of the weeks that this alarm repeats
        instance.__repeat = collections.OrderedDict()
        instance.__repeat['Monday'] = False
        instance.__repeat['Tuesday'] = False
        instance.__repeat['Wednesday'] = False
        instance.__repeat['Thursday'] = False
        instance.__repeat['Friday'] = False
        instance.__repeat['Saturday'] = False
        instance.__repeat['Sunday'] = False
        # Contains the label string
        instance.__label = ''
        # Contains the timestamp of the last time it was modified
        instance.__timestamp = None

        instance.__station_id = None

        # Assigning values using accessors with input sanitation
        instance.hour = hour
        instance.minute = minute
        instance.repeat = days
        instance.enabled = enabled
        instance.label = label
        if timestamp is not None:
            instance.timestamp = timestamp
        if alarm_id is not None:
            instance.id_ = alarm_id
        if station_id is not None:
            instance.station_id = station_id

        # Now we check if the values have been set, if not, it means an input
        # was invalid and the object should not be created.
        valid_inputs = True
        if instance.hour != hour:
            valid_inputs = False
        if instance.minute != minute:
            valid_inputs = False
        if days is not None and instance.repeat != tuple(days):
            valid_inputs = False
        if enabled is not None and instance.enabled != enabled:
            valid_inputs = False
        if label is not None and instance.label != label:
            valid_inputs = False
        if timestamp is not None and instance.timestamp != timestamp:
            valid_inputs = False
        if alarm_id is not None and instance.id_ != alarm_id:
            valid_inputs = False
        if station_id is not None and instance.station_id != station_id:
            valid_inputs = False

        if valid_inputs is True:
            return instance
        else:
            return None

    def __init__(self, hour, minute,
                 days=(False, False, False, False, False, False, False),
                 enabled=True, label='', timestamp=None, alarm_id=None, station_id=None):
        """
        Any additional initialisation will go here. Nothing at the moment.
        Keep in mind all data has already been initialised in the __new__
        constructor.
        """
        pass

    def __str__(self):
        """
        Converts the class instance data into a readable string format.
        :return: String with all the alarm data.
        """
        enabled = 'Yes' if self.enabled is True else 'No'
        ret_str = 'Alarm ID: %3d | Time: %02d:%02d | Enabled: %3s | Repeat: ' %\
                  (self.id_, self.hour, self.minute, enabled)
        for day in self.__repeat:
            if self.__repeat[day] is True:
                ret_str += "%s " % str(day)[:3]
            else:
                ret_str += "--- "

        return ret_str

    #
    # id accesor
    #
    def __get_id(self):
        return self.__id

    def __set_id(self, new_id):
        """
        Sets id value. Must be a positive integer.
        :param new_id: new ID for the alarm instance.
        """
        if isinstance(new_id, int_type) and new_id >= 0:
            self.__id = new_id
        else:
            print('ERROR: Provided AlarmItem().id type is not a positive ' +
                  'Integer: %s!' % new_id, file=sys.stderr)

    id_ = property(__get_id, __set_id)

    #
    # enabled accesor
    #
    def __get_enabled(self):
        return self.__enabled

    def __set_enabled(self, new_enabled):
        """
        Ensure new value is a boolean before setting the enabled state.
        :param new_enabled: new enabled state for the alarm instance.
        """
        if isinstance(new_enabled, bool_type):
            self.__enabled = new_enabled
        else:
            print('ERROR: Provided AlarmItem().enabled type is not a boolean' +
                  ': %s!' % new_enabled, file=sys.stderr)

    enabled = property(__get_enabled, __set_enabled)

    #
    # minute accesor
    #
    def __get_minute(self):
        return self.__minute

    def __set_minute(self, new_minute):
        """
        Checks input is an integer is a value between 0 - 59.
        :param new_minute: new alarm minutes for the alarm instance.
        """
        if isinstance(new_minute, int_type):
            if 0 <= new_minute < 60:
                self.__minute = new_minute
            else:
                print('ERROR: Provided AlarmItem().minute is not between 0 ' +
                      'and 59: %s!' % new_minute, file=sys.stderr)
        else:
            print('ERROR: Provided AlarmItem().minute type is not an Integer' +
                  ': %s!' % new_minute, file=sys.stderr)

    minute = property(__get_minute, __set_minute)

    #
    # hour accesor
    #
    def __get_hour(self):
        return self.__hour

    def __set_hour(self, new_hour):
        """
        Checks input is an integer and a value between 0 - 23.
        :param new_hour: new alarm hours for the alarm instance.
        """
        if isinstance(new_hour, int_type):
            if 0 <= new_hour < 24:
                self.__hour = new_hour
            else:
                print('ERROR: Provided AlarmItem().hour is not between 0 and ' +
                      '23: %s!' % new_hour, file=sys.stderr)
        else:
            print('ERROR: Provided AlarmItem().hour type is not an Integer' +
                  ': %s!' % new_hour, file=sys.stderr)

    hour = property(__get_hour, __set_hour)

    #
    # label accesor
    #
    def __get_label(self):
        return self.__label

    def __set_label(self, new_label):
        """
        Checks that the input can be converted to a string and saves it.
        :param new_label: new label for the alarm instance.
        """
        try:
            self.__label = str(new_label)
        except Exception:
            print('ERROR: Provided AlarmItem().label is not convertible to ' +
                  'a string: %s!' % new_label, file=sys.stderr)

    label = property(__get_label, __set_label)

    #
    # timestamp accesor
    #
    def __get_timestamp(self):
        return self.__timestamp

    def __set_timestamp(self, new_timestamp):
        """
        Sets timestamp value in seconds since 1970. Must be an positive integer.
        Even at 32bit this should last until the year 2038.
        :param new_timestamp: new ID for the alarm instance.
        """
        if isinstance(new_timestamp, int_type) and new_timestamp >= 0:
            self.__timestamp = new_timestamp
        else:
            print('ERROR: Provided AlarmItem().timestamp type is not a ' +
                  'positive Integer: %s!' % new_timestamp, file=sys.stderr)

    timestamp = property(__get_timestamp, __set_timestamp)

    #
    # repeat accesor
    #
    def __get_repeat(self):
        """
        Returns the days of the week alarm repetition in the form of a tuple.
        :return: Tuple with 7 booleans to indicate repetition for the weekdays.
        """
        repeat_tuple = (self.__repeat['Monday'], self.__repeat['Tuesday'],
                        self.__repeat['Wednesday'], self.__repeat['Thursday'],
                        self.__repeat['Friday'], self.__repeat['Saturday'],
                        self.__repeat['Sunday'])
        return repeat_tuple

    def __set_repeat(self, new_repeat):
        """
        Checks that it is a list/tuple of 7 booleans and if so assigns them to
        the _repeat dictionary.
        :param new_repeat: List of containing 7 booleans to indicate the days
                           of the week the alarm repeats.
        """
        if len(new_repeat) == 7:
            for day in new_repeat:
                if not isinstance(day, bool_type):
                    print('ERROR: All items in the AlarmItem().repeat list ' +
                          'have to be Booleans!', file=sys.stderr)
                    break
            else:
                day_int = 0
                for day in self.__repeat:
                    self.__repeat[day] = new_repeat[day_int]
                    day_int += 1
        else:
            print('ERROR: The AlarmItem().repeat must be a list of 7 booleans!',
                  file=sys.stderr)

    repeat = property(__get_repeat, __set_repeat)

    def __get_monday(self):
        return self.__repeat['Monday']

    def __set_monday(self, new_monday):
        if isinstance(new_monday, bool_type):
            self.__repeat['Monday'] = new_monday
        else:
            print('ERROR: New value for the AlarmItem().monday variable has ' +
                  'to be a Boolean !', file=sys.stderr)

    monday = property(__get_monday, __set_monday)

    def __get_tuesday(self):
        return self.__repeat['Tuesday']

    def __set_tuesday(self, new_tuesday):
        if isinstance(new_tuesday, bool_type):
            self.__repeat['Tuesday'] = new_tuesday
        else:
            print('ERROR: New value for the AlarmItem().tuesday variable has ' +
                  'to be a Boolean !', file=sys.stderr)

    tuesday = property(__get_tuesday, __set_tuesday)

    def __get_wednesday(self):
        return self.__repeat['Wednesday']

    def __set_wednesday(self, new_wednesday):
        if isinstance(new_wednesday, bool_type):
            self.__repeat['Wednesday'] = new_wednesday
        else:
            print('ERROR: New value for the AlarmItem().wednesday variable ' +
                  'has to be a Boolean !', file=sys.stderr)

    wednesday = property(__get_wednesday, __set_wednesday)

    def __get_thursday(self):
        return self.__repeat['Thursday']

    def __set_thursday(self, new_thursday):
        if isinstance(new_thursday, bool_type):
            self.__repeat['Thursday'] = new_thursday
        else:
            print('ERROR: New value for the AlarmItem().thursday variable ' +
                  'has to be a Boolean !', file=sys.stderr)

    thursday = property(__get_thursday, __set_thursday)

    def __get_friday(self):
        return self.__repeat['Friday']

    def __set_friday(self, new_friday):
        if isinstance(new_friday, bool_type):
            self.__repeat['Friday'] = new_friday
        else:
            print('ERROR: New value for the AlarmItem().friday variable has ' +
                  'to be a Boolean !', file=sys.stderr)

    friday = property(__get_friday, __set_friday)

    def __get_saturday(self):
        return self.__repeat['Saturday']

    def __set_saturday(self, new_saturday):
        if isinstance(new_saturday, bool_type):
            self.__repeat['Saturday'] = new_saturday
        else:
            print('ERROR: New value for the AlarmItem().saturday variable ' +
                  'has to be a Boolean !', file=sys.stderr)

    saturday = property(__get_saturday, __set_saturday)

    def __get_sunday(self):
        return self.__repeat['Sunday']

    def __set_sunday(self, new_sunday):
        if isinstance(new_sunday, bool_type):
            self.__repeat['Sunday'] = new_sunday
        else:
            print('ERROR: New value for the AlarmItem().sunday variable ' +
                  'has to be a Boolean !', file=sys.stderr)

    sunday = property(__get_sunday, __set_sunday)

    #
    # station_id accesor
    #
    def __get_station_id(self):
        return self.__station_id

    def __set_station_id(self, new_station_id):
        """
        Sets station_id. Must be an positive integer.
        :param new_station_id: new station ID for the alarm instance.
        """
        if isinstance(new_station_id, int_type) and new_station_id >= 0:
            self.__station_id = new_station_id
        else:
            print('ERROR: Provided AlarmItem().station_id type is not a ' +
                  'positive Integer: %s!' % new_station_id, file=sys.stderr)

    station_id = property(__get_station_id, __set_station_id)

    #
    # member methods to retrieve specific data
    #
    def any_day_enabled(self):
        """
        Checks if there are any repeat days enabled.
        :return: A boolean value indicating if an repeat weekday is activated.
        """
        any_enabled = False
        for day in self.__repeat:
            if self.__repeat[day] is True:
                any_enabled = True
        return any_enabled

    def is_active(self):
        """
        Determines if the Alarm is 'active', meaning enabled and at least one
        weekday set to repeat.
        :return: Boolean indicating the 'active' state.
        """
        if self.enabled is True and self.any_day_enabled() is True:
            return True
        else:
            return False

    #
    # member methods to calculate time
    #
    def minutes_to_alert(self, hour, minute, weekday):
        """
        Calculates the time in minutes that will elapse from the initial
        reference input time and weekday and the first time this alarm will have
        to trigger an alert (independently of this alarm being active or not).
        :param hour: start hour, value 0-23.
        :param minute: start minute, value 0-59.
        :param weekday: start weekday, value 0-6.
        :return: Integer indicating the amount in minutes until the alarm
                 triggers from the initial reference time and weekday.
        """
        alarm_day_minute = self.minute + (self.hour * 60)
        ref_day_minute = minute + (hour * 60)
        one_day_minutes = 1440

        # First corner case, check the same day after input time
        if (self.repeat[weekday] is True) and \
                (alarm_day_minute >= ref_day_minute):
            return alarm_day_minute - ref_day_minute

        # Check the rest of the week until, but not including, the same day
        day = weekday + 1
        if day > 6:
            day = 0
        day_count = 1
        while day != weekday:
            if self.repeat[day] is True:
                # Add the days in minutes and relative time to reference
                minutes_difference = day_count * one_day_minutes
                if alarm_day_minute >= ref_day_minute:
                    minutes_difference += alarm_day_minute - ref_day_minute
                else:
                    minutes_difference -= ref_day_minute - alarm_day_minute
                # Returns on first encountered alarm
                return minutes_difference
            else:
                day += 1
                day_count += 1
                if day > 6:
                    day = 0

        # Second corner case, check the same day before input time
        if (self.repeat[weekday] is True) and \
                (ref_day_minute > alarm_day_minute):
            return (one_day_minutes * 7) - ref_day_minute + alarm_day_minute

        # Alarm has no enabled days
        return None

    def diff_alarm(self, min_difference):
        """
        Returns an Alarm instance with the same data as the calling alarm with
        a time difference indicated by the parameter.
        It edits the label to indicate the time difference.
        It does not copy the ID nor the timestamp.
        We are reducing the use case to have a range of -59 to 59 minutes to
        simplify the code.
        :para min_difference: Time difference, positive or negative in minutes
                              from -59 to 59, for the new Alarm.
        :return: Alarm instance with this data + time difference. Returns None
                 if there was an issue with the input data
        """
        # Input sanitation to given user case
        if not isinstance(min_difference, int_type):
            print('ERROR: Provided diff_alarm min_difference type is not an '
                  'Integer: %s!' % min_difference, file=sys.stderr)
            return None
        else:
            if not (-60 < min_difference < 60):
                print('ERROR: Provided diff_alarm min_difference is not between'
                      ' -59 and 59: %s!' % min_difference, file=sys.stderr)
                return None

        extra_hours = 0
        extra_days = 0

        new_minute = self.minute + min_difference
        while new_minute >= 60:
            new_minute %= 60
            extra_hours += 1
        while new_minute < 0:
            new_minute += 60
            extra_hours -= 1

        new_hour = self.hour + extra_hours
        while new_hour >= 24:
            new_hour %= 24
            extra_days += 1
        while new_hour < 0:
            new_hour += 24
            extra_days -= 1

        new_days = list(self.repeat)
        if extra_days < 0:
            # Move all items up by 1 per day
            while extra_days < 0:
                new_days.append(new_days.pop(0))
                extra_days += 1
        elif extra_days > 0:
            # Move all items down by 1 per day, input sanitation protects
            # against this breaking if extra_days > 6
            list_to_head = new_days[(len(new_days) - extra_days):]
            new_days = list_to_head + \
                new_days[0:(len(new_days) - extra_days)]

        new_label = self.label + \
            (" (Alarm %s %+dmin)" % (self.id_, min_difference))

        alarm_diff = AlarmItem(new_hour, new_minute, days=new_days,
                               enabled=self.enabled, label=new_label)
        return alarm_diff
