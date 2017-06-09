#!/usr/bin/env python
'''
Get missions module
Connor Ditmar, April 2017

This module simply gets missions from the interop server and writes to the Pixhawk:
example mission:


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
        self.add_command('mission', self.cmd_mission, "Mission Handling", ["<view>",
                        "<writewps>","<writefence","<writemission>","<test>"])
        #I have hardcoed client for now. DO NOT DO THIS IN THE FUTURE
        self.client = AsyncClient('http://10.1.1.3:8000','testuser','testpass')
        self.wploader = mavwp.MAVWPLoader()
    def usage(self):
        '''show help on command line options'''
        return """Usage: login <url (server url) | username (username) | password (password)> ,
                mission <view> | <writewps> | <writefence> | <writemission>"""


    def cmd_mission(self, args):
        if len(args) != 1:
            print self.usage()
        elif args[0] == "view":
            self.viewmission()
        elif args[0] == "test":
            self.pull_waypoints()

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
            except:
                pass

    def pull_waypoints(self):
        self.wploader.target_system = self.target_system
        self.wploader.target_component = self.target_component
        try:
            mission = self.client.get_missions().result()[0]
            print mission
        except:
            pass
        #try:
        wps = mission.mission_waypoints
        for i in wps:
            if self.wploader.count() == 0:
                self.wploader.add_latlonalt(i.latitude,i.longitude,0)
            wp = self.wploader.wp(i.order-1)
            print wp
            self.wploader.add_latlonalt(i.latitude,i.longitude,i.altitude_msl)
        #except:
        #    print "wp upload failed."
        self.loading_waypoints = True
        self.loading_waypoint_lasttime = time.time()

        wp.target_system = self.target_system
        wp.target_component = self.target_component
        self.master.mav.send(self.wploader.wp(wps[-1].order-1))

def init(mpstate):
    '''initialise module'''
    return MissionHandler(mpstate)
