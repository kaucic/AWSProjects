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

class FarkleBots:
    def __init__(self,NDICE=6):
        self._NDICE = NDICE
        self._keptDiceVals = [5 for x in range(self._NDICE)]
        self.clear_previouslyKeptDice()       
        return

    def set_keptDiceVals(self,diceVals):
        self._keptDiceVals = diceVals
        return

    def get_keptDiceVals(self) -> list:
        return self._keptDiceVals
        
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
    def score_dice(self, diceVals, diceToScore) -> Tuple[int,int,list]:
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

    # Method to determine all subset of dice combinations that score points pertaining to the binary vector diceToScore with spots in diceVals
    # Return lists of the scores, the # of dice that scored, and the dice that scored bool list for those dice for 1 to N dice kept   
    def get_scoring_possibilities(self, diceVals, diceToScore) -> Tuple[list,list,list]:
        return

    # Roll the dice that aren't _previouslyKeptDice
    # Get the dice values from the dice that weren't rolled from the class variable _keptDiceVals
    # Return the a list of values of the dice rolled, list of the previously kept dice, and list of rolled dice
    def roll_dice(self) -> Tuple[list,list]:
        diceVals = self._keptDiceVals
        # Determine which dice to roll
        diceToRoll = [True for x in range(self._NDICE)]
        for i in range(self._NDICE):
            diceToRoll[i] = not self._previouslyKeptDice[i]
        
        for i in range(self._NDICE):
            if diceToRoll[i] == True:
                diceVals[i] = random.randint(1,6)
                logging.info(f"rolling die {i} value is {diceVals[i]}")
 
        logging.info(f"roll_dice dice vals {diceVals} previouslyKeptDice {self._previouslyKeptDice}")
        return diceVals, self._previouslyKeptDice, diceToRoll

    # Compute the score for all the of dice that weren't previously scored
    # _previouslyKeptDice have already been scored, so score the rest of the dice
    # Return the score
    def bank_score(self) -> int:
        diceToScore = [True for x in range(self._NDICE)]
        for i in range(self._NDICE):
            diceToScore[i] = not self._previouslyKeptDice[i]
        score, numDiceThatScored, scoringDice = self.score_dice(self._keptDiceVals,diceToScore)

        logging.info(f"bank_score extra points that were banked {score} numDiceThatScored is {numDiceThatScored} scoringDice {scoringDice}")
        return score

    # Determine whether to stop rolling and bank points or
    # to continue rolling the dice including which dice to keep
    # Return bank (True) or roll (False) and list of which dice to keep
    def bot1_policy(self,diceVals,previouslyKeptDice,turnScore) -> Tuple[bool,list]:
        logging.info(f"bot1_policy called with diceVals {diceVals} previouslyKeptDice {previouslyKeptDice} starting turnScore {turnScore}")
        
        bank = True
        ndice = len(diceVals)
        diceToKeep = [False for x in range(ndice)]
        diceToPickFrom = [False for x in range(ndice)]
        for i in range(ndice):
            diceToPickFrom[i] = not previouslyKeptDice[i]
        numDiceToUse = sum(diceToPickFrom)
        score, numDiceThatScored, scoringDice = self.score_dice(diceVals,diceToPickFrom)
        
        # If all NDICE dice have scored and you are < 3000 keep rolling otherwise stop/bank
        if numDiceThatScored == numDiceToUse:
            if turnScore + score < 3000:
                logging.info(f"bot1_policy all dice scored, rolling all dice, total score {turnScore + score} scoringDice {scoringDice}")
                bank = False
                diceToKeep = scoringDice
            else:
                logging.info(f"bot1_policy all dice scored, stopping, total score {turnScore + score} scoringDice {scoringDice}")
                bank = True
                diceToKeep = scoringDice
        # If not all dice have scored, stop if >= 400
        elif turnScore + score >= 400:
            logging.info(f"bot1_policy greater than or equal to 400, stopping, total score {turnScore + score} scoringDice {scoringDice}")
            bank = True
            diceToKeep = scoringDice
        # Keep the first 1 or 5 and roll the rest of the dice
        else:
            found1 = -1
            found5 = -1
            i = 0
            while i < ndice and found1 == -1:
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

    # Determine whether to stop rolling and bank points or
    # to continue rolling the dice including which dice to keep
    # Return bank (True) or roll (False) and list of which dice to keep# example call:
    #       bank, diceToKeep = game.bot2_policy(diceVals,keptDice,turnScore)
    def bot2_policy(self,diceVals,previouslyKeptDice,turnScore) -> Tuple[bool,list]:
        logging.info(f"bot2_policy called with diceVals {diceVals} previouslyKeptDice {previouslyKeptDice} starting turnScore {turnScore}")
        
        diceToPickFrom = [False for x in range(len(diceVals))]
        for i in range(len(diceVals)):
            diceToPickFrom[i] = not previouslyKeptDice[i]
        
        #The strategy is to keep all dice that scored
        score, numDiceThatScored, diceToKeep = self.score_dice(diceVals,diceToPickFrom)
        
        newTurnScore = turnScore + score
        
        numDiceLeft = 6 - (sum(diceToKeep) + sum(previouslyKeptDice))
        if numDiceLeft == 0:
            numDiceLeft = 6
        print(f"newTurnScore: {newTurnScore}")
        print(f"numDiceLeft: {numDiceLeft}")

        if numDiceLeft == 6 and newTurnScore >= 3000:
            bank = True
        elif numDiceLeft == 5 and newTurnScore >= 1000:
            bank = True
        elif numDiceLeft == 4 and newTurnScore >= 300:
            bank = True
        elif numDiceLeft < 4:
            bank = True

        else:  #Roll again instead of banking
            print("Rolling again!")
            bank = False

        return bank, diceToKeep
    
    # Select the appropriate policy to use based on whichPolicy selected
    def bot_policy(self,whichPolicy,diceVals,previouslyKeptDice,turnScore) -> Tuple[bool,list]:
        if whichPolicy == 1:
            return self.bot1_policy(diceVals,previouslyKeptDice,turnScore)
        elif whichPolicy == 2:
            return self.bot2_policy(diceVals,previouslyKeptDice,turnScore)
        else:
            logging.error(f"ERROR in bot_policy, whichPolicy is {whichPolicy}")
    
    # Do a complete turn using policy specified by whichPolicy
    # Class variables _keptDiceVals and _previouslyKeptDice are modified during the turn
    # Return the score for the turn
    def bot_do_turn(self,whichPolicy=1) -> int:
        # do roll_dice until Farkle or bank_score
        #   if not Farkle
        #       Use policy to bank_score or choose dice to roll

        turnScore = 0
        banked = False

        diceVals,previouslyKeptDice,rolledDice = self.roll_dice()
        self.set_keptDiceVals(diceVals)  # update class variable
        score, numDiceThatScored, scoringDice = self.score_dice(diceVals,rolledDice)
        farkled = score == 0
        if farkled == True:
            logging.info(f"You Farkled on your first roll!!")
            # Sleep for 3 seconds to give time for player to see that he Farkled
            #sleep(3)
        
        while farkled == False and banked == False:
            banked,keptDice = self.bot_policy(whichPolicy,diceVals,previouslyKeptDice,turnScore)
   
            if banked == False:
                # Determine how many points the selected dice are worth
                score, numDiceThatScored, scoringDice = self.score_dice(diceVals,keptDice)
                turnScore += score
                logging.info(f"bot_do_turn You got {score} points for keeping {keptDice} turnScore {turnScore}")
                
                # Append keptDice to previouslyKeptDice
                previouslyKeptDice = self.update_previouslyKeptDice(keptDice)
                
                # If all dice have scored, clear previouslyKeptDice and roll all dice
                if all(previouslyKeptDice):
                    self.clear_previouslyKeptDice()  # clear class variable
                    
                diceVals,previouslyKeptDice,rolledDice = self.roll_dice()
                self.set_keptDiceVals(diceVals)  # update class variable
                # check for Farkle for the dice that were rolled
                score, numDiceThatScored, scoringDice = self.score_dice(diceVals,rolledDice)
                farkled = score == 0
            else:
                score = self.bank_score()
                turnScore += score
                self.clear_previouslyKeptDice()  # clear class variable

        if farkled == True:
            turnScore = 0
            self.clear_previouslyKeptDice()  # clear class variable
            logging.info(f"You Farkled!!")
            
        logging.info(f"bot_turn returning turnScore {turnScore}")
        return turnScore

# Start main program
if __name__ == "__main__":
    doFlaskLogging.set_up_logger()
    inst = FarkleBots()
    dice = [6, 5, 1, 5, 5, 5]
    keptDice = [True, True, False, True, False, True]
    score, numDiceThatScored, scoringDice = inst.score_dice(dice,keptDice)
    logging.info(f"dice are {dice} keptDice are {keptDice} score is {score} numDiceThatScored is {numDiceThatScored} scoringDice are {scoringDice}")
    # Answer should be 500 points using 3 dice with scoringDice[False, True, False, True, False, True]
    
    botScore = inst.bot_do_turn(1)
    logging.info(f"bot1 scored {botScore} points")

    botScore = inst.bot_do_turn(2)
    logging.info(f"bot2 scored {botScore} points")
    doFlaskLogging.clean_up_logger()
