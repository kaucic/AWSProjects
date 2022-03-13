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

class TestFarkleBot1(unittest.TestCase):

    def test(self):
        warnings.simplefilter("ignore", ResourceWarning)
        try:
            inst = FarkleBots()
            diceVals = [3, 5, 3, 3, 6, 1]
            keptDice = [False, False, False, False, False, False]
            turnScore = 0
            bank, diceToKeep = inst.bot1_policy(diceVals,keptDice,turnScore)
            logging.info(f"diceVals are {diceVals} keptDice are {keptDice} turnScore is {turnScore} bank is {bank} diceToKeep is {diceToKeep}")
            if bank != True or diceToKeep != [True, True, True, True, False, True]:
                 self.fail(f"test failed. bank is {bank} diceToKeep is {diceToKeep}")            
        except Exception as err:
            print("Error Message {0}".format(err))
            sys.exit(1)

    def test_two1s_one5(self):
        try:
            inst = FarkleBots()
            diceVals = [1, 2, 5, 4, 1, 3]
            keptDice = [False, False, False, False, True, False]
            turnScore = 0
            bank, diceToKeep = inst.bot1_policy(diceVals,keptDice,turnScore)
            logging.info(f"diceVals are {diceVals} keptDice are {keptDice} turnScore is {turnScore} bank is {bank} diceToKeep is {diceToKeep}")
            if bank != False or diceToKeep != [True, False, False, False, False, False]:
                 self.fail(f"test failed. bank is {bank} diceToKeep is {diceToKeep}")            
        except Exception as err:
            print("Error Message {0}".format(err))
            sys.exit(1)
            
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
