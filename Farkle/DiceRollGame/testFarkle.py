# -*- coding: utf-8 -*-
"""
Created on Tue Sep 07 13:50:26 2021

@author: home
"""

import unittest
import warnings
import sys

import logging
from Farkle import Farkle

class TestFarkle(unittest.TestCase):

    def test(self):
        warnings.simplefilter("ignore", ResourceWarning)
        try:
            inst = Farkle()
            dice = [3, 5, 3, 3, 6, 1]
            keptDice = [True, True, False, True, True, True]
            score, scoringDice = inst.score_dice(dice,keptDice)
            logging.info(f"dice are {dice} keptDice are {keptDice} score is {score} num scoringDice is {scoringDice}")
            if score != 150 or scoringDice != 2:
                 self.fail(f"test failed. score is {score} scoringDice is {scoringDice}")            
        except Exception as err:
            print("Error Message {0}".format(err))
            sys.exit(1)
            
    def test_straight(self):
        try:
            inst = Farkle()
            dice = [6, 5, 3, 4, 1, 2]
            keptDice = [True, True, True, True, True, True]
            score, scoringDice = inst.score_dice(dice,keptDice)
            logging.info(f"dice are {dice} keptDice are {keptDice} score is {score} num scoringDice is {scoringDice}")
            if score != 1500 or scoringDice != 6:
                 self.fail(f"test_straight failed. score is {score} scoringDice is {scoringDice}")            
        except Exception as err:
            print("Error Message {0}".format(err))
            sys.exit(1)

    def test_Farkle(self):
        try:
            inst = Farkle()
            dice = [2, 1, 4, 5, 6, 6]
            keptDice = [True, False, True, False, True, True]
            score, scoringDice = inst.score_dice(dice,keptDice)
            logging.info(f"dice are {dice} keptDice are {keptDice} score is {score} num scoringDice is {scoringDice}")
            if score != 0 or scoringDice != 0:
                 self.fail(f"test_Farkle failed. score is {score} scoringDice is {scoringDice}")            
        except Exception as err:
            print("Error Message {0}".format(err))
            sys.exit(1)

    def test_three_pairs(self):
        try:
            inst = Farkle()
            dice = [2, 1, 4, 4, 2, 1]
            keptDice = [True, True, True, True, True, True]
            score, scoringDice = inst.score_dice(dice,keptDice)
            logging.info(f"dice are {dice} keptDice are {keptDice} score is {score} num scoringDice is {scoringDice}")
            if score != 1500 or scoringDice != 6:
                 self.fail(f"test_Farkle failed. score is {score} scoringDice is {scoringDice}")            
        except Exception as err:
            print("Error Message {0}".format(err))
            sys.exit(1)

    def test_two_triplets(self):
        try:
            inst = Farkle()
            dice = [6, 5, 6, 6, 5, 5]
            keptDice = [True, True, True, True, True, True]
            score, scoringDice = inst.score_dice(dice,keptDice)
            logging.info(f"dice are {dice} keptDice are {keptDice} score is {score} num scoringDice is {scoringDice}")
            if score != 2500 or scoringDice != 6:
                 self.fail(f"test_Farkle failed. score is {score} scoringDice is {scoringDice}")            
        except Exception as err:
            print("Error Message {0}".format(err))
            sys.exit(1)

    def test_two5s_two1s(self):
        try:
            inst = Farkle()
            dice = [2, 1, 1, 5, 6, 5]
            keptDice = [True, True, True, True, True, True]
            score, scoringDice = inst.score_dice(dice,keptDice)
            logging.info(f"dice are {dice} keptDice are {keptDice} score is {score} num scoringDice is {scoringDice}")
            if score != 300 or scoringDice != 4:
                 self.fail(f"test_Farkle failed. score is {score} scoringDice is {scoringDice}")            
        except Exception as err:
            print("Error Message {0}".format(err))
            sys.exit(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
