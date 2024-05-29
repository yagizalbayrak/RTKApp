"""
Project: From Parallel.GAMIT App
Date: 10/05/2024
Reviser: yagiz
"""

from shutil import copyfile, copy, move, rmtree
import os
import datetime
import uuid
import re
import struct
import json
import glob

# app
from pyEvents import Event
from Utils import ecef2lla
from pyRinexName import check_year
import pyRinexName
import pyDate
import pyRunWithRetry
import pyStationInfo
import Utils
from Utils import (file_open,
                   file_write,
                   file_readlines,
                   struct_unpack,
                   chmod_exec)

TYPE_CRINEZ = 0
TYPE_RINEX  = 1
TYPE_RINEZ  = 2
TYPE_CRINEX = 3
TYPE_CRINEZ_2 = 4


class pyRinexException(Exception):
    def __init__(self, value):
        self.value = value
        self.event = Event(Description=value, EventType='error')

    def __str__(self):
        return str(self.value)


class pyRinexExceptionBadFile     (pyRinexException): pass
class pyRinexExceptionSingleEpoch (pyRinexException): pass
class pyRinexExceptionNoAutoCoord (pyRinexException): pass


class RinexRecord(object):

    def __init__(self, NetworkCode=None, StationCode=None):

        self.StationCode = StationCode
        self.NetworkCode = NetworkCode

        self.header            = None
        self.data              = None
        self.firstObs          = None
        self.datetime_firstObs = None
        self.datetime_lastObs  = None
        self.lastObs           = None
        self.antType           = None
        self.marker_number     = None
        self.marker_name       = StationCode
        self.recType           = None
        self.recNo             = None
        self.recVers           = None
        self.antNo             = None
        self.antDome           = None
        self.antOffset         = None
        self.interval          = None
        self.size              = None
        self.x                 = None
        self.y                 = None
        self.z                 = None
        self.lat               = None
        self.lon               = None
        self.h                 = None
        self.date              = None
        self.rinex             = None
        self.crinez            = None
        self.crinez_path       = None
        self.rinex_path        = None
        self.origin_type       = None
        self.obs_types         = None
        self.observables       = None
        self.system            = None
        self.satsys            = None
        self.no_cleanup        = None
        self.multiday          = False
        self.multiday_rnx_list = []
        self.epochs            = None
        self.completion        = None
        self.rel_completion    = None
        self.rinex_version     = None
        self.min_time_seconds  = 3600

        # log list to append all actions performed to rinex file
        self.log = []

        # list of required header records and a flag to know if they were found or not in the current header
        # also, have a tuple of default values in case there is a missing record
        self.required_records = {'RINEX VERSION / TYPE':
                                     {'format_tuple': ('%9.2f', '%11s', '%1s', '%19s', '%1s', '%19s'),
                                      'found': False,
                                      'default': ('',)},

                                 'PGM / RUN BY / DATE':
                                     {'format_tuple': ('%-20s', '%-20s', '%-20s'),
                                      'found': False,
                                      'default': ('pyRinex: 1.00 000', 'Parallel.PPP', '21FEB17 00:00:00')},

                                 'MARKER NAME':
                                     {'format_tuple': ('%-60s',),
                                      'found': False,
                                      'default': (self.StationCode.upper(),)},

                                 'MARKER NUMBER':
                                     {'format_tuple': ('%-20s',),
                                      'found': False,
                                      'default': (self.StationCode.upper(),)},

                                 'OBSERVER / AGENCY':
                                     {'format_tuple': ('%-20s', '%-40s'),
                                      'found': False,
                                      'default': ('UNKNOWN', 'UNKNOWN')},

                                 'REC # / TYPE / VERS':
                                     {'format_tuple': ('%-20s', '%-20s', '%-20s'),
                                      'found': False,
                                      'default': ('0000000', 'ASHTECH Z-XII3', 'CC00')},

                                 'ANT # / TYPE':
                                     {'format_tuple': ('%-20s', '%-20s'),
                                      'found': False,
                                      'default': ('0000', 'ASH700936C_M SNOW')},

                                 'ANTENNA: DELTA H/E/N':
                                     {'format_tuple': ('%14.4f', '%14.4f', '%14.4f'),
                                      'found': False,
                                      'default': (0.0, 0.0, 0.0)},

                                 'APPROX POSITION XYZ':
                                     {'format_tuple': ('%14.4f', '%14.4f', '%14.4f'),
                                      'found': False,
                                      'default': (0.0, 0.0, 6371000.0)},
                                 # '# / TYPES OF OBSERV' : [('%6i',), False, ('',)],
                                 'TIME OF FIRST OBS':
                                     {'format_tuple': ('%6i', '%6i', '%6i', '%6i', '%6i', '%13.7f', '%8s'),
                                      'found': False,
                                      'default': (1, 1, 1, 1, 1, 0, 'GPS')},
                                 'INTERVAL':
                                     {'format_tuple': ('%10.3f',),
                                      'found': False,
                                      'default': (30,)},  # put a wrong interval when first reading the file so that
                                 # RinSum does not fail to read RINEX if interval record is > 60 chars
                                 # DDG: remove time of last observation all together. It just creates problems and
                                 # is not mandatory
                                 # 'TIME OF LAST OBS'    : [('%6i','%6i','%6i','%6i','%6i','%13.7f','%8s'),
                                 # True, (int(first_obs.year), int(first_obs.month), int(first_obs.day),
                                 # int(23), int(59), float(59), 'GPS')],
                                 'COMMENT':
                                     {'format_tuple': ('%-60s',), 'found': True, 'default': ('',)}}

        fieldnames = ['NetworkCode','StationCode','ObservationYear','ObservationMonth','ObservationDay',
                      'ObservationDOY','ObservationFYear','ObservationSTime','ObservationETime','ReceiverType',
                      'ReceiverSerial','ReceiverFw','AntennaType','AntennaSerial','AntennaDome','Filename','Interval',
                      'AntennaOffset', 'Completion']

        self.record = dict.fromkeys(fieldnames)

    def load_record(self):
        r = self.record
        r['NetworkCode']      = self.NetworkCode
        r['StationCode']      = self.StationCode
        r['ObservationYear']  = self.date.year
        r['ObservationMonth'] = self.date.month
        r['ObservationDay']   = self.date.day
        r['ObservationDOY']   = self.date.doy
        r['ObservationFYear'] = self.date.fyear
        r['ObservationSTime'] = self.firstObs
        r['ObservationETime'] = self.lastObs
        r['ReceiverType']     = self.recType
        r['ReceiverSerial']   = self.recNo
        r['ReceiverFw']       = self.recVers
        r['AntennaType']      = self.antType
        r['AntennaSerial']    = self.antNo
        r['AntennaDome']      = self.antDome
        r['Filename']         = self.rinex
        r['Interval']         = self.interval
        r['AntennaOffset']    = self.antOffset
        r['Completion']       = self.completion