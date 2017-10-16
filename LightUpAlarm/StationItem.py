# -*- coding: utf-8 -*-
#
# Class to define Station data.
#
# Copyright (c) 2015 carlosperate http://carlosperate.github.io
# Copyright (c) 207 Yackou http://yackou.github.io
#
# Licensed under The MIT License (MIT), a copy can be found in the LICENSE file
#
from __future__ import unicode_literals, absolute_import, print_function
import collections
try:
    from LightUpAlarm.Py23Compatibility import *
except ImportError:
    from Py23Compatibility import *


class StationItem(object):
    """
    This class defines a Station object, with the following data items.
        id: primary key ID from the alarm database.
        name: String containing the name of the station.
        url: String containing the URL of the station.
    """

    #
    # metaclass methods: constructor, initialiser and print
    #
    def __new__(cls, name, url, station_id=None):
        """
        This is the class constructor. We need to initialise the class instance
        here instead of in __init__ because the accessors input sanitation is
        used to determine the validity of the given inputs. If invalid data is
        inputted to the constructor it returns None instead of the instance.
        :param cls: Class type
        :param name: String containing the name of the station.
        :param url: String containing the URL of the station.
        :param station_id: Integer to indicate the Station ID
        :return: instance of the StationItem class. Returns None if input data is
                invalid.
        """
        instance = object.__new__(cls)
        # ID is only created at first save into db
        instance.__id = None
        # Station data
        instance.__name = ""
        instance.__url = ""

        # Assigning values using accessors with input sanitation
        instance.name = name
        instance.url = url
        if station_id is not None:
            instance.id_ = station_id

        # Now we check if the values have been set, if not, it means an input
        # was invalid and the object should not be created.
        valid_inputs = True
        if instance.name != name:
            valid_inputs = False
        if instance.url != url:
            valid_inputs = False
        if station_id is not None and instance.id_ != station_id:
            valid_inputs = False

        if valid_inputs is True:
            return instance
        else:
            return None

    def __init__(self, name, url, station_id=None):
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
        ret_str = 'Station ID: %3d | Name: %s | url: %s' %\
                  (self.id_, self.name, self.url)

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
            print('ERROR: Provided StationItem().id type is not a positive ' +
                  'Integer: %s!' % new_id, file=sys.stderr)

    id_ = property(__get_id, __set_id)


    #
    # name accesor
    #
    def __get_name(self):
        return self.__name

    def __set_name(self, new_name):
        """
        Checks that the input can be converted to a string and saves it.
        :param new_name: new name for the alarm instance.
        """
        try:
            self.__name = str(new_name)
        except Exception:
            print('ERROR: Provided StationItem().name is not convertible to ' +
                  'a string: %s!' % new_name, file=sys.stderr)

    name = property(__get_name, __set_name)


    #
    # url accesor
    #
    def __get_url(self):
        return self.__url

    def __set_url(self, new_url):
        """
        Checks that the input can be converted to a string and saves it.
        :param new_url: new url for the alarm instance.
        """
        try:
            self.__url = str(new_url)
        except Exception:
            print('ERROR: Provided StationItem().url is not convertible to ' +
                  'a string: %s!' % new_url, file=sys.stderr)

    url = property(__get_url, __set_url)
