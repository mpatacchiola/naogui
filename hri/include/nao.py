#!/usr/bin/env python


#PREREQUISITES:
# Naoqi SDK python, export the path in the terminal before using: export PYTHONPATH=${PYTHONPATH}:/path/to/pynaoqi-python2.7-2.1.3.3-linux64
# export PYTHONPATH=${PYTHONPATH}:/home/massimiliano/Desktop/nao%20idm/pynaoqi-python2.7-2.1.3.3-linux64
# linux "play" mp3 player running in background with subprocess
# sudo apt-get install sox libsox-fmt-mp3
# acapela python text2speech US-Rod voice (with license)
# XML file with trial and experiment list (with exact format)
# minidom python XML parser

import sys
#HERE it is necessary to specify the addres of the official NAO python library
from naoqi import ALProxy


class Puppet(object):

    def __init__(self, NAO_IP, NAO_PORT, SIMULATOR):
        """
        Class initialization
        """
        self._done = False


        #Posture Summary
        print("INIT: Getting robot state... ")
        self._al_motion_proxy = ALProxy("ALMotion", NAO_IP, int(NAO_PORT))
        print self._al_motion_proxy.getSummary()

        print("INIT: Getting the proxy objects... ")
        self._posture_proxy = ALProxy("ALRobotPosture", NAO_IP, int(NAO_PORT))

        if SIMULATOR == False:
		self._video_proxy = ALProxy("ALVideoRecorder", NAO_IP, int(NAO_PORT))
        else:
		print("VIDEO: simulator mode, the video is not recorded. ")         

        self._is_recording = False

    def play_video(self):
        # wake up the robot
	if SIMULATOR == False:
		print("VIDEO: starting the video record... ")
		# This records a 320*240 MJPG video at 10 fps.
		# Note MJPG can't be recorded with a framerate lower than 3 fps.
		date_string = strftime("%d%m%Y_%H%M%S", gmtime())
		self._video_proxy.setResolution(1)
		self._video_proxy.setFrameRate(10)
		self._video_proxy.setVideoFormat("MJPG")
		complete_path = "/home/nao/recordings/cameras" + date_string
		#self._video_proxy.startVideoRecord(complete_path)
		self._video_proxy.startRecording("/home/nao/recordings/cameras", date_string, True)
		self._is_recording = True
	else:
		print("VIDEO: simulator mode, the video is not recorded")

    def stop_video(self):
	if SIMULATOR == False:
                if self._video_proxy.isRecording() == True:
			print("VIDEO: stopping the video... ")
			videoInfo = self._video_proxy.stopRecording()
			self._is_recording = False

    def wake_up(self):
        # wake up the robot
        print("WAKE UP: waking up the robot... ")
	self._al_motion_proxy.wakeUp()
	#self._al_motion_proxy.setAngles("HeadYaw", 0.0, HEAD_SPEED)
	#self._al_motion_proxy.setAngles("HeadPitch", 0.0, HEAD_SPEED)
        self._posture_proxy.goToPosture("Stand", 1)

    def rest(self):
        # the robot rest
        print("REST: the robot is going to sleep... ")
	self._al_motion_proxy.rest()

    def say_something(self, sentence):
	#subprocess.Popen(["play","-q",filePath]) #using this method for the moment
        print("SAY: Neither acapela nor mp3 player have been implemented... ")

    def right_arm_pointing(self, state):
        """
        Move the rigth arm
        """       	
        if state == True:
 	     self._al_motion_proxy.setAngles("RShoulderPitch", 1.0, 0.5) #1.0 radians and 0.5 speed
        elif state == False:
  	     self._al_motion_proxy.setAngles("RShoulderPitch", 1.4, 0.5) #1.0 radians and 0.5 speed            

    def look_to(self, ANGLE, HEAD_SPEED):
        """
        Move the head looking to
        maximum angles: 29 / -38 (-2 +2 radians)
        maximum speed 1.0
        """       	
 	self._al_motion_proxy.setAngles("HeadPitch", ANGLE, HEAD_SPEED)


    def say_yes(self, ANGLE, HEAD_SPEED):
        """
        Move the head saying YES
        """    
	print("YES: moving the head to say yes...")   	
 	#self._al_motion_proxy.setAngles("HeadPitch", HEAD_PITCH_BOTTOM, HEAD_SPEED)
	#time.sleep(SLEEP_TIME)
	self._al_motion_proxy.setAngles("HeadPitch", ANGLE, HEAD_SPEED)
	time.sleep(SLEEP_TIME)
 	self._al_motion_proxy.setAngles("HeadPitch", -ANGLE, HEAD_SPEED)
	time.sleep(SLEEP_TIME)
	self._al_motion_proxy.setAngles("HeadPitch", ANGLE, HEAD_SPEED)
	time.sleep(SLEEP_TIME)
	self._al_motion_proxy.setAngles("HeadYaw", 0.0, HEAD_SPEED)

    def say_no(self, ANGLE, HEAD_SPEED):
        """
        Move the head saying NO
        """
	print("NO: moving the head to say no...")
 	self._al_motion_proxy.setAngles("HeadYaw", ANGLE, HEAD_SPEED)
	time.sleep(SLEEP_TIME)
	self._al_motion_proxy.setAngles("HeadYaw", -ANGLE, HEAD_SPEED)
	time.sleep(SLEEP_TIME)
 	self._al_motion_proxy.setAngles("HeadYaw", ANGLE, HEAD_SPEED)
	time.sleep(SLEEP_TIME)
	self._al_motion_proxy.setAngles("HeadYaw", -ANGLE, HEAD_SPEED)
	time.sleep(SLEEP_TIME)
	self._al_motion_proxy.setAngles("HeadYaw", 0.0, HEAD_SPEED)

    def set_neutral(self, HEAD_SPEED):
        """
        Sets the head back into a neutral pose
        """
	self._al_motion_proxy.setAngles("HeadYaw", 0.0, HEAD_SPEED)
	self._al_motion_proxy.setAngles("HeadPitch", 0.0, HEAD_SPEED)

    def shutdown(self):
	print("SHUTDOWN: unloading the mp3 file in the NAO...")

	print("SHUTDOWN: checking the video status...")
        if self._video_proxy.isRecording() == True:
		print("VIDEO: stopping the video record... ")
		videoInfo = self._video_proxy.stopRecording()
		self._is_recording = False

	print("SHUTDOWN: closing hands...")
	self._al_motion_proxy.closeHand("RHand");
	self._al_motion_proxy.closeHand("LHand");

	print("SHUTDOWN: moving to reset position...")
	self._al_motion_proxy.rest()

	print("SHUTDOWN: bye bye")



