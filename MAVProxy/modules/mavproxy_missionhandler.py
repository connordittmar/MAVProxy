#!/usr/bin/env python
'''
Get missions module
Connor Ditmar, April 2017

This module simply gets missions from the interop server and writes to the Pixhawk:
example mission:
{'active': True,
 'air_drop_pos': {'latitude': 38.141833, 'longitude': -76.425263},
 'emergent_last_known_pos': {'latitude': 38.145823, 'longitude': -76.422396},
 'fly_zones': [],
 'home_pos': {'latitude': 38.14792, 'longitude': -76.427995},
 'id': 1,
 'mission_waypoints': [{'altitude_msl': 200.0,
                        'latitude': 38.142544,
                        'longitude': -76.434088,
                        'order': 1}],
 'off_axis_target_pos': {'latitude': 38.142544, 'longitude': -76.434088},
 'search_grid_points': [{'altitude_msl': 200.0,
                         'latitude': 38.142544,
                         'longitude': -76.434088,
                         'order': 1}]}

'''

import os
import os.path
import sys
from pymavlink import mavutil, mavwp
import errno
import time
import pprint

from MAVProxy.modules.lib import mp_module
from MAVProxy.modules.lib import mp_util
from MAVProxy.modules.lib import mp_settings
from interop import AsyncClient

class MissionHandler(mp_module.MPModule):
    def __init__(self, mpstate):
        """Initialise module"""
        super(MissionHandler, self).__init__(mpstate, "missionhandler",
                                            "Use Interop to configure mission.", public=True)
        self.add_command('login', self.cmd_login, "Login to Server",["<url> (server url)",
                        "<username> (username)","<password> (password)"])
        self.add_command('mission', self.cmd_mission, "Mission Handling", ["<view>",
                        "<writewps>","<writefence","<writemission>"])
        #I have hardcoed client for now. DO NOT DO THIS IN THE FUTURE
        self.client = AsyncClient('http://10.17.163.109:8000','testuser','testpass')
    def usage(self):
        '''show help on command line options'''
        return """Usage: login <url (server url) | username (username) | password (password)> ,
                mission <view> | <writewps> | <writefence> | <writemission>"""


    def cmd_mission(self, args):
        if len(args) != 1:
            print self.usage()
        elif args[0] == "view":
            self.viewmission()

    def viewmission(self):
        '''returns information about module'''
        missions = self.client.get_missions()
        for m in missions.result():
            pprint.pprint(m.serialize())

    def writewps(self, filename):
        missions = self.client.get_missions()
        for m in missions.result():
            self.mission = m
            try:
                self.wploader.save(filename)

def init(mpstate):
    '''initialise module'''
    return MissionHandler(mpstate)
