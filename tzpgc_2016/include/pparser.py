#!/usr/bin/env python

#Copyright (c) 2016 Massimiliano Patacchiola
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from xml.dom import minidom
import os

class Parser(object):

    def __init__(self):
        """
        Class initialization
        """
        self._experiment_loaded = False

        self._number_list = list() #list of the trial number
        self._gaze_list = list() #list for gaze/non_gaze
        self._pointing_list = list() #list for pointing/non_pointing

        self._pmf_list = list() #moltiplication factor for the person
        self._rmf_list = list() #moltiplication factor for the robot
        self._mp3_list = list() #reward given by the robot
        self._mp3t_list = list() #name of the mp3 file
        self._nasty_list = list() #nasty or not robot
        self._size = 0

        #Pretrial list
        self._pretrial_repeat = 0
        self._pretrial_rmf = 0
        self._pretrial_pmf = 0

   
    def LoadFile(self, filePath):
        print(filePath)
        if os.path.isfile(filePath):
            self._path = filePath
            self._doc = minidom.parse(filePath)
            print("PARSER: the XML file was correctly loaded.")
            return True
        else:
            print("PARSER: Error the XML file does not exist, please check if the path is correct.")
            return False

    def parse_pretrial_list(self):
       	items = self._doc.getElementsByTagName("pretrial")
        counter = 0
        print("PARSER: Pretrial list, downloading settigs:")
	for item in items:
		returned = item.getElementsByTagName("repeat")[0]
		self._pretrial_repeat = returned.firstChild.data
                print("repeat ........ %s" %returned.firstChild.data)

		returned = item.getElementsByTagName("pmf")[0]
		self._pretrial_pmf = returned.firstChild.data
                print("pmf ........ %s" %returned.firstChild.data)

		returned = item.getElementsByTagName("rmf")[0]
		self._pretrial_rmf = returned.firstChild.data
                print("rmf ........ %s" %returned.firstChild.data)

        print("PARSER: Pretrial list, trials loaded ........ %s" %counter)


    def parse_experiment_list(self):
       	items = self._doc.getElementsByTagName("trial")
        counter = 0
        print("PARSER: Experiment list, downloading settigs:")
	for item in items:
		returned = item.getElementsByTagName("number")[0]
		self._number_list.append(returned.firstChild.data)
                print("number ........ %s" %returned.firstChild.data)

		returned = item.getElementsByTagName("gaze")[0]
		self._gaze_list.append(returned.firstChild.data)
                print("gaze ........ %s" %returned.firstChild.data)

		returned = item.getElementsByTagName("pointing")[0]
		self._pointing_list.append(returned.firstChild.data)
                print("pointing ........ %s" %returned.firstChild.data)

		returned = item.getElementsByTagName("pmf")[0]
		self._pmf_list.append(returned.firstChild.data)
                print("pmf ........ %s" %returned.firstChild.data)

		returned = item.getElementsByTagName("rmf")[0]
		self._rmf_list.append(returned.firstChild.data)
                print("rmf ........ %s" %returned.firstChild.data)

		returned = item.getElementsByTagName("mp3t")[0]
		self._mp3t_list.append(returned.firstChild.data)
                print("mp3t ........ %s" %returned.firstChild.data)
               
		returned = item.getElementsByTagName("mp3")[0]
		self._mp3_list.append(returned.firstChild.data)
                print("mp3 ........ %s" %returned.firstChild.data)

		returned = item.getElementsByTagName("nasty")[0]
		self._nasty_list.append(returned.firstChild.data)
                print("nasty ........ %s" %returned.firstChild.data)

                print("")
                counter = counter + 1

        self._experiment_loaded = True
        print("PARSER: Experiment list, trials loaded ........ %s" %counter)
        self._size = counter

    def check_file_existence(self, path):
        for file_name in self._mp3_list:
            file_name = path + file_name 
            if not os.path.isfile(file_name):
                print("PARSER: Error the file does not exist ... %s" %file_name)
                return False
        return True
    

    def clear_lists(self):
        print("PARSER: Clearing the objects lists.")
        del self._number_list[:]
        del self._gaze_list[:]
        del self._pointing_list[:]
        del self._mp3_list[:]
        del self._person_moltfact_list[:]
        del self._robot_moltfact_list[:]
        del self._nasty_list[:]
        self._experiment_loaded = False

