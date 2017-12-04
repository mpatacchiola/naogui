#!/usr/bin/env python

##
#
# Massimiliano Patacchiola, Plymouth University 2016
#
# Screen resolution 1920x1080
# It is necessary to have pyQt4 installed
# To generate python code from the .ui file: pyuic4 mainwindow.ui -o design.py

#In this experiment there are two robots, friend and enemy. The collaborator interacts
#with the subject giving alternative choices during the rounds. The enemy just return
#some points that have to be split between the participant and the friendly robot.
#
#First interaction: The participant choose a price, the friendly robot take a 
#preselected value from the XML file
#
#Second interaction: The participant choose another price, the friendly robot
#load two values 'a' and 'b' from the XML file and based on the subject answer
#it chooses which value to select.

# Libraries for Qt
from PyQt4 import QtGui  # Import the PyQt4 module we'll need
from PyQt4.QtCore import QElapsedTimer
from PyQt4.QtCore import QThread
from PyQt4.QtCore import SIGNAL
from PyQt4 import QtCore

import sys  
import os
import time
import math
import random

#python -m pip install pyaudio
#sudo apt-get install python-pyaudio python3-pyaudio
import subprocess

#Importing my custom libraries
sys.path.insert(1, '../include')
sys.path.insert(1, "../include/pynaoqi-python2.7-2.1.3.3-linux64") #import this module for the nao.py module
import design
import pparser
import nao
import logbook

#Robot Paramaters
SPEED = 0.2

## Class WorkerThread
#  
# It is a QThread that send signals
# and receive signals from the GUI
#
class WorkerThread(QThread):
  def __init__(self):
    QThread.__init__(self)

    #Signal variables
    self.enable_components_gui_signal = SIGNAL("enable_components_gui_signal")
    self.no_robot_signal = SIGNAL("no_robot_signal")
    self.yes_robot_signal = SIGNAL("yes_robot_signal")
    self.bad_xml_signal = SIGNAL("bad_xml_signal")
    self.good_xml_signal = SIGNAL("good_xml_signal")
    self.update_gui_signal = SIGNAL("update_gui_signal")
    self.show_start_btn_signal = SIGNAL("show_start_btn_signal")

    #Misc variables
    self.timer = QElapsedTimer()
    self.timer_robot = QElapsedTimer()
    self.myParser = pparser.Parser()    
    self.STATE_MACHINE = 0

    #Status variables
    self._robot_connected = False
    self._xml_uploaded = False
    self._start_pressed = False
    self._confirm_pressed = False
    self._confirm_pressed_robot = False
    self._participant_decision_taken = False
    self._session_info_given = False

    #Sub state of state 1
    self.SUB_STATE = 0

    #Logbook variables
    self._log_first_line = ""
    self._log_timer = 0
    self._log_trial = 0
    self._log_person_total = 0.0
    self._log_leader_total = 0.0
    self._log_player2_total = 0.0
    self._log_player3_total = 0.0
    self._log_person_investment = 0
    self._log_leader_investment = 0
    self._log_player2_investment = 0
    self._log_player3_investment = 0

    self._log_pmf = 0 #person multiplication factor
    self._log_bmf = 0 #player b multiplication factor
    self._log_gaze = False
    self._log_pointing = False


  ## Main function of the Thread
  # 
  # It runs the State Machine
  #
  def run(self):
    #Init the State machine 
    #self.emit(self.enable_signal) #GUI enabled
    self.emit(self.enable_components_gui_signal, True,  False, False) #GUI components
    self.timer.start()
    self.timer_robot.start()
    self.timer_robot_deadline = 0 # deadline for the robot
    self.timer_robot_waiting = 2000 # robots waits 2 seconds then look to participant
    self.STATE_MACHINE = 0

    while True:
        time.sleep(0.050) #50 msec sleep to evitate block
        #STATE-0 init
        if self.STATE_MACHINE == 0:
            if self._robot_connected==True and self._xml_uploaded==True and self._start_pressed==True and self._session_info_given==True:                            
                self.logger = logbook.Logbook() #Logbook Init
                self.logger.AddTextLine(self._log_first_line)  #Add the first line to the logbook
                self.emit(self.show_start_btn_signal, False)
                self._start_pressed = False
                self.STATE_MACHINE = 1 #switching to next state
            else:
                current_time = time.strftime("%H:%M:%S", time.gmtime())
                status = "robot_coonnected = " + str(self._robot_connected) + "\n" 
                status += "xml_uploaded = " + str(self._xml_uploaded) + "\n" 
                status += "start_pressed = " + str(self._start_pressed) + "\n"
                status += "session_info_given = " + str(self._session_info_given) + "\n"
                print "[0] " + current_time + " Waiting... \n" + status
                time.sleep(3)

        #STATE-1 Hello world
        if self.STATE_MACHINE == 1:
            #Init all the variables
            if self.SUB_STATE == 0:
                self._confirm_pressed = False
                self._confirm_pressed_robot = False
                self._start_pressed = False
                self._participant_decision_taken = False
                print "[1] Hello world!"
                sentence = self.myParser._word0_list[self._log_trial]
                if self.myParser._gestures_list[self._log_trial] == "True":
                    self.myPuppet1.animated_say_something(str(sentence))
                else:
                    self.myPuppet1.say_something(str(sentence))
                if self.myParser._gaze_list[self._log_trial] == "True":
                    self.myPuppet1.look_to("HeadYaw", -60.0, SPEED)
                    time.sleep(random.randint(1,2))
                print "[1] Reset the head pose!"                 
                self.myPuppet1.look_to("HeadYaw", 0.0, SPEED)
                self.myPuppet2.look_to("HeadYaw", 0.0, SPEED)
                self.myPuppet3.look_to("HeadYaw", 0.0, SPEED)
                self.myPuppet1.look_to("HeadPitch", 0.0, SPEED)
                self.myPuppet2.look_to("HeadPitch", 0.0, SPEED)
                self.myPuppet3.look_to("HeadPitch", 0.0, SPEED)
                time.sleep(1) 
                print "[1] Enablig components"
                self.emit(self.enable_components_gui_signal, False,  False, True) #GUI components
                self.STATE_MACHINE = 2
 

        #STATE-2 Reset variables and Robot talks
        if self.STATE_MACHINE == 2:
            #RESET all the values at each new cycle
            self._log_person_investment = 0
            self._log_leader_investment = 0
            self._log_player2_investment = 0
            self._log_player3_investment = 0
            #Reset the GUI and enable component
            print "[2] Enabling buttons..." 
            self.emit(self.enable_components_gui_signal, False,  False, True)  #GUI components
            self.emit(self.update_gui_signal, self._log_person_total, self._log_leader_total, self._log_player2_total, self._log_player3_total, "Please wait...")
            #The robot choose and now will look to the participant because the waiting time elapsed
            if self.myParser._gaze_list[self._log_trial] == "True":
                    self.myPuppet2.look_to("HeadYaw", 60.0, SPEED)
                    self.myPuppet3.look_to("HeadYaw", 60.0, SPEED)
                    time.sleep(random.randint(0,2))
                    #self.myPuppet1.look_to("HeadPitch", 5.0, SPEED)
            print "[2] Switching to the next state"
            self.STATE_MACHINE = 3 #next state       
            print "[3] Waiting for the subject and robot answer..." #going to state 3


        #STATE-3 First interaction: the leader makes his choice
        if self.STATE_MACHINE == 3:  
            self._log_leader_investment = int(self.myParser._pinv1_list[self._log_trial])
            if self.myParser._pointing_list[self._log_trial] == "True":
                  print "[3] pointing == True"
                  self.myPuppet1.left_arm_pointing(True, SPEED)
            time.sleep(1)
            if self.myParser._pointing_list[self._log_trial] == "True":
                  print "[3] pointing == False"
                  self.myPuppet1.left_arm_pointing(False, SPEED)
            sentence = str(self.myParser._word1_list[self._log_trial])
            if self.myParser._gestures_list[self._log_trial] == "True":
                  self.myPuppet1.animated_say_something(str(sentence))
            else:
                  self.myPuppet1.say_something(str(sentence))
            if self.myParser._gaze_list[self._log_trial] == "True":
                    self.myPuppet2.look_to("HeadYaw", 60.0, SPEED)
                    self.myPuppet3.look_to("HeadYaw", -60.0, SPEED)
                    #time.sleep(random.randint(0,2))
                    #self.myPuppet1.look_to("HeadPitch", 5.0, SPEED)
                    self.myPuppet1.look_to("HeadYaw", -60.0, SPEED)
            #Update with the leader score
            local_string = "Pepper invested: " + str(self._log_leader_investment) + '\n' 
            self.emit(self.update_gui_signal, self._log_person_total, self._log_leader_total, self._log_player2_total, self._log_player3_total, local_string)
            #time.sleep(random.randint(1,2))
            self.STATE_MACHINE = 4 #next state

        #STATE-4 The two NAOs invest
        if self.STATE_MACHINE == 4:  
            self._log_player2_investment = int(self.myParser._pinv2_list[self._log_trial])
            self._log_player3_investment = int(self.myParser._pinv3_list[self._log_trial])
            if self.myParser._gaze_list[self._log_trial] == "True":
                    self.myPuppet2.look_to("HeadYaw", 0.0, SPEED)
                    self.myPuppet3.look_to("HeadYaw", -60.0, SPEED)
                    #self.myPuppet2.look_to("HeadPitch", 5.0, SPEED)
                    #self.myPuppet3.look_to("HeadPitch", 5.0, SPEED)
            #time.sleep(random.randint(2,3))
            #Player 2 investment
            sentence = str(self.myParser._word2_list[self._log_trial])
            if self.myParser._gestures_list[self._log_trial] == "True":
                    self.myPuppet2.animated_say_something(str(sentence))
            else:
                    self.myPuppet2.say_something(str(sentence))
            local_string = "Pepper invested: " + str(self._log_leader_investment) + '\n' 
            local_string += "Tommy invested: " + str(self._log_player2_investment) + '\n'
            self.emit(self.update_gui_signal, self._log_person_total, self._log_leader_total, self._log_player2_total, self._log_player3_total, local_string)                        
            if self.myParser._gaze_list[self._log_trial] == "True":
                    self.myPuppet2.look_to("HeadYaw", 40.0, SPEED)
                    self.myPuppet3.look_to("HeadYaw", 0.0, SPEED)             
            #time.sleep(random.randint(1,3))
            #Player 3 investment
            sentence = str(self.myParser._word3_list[self._log_trial])
            if self.myParser._gestures_list[self._log_trial] == "True":
                    self.myPuppet3.animated_say_something(str(sentence))
            else:
                    self.myPuppet3.say_something(str(sentence))
            if self.myParser._gaze_list[self._log_trial] == "True":
                    self.myPuppet2.look_to("HeadYaw", 0.0, SPEED)

            print "[4] First interaction"                         
            print("[4] Leader: " + str(self._log_leader_investment))
            print("[4] Player 2: " + str(self._log_player2_investment))
            print("[4] Player 3: " + str(self._log_player3_investment)) 
            local_string = "Pepper invested: " + str(self._log_leader_investment) + '\n' 
            local_string += "Tommy invested: " + str(self._log_player2_investment) + '\n'
            local_string += "Jones invested: " + str(self._log_player3_investment) + '\n'
            local_string += "Please select a value to invest..." + '\n'
            self.emit(self.enable_components_gui_signal, False,  True, True)  #GUI components   
            self.emit(self.update_gui_signal, self._log_person_total, self._log_leader_total, self._log_player2_total, self._log_player3_total, local_string)
            #time.sleep(random.randint(1,2))
            if self.myParser._gaze_list[self._log_trial] == "True":
                    self.myPuppet1.look_to("HeadYaw", 0.0, SPEED)
                    #self.myPuppet2.look_to("HeadYaw", 0.0, SPEED)
                    #self.myPuppet3.look_to("HeadYaw", 0.0, SPEED)
                    #self.myPuppet1.look_to("HeadPitch", 5.0, SPEED)
                    #self.myPuppet2.look_to("HeadPitch", 0.0, SPEED)
                    #self.myPuppet3.look_to("HeadPitch", 0.0, SPEED)      
            self.STATE_MACHINE = 5 #next state

        #STATE-5 The participant choose
        if self.STATE_MACHINE == 5:
            if self._confirm_pressed == True:   #when subject gives the answer
                self._confirm_pressed = False
                print "[5] The participant pressed: " + str(self._log_person_investment)
                #Updating the GUI
                local_string = "You invested: " + str(self._log_person_investment) + '\n'
                local_string += "Pepper invested: " + str(self._log_leader_investment) + '\n' 
                local_string += "Tommy invested: " + str(self._log_player2_investment) + '\n'
                local_string += "Jones invested: " + str(self._log_player3_investment) + '\n'
                local_string += "In total has been invested: " + str(self._log_person_investment + self._log_leader_investment + self._log_player2_investment + self._log_player3_investment) + '\n'
                #total, player_investment, round_total, robot_investment, text_label=""
                self.emit(self.enable_components_gui_signal, False,  False, True)  #GUI components
                self.emit(self.update_gui_signal, self._log_person_total, self._log_leader_total, self._log_player2_total, self._log_player3_total, local_string)
                time.sleep(1.0)
                #The Leader say the investment
                sentence = self.myParser._word4_list[self._log_trial]
                sentence = str(sentence) #convert to string
                if(sentence != "." and sentence != "" and sentence != "-"):
                    #Check if XXX is present and replace it with the
                    has_substring = sentence.find("XXX")
                    if(has_substring != -1):
                        print "[5] Found the substring 'XXX' at location: " + str(has_substring)
                        sentence = sentence.replace("XXX", str(self._log_person_investment))
                    has_substring = sentence.find("YYY")
                    if(has_substring != -1):
                        print "[5] Found the substring 'YYY' at location: " + str(has_substring)
                        sentence = sentence.replace("YYY", str(self._log_person_investment + self._log_leader_investment + self._log_player2_investment + self._log_player3_investment))
                    if self.myParser._gestures_list[self._log_trial] == "True":
                        self.myPuppet1.animated_say_something(str(sentence))
                    else:
                        self.myPuppet1.say_something(str(sentence))
                else:
                    print "[5] Saying Nothing because the sentence in the XML file is '" + str(sentence) + "'"
                #time.sleep(random.randint(1,2))
                if self.myParser._gaze_list[self._log_trial] == "True":
                    self.myPuppet1.look_to("HeadYaw", 60.0, SPEED)
                    time.sleep(random.randint(1,2))
                    self.myPuppet2.look_to("HeadYaw", 60.0, SPEED)
                    self.myPuppet3.look_to("HeadYaw", 60.0, SPEED)   
                self.STATE_MACHINE = 6 #next state


        #STATE-6  The Banker robot gives a reward
        if self.STATE_MACHINE == 6:
            #Update the TOTAL
            banker_investment = (self._log_person_investment + self._log_leader_investment + self._log_player2_investment + self._log_player3_investment) * 3.0 *  float(self.myParser._bmf_list[self._log_trial])
            banker_investment -= abs( self._log_leader_investment - ((self._log_person_investment + self._log_player2_investment + self._log_player3_investment)/3.0) )
            banker_investment /= 3.0
            banker_investment = round(banker_investment,1) #round to first decimal place
            abs_value = round(abs( self._log_leader_investment - ((self._log_person_investment + self._log_player2_investment + self._log_player3_investment)/3.0) ), 1)
            if banker_investment < 0: banker_investment = 0.0
            print "[6] The Banker invested: " + str(banker_investment)
            local_string = "The banker received: " + str((self._log_person_investment + self._log_leader_investment + self._log_player2_investment + self._log_player3_investment))+ '\n'
            local_string += "The investments differed of: " + str(abs_value) + " in average" + '\n'
            local_string += "The banker returned: " + str(banker_investment) + " each" + '\n'
            local_string += "Please press START to begin a new round..." + '\n' 
            #total, pinv, round_tot, rinv, rslider, text
            self._log_person_total += (10.0 - self._log_person_investment) + banker_investment
            self._log_person_total = round(self._log_person_total,1)
            self._log_leader_total += (10.0 - self._log_leader_investment) + banker_investment
            self._log_leader_total = round(self._log_leader_total,1)
            self._log_player2_total += (10.0 - self._log_player2_investment) + banker_investment
            self._log_player2_total = round(self._log_player2_total,1)
            self._log_player3_total += (10.0 - self._log_player3_investment) + banker_investment
            self._log_player3_total = round(self._log_player3_total,1)
            self.emit(self.update_gui_signal, self._log_person_total, self._log_leader_total, self._log_player2_total,  self._log_player3_total, local_string)
            time.sleep(2)
            if self.myParser._gaze_list[self._log_trial] == "True":
                    self.myPuppet1.look_to("HeadYaw", 0.0, SPEED)
                    self.myPuppet2.look_to("HeadYaw", 0.0, SPEED)
                    self.myPuppet3.look_to("HeadYaw", 0.0, SPEED)
            time.sleep(random.randint(1,2))
            #Check the absolute value and decide the sentence to say
            if abs_value <= 2.0:
                sentence = self.myParser._word6_list[self._log_trial]
            else:
                sentence = self.myParser._word5_list[self._log_trial]
            sentence = str(sentence) #convert to string
            if(sentence != "." and sentence != "" and sentence != "-"):
                    #Check if XXX is present and replace it with the
                    has_substring = sentence.find("XXX")
                    if(has_substring != -1):
                        print "[6] Found the substring 'XXX' at location: " + str(has_substring)
                        sentence = sentence.replace("XXX", str(banker_investment))
                    has_substring = sentence.find("YYY")
                    if(has_substring != -1):
                        print "[6] Found the substring 'YYY' at location: " + str(has_substring)
                        sentence = sentence.replace("YYY", str(abs_value))
                    if self.myParser._gestures_list[self._log_trial] == "True":
                        self.myPuppet1.animated_say_something(str(sentence))
                    else:
                        self.myPuppet1.say_something(str(sentence))
            else:
                    print "[6] Saying Nothing because the sentence in the XML file is '" + str(sentence) + "'"
            time.sleep(2)
            #if self.myParser._gaze_list[self._log_trial] == "True":
            #        self.myPuppet1.look_to("HeadPitch", 5.0, SPEED)
            print "[7] Switch to the next state"
            self.STATE_MACHINE = 9 #next state


        #STATE-9 Saving in the logbook
        if self.STATE_MACHINE == 9:
            print "[9] Saving the trial in the logbook"
            self.logger.AddLine(self._log_trial+1, self._log_person_investment, self._log_leader_investment, self._log_player2_investment, 
                               self._log_player3_investment, self._log_bmf, self._log_person_total, self._log_gaze, self._log_pointing, self._log_timer)
            print ("[9] trial, person_investment, robot_investment, person_investment_second, log_robot_investment_second, player_b_investment, pmf, bmf, person_total, gaze, pointing, timer, timer_second")
            print ("[9] " + str(self._log_trial+1) + "," + str(self._log_person_investment) + "," + str(self._log_leader_investment) + 
                   "," + "," +  str(0) + "," + str(self._log_bmf) + "," + str(self._log_person_total) + "," + str(self._log_gaze) + 
                   "," + str(self._log_pointing) + "," + str(self._log_timer) )

            if self._log_trial+1 != self.myParser._size:
                self.STATE_MACHINE = 10 #cycling to state 12
                self.emit(self.enable_components_gui_signal, True, False, False) #Enable the Start Button
                self._log_trial = self._log_trial + 1
            elif self._log_trial+1 == self.myParser._size:
                self.STATE_MACHINE = 11 #experiment finished               

        #STATE-10 Waiting for the subject pressing START
        if self.STATE_MACHINE == 10:
            if self._start_pressed == True: 
                self._start_pressed = False
                print "[10] Start pressed..."
                self.emit(self.enable_components_gui_signal, False,  False, False)
                self.STATE_MACHINE = 2 #cycling to state 2
                time.sleep(1)

        #STATE-11 Final state is called to shutdown the robot
        if self.STATE_MACHINE == 11:
            print "[11] The game is finished"
            self._xml_uploaded = False #reset status variable
            self._start_pressed = False
            self._log_trial = 0
            self.STATE_MACHINE = 0 #cycling to state 0
            #total, player_investment, round_total, your_investment, robot_investment 
            local_string = "Your score is: " + str(self._log_person_total) + '\n'
            local_string += "The game is finished. Thank you..."
            self.myPuppet1.say_something("Thank you, It was nice to play with you.")
            #total, player_investment, round_total, robot_investment, text_label=""
            self.emit(self.update_gui_signal, 0, 0, 0, 0, local_string) 
            self.emit(self.enable_components_gui_signal, False, False, False) #GUI components disabled
            time.sleep(5)


  def start_experiment(self):
    self._start_pressed = True

  def confirm(self, person_investment):
    self._confirm_pressed = True
    self._log_person_investment = int(person_investment)

  def confirm_robot(self, robot_investment):
    self._confirm_pressed_robot = True
    self._log_leader_investment = int(robot_investment)

  def ip(self, ip_string, port_string, ip_string_2, port_string_2, ip_string_3, port_string_3):
    print "IP: " + str(ip_string)
    is_first_connected = False
    is_second_connected = False
    is_third_connected = False
    try:
        self.myPuppet1 = nao.Puppet(ip_string, port_string, True)
        self.emit(self.yes_robot_signal)
    except Exception,e:
        print "\nERROR: Impossible to find the FIRST robot!\n"
        print "Error was: ", e
        self.emit(self.no_robot_signal)
        self._robot_connected=False
    try:
        self.myPuppet2 = nao.Puppet(ip_string_2, port_string_2, True)
        self.emit(self.yes_robot_signal)
    except Exception,e:
        print "\nERROR: Impossible to find the SECOND robot!\n"
        print "Error was: ", e
        self.emit(self.no_robot_signal)
        self._robot_connected=False
    try:
        self.myPuppet3 = nao.Puppet(ip_string_3, port_string_3, True)
        self.emit(self.yes_robot_signal)
    except Exception,e:
        print "\nERROR: Impossible to find the THIRD robot!\n"
        print "Error was: ", e
        self.emit(self.no_robot_signal)
        self._robot_connected=False
    # Both connected
    self._robot_connected=True

  def xml(self, path):
    print("Looking for external files... ")
    if not os.path.isfile(str(path)):
            print("\n# ERROR: I cannot find the XML file. The programm will be stopped!\n")
            self._xml_uploaded = False
            return
    print("Initializing XML Parser... ")
    try:
        self.myParser.LoadFile(str(path))
        self.myParser.parse_experiment_list()
        self._xml_uploaded = True
    except:
        self.emit(self.bad_xml_signal)
        print("\n # ERROR: Impossible to read the XML file! \n")
        self._xml_uploaded = False


  def wake(self, state):
        if state == True:
             self.myPuppet1.wake_up()
             self.myPuppet2.wake_up()
             self.myPuppet3.wake_up()
        else:     
             self.myPuppet1.rest()
             self.myPuppet2.rest()
             self.myPuppet3.rest()

  def face_tracking(self, state):
        self.myPuppet1.enable_face_tracking(state)
        self.myPuppet2.enable_face_tracking(state)
        self.myPuppet3.enable_face_tracking(state)

  def session_info_update(self, info1, info2, info3):
      my_string = str(info1) + "," + str(info2) + "," + str(info3)
      print("SESSION INFO: ", info1, info2, info3)
      self._log_first_line = my_string
      self._session_info_given = True
        
  def stop(self):
    self.stopped = 1

  def __del__(self):
    self.wait()


## Class ExampleApp
#  
# It is a GUI class created in pyQT
# and receive signals from the GUI
#
class ExampleApp(QtGui.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.btnBrowse.clicked.connect(self.browse_folder)  # When the button is pressed execute browse_folder function
        #self.btnStartExperiment.clicked.connect(lambda: self.start_experiment(1))
        self.btnStartExperiment.clicked.connect(self.start_experiment)
        self.btnConnectToNao.clicked.connect(self.connect_pressed)
        self.btnWakeUp.clicked.connect(self.wake_up_pressed)
        self.btnRest.clicked.connect(self.rest_pressed)
        self.btnFaceTrackingEnable.clicked.connect(lambda:  self.face_tracking_pressed(True))
        self.btnFaceTrackingDisable.clicked.connect(lambda:  self.face_tracking_pressed(False))
        self.btnSessionInfoConfirm.clicked.connect(self.session_info_pressed)

        #Buttons investment
        self.pushButton_0.clicked.connect(lambda: self.confirm_pressed(0))
        self.pushButton_1.clicked.connect(lambda: self.confirm_pressed(1))
        self.pushButton_2.clicked.connect(lambda: self.confirm_pressed(2))
        self.pushButton_3.clicked.connect(lambda: self.confirm_pressed(3))
        self.pushButton_4.clicked.connect(lambda: self.confirm_pressed(4))
        self.pushButton_5.clicked.connect(lambda: self.confirm_pressed(5))
        self.pushButton_6.clicked.connect(lambda: self.confirm_pressed(6))
        self.pushButton_7.clicked.connect(lambda: self.confirm_pressed(7))
        self.pushButton_8.clicked.connect(lambda: self.confirm_pressed(8))
        self.pushButton_9.clicked.connect(lambda: self.confirm_pressed(9))
        self.pushButton_10.clicked.connect(lambda: self.confirm_pressed(10))

        #Signal to be sent to Thread
        self.start_signal = SIGNAL("start_signal")
        self.confirm_signal = SIGNAL("confirm_signal")
        self.confirm_signal_robot = SIGNAL("confirm_signal_robot")
        self.xml_path_signal = SIGNAL("xml_path_signal")
        self.ip_signal = SIGNAL("ip_signal")
        self.wake_up_signal = SIGNAL("wake_up_signal")
        self.face_tracking_signal = SIGNAL("face_tracking_signal")
        self.session_info_signal = SIGNAL("session_info_signal")

        self.showMaximized()

    def start_experiment(self):
        self.emit(self.start_signal)
        #self.btnStartExperiment.hide() #hiding the start button

    def confirm_pressed(self, person_investment):
        self.emit(self.confirm_signal, person_investment)
        print "CONFIRM: " + str(person_investment)

    def confirm_pressed_robot(self, robot_investment):
        self.emit(self.confirm_signal_robot, robot_investment)
        print "CONFIRM ROBOT: " + str(robot_investment)

    def connect_pressed(self):
        ip_string = str(self.lineEditNaoIP.text())
        port_string = str(self.lineEditNaoPort.text())
        ip_string_2 = str(self.lineEditNaoIP_2.text())
        port_string_2 = str(self.lineEditNaoPort_2.text())
        ip_string_3 = str(self.lineEditNaoIP_3.text())
        port_string_3 = str(self.lineEditNaoPort_3.text())
        #print "IP: " + ip_string
        self.emit(self.ip_signal, ip_string, port_string, ip_string_2, port_string_2, ip_string_3, port_string_3)

    def face_tracking_pressed(self, state):
        self.emit(self.face_tracking_signal, state)

    def wake_up_pressed(self):
        self.emit(self.wake_up_signal, True)

    def rest_pressed(self):
        self.emit(self.wake_up_signal, False)

    def session_info_pressed(self):
        info1 = str(self.textEditSubjectNumber.toPlainText())
        info2 = str(self.textEditSessionNumber.toPlainText())
        info3 = str(self.textEditOther.toPlainText())
        self.emit(self.session_info_signal, info1, info2, info3)

    def show_start_btn(self, is_visible):
        if is_visible == True:
            self.btnStartExperiment.show()
        elif is_visible == False:        
            self.btnStartExperiment.hide()

    #start_btn, confirm_btn, person_slider, show_slider
    def enable_components_gui(self, start_btn, confirm_btn, confirm_btn_robot):
        if  start_btn == True:
            self.btnStartExperiment.show()
        elif  start_btn == False:        
            self.btnStartExperiment.hide()

        #Enabling the confirm buttons
        self.pushButton_0.setEnabled(confirm_btn)
        self.pushButton_1.setEnabled(confirm_btn)
        self.pushButton_2.setEnabled(confirm_btn)
        self.pushButton_3.setEnabled(confirm_btn)
        self.pushButton_4.setEnabled(confirm_btn)
        self.pushButton_5.setEnabled(confirm_btn)
        self.pushButton_6.setEnabled(confirm_btn)
        self.pushButton_7.setEnabled(confirm_btn)
        self.pushButton_8.setEnabled(confirm_btn)
        self.pushButton_9.setEnabled(confirm_btn)
        self.pushButton_10.setEnabled(confirm_btn)

        if confirm_btn == True:
            #self.pushButton_0.setStyleSheet("background-color: green")
            self.pushButton_0.setStyleSheet("border-style: solid")
            self.pushButton_0.setStyleSheet("border-color: green")
        elif confirm_btn == False:
            #self.pushButton_0.setStyleSheet("background-color: red")
            self.pushButton_0.setStyleSheet("border-style: solid")
            self.pushButton_0.setStyleSheet("border-color: red")


    #total, player_investment, round_total, robot_investment, text_label=""
    def update_gui(self, person_total, player1_total, player2_total, player3_total, text_label=""):
        #Update the total bar
        self.lcdNumberTotal.display(person_total)
        self.lcdNumberTotal1.display(player1_total)
        self.lcdNumberTotal2.display(player2_total)
        self.lcdNumberTotal3.display(player3_total)
        #Update the textEdit label
        self.textEdit.clear() #clear the textedit            
        self.textEdit.append(QtCore.QString(text_label))      


    def browse_folder(self):
        selected_file = QtGui.QFileDialog.getOpenFileName(self, "Select a configuration file", "../etc/xml","XML files(*.xml)")
        if selected_file: # if user didn't pick a directory don't continue
            self.textEditXML.setText(selected_file) # self.listWidget.addItem(selected_file)  # add file to the listWidget
            self.emit(self.xml_path_signal, selected_file)
        else:
            msgBox = QtGui.QMessageBox()
            msgBox.setIcon(QtGui.QMessageBox.Warning)
            msgBox.setWindowTitle("No file selected")
            msgBox.setText("ATTENTION: You did not select any XML file.");
            msgBox.exec_();

    def no_robot_error(self):
            msgBox = QtGui.QMessageBox()
            msgBox.setIcon(QtGui.QMessageBox.Critical)
            msgBox.setWindowTitle("Ops... Connection Error")
            msgBox.setText("ERROR: It was not possible to find the robot. \nFollow these tips and try to connect again. \n \n1- Check if the robot is running correctly. \n2- Check if the wifi router is running properly. \n3- Press the button on the robot chest to verify if the IP address is correct. \n4- Check if another software or GUI is connected to the robot. \n");
            msgBox.exec_();
            self.btnWakeUp.setEnabled(False)
            self.btnRest.setEnabled(False)
            self.btnFaceTrackingEnable.setEnabled(False)
            self.btnFaceTrackingDisable.setEnabled(False)

    def yes_robot_confirmation(self):
            msgBox = QtGui.QMessageBox()
            msgBox.setIcon(QtGui.QMessageBox.Information)
            msgBox.setWindowTitle("Well Done!")
            msgBox.setText("I found the robot, the connection was successfully established!")
            msgBox.exec_();
            self.btnWakeUp.setEnabled(True)
            self.btnRest.setEnabled(True)
            self.btnFaceTrackingEnable.setEnabled(True)
            self.btnFaceTrackingDisable.setEnabled(True)

    def bad_xml_error(self):
            msgBox = QtGui.QMessageBox()
            msgBox.setIcon(QtGui.QMessageBox.Critical)
            msgBox.setWindowTitle("Ops... malformed XML file")
            msgBox.setText("ERROR: It was not possible to read the XML file. \nFollow these tips and try to select again. \n \n1- Verify if you can open correctly the file with a text editor (es. notepad). \n2- Once opened the file, check if for each open bracket <trial> there is a closed bracket </trial>. \n3- Check if the name of the audio files is correct.\n");
            msgBox.exec_();

    def good_xml_confirmation(self):
            msgBox = QtGui.QMessageBox()
            msgBox.setIcon(QtGui.QMessageBox.Information)
            msgBox.setWindowTitle("Very Good!")
            msgBox.setText("I opened the XML file correctly. Be carefull, this does not mean that what you write inside the file is correct...")
            msgBox.exec_();

def main():

    #New instance of QApplication
    app = QtGui.QApplication(sys.argv)  
    form = ExampleApp()

    #Creating the main thread
    thread = WorkerThread()

    #Connecting: form > thread
    thread.connect(form, form.start_signal, thread.start_experiment)
    thread.connect(form, form.xml_path_signal, thread.xml) #sending XML path
    thread.connect(form, form.confirm_signal, thread.confirm)
    thread.connect(form, form.confirm_signal_robot, thread.confirm_robot)
    thread.connect(form, form.ip_signal, thread.ip)
    thread.connect(form, form.wake_up_signal, thread.wake)
    thread.connect(form, form.face_tracking_signal, thread.face_tracking)
    thread.connect(form, form.session_info_signal, thread.session_info_update)

    #Connecting: thread > form
    form.connect(thread, thread.enable_components_gui_signal, form.enable_components_gui)
    form.connect(thread, thread.no_robot_signal, form.no_robot_error)
    form.connect(thread, thread.yes_robot_signal, form.yes_robot_confirmation)
    form.connect(thread, thread.bad_xml_signal, form.bad_xml_error)
    form.connect(thread, thread.good_xml_signal, form.good_xml_confirmation)
    form.connect(thread, thread.update_gui_signal, form.update_gui)
    form.connect(thread, thread.show_start_btn_signal, form.show_start_btn)

    #Starting thread
    thread.start()

    #Show the form and execute the app
    form.show()  
    app.exec_()  



if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  # run the main function





