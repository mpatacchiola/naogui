#!/usr/bin/env python

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
        self._gestures_list = list() #list for pointing/non_pointing

        self._bmf_list = list() #moltiplication factor for the player B
        self._word0_list = list() #sentece in the first interaction
        self._word1_list = list() #sentece in the first interaction
        self._word2_list = list() #sentece in the second interaction
        self._word3_list = list() #sentece in the second interaction
        self._word4_list = list() #sentece in the second interaction
        self._word5_list = list() #sentece in the second interaction
        self._word6_list = list() #sentece in the second interaction
        self._pinv1_list = list() #robot investement in 1st interaction
        self._pinv2_list = list() #Option 'a' for robot investement in 2nd interaction
        self._pinv3_list = list() #Option 'a' for robot investement in 2nd interaction

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

		returned = item.getElementsByTagName("gestures")[0]
		self._gestures_list.append(returned.firstChild.data)
                print("gestures ........ %s" %returned.firstChild.data)

		returned = item.getElementsByTagName("bmf")[0]
		self._bmf_list.append(returned.firstChild.data)
                print("bmf ........ %s" %returned.firstChild.data)

		returned = item.getElementsByTagName("pinv1")[0]
		self._pinv1_list.append(returned.firstChild.data)
                print("pinv1 ........ %s" %returned.firstChild.data)

		returned = item.getElementsByTagName("pinv2")[0]
		self._pinv2_list.append(returned.firstChild.data)
                print("pinv2 ........ %s" %returned.firstChild.data)

		returned = item.getElementsByTagName("pinv3")[0]
		self._pinv3_list.append(returned.firstChild.data)
                print("pinv3 ........ %s" %returned.firstChild.data)

		returned = item.getElementsByTagName("word0")[0]
		self._word0_list.append(returned.firstChild.data)
                print("word0 ........ %s" %returned.firstChild.data)

		returned = item.getElementsByTagName("word1")[0]
		self._word1_list.append(returned.firstChild.data)
                print("word1 ........ %s" %returned.firstChild.data)

		returned = item.getElementsByTagName("word2")[0]
		self._word2_list.append(returned.firstChild.data)
                print("word2 ........ %s" %returned.firstChild.data)

		returned = item.getElementsByTagName("word3")[0]
		self._word3_list.append(returned.firstChild.data)
                print("word3 ........ %s" %returned.firstChild.data)

		returned = item.getElementsByTagName("word4")[0]
		self._word4_list.append(returned.firstChild.data)
                print("word4 ........ %s" %returned.firstChild.data)

		returned = item.getElementsByTagName("word5")[0]
		self._word5_list.append(returned.firstChild.data)
                print("word5 ........ %s" %returned.firstChild.data)

		returned = item.getElementsByTagName("word6")[0]
		self._word6_list.append(returned.firstChild.data)
                print("word6 ........ %s" %returned.firstChild.data)

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
        self._experiment_loaded = False

