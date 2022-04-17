# -*- coding: utf-8 -*-
"""
Created on Tue Sep 07 13:50:26 2021

@author: home
"""

import unittest
import warnings
import sys

import logging
from FarkleBots import FarkleBots

class TestFarkleBot2(unittest.TestCase):

    def test(self):
        warnings.simplefilter("ignore", ResourceWarning)
        try:
            diceVals = [3, 5, 3, 3, 6, 1]
            keptDice = [False, False, False, False, False, False]
            turnScore = 0
            totals = [10 for x in range(3)]
            botID = 2
            bank, diceToKeep = FarkleBots.bot2_policy(diceVals,keptDice,turnScore,totals,botID)
            logging.info(f"diceVals are {diceVals} keptDice are {keptDice} turnScore is {turnScore} bank is {bank} diceToKeep is {diceToKeep}")
            if bank != True or diceToKeep != [True, True, True, True, False, True]:
                 self.fail(f"test failed. bank is {bank} diceToKeep is {diceToKeep}")            
        except Exception as err:
            print("Error Message {0}".format(err))
            sys.exit(1)
            
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
