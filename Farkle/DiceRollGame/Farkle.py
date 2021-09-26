# -*- coding: utf-8 -*-
"""
Created on Mon Sep 06 13:50:26 2021

@author: home
"""

from typing import Tuple

import random
from time import sleep

import logging
import doFlaskLogging

NDICE = 6

class Farkle:
    def __init__(self):
        self._keptDiceVals = [6 for x in range(NDICE)]
        self.clear_previouslyKeptDice()       
        return

    def get_previouslyKeptDice(self):
        return self._previouslyKeptDice

    def clear_previouslyKeptDice(self):
        self._previouslyKeptDice = [False for x in range(NDICE)]
        return self._previouslyKeptDice

    def update_previouslyKeptDice(self,keptDice):
        # Update previouslyKeptDice
        for i in range(NDICE):
            self._previouslyKeptDice[i] = self._previouslyKeptDice[i] or keptDice[i]
        return self._previouslyKeptDice

    # Method to compute the Farkle score pertaining to the binary vector diceToScore with spots in diceVals
    # Return the score and the dice that scored
    # TODO: complete and fix the scoring and return the dice that scored instead of the number of dice used     
    def score_dice(self, diceVals, diceToScore) -> Tuple[int,list]:
        count = 0
        diceThatScored = 0
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
            diceThatScored = 6
        else:
            score = 0
            if count > 2:
                for key, val in vals.items():
                    if val == 6:
                        score = 3000
                        diceThatScored = 6
                    if val == 5:
                        score = 2000
                        diceThatScored = 5
                    elif val == 4:
                        score = 1000
                        diceThatScored = 4
                    elif val == 3:
                        num_triplets += 1
                        score = 100 * key
                        if key == 1:
                            score = 300
                        diceThatScored += 3
                    elif val == 2:
                        num_pairs += 1

            if 1 in vals:
                if vals[1] < 3:
                    score += vals[1] * 100
                    diceThatScored += vals[1]
            if 5 in vals:
                if vals[5] < 3:
                    score += vals[5] * 50
                    diceThatScored += vals[5]

        # Fix score for Three pairs and Two triplets
        if num_triplets == 2:
            score = 2500
            diceThatScored = 6
        elif num_pairs == 3:
            score = 1500
            diceThatScored = 6
        
        logging.info(f"score_dice score {score} for diceToScore {diceToScore} diceThatScored {diceThatScored}")
        return score, diceThatScored

    # Roll the dice that aren't previouslyKeptDice
    # As a side effect update the class variable _keptDiceVals
    # Return the a list of values of the dice rolled, list of the previously kept dice, and list of rolled dice
    def roll_dice(self) -> Tuple[list,list]:
        # Determine which dice to roll
        diceToRoll = [True for x in range(NDICE)]
        for i in range(NDICE):
            diceToRoll[i] = not self._previouslyKeptDice[i]
        
        for i in range(NDICE):
            if diceToRoll[i] == True:
                self._keptDiceVals[i] = random.randint(1,6)
                logging.info(f"rolling die {i} value is {self._keptDiceVals[i]}")
 
        logging.info(f"roll_dice dice vals {self._keptDiceVals} previouslyKeptDice {self._previouslyKeptDice}")
        return self._keptDiceVals, self._previouslyKeptDice, diceToRoll

    # Compute the score for all the of dice that weren't previously scored
    # _previouslyKeptDice have already been scored, so score the rest of the dice
    # As a side effect, reset the class variable _previouslyKeptDice
    # Return the score
    def bank_score(self) -> int:
        diceToScore = [True for x in range(NDICE)]
        for i in range(NDICE):
            diceToScore[i] = not self._previouslyKeptDice[i]
        score, scoringDice = self.score_dice(self._keptDiceVals,diceToScore)
        self.clear_previouslyKeptDice()

        logging.info(f"bank_score extra points that were banked {score} count is {scoringDice}")
        return score

    # Determine whether to stop rolling and bank points or
    # to continue rolling the dice including which dice to keep
    # Return bank (True) or roll (False) and list of which dice to keep
    def bot1_policy(self,diceVals,diceToPickFrom,previouslyKeptDice,turnScore) -> Tuple[bool,list]:
        logging.info(f"bot1_policy called with diceVals {diceVals} diceToPickFrom {diceToPickFrom} previouslyKeptDice {previouslyKeptDice} starting turnScore {turnScore}")
        
        bank = True
        diceToKeep = [False for x in range(NDICE)]
        numDiceUsed = sum(diceToPickFrom)
        score, scoringDice = self.score_dice(diceVals,diceToPickFrom)
        
        # If all NDICE dice have scored and you are < 3000 keep rolling otherwise stop/bank
        if scoringDice == numDiceUsed:
            if turnScore + score < 3000:
                logging.info(f"bot1_policy all dice scored, rolling all dice, total score {turnScore + score} scoringDice {scoringDice}")
                bank = False
                diceToKeep = diceToPickFrom
            else:
                logging.info(f"bot1_policy all dice scored, stopping, total score {turnScore + score} scoringDice {scoringDice}")
                bank = True
                diceToKeep = diceToPickFrom
        # If not all dice have scored, stop if >= 500
        elif turnScore + score >= 500:
            logging.info(f"bot1_policy more than 500, stopping, total score {turnScore + score} scoringDice {scoringDice}")
            bank = True
            diceToKeep = diceToPickFrom
        # Keep the first 1 or 5 and roll the rest of the dice
        else:
            found1 = -1
            found5 = -1
            i = 0
            while i < NDICE and found1 == -1:
                if diceToPickFrom[i]:
                    if diceVals[i] == 1:
                        found1 = i
                    elif diceVals[i] == 5:
                        found5 = i
                i += 1

            if found1 != -1:
                logging.info(f"bot1_policy 1 found at die {found1}, rolling, total score {turnScore + 100} scoringDice 1")
                bank = False
                diceToKeep[found1] = True
            elif found5 != -1:
                logging.info(f"bot1_policy 5 found at die {found5}, rolling, total score {turnScore + 50} scoringDice 1")
                bank = False
                diceToKeep[found5] = True

        logging.info(f"bot1_policy returning bank {bank} diceToKeep {diceToKeep}")
        return bank, diceToKeep

    # Select the appropriate policy to use based on whichPolicy selected
    def bot_policy(self,whichPolicy,diceVals,diceToPickFrom,previouslyKeptDice,turnScore) -> Tuple[bool,list]:
        if whichPolicy == 1:
            return self.bot1_policy(diceVals,diceToPickFrom,previouslyKeptDice,turnScore)
        else:
            logging.error(f"ERROR in bot_policy, whichPolicy is {whichPolicy}")
    
    # Do a complete turn using policy specified by whichPolicy
    # Return the score for the turn
    def bot_do_turn(self,whichPolicy) -> int:
        # do roll_dice until Farkle or bank_score
        #   if not Farkle
        #       bank_score or choose dice to roll

        turnScore = 0
        banked = False

        diceVals,previouslyKeptDice,rolledDice = self.roll_dice()
        score,diceThatScored = self.score_dice(diceVals,rolledDice)
        farkled = score == 0
        if farkled == True:
            logging.info(f"You Farkled on your first roll!!")
            # Sleep for 3 seconds to give time for browswer get_game_state to update
            sleep(3.0)
        
        while farkled == False and banked == False:
            banked,keptDice = self.bot_policy(whichPolicy,diceVals,rolledDice,previouslyKeptDice,turnScore)
   
            if banked == False:
                # Determine how many points the selected dice are worth
                score,diceThatScored = self.score_dice(diceVals,keptDice)
                turnScore += score
                logging.info(f"bot_do_turn You got {score} points for keeping {keptDice} turnScore {turnScore}")
                
                # Append keptDice to previouslyKeptDice
                previouslyKeptDice = self.update_previouslyKeptDice(keptDice)
                
                # If all dice have scored, clear previouslyKeptDice and roll all dice
                if all(previouslyKeptDice):
                    self.clear_previouslyKeptDice()
                    
                diceVals,previouslyKeptDice,rolledDice = self.roll_dice()
                # check for Farkle for the dice that were rolled
                score,diceThatScored = self.score_dice(diceVals,rolledDice)
                farkled = score == 0
            else:
                score = self.bank_score()
                turnScore += score

            # Sleep for 3 seconds to give time for browswer get_game_state to update
            sleep(1./1000)

        if farkled == True:
            turnScore = 0
            logging.info(f"You Farkled!!")
            
        logging.info(f"bot_turn returning turnScore {turnScore}")
        return turnScore

# Start main program
if __name__ == "__main__":
    doFlaskLogging.set_up_logger()
    inst = Farkle()
    dice = [6, 5, 1, 5, 5, 5]
    keptDice = [True, True, False, True, True, True]
    score, scoringDice = inst.score_dice(dice,keptDice)
    logging.info(f"dice are {dice} keptDice are {keptDice} score is {score} count is {scoringDice}")
    
    botScore = inst.bot_do_turn(1)
    logging.info(f"bot scored {botScore} points")
    doFlaskLogging.clean_up_logger()
