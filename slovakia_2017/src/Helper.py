#!/usr/bin/python

from pygame.sprite import DirtySprite
import random
import time
import logging
from pygame.surface import Surface
from src.Properties import Color, Size
from tts_client import invoke_tts
from utils import *

RATE_PERCENTAGE_MAX = 25
RATE_PERCENTAGE_MIN = -25

# RANGE_PERCENTAGE_MAX = 50  # RG
# RANGE_PERCENTAGE_MIN = -50  # RG

ENERGY_PERCENTAGE_MAX = 5  # RG
ENERGY_PERCENTAGE_MIN = -5  # RG

FOMEAN_PERCENTAGE_MAX = 10  # RG
FOMEAN_PERCENTAGE_MIN = -10  # RG

#mpatacchiola: include for the robot libraries
import threading
import sys
sys.path.insert(1, "./pynaoqi-python2.7-2.1.3.3-linux64") #import this module for the nao.py module
from naoqi import ALProxy
import random #randint to generate random advice
import csv #to read the configuration file with the robot IP and PORT
#mpatacchiola: creating the motion object
def robot_animation(advice, avatar_name, csv_path='./robot.csv', verbose=True):
    '''Given the name of the avatar and an advice it animates one of the robots.

    The gestures are sampled among the NAO animations.
    The function will look for a file called 'robot.csv' containing:
    comma separated values for [Avatar name, IP address, PORT number].
    The file must be in the root folder.
    @param advice the advice string
    @param avatar_name the name of the avatar (Veronika, Monika, Tereza)
    @param csv_path the path where the CSV file is located (default is root)
    @param verbose if True it prints the steps on terminal
    '''
    avatar_found = False
    with open(csv_path, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            conf_avatar_name = row[0]
            conf_nao_ip = row[1]
            conf_nao_port = row[2]
            if(conf_avatar_name == avatar_name):
                avatar_found = True
                NAO_IP = conf_nao_ip
                NAO_PORT = conf_nao_port
                break
    if(avatar_found == False):
        if verbose: print("ROBOT ERROR: AVATAR '" + str(avatar_name) + "' NOT FOUND!")
        return 0
    if verbose: print "ROBOT init..."
    if verbose: print("ROBOT IP: " + str(NAO_IP))
    if verbose: print("ROBOT PORT: " + str(NAO_PORT))
    if verbose: print("ROBOT avatar: " + str(avatar_name))
    if verbose: print("ROBOT advice: " + str(advice))
    animated_speech_proxy = ALProxy("ALAnimatedSpeech", NAO_IP, int(NAO_PORT))
    #set the local configuration
    configuration = {"bodyLanguageMode":"contextual"}
    #say the text with the local configuration
    gesture_list = list()
    gesture_list.append("^start(animations/Stand/Gestures/Choice_1) ")
    gesture_list.append("^start(animations/Stand/Gestures/Choice_2) ")
    gesture_list.append("^start(animations/Stand/Gestures/Explain_1) ")
    gesture_list.append("^start(animations/Stand/Gestures/Explain_2) ")
    gesture_list.append("^start(animations/Stand/Gestures/Explain_4) ")
    gesture_list.append("^start(animations/Stand/Gestures/Explain_6) ")
    gesture_list.append("^start(animations/Stand/Gestures/Explain_7) ")
    gesture_list.append("^start(animations/Stand/Gestures/Explain_8) ")
    gesture_list.append("^start(animations/Stand/Gestures/Explain_9) ")
    sampled_gesture = gesture_list[random.randint(0,len(gesture_list)-1)]
    full_string = sampled_gesture + advice #the gesture plus the advice
    animated_speech_proxy.say(full_string, configuration)

class HelperUnknownSignal(Surface):
    def __init__(self, names=''):
        super(HelperUnknownSignal, self).__init__(Size.HELPER_UNKNOWN_SIGNAL, pygame.SRCALPHA)
        self.fill(color=Color.DIRECTION)
        center_x, center_y = self.get_rect().center
        
        mytext = _('not-understood')
        line1 = largeText.render(unicode(mytext.decode('utf8')), True, Color.WHITE)
        mytext = _('please-repeat')
        line2 = smallText.render(unicode(mytext.decode('utf8')), True, Color.WHITE)
        mytext = _('and-remember-who1')
        line3 = miniText.render(unicode(mytext.decode('utf8')), True, Color.WHITE)
        mytext = _('and-remember-who2') % names
        line4 = miniText.render(unicode(mytext.decode('utf8')), True, Color.WHITE)
        
#AG        line1 = largeText.render(_('not-understood'), True, Color.WHITE)
#AG        line2 = smallText.render(_('please-repeat'), True, Color.WHITE)
#AG        line3 = miniText.render(_('and-remember-who1'), True, Color.WHITE)
#AG        line4 = miniText.render(_('and-remember-who2') % names, True, Color.WHITE)

        self.blit(line1, (center_x - (line1.get_width() / 2), 10))
        self.blit(line2, (center_x - (line2.get_width() / 2), 50))
        self.blit(line3, (center_x - (line3.get_width() / 2), 90))
        self.blit(line4, (center_x - (line4.get_width() / 2), 120))


CHARACTERS = {0: ('Tereza',
                  pygame.image.load('resources/characters/eugenia.png'),
                  '+0%',  # RG it used to say +5%
                  pygame.image.load('resources/characters/thumb_eugenia.png'),
                  'Tereza'),
              1: ('Monika',
                  pygame.image.load('resources/characters/amanda.png'),
                  '-10%',  # RG it used to say -20%
                  pygame.image.load('resources/characters/thumb_amanda.png'),
                  'Monika'),
              2: ('Veronika',
                  pygame.image.load('resources/characters/veronica.png'),
                  '+0%',  # RG it used to say +5%
                  pygame.image.load('resources/characters/thumb_veronica.png'),
                  'Veronika'),#####AG:FIX!
              3: ('undetermined',
                  HelperUnknownSignal(),
                  None,
                  None,
                  '')}

advice_prefixes = [_('advice-prefix-1'),
                   _('advice-prefix-2'),
                   _('advice-prefix-3'),
                   _('advice-prefix-4'),
                   _('advice-prefix-5'),
                   _('advice-prefix-6'),
                   _('advice-prefix-7'),
                   _('advice-prefix-8'),
                   _('advice-prefix-9'),
                   _('advice-prefix-10')]

advices_suffixes = {1: _('advice-suffix-1'),
                    2: _('advice-suffix-2'),
                    3: _('advice-suffix-3'),
                    4: _('advice-suffix-4'),
                    5: _('advice-suffix-5'),
                    6: _('advice-suffix-6'),
                    7: _('advice-suffix-7'),
                    8: _('advice-suffix-8'),
                    9: _('advice-suffix-9'),
                    10: _('advice-suffix-10'),
                    11: _('advice-suffix-11'),
                    12: _('advice-suffix-12'),
                    13: _('advice-suffix-13')}


class Helper(DirtySprite):
    def __init__(self, id, game, initial_score=0):
        self.game = game
        super(Helper, self).__init__()
        self.last_advice = 0
        self.score = initial_score
        self.rate = 0
        # self.pitch_range = 0 # RG
        self.energy = 0  # RG
        self.f0mean = 0  # RG
        self.id = id
        self.name, self.image, self.pitch, self.thumb, self.nombre = CHARACTERS[id]
        logging.info('Helper=> [%(name)s] initial score: [%(score)i]',
                     {'name': self.name, 'score': self.score})
        self.rect = self.image.get_rect()
        self.hide()

    # def set_configuration(self, config):
    #     self.conf = config

    def get_possible_advices(self):
        advs = {}
        possibles = list(set(values_of(self.game.human_player.hand)))
        for val in possibles:
            if val not in values_of(self.game.comp_player.hand):
                key = -15
            else:
                a = cant_of_same_rank(self.game.human_player.hand, val)
                b = cant_of_same_rank(self.game.comp_player.hand, val)
                if a + b == 4:
                    key = 5
                else:
                    key = b
            # Si no esta en el dict, la creo
            if key in advs:
                advs[key].append(val)
            else:
                advs[key] = [val]

        return advs

    def get_an_advice(self):
        advices = self.get_possible_advices()
        # candidates = list(set(self.game.human_player.hand))
        s = self.choose_better_advs(advices.keys())
        candidates = advices[s]
        self.score += s
        logging.info('Helper=> [%(name)s] updated score to: [%(score)i]',
                     {'name': self.name, 'score': self.score})
        # if not candidates:
        # candidates = values_of(self.game.human_player.hand) # if no intersection between those two, random guess
        return random.choice(candidates)

    def speech_advice(self):
        advice = random.choice(advice_prefixes) + advices_suffixes[self.last_advice]
        logging.info('Helper=> [%(nombre)s] giving advice: %(advice)s', {'nombre': self.name, 'advice': advice})
        invoke_tts(filename=self.game.get_response_filename(),
                   rate_change=self.calculate_percentage_rate(),
                   # range_change=self.calculate_percentage_range(),
                   energy_change=self.calculate_percentage_energy(),
                   f0mean_change=self.calculate_percentage_f0mean(),
                   pitch=self.pitch,
                   advice=advice)  # RG

        #mpatacchiola: calling the robot animation function
        t = threading.Thread(target=robot_animation, args=(advice, self.name,))
        t.start()
        #robot_animation(advice=advice, avatar_name=self.name, verbose=True)
        pygame.mixer.music.play()

    def calculate_percentage_rate(self):
        if self.rate < 0:
            return str(self.rate)+'%'
        else:
            return '+'+str(self.rate)+'%'

    # def calculate_percentage_range(self): # RG
        if self.pitch_range < 0:
            return str(self.pitch_range)+'%'
        else:
            return '+'+str(self.pitch_range)+'%'

    def calculate_percentage_energy(self):  # RG
        if self.energy < 0:
            return str(self.energy)+'%'
        else:
            return '+'+str(self.energy)+'%'

    def calculate_percentage_f0mean(self):  # RG
        if self.f0mean < 0:
            return str(self.f0mean)+'%'
        else:
            return '+'+str(self.f0mean)+'%'

    def help(self):
        nro = self.get_an_advice()
        self.last_advice = nro
        logging.info('Audio=> [%(nombre)s] giving advice: %(rank)02d', {'nombre': self.name, 'rank': nro})
        self.speech_advice()
        self.game.human_player.update_enabled_cards(nro)
        return True

    def choose_better_advs(self, keys):
        score = keys[0]
        for k in keys:
            if abs(self.score + k) < abs(self.score + score):
                score = k
        return score

    def hide(self):
        self.visible = False

    def show(self):
        self.visible = True

    def is_talking(self):
        return pygame.mixer.music.get_busy()


class PracticeHelper(Helper):
    def __init__(self, id, game, initial_score=0):
        super(PracticeHelper, self).__init__(id, game, initial_score)

    def adapt_rates(self, new_ap_value, ap_feature):  # RG
        logging.info('Audio=> Practice helper does not adapt %s', ap_feature.upper())  # RG
        if ap_feature == 'rate':  # RG
            self.game.historic_rate.append(new_ap_value)
        # elif ap_feature == 'range':
        #    self.game.historic_range.append(new_ap_value)
        elif ap_feature == 'energy':
            self.game.historic_energy.append(new_ap_value)
        elif ap_feature == 'f0mean':
            self.game.historic_f0mean.append(new_ap_value)
        pass


class EntrainingHelper(Helper):
    def __init__(self, id, game, initial_score):
        super(EntrainingHelper, self).__init__(id, game, initial_score)
        self.initial_rate = game.rate_base
        # self.initial_range = game.range_base  # RG
        self.initial_energy = game.energy_base  # RG
        self.initial_f0mean = game.f0mean_base  # RG

    def adapt_rates(self, new_ap_value, ap_feature):  # RG
        logging.info('Audio=> ## Adapting %s ## ', ap_feature.upper())  # RG

        if ap_feature == 'rate':  # RG
            initial_ap = self.initial_rate
            percentage_max = RATE_PERCENTAGE_MAX
            percentage_min = RATE_PERCENTAGE_MIN
        # elif ap_feature == 'range':
        #    initial_ap = self.initial_range
        #    percentage_max = RANGE_PERCENTAGE_MAX
        #    percentage_min = RANGE_PERCENTAGE_MIN
        elif ap_feature == 'energy':
            initial_ap = self.initial_energy
            percentage_max = ENERGY_PERCENTAGE_MAX
            percentage_min = ENERGY_PERCENTAGE_MIN
        elif ap_feature == 'f0mean':
            initial_ap = self.initial_f0mean
            percentage_max = FOMEAN_PERCENTAGE_MAX
            percentage_min = FOMEAN_PERCENTAGE_MIN

        pt = (new_ap_value - initial_ap) / initial_ap

        partial = int(round(pt, 2) * 100)
        ap_change = max(min(partial, percentage_max), percentage_min)  # RG

        if ap_feature == 'rate':  # RG
            self.game.historic_rate.append(new_ap_value)
            self.rate = ap_change
        # elif ap_feature == 'range':
        #    self.game.historic_range.append(new_ap_value)
        #    self.pitch_range = ap_change
        elif ap_feature == 'energy':
            self.game.historic_energy.append(new_ap_value)
            self.energy = ap_change
        elif ap_feature == 'f0mean':
            self.game.historic_f0mean.append(new_ap_value)
            self.f0mean = ap_change

        logging.info('Audio=> Measured %(ap_feature)s: [%(new_ap_value)g] - Change: [%(percent_change)g percent] - Base value: [%(base_value)g]',
                     {'ap_feature': ap_feature, 'new_ap_value': new_ap_value, 'percent_change': ap_change, 'base_value': initial_ap})  # RG


class DisentrainingHelper(Helper):
    def __init__(self, id, game, initial_score):
        super(DisentrainingHelper, self).__init__(id, game, initial_score)
        self.initial_rate = game.rate_base
        # self.initial_range = game.range_base  # RG
        self.initial_energy = game.energy_base  # RG
        self.initial_f0mean = game.f0mean_base  # RG

    def adapt_rates(self, new_ap_value, ap_feature):  # RG
        logging.info('Audio=> ## DE-Adapting %s ## ', ap_feature.upper())  # RG

        if ap_feature == 'rate':  # RG
            initial_ap = self.initial_rate
            percentage_max = RATE_PERCENTAGE_MAX
            percentage_min = RATE_PERCENTAGE_MIN
        # elif ap_feature == 'range':
        #    initial_ap = self.initial_range
        #    percentage_max = RANGE_PERCENTAGE_MAX
        #    percentage_min = RANGE_PERCENTAGE_MIN
        elif ap_feature == 'energy':
            initial_ap = self.initial_energy
            percentage_max = ENERGY_PERCENTAGE_MAX
            percentage_min = ENERGY_PERCENTAGE_MIN
        elif ap_feature == 'f0mean':
            initial_ap = self.initial_f0mean
            percentage_max = FOMEAN_PERCENTAGE_MAX
            percentage_min = FOMEAN_PERCENTAGE_MIN

        pt = (new_ap_value - initial_ap) / initial_ap

        partial = int(round(pt, 2) * -100)  # RG: this must be one of the most important minus signs in science! And it's well hidden!
        ap_change = max(min(partial, percentage_max), percentage_min)  # RG

        if ap_feature == 'rate':  # RG
            self.game.historic_rate.append(new_ap_value)
            self.rate = ap_change
        # elif ap_feature == 'range':
        #    self.game.historic_range.append(new_ap_value)
        #    self.pitch_range = ap_change
        elif ap_feature == 'energy':
            self.game.historic_energy.append(new_ap_value)
            self.energy = ap_change
        elif ap_feature == 'f0mean':
            self.game.historic_f0mean.append(new_ap_value)
            self.f0mean = ap_change

        logging.info('Audio=> Measured %(ap_feature)s: [%(new_ap_value)g] - Change: [%(percent_change)g percent] - Base value: [%(base_value)g]',
                     {'ap_feature': ap_feature, 'new_ap_value': new_ap_value, 'percent_change': ap_change, 'base_value': initial_ap})  # RG


class UnknownHelper(Helper):
    def __init__(self, id, game):
        super(UnknownHelper, self).__init__(id, game)
        self.image = HelperUnknownSignal(game.helper_names)
        self.clock = None

    def help(self):
        self.clock = time.time()
        return False

    def adapt_rates(self, new_ap_value, ap_feature):
        logging.error('Audio=> Not adapting %(ap_feature)s because the helper is %(helper_name)s',
                      {'helper_name': self.name, 'ap_feature': ap_feature})

    def is_talking(self):
        return time.time() - self.clock < 3
