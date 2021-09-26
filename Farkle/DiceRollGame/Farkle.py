# -*- coding: utf-8 -*-
"""
Created on Mon Sep 06 13:50:26 2021

@author: home
"""
from typing import Tuple

import random

import logging
import doFlaskLogging

NDICE = 6

class Farkle:
    def __init__(self):
        self._previouslyKeptDice = [False for x in range(NDICE)]
        self._keptDiceVals = [1 for x in range(NDICE)]
        
        return

    # Method to compute the Farkle score pertaining to the binary vector diceToScore with spots in diceVals
    # Return the score and the dice that scored
    # TODO: complete and fix the scoring and return the dice that scored instead of the number of dice used     
    def score_dice(self, diceVals, diceToScore) -> Tuple[int,list]:
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
        
        logging.info(f"score_dice score {score} for diceToScore {diceToScore}")
        return score, dice_that_scored

    # Roll the dice that aren't keptDice or previouslyKeptDice
    # If all dice are kept or previously kept then roll all NDICE dice
    # As a side effect update the class variables _previouslyKeptDice and _keptDiceVals
    # Return the a list of values of the dice rolled and a list of the kept dice
    def roll_dice(self,keptDice) -> Tuple[list,list]:
        # Determine which dice to roll
        diceToRoll = [True for x in range(NDICE)]
        for i in range(NDICE):
            diceToRoll[i] = not (self._previouslyKeptDice[i] or keptDice[i])
        
        # If all dice have scored, clear flags and roll all dice
        if not any(diceToRoll):
            self._previouslyKeptDice = [False for x in range(NDICE)]
            diceToRoll = [True for x in range(NDICE)]

        for i in range(NDICE):
            if diceToRoll[i] == True:
                self._keptDiceVals[i] = random.randint(1,6)
                logging.info(f"rolling die {i} value is {self._keptDiceVals[i]}")
 
        logging.info(f"roll_dice dice vals {self._keptDiceVals} previouslyKeptDice {self._previouslyKeptDice}")
        return self._keptDiceVals, self._previouslyKeptDice

    # Compute the score for all the of dice that weren't previously scored
    # _previouslyKeptDice have already been scored, so score the rest of the dice
    # As a side effect, reset the class variable _previouslyKeptDice
    # Return the score
    def bank_score(self) -> int:
        diceToScore = [True for x in range(NDICE)]
        for i in range(NDICE):
            diceToScore[i] = not self._previouslyKeptDice[i]
        score, scoringDice = self.score_dice(self._keptDiceVals,diceToScore)
        logging.info(f"bank_score extra points that were banked {score} count is {scoringDice}")

        return score

    # Determine whether to stop rolling and bank points or
    # to continue rolling the dice including which dice to keep
    # Return bank (True) or roll (False) and list of which dice to keep
    def bot1_policy(self,diceVals,previouslyKeptDice,turnScore) -> Tuple[bool,list]:
        #bank = True
        diceToKeep = [True for x in range(NDICE)]
        bank = False
        diceToKeep[2] = False

        logging.info(f"bot1_policy bank {bank} diceToKeep {diceToKeep}")
        return bank, diceToKeep

    # Do a complete turn using policy specified by policy
    # Return the score for the turn
    def bot_do_turn(self) -> int:
        # do roll_dice until Farkle or bank_score
        #   if not Farkle
        #       bank_score or choose dice to roll

        turnScore = 0
        banked = False
        keptDice = [False for x in range(NDICE)]
        diceToScore = [True for x in range(NDICE)]

        diceVals,previouslyKeptDice = self.roll_dice(keptDice)
        score,dice_that_scored = self.score_dice(diceVals,diceToScore)
        farkled = score == 0
        if farkled == True:
            logging.info(f"You Farkled on your first roll!!")
        while farkled == False and banked == False:
            banked,keptDice = self.bot1_policy(diceVals,previouslyKeptDice,turnScore)
            if banked == False:
                # Determine how many points the selected dice are worth
                score,dice_that_scored = self.score_dice(diceVals,keptDice)
                logging.info(f"You got {score} points for keeping {keptDice}")
                turnScore += score
                diceVals,previouslyKeptDice = self.roll_dice(keptDice)
                # check for Farkle for the dice that were rolled
                for i in range(NDICE):
                    diceToScore[i] = not (previouslyKeptDice[i] or keptDice[i])
                score,dice_that_scored = self.score_dice(diceVals,diceToScore)
                farkled = score == 0
            else:
                score = self.bank_score()
                turnScore += score

        if farkled == True:
            turnScore = 0
            logging.info(f"You Farkled!!")
            
        logging.info(f"bot_turn turnScore {turnScore}")
        return turnScore

# Start main program
if __name__ == "__main__":
    doFlaskLogging.set_up_logger()
    inst = Farkle()
    dice = [6, 5, 1, 5, 5, 5]
    keptDice = [True, True, False, True, True, True]
    score, scoringDice = inst.score_dice(dice,keptDice)
    logging.info(f"dice are {dice} keptDice are {keptDice} score is {score} count is {scoringDice}")
    
    botScore = inst.bot_do_turn()
    logging.info(f"bot scored {botScore} points")
    doFlaskLogging.clean_up_logger()
