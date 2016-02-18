#!/usr/bin/env python

import os
import time

class Logbook(object):

    def __init__(self):
        """
        Class initialization
        """
        self._id = time.strftime("%d%m%Y_%H%M%S", time.gmtime()) #id of the log, it's the timestamp
        self._trial = 0
        self._pinv = 0.0
        self._rinv = 0.0
        self._pmult = 0.0
        self._rmult = 0.0
        self._gaze = False
        self._pointing = False
        self._mp3 = ""
        self._timer = 0

        #create the file
        open(self._id + ".csv", 'a').close()

    def AddLine(self, trial, pinv, rinv, pmult, rmult, gaze, pointing, mp3, timer):
        try:
            path_to_file = self._id + ".csv"
            with open(path_to_file, "w+") as f:
                f.write(str(self._trial) + "," + str(self._pinv) + "," + '\n')
                f.close()
        except:
            # log exception
            print("LOGBOOK: execpion adding a line to the file.")
               
          
    def SaveFile(self, filePath):
        print(filePath)
        if os.path.isfile(filePath):
            self._path = filePath
            self._doc = minidom.parse(filePath)
            print("PARSER: the XML file was correctly loaded.")
            return True
        else:
            print("PARSER: Error the XML file does not exist, please check if the path is correct.")
            return False

