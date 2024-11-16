 # -*- coding: utf-8 -*-
"""
Created on Mon Sep 06 13:50:26 2021

@author: home
"""

from typing import Tuple

#from time import sleep
from FarkleFuncs import FarkleFuncs

import logging

class FarkleBots:
    def __init__(self):
        return
      
    # Method to determine all subset of dice combinations that score points pertaining to the binary vector diceToScore with spots in diceVals
    # Return lists of the scores, the # of dice that scored, and the dice that scored bool list for those dice for 1 to N dice kept   
    @staticmethod
    def get_scoring_possibilities(diceVals, diceToScore) -> Tuple[list,list,list]:
        logging.info(f"get_scoring_possibilities called with diceVals {diceVals} and diceToScore {diceToScore}")

        #TODO need to compute all possibilities and see which ones score by calling score_dice
        score, numDiceThatScored, scoringDice = FarkleFuncs.score_dice(diceVals,diceToScore)
        return

    # Determine whether to stop rolling and bank points or
    # to continue rolling the dice including which dice to keep
    # Return bank (True) or roll (False) and list of which dice to keep
    # Currently the players' currents scores (totals) and the bot's index (botIdx) aren't used
    @staticmethod
    def bot1_policy(diceVals,previouslyKeptDice,turnScore,totals,botIdx) -> Tuple[bool,list]:
        logging.info(f"bot1_policy called with diceVals {diceVals} previouslyKeptDice {previouslyKeptDice} starting turnScore {turnScore}")
        
        bank = True
        ndice = len(diceVals)
        diceToKeep = [False for x in range(ndice)]
        diceToPickFrom = [False for x in range(ndice)]
        for i in range(ndice):
            diceToPickFrom[i] = not previouslyKeptDice[i]
        numDiceToUse = sum(diceToPickFrom)
        score, numDiceThatScored, scoringDice = FarkleFuncs.score_dice(diceVals,diceToPickFrom)
        
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
    @staticmethod
    def bot2_policy(diceVals,previouslyKeptDice,turnScore,totals,botIdx) -> Tuple[bool,list]:
        logging.info(f"bot2_policy called with diceVals {diceVals} previouslyKeptDice {previouslyKeptDice} starting turnScore {turnScore}")
        
        diceToPickFrom = [False for x in range(len(diceVals))]
        for i in range(len(diceVals)):
            diceToPickFrom[i] = not previouslyKeptDice[i]
        
        #The strategy is to keep all dice that scored
        score, numDiceThatScored, diceToKeep = FarkleFuncs.score_dice(diceVals,diceToPickFrom)
        
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
    @staticmethod
    def bot_policy(whichPolicy,diceVals,previouslyKeptDice,turnScore,totals,botIdx) -> Tuple[bool,list]:
        whichPolicy = 1
        if whichPolicy == 1:
            return FarkleBots.bot1_policy(diceVals,previouslyKeptDice,turnScore,totals,botIdx)
        elif whichPolicy == 2:
            return FarkleBots.bot2_policy(diceVals,previouslyKeptDice,turnScore,totals,botIdx)
        else:
            logging.error(f"ERROR in bot_policy, whichPolicy is {whichPolicy}")
    
    # Do a complete turn using policy specified by whichPolicy
    # Inputs: totals is list of each player's score, totals[0] is not used
    # botIdx is index of the bot in the totals list
    # Currently the players' scores aren't used 
    # Class variables _keptDiceVals and _previouslyKeptDice are modified during the turn
    # Return the score for the turn
    
    

    
    def old_bot_do_turn(self,totals,botIdx,whichPolicy=1) -> int: 
        # do roll_dice until Farkle or bank_score
        #   if not Farkle
        #       Use policy to bank_score or choose dice to roll

        diceObj = FarkleFuncs();
        turnScore = 0
        banked = False

        # Always roll the dice to start the turn
        

        diceVals,previouslyKeptDice,rolledDice = diceObj.roll_dice()
        diceObj.set_keptDiceVals(diceVals)  # update class variable
        score, numDiceThatScored, scoringDice = FarkleFuncs.score_dice(diceVals,rolledDice)
        farkled = score == 0
        if farkled == True:
            logging.info(f"You Farkled on your first roll!!")
            # Sleep for 3 seconds to give time for player to see that he Farkled
            #sleep(3)
        
        while farkled == False and banked == False:
            banked,keptDice = FarkleBots.bot_policy(whichPolicy,diceVals,previouslyKeptDice,turnScore,totals,botIdx)
   
            if banked == False:
                # Determine how many points the selected dice are worth
                score, numDiceThatScored, scoringDice = FarkleFuncs.score_dice(diceVals,keptDice)
                turnScore += score
                logging.info(f"bot_do_turn You got {score} points for keeping {keptDice} turnScore {turnScore}")
                
                # Append keptDice to previouslyKeptDice
                previouslyKeptDice = diceObj.update_previouslyKeptDice(keptDice)
                
                # If all dice have scored, clear previouslyKeptDice and roll all dice
                if all(previouslyKeptDice):
                    diceObj.clear_previouslyKeptDice()  # clear class variable
                    
                diceVals,previouslyKeptDice,rolledDice = diceObj.roll_dice()
                diceObj.set_keptDiceVals(diceVals)  # update class variable
                # check for Farkle for the dice that were rolled
                score, numDiceThatScored, scoringDice = FarkleFuncs.score_dice(diceVals,rolledDice)
                farkled = score == 0
            else:
                score = diceObj.bank_score()
                turnScore += score
                diceObj.clear_previouslyKeptDice()  # clear class variable

        if farkled == True:
            turnScore = 0
            diceObj.clear_previouslyKeptDice()  # clear class variable
            logging.info(f"You Farkled!!")
            
        logging.info(f"bot_turn {whichPolicy} returning turnScore {turnScore}")
        return turnScore

# Start main program
if __name__ == "__main__":
    doFlaskLogging.set_up_logger()
    inst = FarkleBots()
    totals = [75 for x in range(3)]
    botIdx = 2
    
    botScore = inst.bot_do_turn(totals,botIdx,1)
    logging.info(f"bot1 scored {botScore} points")

    botScore = inst.bot_do_turn(totals,botIdx,2)
    logging.info(f"bot2 scored {botScore} points")
    doFlaskLogging.clean_up_logger()
 