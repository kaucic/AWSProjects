# -*- coding: utf-8 -*-
"""
Created on Sun Sep 26 13:50:26 2021

@author: home
"""

import logging
from FarkleBots import FarkleBots
import math

def run_bot_turns(N,whichPolicy,fname):
    fd = open(fname,'wt')
    inst = FarkleBots()
    totals = [1010 for x in range(3)]
    botIdx = 1

    sum = 0.0
    sumSquared = 0.0
    maxScore = 0
    for i in range(N):
        turnScore = inst.bot_do_turn(totals,botIdx,whichPolicy)
        print (f"{i}: turnScore = {turnScore}")
        fd.write(f"{turnScore}\n")
        
        sum += turnScore
        sumSquared += (turnScore * turnScore)
        if turnScore > maxScore:
            maxScore = turnScore

    ave = sum/N
    var = sumSquared/N - ave*ave
    print (f"\nAverage score = {sum/N}")
    print (F"std = {math.sqrt(var)}")
    print (f"Max score = {maxScore}")
    
    fd.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_bot_turns(100,1,'scores1.txt')
    #run_bot_turns(5000,2,'scores2.txt')
