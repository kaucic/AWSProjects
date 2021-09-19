# -*- coding: utf-8 -*-
"""
Created on Mon Sep 06 13:50:26 2021

@author: home
"""
from typing import Tuple

import logging
import doFlaskLogging

class Farkle:
    def __init__(self):
        return

    # Method to compute the Farkle score pertaining to the binary vector diceToScore with spots in diceVals
    # Return the score and the dice that scored
    # TODO: complete and fix the scoring and return the dice that scored instead of the number of dice used     
    def score_dice(self, diceVals, diceToScore)  -> Tuple[int,list]:
        count = 0
        dice_that_scored = 0
        vals = {}
        # Populate hash table
        for i in range(len(diceVals)):
            if diceToScore[i] == True:
                count += 1
                if diceVals[i] in vals:
                    vals[diceVals[i]] += 1
                else:
                    vals[diceVals[i]] = 1
        
        
        # Check for a straight
        num_pairs = 0
        num_triplets = 0
        if 1 in vals and 2 in vals and 3 in vals and 4 in vals and 5 in vals and 6 in vals:
            score = 1500
            dice_that_scored = 6
        else:
            score = 0
            if count > 2:
                for key, val in vals.items():
                    if val == 6:
                        score = 3000
                        dice_that_scored = 6
                    if val == 5:
                        score = 2000
                        dice_that_scored = 5
                    elif val == 4:
                        score = 1000
                        dice_that_scored = 4
                    elif val == 3:
                        num_triplets += 1
                        score = 100 * key
                        if key == 1:
                            score = 300
                        dice_that_scored += 3
                    elif val == 2:
                        num_pairs += 1

            if 1 in vals:
                if vals[1] < 3:
                    score += vals[1] * 100
                    dice_that_scored += vals[1]
            if 5 in vals:
                if vals[5] < 3:
                    score += vals[5] * 50
                    dice_that_scored += vals[5]

        # Fix score for Three pairs and Two triplets
        if num_triplets == 2:
            score = 2500
            dice_that_scored = 6
        elif num_pairs == 3:
            score = 1500
            dice_that_scored = 6
        
        return score, dice_that_scored

    def roll_dice(self,keptDice):
        return

    def bank_score(self):
        return

    def bot1_policy(self,diceVals,previouslyKeptDice,turnScore):
        return True

    def bot1_do_turn(self):
        # do roll_dice until Farkle or bank_score
        #   if not Farkle
        #       bank_score or choose dice to roll

        turnScore = 0
        banked = False
        keptDice = [False for x in range(NDICE)]
        
        farkled,diceVals,previouslyKeptDice = self.roll_dice(keptDice)
        while farkled == False and banked == False:
            banked,keptDice = self.bot1_policy(diceVals,previouslyKeptDice,turnScore)
            if banked == False:
                farkled,diceVals,previouslyKeptDice = self.roll_dice(keptDice)
            else:
                turnScore,totals = self.bank_score()

        return turnScore,totals

# Start main program
if __name__ == "__main__":
    doFlaskLogging.set_up_logger()
    inst = Farkle()
    dice = [6, 5, 1, 5, 5, 5]
    keptDice = [True, True, False, True, True, True]
    score, scoringDice = inst.scoreDice(dice,keptDice)
    logging.info(f"dice are {dice} keptDice are {keptDice} score is {score} count is {scoringDice}")
    doFlaskLogging.clean_up_logger()
