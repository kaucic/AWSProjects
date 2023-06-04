# -*- coding: utf-8 -*-
"""
Created on Tue Sep 07 13:50:26 2021

@author: home
"""

import unittest
import warnings
import sys

import logging
from FarkleFuncs import FarkleFuncs

import boto3

class FarkleTests(unittest.TestCase):

    def test(self):
        try:
            dice = [2, 5, 1, 5, 6, 5]
            keptDice = [False, False, True, False, False, False]
            diceObj = FarkleFuncs() # Dice variable that contains variables _previouslyKeptDice and _keptDiceVals
            diceObj.set_diceVals_and_keptDice(dice,keptDice)
            returned_dice = diceObj.get_diceVals()
            returned_kept_dice = diceObj.get_previouslyKeptDice()
            score, numDiceThatScored, scoringDice = FarkleFuncs.score_dice(returned_dice,returned_kept_dice)
            logging.info(f"dice are {returned_dice} keptDice are {returned_kept_dice} score is {score} numDiceThatScored is {numDiceThatScored} scoringDice is {scoringDice}")
            if score != 100 or numDiceThatScored != 1 or scoringDice != [False, False, True, False, False, False]:
                 self.fail(f"test_setters_and_getter failed. score is {score} scoringDice is {scoringDice}") 
            banked_score = diceObj.bank_score()
            logging.info(f"dice are {returned_dice} banked_score is {banked_score}")
            if banked_score != 500:
                 self.fail(f"test_setters_and_getter failed. dice are {returned_dice} banked_score is {banked_score}")            
        except Exception as err:
            print("Error Message {0}".format(err))
            sys.exit(1)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
    