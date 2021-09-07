# -*- coding: utf-8 -*-
"""
Created on Mpn Sep 06 13:50:26 2021

@author: home
"""
from typing import Tuple

import logging
import doFlaskLogging

class Farkle:
    def __init__(self):
        return

    # Method to compute the Farkle score pertaining to the binary vector diceToScore
    # Return the score and the dice that scored
    # TODO: complete and fix the scoring and return the dice that scored instead of the number of dice used     
    def scoreDice(self, diceVals, diceToScore)  -> Tuple[int,list]:
        count = 0
        vals = {}
        # Populate hash table
        for i in range(len(diceVals)):
            if diceToScore[i] == True:
                count += 1
                if diceVals[i] in vals:
                    vals[diceVals[i]] += 1
                else:
                    vals[diceVals[i]] = 1
        
        score = 0
        if count > 2:
            for key, val in vals.items():
                if val == 6:
                    score = 3000
                if val == 5:
                    score = 2000
                elif val == 4:
                    score = 1000
                elif val == 3:
                    score = 100 * key
                    if key == 1:
                        score = 300

        if 1 in vals:
            if vals[1] < 3:
                score += vals[1] * 100
        if 5 in vals:
            if vals[5] < 3:
                score += vals[5] * 50
        
        return score, count


# Start main program
if __name__ == "__main__":
    doFlaskLogging.set_up_logger()
    inst = Farkle()
    dice = [6, 5, 1, 5, 5, 5]
    keptDice = [True, True, False, True, True, True]
    score, scoringDice = inst.scoreDice(dice,keptDice)
    logging.info(f"dice are {dice} score is {score} count is {scoringDice}")
    doFlaskLogging.clean_up_logger()
