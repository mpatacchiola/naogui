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
    self.colour_robot_button_signal = SIGNAL("colour_robot_button_signal")

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
    self._log_person_total = 0
    self._log_robot_total = 0
    self._log_person_investment = 0
    self._log_robot_investment = 0
    self._log_player_b_investment = 0

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
                self.myPuppet.say_something("Hello Banker, let's play together.")
                time.sleep(1)
                print "[1] Enablig components"
                self.emit(self.enable_components_gui_signal, False,  True, True) #GUI components
                self.STATE_MACHINE = 2
 

        #STATE-2 Reset variables and Robot talks
        if self.STATE_MACHINE == 2:
            #UPDATE Multiplication values
            self._log_pmf = float(self.myParser._pmf_list[self._log_trial])
            self._log_bmf = float(self.myParser._bmf_list[self._log_trial])
            #RESET all the values at each new cycle
            self._log_person_investment = 0
            self._log_person_investment = 0 
            self._log_robot_investment = 0
            self._log_player_b_investment = 0
            local_string = "Please select a value to invest..."
            #Reset the GUI and enable component
            print "[2] Enabling buttons..." 
            self.emit(self.enable_components_gui_signal, False,  True, True)  #GUI components
            self.emit(self.update_gui_signal, self._log_person_total, self._log_robot_total, local_string)
            print "[2] Starating timer subject and timer robot"
            self.timer.restart() #RESET here the timer 
            self.timer_robot.restart()
            self.timer_robot_deadline = int(self.myParser._time_list[self._log_trial]) #random.randint(1,3)   
            print "[2] Switching to the next state"
            self.STATE_MACHINE = 3 #next state       
            print "[3] Waiting for the subject and robot answer..." #going to state 3

        #STATE-3 First interaction: waiting for the subject investment
        #When the subject choose it update the GUI showing zeros for the robots
        #and the multiplied factor for the human
        if self.STATE_MACHINE == 3:       
            # Wait for a random time between 1 and 3 seconds and then the robot decide
            if self.timer_robot.elapsed() > self.timer_robot_deadline and self._confirm_pressed_robot == False:  
                self._log_robot_investment = int(self.myParser._rinv_list[self._log_trial])
                if(self._log_robot_investment < 0): self._log_robot_investment = 0
                if(self._log_robot_investment > 10): self._log_robot_investment = 10
                self._confirm_pressed_robot = True
                print "[2] Looking to the monitor" 
                #self.myPuppet.enable_face_tracking(False) #disable face tracking             
                self.myPuppet.look_to("HeadPitch", 35.0, SPEED)
                #time.sleep(random.randint(3, 6)) #random sleep
                print "[2] Pointing or not" 
                #Pointing (or not) while looking to the screen
                if self.myParser._pointing_list[self._log_trial] == "True":
                  print "[2] pointing == True"
                  self._log_pointing = "True"
                  self.myPuppet.left_arm_pointing(True, SPEED)
                #If the condition is pointing==FALSE then does not move the arm
                elif self.myParser._pointing_list[self._log_trial] == "False":
                  print "[2] pointing == False"
                  self._log_pointing = "False"
                  self.myPuppet.right_arm_pointing(False, SPEED)
                  self.myPuppet.left_arm_pointing(False, SPEED)
                #Change button colour
                self.emit(self.colour_robot_button_signal, int(self._log_robot_investment), "lightgreen")
                #Reset the arms
                print "[2] Reset the arms"
                self.myPuppet.right_arm_pointing(False, SPEED)
                self.myPuppet.left_arm_pointing(False, SPEED)
            #The robot choose and now will look to the participant because the waiting time elapsed
            if self.timer_robot.elapsed() > (self.timer_robot_waiting + self.timer_robot_deadline) and self._confirm_pressed_robot == True and self._confirm_pressed == False:
                if self.myParser._gaze_list[self._log_trial] == "True":
                    self.myPuppet.look_to("HeadYaw", 60.0, SPEED)
            # The participant decided, record the timer
            if self._confirm_pressed == True and self._participant_decision_taken == False:
                self._log_timer = self.timer.elapsed() #record the time
                self._participant_decision_taken = True
                print "[3] The participant pressed: " + str(self._log_person_investment)
                print "[3] TIME: " + str(self._log_timer)     
                if self.myParser._gaze_list[self._log_trial] == "True":
                    self.myPuppet.look_to("HeadYaw", 0.0, SPEED) 
            # Wait for both robot and participant to decide
            if self._confirm_pressed == True and self._confirm_pressed_robot == True:   #when subject gives the answer
                print "[3] INVESTMENT: " + str(self._log_person_investment)
                print "[3] ROBOT INVESTMENT: " + str(self._log_robot_investment)
                self._log_person_investment = self._log_person_investment
                self._confirm_pressed = False #reset the variable state
                self._confirm_pressed_robot = False
                self._participant_decision_taken = False
                self.emit(self.enable_components_gui_signal, False,  False, False) #GUI components
                local_string = ""
                self.emit(self.update_gui_signal, self._log_person_total, self._log_robot_total, local_string)
                #The person turn is finished, now switching to robot turn
                self.STATE_MACHINE = 5 #next state


        #STATE-5 First interaction: the robot calculates its own investment
        if self.STATE_MACHINE == 5:
            print "[5] First interaction"                         
            #Updating the investment values
            #The investment of the robot is taken from the XML file
            print("[5] The Robot mate returned: " + str(self._log_robot_investment))
            #the other values do not change
            time.sleep(1)

            #Updating the GUI
            local_string = "Player A invested: " + str(self._log_person_investment) + '\n'
            local_string += "Player B invested: " + str(self._log_robot_investment) + '\n' 
            #total, player_investment, round_total, robot_investment, text_label=""
            self.emit(self.update_gui_signal, self._log_person_total, self._log_robot_total, local_string)
            #Looking (or not) the subject
            #if self.myParser._gaze_list[self._log_trial] == "True":
            #  print "[5] looking == True"
            #  self._log_gaze = "True"
            #  self.myPuppet.look_to("HeadPitch", 0, SPEED) #angle(radians) + speed
            #  time.sleep(0.2)
            #  #self.myPuppet.enable_face_tracking(True) #enables face tracking
            #elif self.myParser._gaze_list[self._log_trial] == "False":
            #  print "[5] looking == False"
            #  self._log_gaze = "False"
            #  #self.myPuppet.enable_face_tracking(False) #disable face tracking
            #  self.myPuppet.look_to("HeadPitch", 35.0, SPEED) #angle(radians) + speed
            #Change state
            time.sleep(1.0) #(reduced) Long sleep to enable the participant to uderstand what's going on
            self.STATE_MACHINE = 6 #next state

        #STATE-6 First interaction: the robot talks and says the investment of the person and its own
        if self.STATE_MACHINE == 6:
            print "[6] Looking to the monitor" 
            self.myPuppet.enable_face_tracking(False) #disable face tracking           
            self.myPuppet.look_to("HeadPitch", 35.0, SPEED)
            time.sleep(1.5)
            #Change button colour
            self.emit(self.colour_robot_button_signal, int(self._log_robot_investment), "")
            if self.myParser._gaze_list[self._log_trial] == "True":
                print "[6] Enabling again face tracking"
                self.myPuppet.look_to("HeadPitch", 0, SPEED)
                time.sleep(0.5)
                #self.myPuppet.enable_face_tracking(True) #enables face tracking
            print "[6] The robot says the investments..."
            #Take a sentence from the XML, XXX substring is replaced 
            #with the multiplied value given from the person to the robot. 
            self._sentence = self.myParser._word1_list[self._log_trial]
            self._sentence = str(self._sentence) #convert to string
            #If the sentence in the XML file is equal to "." or "-" or ""
            #then it does not say anything...
            if(self._sentence != "." and self._sentence != "" and self._sentence != "-"):
                #Check if XXX is present and replace it with the
                #multiplied person investment value...
                has_substring = self._sentence.find("XXX")
                if(has_substring != -1):
                    print "[6] Found the substring 'XXX' at location: " + str(has_substring)
                    self._sentence = self._sentence.replace("XXX", str(int(self._log_person_investment)))
                has_substring = self._sentence.find("YYY")
                if(has_substring != -1):
                    print "[6] Found the substring 'YYY' at location: " + str(has_substring)
                    self._sentence = self._sentence.replace("YYY", str(int(self._log_robot_investment)))
                print "[6] Saying: '" + self._sentence + "'"
                #It says the sentence generated above only if
                #the valued returned by the person is different from zero.
                self.myPuppet.say_something(str(self._sentence))
            else:
                print "[6] Saying Nothing because the sentence in the XML file is '" + str(self._sentence) + "'" 
            if self.myParser._gaze_list[self._log_trial] == "True":
                print "[6] looking to the monitor..."
                #The robot looks to the monitor (thinking what to do)
                #self.myPuppet.enable_face_tracking(False) #disable face tracking
                self.myPuppet.look_to("HeadPitch", 35.0, SPEED) #angle(radians) + speed
            self.STATE_MACHINE = 7 #next state

        #STATE-7  The Banker robot gives a reward
        if self.STATE_MACHINE == 7:
            if self.myParser._gaze2_list[self._log_trial] == "True":
                print "[7] Looking to the screen Robot 2"
                self.myPuppet_2.look_to("HeadPitch", 35.0, SPEED)
                time.sleep(0.5)
                #self.myPuppet_2.enable_face_tracking(False) #enables face tracking
            print "[7] The banker is thinking (it takes time)..."            
            time.sleep(random.randint(2, 4))
            print "[7] Waiting for Banker Robot reward..." 
            #Updating the multiplication values
            self._log_player_b_investment = int(self.myParser._binv_list[self._log_trial]) # Player B return for the robot
            if(self._log_player_b_investment<0): self._log_player_b_investment = 0 #equal to zero if negative
            # Pointing or not
            if self.myParser._pointing2_list[self._log_trial] == "True":
                  print "[7] pointing == True"
                  #Sort a random value and use it to move the arm
                  random_value = random.random()              
                  if (random_value >= 0.0 and random_value <= 0.5):
                      self.myPuppet_2.left_arm_pointing(True, SPEED)
                  #right arm movement
                  elif (random_value > 0.5 and random_value <= 1.0):
                       self.myPuppet_2.right_arm_pointing(True, SPEED)
            #Reset the arms (if they have been moved)
            print "[7] pointing == False"
            self.myPuppet_2.right_arm_pointing(False, SPEED)
            self.myPuppet_2.left_arm_pointing(False, SPEED)
            #Update the TOTAL
            print "[7] The Banker invested: " + str(self._log_player_b_investment)
            #The total of the person in the single round is given from
            #the amount not invested + the money that player b gave back (half of them)
            self._log_person_total += (10-self._log_person_investment) + int(self._log_person_investment * 3.0 * float(self.myParser._bmf_list[self._log_trial]))
            self._log_robot_total += (10-self._log_robot_investment) + int(self._log_player_b_investment) # TODO: take this value from CSV
            local_string = "Player A: " + str(self._log_person_investment) + " and Player B: " + str(self._log_robot_investment) + '\n'
            local_string += "The banker received: " + str(int(self._log_person_investment * 3.0)) + " from Player A"
            local_string += " and received " + str(int(self._log_robot_investment * 3.0)) + " from Player B" + '\n' 
            local_string += "The banker returned to Player A: " + str(int(self._log_person_investment * 3.0 * float(self.myParser._bmf_list[self._log_trial]))) + '\n'
            local_string += "The banker returned to Player B: " + str(int(self._log_player_b_investment)) + '\n' # TODO: change this variable and take it from XML
            local_string += "Please press START to begin a new round..." + '\n' 
            #total, pinv, round_tot, rinv, rslider, text
            self.emit(self.update_gui_signal, self._log_person_total, self._log_robot_total, local_string)
            if self.myParser._gaze2_list[self._log_trial] == "True":
                print "[7] Enabling face tracking Robot 2"
                self.myPuppet_2.look_to("HeadPitch", 0, SPEED)
                time.sleep(0.5)
                #self.myPuppet_2.enable_face_tracking(True) #enables face tracking
            print "[7] Switch to the next state"
            self.STATE_MACHINE = 8 #next state

        #STATE-8 Banker talks and says the reward to the players
        if self.STATE_MACHINE == 8:

            print "[8] Banker looks to participant"
            self.myPuppet_2.look_to("HeadYaw", -20.0, SPEED)
            time.sleep(0.5)

            print "[8] The Banker says to player A what returned"
            #Take a sentence from the XML
            self._sentence = self.myParser._word2_list[self._log_trial]
            self._sentence = str(self._sentence) #convert to string
            #If the sentence in the XML file is equal to "." or "-" or "" it does not say anything.
            if(self._sentence != "." and self._sentence != "" and self._sentence != "-"):
                #Check if XXX is present and replace it 
                has_substring = self._sentence.find("XXX")
                if(has_substring != -1):
                    print "[8] Found the substring 'XXX' at location: " + str(has_substring)
                    self._sentence = self._sentence.replace("XXX", str(self._log_person_investment))
                has_substring = self._sentence.find("YYY")
                if(has_substring != -1):
                    print "[8] Found the substring 'YYY' at location: " + str(has_substring)
                    self._sentence = self._sentence.replace("YYY", str(int(self._log_person_investment * 3.0 * float(self.myParser._bmf_list[self._log_trial]))))
                self.myPuppet_2.say_something(str(self._sentence))
            else:
                print "[8] Saying Nothing because the sentence in the XML file is '" + str(self._sentence) + "'"

            #Sleep between the two sentences
            #time.sleep(3.0)

            print "[8] Banker looks to participant"
            self.myPuppet_2.look_to("HeadYaw", +20.0, SPEED)
            time.sleep(0.5)

            print "[8] The banker says to player B what returned"
            #Take a sentence from the XML
            self._sentence = self.myParser._word3_list[self._log_trial]
            self._sentence = str(self._sentence) #convert to string
            #If the sentence in the XML file is equal to "." or "-" or "" it does not say anything.
            if(self._sentence != "." and self._sentence != "" and self._sentence != "-"):
                #Check if XXX is present and replace it 
                has_substring = self._sentence.find("XXX")
                if(has_substring != -1):
                    print "[8] Found the substring 'XXX' at location: " + str(has_substring)
                    self._sentence = self._sentence.replace("XXX", str(self._log_person_investment))
                has_substring = self._sentence.find("YYY")
                if(has_substring != -1):
                    print "[8] Found the substring 'YYY' at location: " + str(has_substring)
                    self._sentence = self._sentence.replace("YYY", str(int(self._log_person_investment * 3.0 * float(self.myParser._bmf_list[self._log_trial]))))
                self.myPuppet_2.say_something(str(self._sentence))
            else:
                print "[8] Saying Nothing because the sentence in the XML file is '" + str(self._sentence) + "'"

            print "[8] Banker looks to the monitor"
            self.myPuppet_2.look_to("HeadYaw", 0.0, SPEED)
            self.myPuppet_2.look_to("HeadPitch", 35.0, SPEED) #angle(radians) + speed
            time.sleep(0.5)

            self.STATE_MACHINE = 9 #next state

        #STATE-9 Saving in the logbook
        if self.STATE_MACHINE == 9:
            print "[9] Saving the trial in the logbook"
            self.logger.AddLine(self._log_trial+1, self._log_person_investment, self._log_robot_investment, self._log_player_b_investment, 
                                self._log_pmf, self._log_bmf, self._log_person_total, self._log_gaze, self._log_pointing, self._log_timer)
            print ("[9] trial, person_investment, robot_investment, person_investment_second, log_robot_investment_second, player_b_investment, pmf, bmf, person_total, gaze, pointing, timer, timer_second")
            print ("[9] " + str(self._log_trial+1) + "," + str(self._log_person_investment) + "," + str(self._log_robot_investment) + 
                   "," + "," +  str(self._log_pmf) + "," + str(self._log_bmf) + "," + str(self._log_person_total) + "," + str(self._log_gaze) + 
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
            local_string = "Player A score is: " + str(self._log_person_total) + '\n'
            local_string += "Player B score is: " + str(self._log_robot_total) + '\n'
            local_string += "The game is finished. Thank you..."
            self.myPuppet.say_something("Thank you, It was nice to play with you.")
            #total, player_investment, round_total, robot_investment, text_label=""
            self.emit(self.update_gui_signal, 0, 0, local_string) 
            self.emit(self.enable_components_gui_signal, False, False, False) #GUI components disabled
            time.sleep(5)


  def start_experiment(self):
    self._start_pressed = True

  def confirm(self, person_investment):
    self._confirm_pressed = True
    self._log_person_investment = int(person_investment)

  def confirm_robot(self, robot_investment):
    self._confirm_pressed_robot = True
    self._log_robot_investment = int(robot_investment)

  def ip(self, ip_string, port_string, ip_string_2, port_string_2):
    print "IP: " + str(ip_string)
    is_first_connected = False
    is_second_connected = False
    try:
        self.myPuppet = nao.Puppet(ip_string, port_string, True)
        self.emit(self.yes_robot_signal)
    except Exception,e:
        print "\nERROR: Impossible to find the FIRST robot!\n"
        print "Error was: ", e
        self.emit(self.no_robot_signal)
        self._robot_connected=False
    try:
        self.myPuppet_2 = nao.Puppet(ip_string_2, port_string_2, True)
        self.emit(self.yes_robot_signal)
    except Exception,e:
        print "\nERROR: Impossible to find the SECOND robot!\n"
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
             self.myPuppet.wake_up()
             self.myPuppet_2.wake_up()
        else:     
             self.myPuppet.rest()
             self.myPuppet_2.rest()

  def face_tracking(self, state):
        self.myPuppet.enable_face_tracking(state)
        self.myPuppet_2.enable_face_tracking(state)


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

        #Buttons investment robot
        self.pushButton_0r.clicked.connect(lambda: self.confirm_pressed_robot(0))
        self.pushButton_1r.clicked.connect(lambda: self.confirm_pressed_robot(1))
        self.pushButton_2r.clicked.connect(lambda: self.confirm_pressed_robot(2))
        self.pushButton_3r.clicked.connect(lambda: self.confirm_pressed_robot(3))
        self.pushButton_4r.clicked.connect(lambda: self.confirm_pressed_robot(4))
        self.pushButton_5r.clicked.connect(lambda: self.confirm_pressed_robot(5))
        self.pushButton_6r.clicked.connect(lambda: self.confirm_pressed_robot(6))
        self.pushButton_7r.clicked.connect(lambda: self.confirm_pressed_robot(7))
        self.pushButton_8r.clicked.connect(lambda: self.confirm_pressed_robot(8))
        self.pushButton_9r.clicked.connect(lambda: self.confirm_pressed_robot(9))
        self.pushButton_10r.clicked.connect(lambda: self.confirm_pressed_robot(10))


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
        #self.pushButton_0r.setStyleSheet("background-color: red") #TODO: fix this line
        self.emit(self.confirm_signal_robot, robot_investment)
        print "CONFIRM ROBOT: " + str(robot_investment)

    def connect_pressed(self):
        ip_string = str(self.lineEditNaoIP.text())
        port_string = str(self.lineEditNaoPort.text())
        ip_string_2 = str(self.lineEditNaoIP_2.text())
        port_string_2 = str(self.lineEditNaoPort_2.text())
        #print "IP: " + ip_string
        self.emit(self.ip_signal, ip_string, port_string, ip_string_2, port_string_2)

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

        #Enabling the confirm buttons for robot
        self.pushButton_0r.setEnabled(confirm_btn_robot)
        self.pushButton_1r.setEnabled(confirm_btn_robot)
        self.pushButton_2r.setEnabled(confirm_btn_robot)
        self.pushButton_3r.setEnabled(confirm_btn_robot)
        self.pushButton_4r.setEnabled(confirm_btn_robot)
        self.pushButton_5r.setEnabled(confirm_btn_robot)
        self.pushButton_6r.setEnabled(confirm_btn_robot)
        self.pushButton_7r.setEnabled(confirm_btn_robot)
        self.pushButton_8r.setEnabled(confirm_btn_robot)
        self.pushButton_9r.setEnabled(confirm_btn_robot)
        self.pushButton_10r.setEnabled(confirm_btn_robot)

        if confirm_btn == True:
            #self.pushButton_0.setStyleSheet("background-color: green")
            self.pushButton_0.setStyleSheet("border-style: solid")
            self.pushButton_0.setStyleSheet("border-color: green")
        elif confirm_btn == False:
            #self.pushButton_0.setStyleSheet("background-color: red")
            self.pushButton_0.setStyleSheet("border-style: solid")
            self.pushButton_0.setStyleSheet("border-color: red")


    #total, player_investment, round_total, robot_investment, text_label=""
    def update_gui(self, person_total, robot_total, text_label=""):
        #Update the total bar
        self.lcdNumberTotal.display(int(person_total))
        self.lcdNumberTotalRobot.display(int(robot_total))  
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

    def colour_robot_button(self, button_id, colour):
        if button_id == 0:
            self.pushButton_0r.setStyleSheet("background-color: " + str(colour)) #TODO: fix this line
        elif button_id == 1:
            self.pushButton_1r.setStyleSheet("background-color: " + str(colour)) #TODO: fix this line
        elif button_id == 2:
            self.pushButton_2r.setStyleSheet("background-color: " + str(colour)) #TODO: fix this line
        elif button_id == 3:
            self.pushButton_3r.setStyleSheet("background-color: " + str(colour)) #TODO: fix this line
        elif button_id == 4:
            print(str(self.pushButton_4r.palette().color(1)))
            self.pushButton_4r.setStyleSheet("background-color: " + str(colour)) #TODO: fix this line
        elif button_id == 5:
            self.pushButton_5r.setStyleSheet("background-color: " + str(colour)) #TODO: fix this line
        elif button_id == 6:
            self.pushButton_6r.setStyleSheet("background-color: " + str(colour)) #TODO: fix this line
        elif button_id == 7:
            self.pushButton_7r.setStyleSheet("background-color: " + str(colour)) #TODO: fix this line
        elif button_id == 8:
            self.pushButton_8r.setStyleSheet("background-color: " + str(colour)) #TODO: fix this line
        elif button_id == 9:
            self.pushButton_9r.setStyleSheet("background-color: " + str(colour)) #TODO: fix this line
        elif button_id == 10:
            self.pushButton_10r.setStyleSheet("background-color: " + str(colour)) #TODO: fix this line

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
    form.connect(thread, thread.colour_robot_button_signal, form.colour_robot_button)

    #Starting thread
    thread.start()

    #Show the form and execute the app
    form.show()  
    app.exec_()  



if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  # run the main function





