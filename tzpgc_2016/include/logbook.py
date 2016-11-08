#!/usr/bin/env python

#Copyright (c) 2016 Massimiliano Patacchiola
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

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
        self._timer = 0
        self._mp3 = ""

        #create the file
        open(self._id + ".csv", 'a').close()

        #Write the header as first line
        try:
           path_to_file = self._id + ".csv"
           with open(path_to_file, "a") as f:
               f.write( "trial," + "pinv," +  "rinv," + "pmult," + "rmult," + "total," + "gaze," + "pointing," + "timer," + "audio" + '\n')
               f.close()
        except:
           # log exception
           print("* LOGBOOK: execpion creating the header.")

    def AddTextLine(self, stringToAdd):
        try:
            path_to_file = self._id + ".csv"
            with open(path_to_file, "a") as f:
                f.write( stringToAdd + '\n')
                f.close()
        except:
            # log exception
            print("* LOGBOOK: execpion adding a text line to the file.")

    def AddLine(self, trial, pinv, rinv, pmult, rmult, total, gaze, pointing, timer, mp3 ):
        try:
            self._trial = trial
            self._pinv = pinv
            self._rinv = rinv
            self._pmult = pmult
            self._rmult = rmult
            self._gaze = gaze
            self._pointing = pointing
            self._mp3 = mp3
            self._timer = timer

            path_to_file = self._id + ".csv"
            with open(path_to_file, "a") as f:
                f.write( str(trial) + "," + str(pinv) + "," +  str(rinv) + "," + str(pmult) + "," + str(rmult) + "," + str(total) + "," + str(gaze) + "," + str(pointing) + "," + str(timer) + "," + str(mp3) + '\n')
                f.close()
        except:
            # log exception
            print("* LOGBOOK: execpion adding a line to the file.")
               
          
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

