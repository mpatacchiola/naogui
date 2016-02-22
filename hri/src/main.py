#!/usr/bin/env python


#------- Massimiliano Patacchiola -------
#------- Plymouth University 2016 -------
#
# It is necessary to have pyQt4 installed
#
# To generate python code from the .ui file:
# pyuic4 mainwindow.ui -o design.py
#
#

# Libraries for Qt
from PyQt4 import QtGui  # Import the PyQt4 module we'll need
from PyQt4.QtCore import QElapsedTimer
from PyQt4.QtCore import QThread
from PyQt4.QtCore import SIGNAL

import sys  
import os
import time

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


class WorkerThread(QThread):
  def __init__(self):
    QThread.__init__(self)

    #Signal variables
    self.disable_signal = SIGNAL("disable_signal")
    self.enable_signal = SIGNAL("enable_signal")
    self.no_robot_signal = SIGNAL("no_robot_signal")
    self.yes_robot_signal = SIGNAL("yes_robot_signal")
    self.bad_xml_signal = SIGNAL("bad_xml_signal")
    self.good_xml_signal = SIGNAL("good_xml_signal")
    self.update_lcd_signal = SIGNAL("update_lcd_signal")

    #Misc variables
    self.myParser = parser.Parser()
    self.timer = QElapsedTimer()
    self.STATE_MACHINE = 0

    #Status variables
    self._robot_connected = False
    self._xml_uploaded = False
    self._start_pressed = False
    self._confirm_pressed = False

   #Logbook variables
    self._log_timer = 0
    self._log_trial = 0
    self._log_ptresure = 10
    self._log_pinv = 0
    self._log_rinv = 0
    self._log_pmult = 0
    self._log_rmult = 0
    self._log_gaze = False
    self._log_pointing = False
    self._log_mp3 = ""

  def run(self):
    #Init the State machine 
    self.emit(self.enable_signal) #GUI enabled
    self.timer.start()
    self.STATE_MACHINE = 0

    while True:

        time.sleep(0.05) #50 msec sleep to evitate block

        #STATE-0 init
        if self.STATE_MACHINE == 0:
            if self._robot_connected==True and self._xml_uploaded==True and self._start_pressed==True:
                self.STATE_MACHINE = 1 #switching to next state
                self.emit(self.disable_signal) #GUI disabled
                self.logger = logbook.Logbook() #Logbook Init
            else:
                current_time = time.strftime("%H:%M:%S", time.gmtime())
                status = "robot_coonnected = " + str(self._robot_connected) + "\n" + "xml_uploaded = " + str(self._xml_uploaded) + "\n" + "start_pressed = " + str(self._start_pressed) + "\n"
                print "[0] " + current_time + " Waiting... \n" + status
                time.sleep(3)

        #STATE-1 Hello!
        if self.STATE_MACHINE == 1:
            print "[1] Robot Hello"
            #Reset thr investment values
            self.emit(self.update_lcd_signal, self._log_ptresure, self._log_rinv) #GUI lcd reset
            if self.myParser._gaze_list[self._log_trial] == "True":
              print "[1] looking == True"
              self._log_gaze = "True"
              self.myPuppet.look_to(0, 0.5) #angle(radians) + speed
            elif self.myParser._gaze_list[self._log_trial] == "False":
              print "[1] looking == False"
              self._log_gaze = "False"
              self.myPuppet.look_to(1, 0.5) #angle(radians) + speed 
            time.sleep(2)
            self._log_mp3 = self.myParser._mp3_list[self._log_trial]
            mp3_path = "../share/mp3/" + self._log_mp3
            subprocess.Popen(["play","-q", mp3_path])
            time.sleep(6)
            self.STATE_MACHINE = 5 #Jumping to state 5
            #From here we skip the first item in the list (hello)
            #self._log_trial = self._log_trial + 1 
 
        #STATE-2 robot look or not and talk
        if self.STATE_MACHINE == 2:
            #Updating the multiplication values
            self._log_pmult = float(self.myParser._pmf_list[self._log_trial])
            self._log_rmult = float(self.myParser._rmf_list[self._log_trial])       
            print "[2] Robot Talking + Looking/Non-Looking"            
            self.myPuppet.look_to(1, 0.5)
            if self.myParser._gaze_list[self._log_trial] == "True":
              print "[2] looking == True"
              self._log_gaze = "True"
              self.myPuppet.look_to(0, 0.5) #angle(radians) + speed
            elif self.myParser._gaze_list[self._log_trial] == "False":
              print "[2] looking == False"
              self._log_gaze = "False"
              self.myPuppet.look_to(1, 0.5) #angle(radians) + speed

            print "[2] bla bla bla ..."
            self._log_mp3 = self.myParser._mp3_list[self._log_trial]
            mp3_path = "../share/mp3/" + self._log_mp3
            subprocess.Popen(["play","-q", mp3_path])
            time.sleep(4) #sleep as long as the mp3 file
            #when mp3 file finish          
            self.STATE_MACHINE = 3 #next state
            self.timer.restart() #RESET here the timer
            print "[3] Waiting for the subject answer..." #going to state 3

        #STATE-3 waiting for the subject investment
        if self.STATE_MACHINE == 3:                      
            self.emit(self.enable_signal) #GUI enbled                      
            if self._confirm_pressed == True:   #when subject give the answer
                self._log_timer = self.timer.elapsed() #record the time
                print "[3] TIME: " + str(self._log_timer)
                print "[3] INVESTMENT: " + str(self._log_pinv)
                self._confirm_pressed = False #reset the variable state
                self.emit(self.disable_signal) #GUI disabled
                #Updating the investment values
                #self._log_ptresure = float(self._log_ptresure) - float(self._log_pinv) #TODO I should subtract this value or not?
                self.emit(self.update_lcd_signal, self._log_ptresure, self._log_pinv) #GUI lcd updated
                self.STATE_MACHINE = 4 #next state
                time.sleep(2) #Sleep to evitate fast movements of the robot just after the answer

        #STATE-4 Pointing or not and gives the reward
        if self.STATE_MACHINE == 4:
            print "[4] Pointing/Non-Pointing"                         
            if self.myParser._pointing_list[self._log_trial] == "True":
              print "[4] pointing == True"
              self._log_pointing = "True"
              self.myPuppet.right_arm_pointing(True)
            elif self.myParser._pointing_list[self._log_trial] == "False":
              print "[4] pointing == False"
              self._log_pointing = "False"
              self.myPuppet.right_arm_pointing(False)
            time.sleep(2) 
            #Updating the investment values           
            self._log_rinv = float(self._log_pinv) * float(self._log_rmult)
            self._log_ptresure = self._log_ptresure + self._log_rinv
            self.emit(self.update_lcd_signal, self._log_ptresure, self._log_rinv) #GUI lcd updated
            time.sleep(2)
            self.myPuppet.right_arm_pointing(False) #reset the arm position
            time.sleep(2)
            self.STATE_MACHINE = 5 #next state

        #STATE-5 Saving in the logbook
        if self.STATE_MACHINE == 5:
            print "[5] Saving the trial in the logbook"
            #TODO save the correct informations
            self.logger.AddLine(self._log_trial+1, self._log_pinv, self._log_rinv, self._log_pmult, self._log_rmult, self._log_gaze, self._log_pointing, self._log_timer, self._log_mp3)
            print "[3] " + str(self._log_trial+1) + "," + str(self._log_pinv) + "," + str(self._log_rinv) + "," + str(self._log_pmult) + "," + str(self._log_rmult) + "," + str(self._log_gaze) + "," + str(self._log_pointing) + "," + str(self._log_timer)+ "," + str(self._log_mp3)

            time.sleep(1)

            if self._log_trial+1 != self.myParser._size:
                self.STATE_MACHINE = 2 #cycling to state 2
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
            #subprocess.Popen(["play","-q", "bye.wav"])
            time.sleep(5)


  def start_experiment(self):
    self._start_pressed = True

  def confirm(self, investment):
    self._confirm_pressed = True
    self._log_pinv = float(investment) * float(self._log_pmult)
    #self._log_ptresure = float(self._log_ptresure) + float(self._log_pinv)

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
        self.emit(self.good_xml_signal)
        self._xml_uploaded = True
    except:
        self.emit(self.bad_xml_signal)
        print("\nERROR: Impossible to read the XML file!\n")
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

    def confirm_pressed(self):
        self.emit(self.confirm_signal, self.horizontalSlider.sliderPosition())

    def connect_pressed(self):
        ip_string = str(self.lineEditNaoIP.text())
        port_string = str(self.lineEditNaoPort.text())
        #print "IP: " + ip_string
        self.emit(self.ip_signal, ip_string, port_string)

    def wake_up_pressed(self):
        self.emit(self.wake_up_signal, True)

    def rest_pressed(self):
        self.emit(self.wake_up_signal, False)          

    def disable_gui(self):
        self.horizontalSlider.setEnabled(False)
        self.btnConfirm.setEnabled(False)
        self.btnStartExperiment.hide() #hiding the start button
        self.horizontalSlider.setValue(5)

    def enable_gui(self):
        self.horizontalSlider.setEnabled(True)
        self.btnConfirm.setEnabled(True)

    def update_lcd(self, ptreasure, rinv):
        self.lcdNumberTresure.display(float(ptreasure))
        self.lcdNumberGiven.display(float(rinv))

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
            msgBox.setText("ERROR: It was not possible to read the XML file. \nFollow these tips and try to select again. \n \n1- Verify if you can open correctly the file with a text editor (es. notepad). \n2- Once opened the file, check if for each open bracket <trial> there is a closed bracket </trial>. \n");
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
    form.connect(thread, thread.disable_signal, form.disable_gui)
    form.connect(thread, thread.enable_signal, form.enable_gui)
    form.connect(thread, thread.no_robot_signal, form.no_robot_error)
    form.connect(thread, thread.yes_robot_signal, form.yes_robot_confirmation)
    form.connect(thread, thread.bad_xml_signal, form.bad_xml_error)
    form.connect(thread, thread.good_xml_signal, form.good_xml_confirmation)
    form.connect(thread, thread.update_lcd_signal, form.update_lcd)

    #Starting thread
    thread.start()

    #Show the form and execute the app
    form.show()  
    app.exec_()  



if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  # run the main function





