#!/usr/bin/python
import gettext
import sys

reload(sys)
sys.setdefaultencoding('utf8')

texts = gettext.translation('gofish', localedir='locale', languages=['sk'])
texts.install()

import os
import pygame
import random
import sys
import logging
from src.InterGameScreen import *
from src.GameConfigurations import PracticeGame, GameTypeOne, GameTypeTwo
from src.Helper import CHARACTERS
from src.Train import Train
from src.InputName import InputName
from src.Properties import PLAYING_MODE_ONE, PLAYING_MODE_TWO, SCREEN_RES
from src.utils import internet_on

#mpatacchiola: include for the robot libraries
import sys
sys.path.insert(1, "./pynaoqi-python2.7-2.1.3.3-linux64") #import this module for the nao.py module
from naoqi import ALProxy
import csv

def robot_check(csv_path='./robot.csv'):
    avatar_found = False
    with open(csv_path, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            conf_avatar_name = row[0]
            conf_nao_ip = row[1]
            conf_nao_port = row[2]
            try:
                animated_speech_proxy = ALProxy("ALAnimatedSpeech", conf_nao_ip, int(conf_nao_port))
                configuration = {"bodyLanguageMode":"contextual"}
                animated_speech_proxy.say("^start(animations/Stand/Gestures/Choice_1) Hello", configuration)
                print("ROBOT: IP=" + str( conf_nao_ip) + str("; PORT=") + str(conf_nao_port) + " CONNECTED!")
            except:
                raise Exception("ROBOT ERROR: not found the robot at IP=" + str( conf_nao_ip) + str("; PORT=") + str(conf_nao_port))


class UI:
    def __init__(self, gameMode=PLAYING_MODE_ONE, helper=1):
    	# change the following line to run in fullscreen mode
        self.screen = pygame.display.set_mode(SCREEN_RES)#, pygame.FULLSCREEN)
        self.game_mode = gameMode
        self.helper = helper
        # self.test_hash = self.__generate_test_hash()
        self.results = []

    def __generate_logger(self):
        directory_test = 'logs/test-' + str(self.test_hash)

        while (os.path.exists(directory_test)):
            directory_test += '_2'
            self.test_hash += '_2'
        os.makedirs(directory_test)
        print '*** Logging into', directory_test + '/game.log'
        logging.basicConfig(filename=directory_test + '/game.log',
                            format='%(asctime)s - %(levelname)s: %(message)s',
                            datefmt='%m/%d/%Y %I_%M_%S %p',
                            level=logging.INFO,
                            encoding = "UTF-8")
        logging.info('General=> *** Starting Test ****')

    @staticmethod
    def __generate_test_hash():
        return random.getrandbits(32)

    def main_loop(self):

        if not internet_on():
            print 'No internet connection.'
            return

        try:
            #input = InputName(self.screen)
            #name = input.get_name()
            name = "02 03 2017"

            self.test_hash = name.lower().replace(' ', '_')
            # self.test_hash = str(random.getrandbits(1))
            self.__generate_logger()

            log_info_game = {'game_mode_parameter': self.game_mode,
                             'game_helper_parameter': self.helper,
                             'entrainment_helper_name': (CHARACTERS[self.helper%2])[0],
                             'player_number': self.test_hash}
            logging.info("General=> Starting test - %s", log_info_game)

            train = Train(self.screen)
            train.start()

            practiceGame = PracticeGame(screen=self.screen)
            practiceGame.config(self.test_hash)
            _, rate_avg, energy_avg, f0mean_avg = practiceGame.play()  # RG

            score_screen = InterGameScreen(screen=self.screen, step=0, scores=[practiceGame.human_player.score])
            score_screen.show()

            score_helper_1 = 0
            score_helper_2 = 0

            for j in range(1, CANT_GAMES+1):
                if modeAdmin == PLAYING_MODE_ONE:
                    game = GameTypeOne(screen=self.screen,
                                       rate_base=rate_avg,
                                       #  range_base=range_avg,  # RG
                                       energy_base=energy_avg,  # RG
                                       f0mean_base=f0mean_avg,  # RG
                                       entrainment_helper=self.helper,
                                       score_h1=score_helper_1,
                                       score_h2=score_helper_2)
                elif modeAdmin == PLAYING_MODE_TWO:
                    game = GameTypeTwo(screen=self.screen,
                                       rate_base=rate_avg,
                                       #  range_base=range_avg,  # RG
                                       energy_base=energy_avg,  # RG
                                       f0mean_base=f0mean_avg,  # RG
                                       entrainment_helper=self.helper,
                                       score_h1=score_helper_1,
                                       score_h2=score_helper_2)
                game.config(self.test_hash)
                score, rate_avg, energy_avg, f0mean_avg = game.play()  # RG
                self.results.append(score)

                # Recupero los scores de los
                score_helper_1 = game.known_helpers[0].score
                score_helper_2 = game.known_helpers[1].score

                score_screen = InterGameScreen(screen=self.screen, step=j, scores=self.results)
                score_screen.show()
        except (KeyboardInterrupt, SystemExit):
            raise


if __name__ == "__main__":
    # Tomo el modo de Juego x parametro:
    if len(sys.argv) < 3:
        raise Exception("\n Usage: \n \t \t \t UI.py <mode> <entrainment_helper>  \n <mode> may be: play_one or play_two \n <entrainment_helper> may be: 1 or 2")

    #mpatacchiola
    #check if the robots are connected
    #if one is not connected throw an exception
    robot_check(csv_path='./robot.csv')

    modeAdmin = sys.argv[1]
    if modeAdmin not in [PLAYING_MODE_ONE, PLAYING_MODE_TWO]:
        raise Exception("Invalid <mode> argument: play_one or play_two")
    entrainment_helper = sys.argv[2]
    if entrainment_helper not in ['1', '2']:
        raise Exception("Invalid <entrainment_helper> argument: 1 or 2")


    interface = UI(gameMode=modeAdmin, helper=int(entrainment_helper))
    interface.main_loop()

