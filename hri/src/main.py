#!/usr/bin/env python

## @package NAO
#
#Massimiliano Patacchiola, Plymouth University 2016
#
# Scree resolution 1920x1080
# It is necessary to have pyQt4 installed
# To generate python code from the .ui file: pyuic4 mainwindow.ui -o design.py
#

# Libraries for Qt
from PyQt4 import QtGui  # Import the PyQt4 module we'll need
from PyQt4.QtCore import QElapsedTimer
from PyQt4.QtCore import QThread
from PyQt4.QtCore import SIGNAL

import sys  
import os
import time
import math

#python -m pip install pyaudio
#sudo apt-get install python-pyaudio python3-pyaudio
import subprocess

#Importing my custom libraries
sys.path.insert(1, '../include')
sys.path.insert(1, "../include/pynaoqi-python2.7-2.1.3.3-linux64") #import this module for the nao.py module
import design
import parser
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
    self.disable_signal = SIGNAL("disable_signal")
    self.enable_signal = SIGNAL("enable_signal")
    self.no_robot_signal = SIGNAL("no_robot_signal")
    self.yes_robot_signal = SIGNAL("yes_robot_signal")
    self.bad_xml_signal = SIGNAL("bad_xml_signal")
    self.good_xml_signal = SIGNAL("good_xml_signal")
    self.update_gui_signal = SIGNAL("update_gui_signal")
    self.show_start_btn_signal = SIGNAL("show_start_btn_signal")

    #Misc variables
    self.myParser = parser.Parser()
    self.timer = QElapsedTimer()
    self.STATE_MACHINE = 0

    #Status variables
    self._robot_connected = False
    self._xml_uploaded = False
    self._start_pressed = False
    self._confirm_pressed = False

    #sub state of state 1
    self.SUB_STATE = 0

    #Logbook variables
    self._log_timer = 0
    self._log_trial = 0
    self._log_round = 10
    self._log_total = 0
    self._log_player_investment = 0
    self._log_person_investment = 0   
    self._log_robot_investment = 0
    self._log_multiplied_person_investment = 0

    self._log_pmult = 0
    self._log_rmult = 0
    self._log_gaze = False
    self._log_pointing = False
    self._log_mp3 = ""


  ## Main function of the Thread
  # 
  # It runs the State Machine
  #
  def run(self):
    #Init the State machine 
    #self.emit(self.enable_signal) #GUI enabled
    self.emit(self.enable_components_gui_signal, True,  False, False, False) #GUI components
    self.timer.start()
    self.STATE_MACHINE = 0

    while True:

        time.sleep(0.05) #50 msec sleep to evitate block

        #STATE-0 init
        if self.STATE_MACHINE == 0:
            if self._robot_connected==True and self._xml_uploaded==True and self._start_pressed==True:
                #When there are zero pretrial then jump to state 2
                #If there are more than zero pretrial go to state 1
                if self.myParser._pretrial_repeat == 0:
                    self.STATE_MACHINE = 2
                elif self.myParser._pretrial_repeat > 0:
                    self.STATE_MACHINE = 1 #switching to next state
                self.SUB_STATE = 0 #substate of state machine 1 set to zero
                #self.emit(self.disable_signal) #GUI disabled                
                self.logger = logbook.Logbook() #Logbook Init
                self.emit(self.show_start_btn_signal, False)
                self._start_pressed = False
            else:
                #self.emit(self.disable_signal) #GUI disabled
                current_time = time.strftime("%H:%M:%S", time.gmtime())
                status = "robot_coonnected = " + str(self._robot_connected) + "\n" + "xml_uploaded = " + str(self._xml_uploaded) + "\n" + "start_pressed = " + str(self._start_pressed) + "\n"
                print "[0] " + current_time + " Waiting... \n" + status
                time.sleep(3)

        #STATE-1 pretraining phase, subject play with researcher
        if self.STATE_MACHINE == 1:

            #SUB_STATE == 0
                #Init all the variables
                #self._pretrial_is_person_turn == True
            if self.SUB_STATE == 0:
                self._pretrial_counter = 0
                self._confirm_pressed = False
                self._start_pressed = False
                self.SUB_STATE = 1
                #self.emit(self.enable_signal) #GUI enabled
                print "[1][0] Enablig components"
                self.emit(self.enable_components_gui_signal, False,  True, True, False) #GUI components
                
            #SUB_STATE == 1
                #Waiting person answer CONFIRM
                #Print the result when person reply
            if self.SUB_STATE == 1:
                if self._confirm_pressed == True:
                    print "[1][1] Person Confirm Pressed"
                    self._confirm_pressed = False
                    self._log_round = float(self._log_round) - float(self._log_person_investment)
                    self._log_multiplied_person_investment = self._log_person_investment * float(self.myParser._pretrial_pmf)
                    self._log_player_investment = self._log_multiplied_person_investment
                    self._log_robot_investment = 0
                    person_slider_value = self._log_person_investment
                    #total, player_investment, round_total, your_investment, robot_investment, robot_slider_value
                    self.emit(self.update_gui_signal, self._log_total, self._log_player_investment, self._log_round, self._log_person_investment, self._log_robot_investment, person_slider_value, 15)
                    self.emit(self.enable_components_gui_signal, False,  True, False, True) #GUI components
                    print "[1][1] Waiting for researcher feedback..." 
                    self.SUB_STATE = 2

            #SUB_STATE == 2
                #Waiting researcher answer
                #Print result when researcher answer
                #Switch to SUBSTATE 3
            if self.SUB_STATE == 2:
                if self._confirm_pressed == True:
                    print "[1][2] Researcher Confirm Pressed"
                    self._confirm_pressed = False
                    #Updating the investment values
                    #TODO understand if in the pretrial mode the robot_investment should be multiplied or not           
                    #self._log_robot_investment = float(self._log_person_investment) * float(self.myParser._pretrial_rmf) #TODO this must be active or not?
                    self._log_total = self._log_total + self._log_round + self._log_robot_investment
                    self._log_player_investment = self._log_robot_investment
                    person_slider_value = self._log_person_investment
                    robot_slider_value = self._log_robot_investment
                    self.emit(self.update_gui_signal, self._log_total, self._log_player_investment, self._log_round, self._log_person_investment, self._log_robot_investment, person_slider_value, robot_slider_value)
                    #TODO check if this pause is ok or not
                    #self.emit(self.disable_signal) #GUI disabled
                    self.emit(self.enable_components_gui_signal, False,  False, False, False) #GUI components
                    time.sleep(5)
                    self.emit(self.enable_components_gui_signal, False,  True, True, False) #GUI components
                    #self.emit(self.enable_signal) #GUI enabled                                                     
                    self.SUB_STATE = 3

            #SUB_STATE == 3
                #Check if pretrial is finished:
                #If pretrial is not finished jump to SUB_STATE 1
                #if Pretrial is finished show the START button and jump to SUB_STATE 4
            if self.SUB_STATE == 3:
                if int(self._pretrial_counter) == int(self.myParser._pretrial_repeat):
                    #Pretrial finished
                    print "[1][3] Pretrial finished, starting the experiment..."
                    self.emit(self.show_start_btn_signal, True) #show the button START
                    #self.emit(self.disable_signal) #GUI disabled
                    self.emit(self.enable_components_gui_signal, True,  False, False, False) #GUI components
                    self.SUB_STATE = 4
                else:
                    self._pretrial_counter = self._pretrial_counter + 1
                    #Updating the investment values (RESET)
                    self._log_round = 10
                    self._log_person_investment = 0
                    self._log_robot_investment = 0
                    self._log_player_investment = 0
                    #total, player_investment, round_total, your_investment, robot_investment, robot_slider_value
                    self.emit(self.update_gui_signal, self._log_total, self._log_player_investment, self._log_round, self._log_person_investment, self._log_robot_investment, 5, 15)
                    print "[1][3] New Round: " + str(self._pretrial_counter) + " / " + str(self.myParser._pretrial_repeat)
                    self.SUB_STATE = 1


            #SUB_STATE == 4
                #When the START button is pressed go to STATE_MACHINE=2 
            if self.SUB_STATE == 4:
                if self._start_pressed == True: 
                    self._start_pressed = False
                    #Updating the investment values (RESET)
                    self._log_round = 10
                    self._log_person_investment = 0
                    self._log_robot_investment = 0
                    self._log_player_investment = 0
                    self._log_total = 0
                    #total, player_investment, round_total, your_investment, robot_investment, robot_slider_value
                    self.emit(self.update_gui_signal, self._log_total, self._log_player_investment, self._log_round, self._log_person_investment, self._log_robot_investment, 5, 15)
                    #self.emit(self.show_start_btn_signal, False)
                    self.emit(self.enable_components_gui_signal, False,  False, False, False) #GUI components
                    self.STATE_MACHINE = 2
                    time.sleep(5) #small pause before starting
            
 
        #STATE-2 robot look or not and talk
        if self.STATE_MACHINE == 2:
            #Updating the multiplication values
            self._log_pmult = float(self.myParser._pmf_list[self._log_trial])
            self._log_rmult = float(self.myParser._rmf_list[self._log_trial])
            #Updating the investment values (RESET)
            self._log_round = 10
            self._log_person_investment = 0
            self._log_robot_investment = 0
            self._log_player_investment = 0
            #total, player_investment, round_total, your_investment, robot_investment, robot_slider_value
            self.emit(self.update_gui_signal, self._log_total, self._log_player_investment, self._log_round, self._log_person_investment, self._log_robot_investment, 5, 15)     
            print "[2] Robot Talking + Looking/Non-Looking"            
            #self.myPuppet.look_to(1, SPEED)
            #time.sleep(2)
            if self.myParser._gaze_list[self._log_trial] == "True":
              print "[2] looking == True"
              self._log_gaze = "True"
              self.myPuppet.look_to(0, SPEED) #angle(radians) + speed
            elif self.myParser._gaze_list[self._log_trial] == "False":
              print "[2] looking == False"
              self._log_gaze = "False"
              self.myPuppet.look_to(1, SPEED) #angle(radians) + speed

            print "[2] bla bla bla ..."
            self._log_mp3 = self.myParser._mp3_list[self._log_trial]
            mp3_path = "../share/mp3/" + self._log_mp3
            subprocess.Popen(["play","-q", mp3_path])
            time.sleep(4) #sleep as long as the mp3 file
            #when mp3 file finish          
            self.STATE_MACHINE = 3 #next state
            #The robot look the screen
            self.myPuppet.look_to(1, SPEED) #angle(radians) + speed
            time.sleep(1)
            #Reset the timer and switch to the next state
            self.timer.restart() #RESET here the timer
            print "[3] Waiting for the subject answer..." #going to state 3

        #STATE-3 waiting for the subject investment
        if self.STATE_MACHINE == 3:                      
            #self.emit(self.enable_signal) #GUI enbled
            self.emit(self.enable_components_gui_signal, False,  True, True, False)  #GUI components                    
            if self._confirm_pressed == True:   #when subject give the answer
                self._log_timer = self.timer.elapsed() #record the time
                print "[3] TIME: " + str(self._log_timer)
                print "[3] INVESTMENT: " + str(self._log_person_investment)
                self._confirm_pressed = False #reset the variable state
                #self.emit(self.disable_signal) #GUI disabled
                self.emit(self.enable_components_gui_signal, False,  False, False, True) #GUI components
                #Updating the investment values
                self._log_round = float(self._log_round) - float(self._log_person_investment)
                self._log_multiplied_person_investment = self._log_person_investment * float(self._log_pmult)
                self._log_player_investment = self._log_multiplied_person_investment
                self._log_robot_investment = 0
                person_slider_value = self._log_person_investment
                #total, player_investment, round_total, your_investment, robot_investment
                self.emit(self.update_gui_signal, self._log_total, self._log_player_investment, self._log_round, self._log_person_investment, self._log_robot_investment, person_slider_value, 15)
                self.STATE_MACHINE = 4 #next state
                time.sleep(1) #Sleep to evitate fast movements of the robot just after the answer

        #STATE-4 Pointing or not and gives the reward
        if self.STATE_MACHINE == 4:
            print "[4] Pointing/Non-Pointing"                         
            if self.myParser._gaze_list[self._log_trial] == "True":
              print "[2] looking == True"
              self._log_gaze = "True"
              self.myPuppet.look_to(0, SPEED) #angle(radians) + speed
            elif self.myParser._gaze_list[self._log_trial] == "False":
              print "[2] looking == False"
              self._log_gaze = "False"
              self.myPuppet.look_to(1, SPEED) #angle(radians) + speed

            time.sleep(1)

            if self.myParser._pointing_list[self._log_trial] == "True":
              print "[4] pointing == True"
              self._log_pointing = "True"
              self.myPuppet.right_arm_pointing(True, SPEED)
            elif self.myParser._pointing_list[self._log_trial] == "False":
              print "[4] pointing == False"
              self._log_pointing = "False"
              self.myPuppet.right_arm_pointing(False, SPEED)

            time.sleep(0.5) 

            #Updating the investment values           
            self._log_robot_investment = float(self._log_person_investment) * float(self._log_rmult)
            #check if nasty orn not and floor or ceil the number
            if self.myParser._nasty_list[self._log_trial] == "True":
                 self._log_robot_investment = math.floor(self._log_robot_investment)
            elif self.myParser._nasty_list[self._log_trial] == "False":
                 self._log_robot_investment = math.ceil(self._log_robot_investment)
            self._log_total = self._log_total + self._log_round + self._log_robot_investment
            self._log_player_investment = self._log_robot_investment
            person_slider_value = self._log_person_investment
            robot_slider_value = self._log_robot_investment
            self.emit(self.update_gui_signal, self._log_total, self._log_player_investment, self._log_round, self._log_person_investment, self._log_robot_investment, person_slider_value, robot_slider_value)
            time.sleep(1)
            self.myPuppet.right_arm_pointing(False, SPEED) #reset the arm position
            time.sleep(2)
            self.STATE_MACHINE = 5 #next state        

        #STATE-5 Saving in the logbook
        if self.STATE_MACHINE == 5:
            print "[5] Saving the trial in the logbook"
            self.logger.AddLine(self._log_trial+1, self._log_person_investment, self._log_robot_investment, self._log_pmult, self._log_rmult, self._log_total, self._log_gaze, self._log_pointing, self._log_timer, self._log_mp3)
            print "[3] " + str(self._log_trial+1) + "," + str(self._log_person_investment) + "," + str(self._log_robot_investment) + "," + str(self._log_pmult) + "," + str(self._log_rmult) + "," + str(self._log_total) + "," + str(self._log_gaze) + "," + str(self._log_pointing) + "," + str(self._log_timer)+ "," + str(self._log_mp3)

            time.sleep(1)

            if self._log_trial+1 != self.myParser._size:
                self.STATE_MACHINE = 2 #cycling to state 2
                self.emit(self.enable_components_gui_signal, False,  False, False, False) #GUI components
                self._log_trial = self._log_trial + 1
            elif self._log_trial+1 == self.myParser._size:
                self.STATE_MACHINE = 6 #experiment finished               

        #STATE-6 Final state is called to shutdown the robot
        if self.STATE_MACHINE == 6:
            print "[6] The experiment is finished"
            self._xml_uploaded = False #reset status variable
            self._start_pressed = False
            self._log_trial = 0
            self.STATE_MACHINE = 0 #cycling to state 0
            #Updating the investment values (RESET)
            self._log_round = 10
            self._log_person_investment = 0
            self._log_robot_investment = 0
            self._log_player_investment = 0
            #total, player_investment, round_total, your_investment, robot_investment, robot_slider_value
            self.emit(self.update_gui_signal, self._log_total, self._log_player_investment, self._log_round, self._log_person_investment, self._log_robot_investment, 5, 15) 
            self.emit(self.enable_components_gui_signal, False,  False, False, False) #GUI components
            time.sleep(5)


  def start_experiment(self):
    self._start_pressed = True

  def confirm(self, person_investment, robot_investment):
    self._confirm_pressed = True
    self._log_person_investment = float(person_investment)
    self._log_robot_investment = float(robot_investment)

  def ip(self, ip_string, port_string):
    print "IP: " + str(ip_string) 

    try:
        self.myPuppet = nao.Puppet(ip_string, port_string, True)
        self.emit(self.yes_robot_signal)
        self._robot_connected=True
    except Exception,e:
        print "\nERROR: Impossible to find the robot!\n"
        print "Error was: ", e
        self.emit(self.no_robot_signal)
        self._robot_connected=False

  def xml(self, path):
    print("Looking for external files... ")
    if not os.path.isfile(str(path)):
            print("\nERROR: I cannot find the XML file. The programm will be stopped!\n")
            self._xml_uploaded = False
            return
    print("Initializing XML Parser... ")
    try:
        self.myParser.LoadFile(str(path))
        self.myParser.parse_experiment_list()
        self.myParser.parse_pretrial_list()
        file_existance = self.myParser.check_file_existence("../share/mp3/")
        if file_existance == True:
            self.emit(self.good_xml_signal)
            self._xml_uploaded = True
        elif file_existance == False:
            self.emit(self.bad_xml_signal)
            print("\n ######## ERROR: Some audio files do not exist. ######## \n")
            self._xml_uploaded = False 
    except:
        self.emit(self.bad_xml_signal)
        print("\n ####### ERROR: Impossible to read the XML file! ########\n")
        self._xml_uploaded = False


  def wake(self, state):
        if state == True:
             self.myPuppet.wake_up()
        else:     
             self.myPuppet.rest()

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
        self.btnConfirm.clicked.connect(self.confirm_pressed)
        self.btnConnectToNao.clicked.connect(self.connect_pressed)
        self.btnWakeUp.clicked.connect(self.wake_up_pressed)
        self.btnRest.clicked.connect(self.rest_pressed)

        #Signal to be sent to Thread
        self.start_signal = SIGNAL("start_signal")
        self.confirm_signal = SIGNAL("confirm_signal")
        self.xml_path_signal = SIGNAL("xml_path_signal")
        self.ip_signal = SIGNAL("ip_signal")
        self.wake_up_signal = SIGNAL("wake_up_signal")

        self.showMaximized()

    def start_experiment(self):
        self.emit(self.start_signal)
        #self.btnStartExperiment.hide() #hiding the start button

    def confirm_pressed(self):
        self.emit(self.confirm_signal, self.horizontalSlider.sliderPosition(), self.horizontalSliderRobot.sliderPosition())

    def connect_pressed(self):
        ip_string = str(self.lineEditNaoIP.text())
        port_string = str(self.lineEditNaoPort.text())
        #print "IP: " + ip_string
        self.emit(self.ip_signal, ip_string, port_string)

    def wake_up_pressed(self):
        self.emit(self.wake_up_signal, True)

    def rest_pressed(self):
        self.emit(self.wake_up_signal, False)

    def show_start_btn(self, is_visible):
        if is_visible == True:
            self.btnStartExperiment.show()
        elif is_visible == False:        
            self.btnStartExperiment.hide()

    def enable_components_gui(self, start_btn, confirm_btn, person_slider, robot_slider):
        if  start_btn == True:
            self.btnStartExperiment.show()
        elif  start_btn == False:        
            self.btnStartExperiment.hide()
        self.btnConfirm.setEnabled(confirm_btn)
        self.horizontalSlider.setEnabled(person_slider)
        self.horizontalSliderRobot.setEnabled(robot_slider)

    def disable_gui(self):
        self.horizontalSlider.setEnabled(False)
        self.btnConfirm.setEnabled(False)
        #self.horizontalSlider.setValue(5)
        #self.horizontalSliderRobot.setValue(15)
        self.horizontalSliderRobot.setEnabled(True)        

    def enable_gui(self):
        self.horizontalSlider.setEnabled(True)
        self.btnConfirm.setEnabled(True)
        self.horizontalSliderRobot.setEnabled(True)

    def update_gui(self, total, player_investment, round_total, your_investment, robot_investment, person_slider_value, robot_slider_value):
        self.lcdNumberTotal.display(float(total))
        self.lcdNumberPlayerInvestment.display(float(player_investment))
        self.lcdNumberRound.display(float(round_total))
        self.lcdNumberYourInvestment.display(float(your_investment))
        self.lcdNumberRobotInvestment.display(float(robot_investment))
        self.horizontalSlider.setValue(person_slider_value)
        self.horizontalSliderRobot.setValue(robot_slider_value)

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

    def yes_robot_confirmation(self):
            msgBox = QtGui.QMessageBox()
            msgBox.setIcon(QtGui.QMessageBox.Information)
            msgBox.setWindowTitle("Well Done!")
            msgBox.setText("I found the robot, the connection was successfully established!")
            msgBox.exec_();
            self.btnWakeUp.setEnabled(True)
            self.btnRest.setEnabled(True)

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
    thread.connect(form, form.ip_signal, thread.ip)
    thread.connect(form, form.wake_up_signal, thread.wake)

    #Connecting: thread > form
    form.connect(thread, thread.enable_components_gui_signal, form.enable_components_gui)
    form.connect(thread, thread.disable_signal, form.disable_gui)
    form.connect(thread, thread.enable_signal, form.enable_gui)
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





