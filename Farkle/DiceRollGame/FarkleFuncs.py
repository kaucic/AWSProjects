# -*- coding: utf-8 -*-
"""
Created on Mon Sep 06 13:50:26 2021

@author: home
"""

from typing import Tuple

import random

import logging
import doFlaskLogging

class FarkleFuncs:
    def __init__(self,NDICE=6):
        self._NDICE = NDICE
        self._diceVals = [5 for x in range(self._NDICE)]
        self.clear_previouslyKeptDice()       
        return

    def get_diceVals(self) -> list:
        return self._diceVals
        
    def get_previouslyKeptDice(self) -> list:
        return self._previouslyKeptDice

    def clear_previouslyKeptDice(self) -> list:
        self._previouslyKeptDice = [False for x in range(self._NDICE)]
        return self._previouslyKeptDice

    def update_previouslyKeptDice(self,keptDice) -> list:
        # Update previouslyKeptDice
        for i in range(self._NDICE):
            self._previouslyKeptDice[i] = self._previouslyKeptDice[i] or keptDice[i]
        return self._previouslyKeptDice

    # Method to compute the Farkle score pertaining to the binary vector diceToScore with spots in diceVals
    # Return the score, the # of dice that scored, and the dice that scored bool list
    @staticmethod   
    def score_dice(diceVals, diceToScore) -> Tuple[int,int,list]:
        count = 0
        num_dice_that_scored = 0
        dice_that_scored = [False for x in range(len(diceVals))]

        # vals is a histogram of die number buckets (1-6) and the number of dice with that die number
        vals = {}
        
        # Populate hash table
        for i in range(len(diceVals)):
            if diceToScore[i] == True:
                count += 1
                if diceVals[i] in vals:
                    vals[diceVals[i]] += 1
                else:
                    vals[diceVals[i]] = 1
        
        num_pairs = 0
        num_triplets = 0
        # Check for a straight
        if 1 in vals and 2 in vals and 3 in vals and 4 in vals and 5 in vals and 6 in vals:
            score = 1500
            num_dice_that_scored = 6
            dice_that_scored = [True for x in range(len(diceVals))]
        else:
            score = 0
            if count > 2:
                # key is the die number (1-6) and val is the number of occurances of that die value
                for key, val in vals.items():
                    # Check for 6 of a kind
                    if val == 6:
                        score = 3000
                        num_dice_that_scored = 6
                        for i, use in enumerate(diceToScore):
                            if use and diceVals[i] == key:
                                dice_that_scored[i] = True
                    # Check for 5 of a kind
                    if val == 5:
                        score = 2000
                        num_dice_that_scored = 5
                        for i, use in enumerate(diceToScore):
                            if use and diceVals[i] == key:
                                dice_that_scored[i] = True
                    # Check for 4 of a kind
                    elif val == 4:
                        score = 1000
                        num_dice_that_scored = 4
                        for i, use in enumerate(diceToScore):
                            if use and diceVals[i] == key:
                                dice_that_scored[i] = True
                    # Check for 3 of a kind (triplets)
                    elif val == 3:
                        num_triplets += 1
                        if key == 1:
                            score = 300
                        else:
                            score = 100 * key
                        num_dice_that_scored += 3
                        for i, use in enumerate(diceToScore):
                            if use and diceVals[i] == key:
                                dice_that_scored[i] = True
                    # Check for 2 of a kind (pairs)
                    elif val == 2:
                        num_pairs += 1

            # Find the ones
            if 1 in vals:
                if vals[1] < 3:
                    score += vals[1] * 100
                    num_dice_that_scored += vals[1]
            # Find the fives
            if 5 in vals:
                if vals[5] < 3:
                    score += vals[5] * 50
                    num_dice_that_scored += vals[5]
            # Mark the ones and fives that scored
            for i, use in enumerate(diceToScore):
                if use and ((diceVals[i] == 1) or (diceVals[i] == 5)):
                    dice_that_scored[i] = True

        # Fix score for Three pairs and Two triplets
        if num_triplets == 2:
            score = 2500
        elif num_pairs == 3:
            score = 1500
            num_dice_that_scored = 6
            dice_that_scored = [True for x in range(len(diceVals))]
        
        logging.info(f"score_dice score {score} for diceToScore {diceToScore} num_dice_that_scored {num_dice_that_scored} dice_that_scored {dice_that_scored}")

        return score, num_dice_that_scored, dice_that_scored

    # Roll the dice that aren't _previouslyKeptDice
    # Get the dice values from the dice that weren't rolled from the class variable _diceVals
    # _diceVals is updated based on the new roll
    # Return the a list of values of the dice rolled, list of the previously kept dice, and list of rolled dice
    def roll_dice(self) -> Tuple[list,list]:
        # Determine which dice to roll
        diceToRoll = [True for x in range(self._NDICE)]
        for i in range(self._NDICE):
            diceToRoll[i] = not self._previouslyKeptDice[i]
        
        for i in range(self._NDICE):
            if diceToRoll[i] == True:
                self._diceVals[i] = random.randint(1,6)
                logging.info(f"rolling die {i} value is {self._diceVals[i]}")
 
        logging.info(f"roll_dice dice vals {self._diceVals} previouslyKeptDice {self._previouslyKeptDice}")
        return self._diceVals, self._previouslyKeptDice, diceToRoll

    # Compute the score for all the of dice that weren't previously scored
    # _previouslyKeptDice have already been scored, so score the rest of the dice
    # Return the score
    def bank_score(self) -> int:
        diceToScore = [True for x in range(self._NDICE)]
        for i in range(self._NDICE):
            diceToScore[i] = not self._previouslyKeptDice[i]
        score, numDiceThatScored, scoringDice = FarkleFuncs.score_dice(self._diceVals,diceToScore)

        logging.info(f"bank_score extra points that were banked {score} numDiceThatScored is {numDiceThatScored} scoringDice {scoringDice}")
        return score

# Start main program
if __name__ == "__main__":
    doFlaskLogging.set_up_logger()
    inst = FarkleFuncs()
    
    # Test score dice
    dice = [6, 5, 1, 5, 5, 5]
    keptDice = [True, True, False, True, False, True]
    score, numDiceThatScored, scoringDice = FarkleFuncs.score_dice(dice,keptDice)
    logging.info(f"dice are {dice} keptDice are {keptDice} score is {score} numDiceThatScored is {numDiceThatScored} scoringDice are {scoringDice}")
    # Answer should be 500 points using 3 dice with scoringDice[False, True, False, True, False, True]

    # Smoke test roll dice
    diceVals,previouslyKeptDice,rolledDice = inst.roll_dice()
    logging.info(f"diceVals are {diceVals} previouslyKeptDice are {previouslyKeptDice} rolledDice are {rolledDice}")

    # Smoke test bank
    score = inst.bank_score()
    logging.info(f"score is {score} for {diceVals}")

    doFlaskLogging.clean_up_logger()
