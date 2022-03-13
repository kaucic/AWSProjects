# -*- coding: utf-8 -*-
"""
Created on Sun Sep 26 13:50:26 2021

@author: home
"""

import logging
from FarkleBots import FarkleBots

def run_bot_turns(N,whichPolicy,fname):
    fd = open(fname,'wt')
    inst = FarkleBots()

    sum = 0.0
    maxScore = 0
    for i in range(N):
        turnScore = inst.bot_do_turn(whichPolicy)
        print (f"{i}: turnScore = {turnScore}")
        fd.write(f"{turnScore}\n")
        
        sum += turnScore
        if turnScore > maxScore:
            maxScore = turnScore

    print (f"\nAverage score = {sum/N}")
    print (f"Max score = {maxScore}")
    
    fd.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_bot_turns(5000,1,'scores1.txt')
    #run_bot_turns(5000,2,'scores2.txt')
