from flask import Flask, jsonify, json, Response, request
from flask_cors import CORS

import random

import logging
import doFlaskLogging

from FarkleBots import FarkleBots

application = Flask(__name__)
CORS(application)

gameID = 0
NDICE = 6
NPlayers = 2
# Note: Index 0 is not used, so Player 1 is index 1
player = 1
previouslyKeptDice = [False for x in range(NDICE)]
diceVals = [1 for x in range(NDICE)]
turnScore = 0
totals = [0 for x in range(NPlayers+1)]
playerNames = ['nobody' for x in range(NPlayers+1)]

@application.route("/")
def health_check():
    return jsonify({"message" : "Health check is good.  Try /roll_dice instead."})
    #return "<h1>Health Check is good.  Try /roll_dice instead.</h1>"

@application.route('/init', methods=['GET'])
def init():
    logging.info(f"init GET called")

    global gameID, NDICE, NPlayers, playerNames, player, diceVals, previouslyKeptDice, turnScore, totals
    gameID += 1
    player = 1
    previouslyKeptDice = [False for x in range(NDICE)]
    diceVals = [1 for x in range(NDICE)]
    turnScore = 0
    totals = [0 for x in range(NPlayers+1)]
    playerNames[1] = 'Bob'
    playerNames[2] = 'Ron'

    body = {'gameID' : gameID, 'playerNames' : playerNames, 'player' : player, 'totals' : totals, 'turnScore' : turnScore, 'diceVals' : diceVals, 'previouslyKeptDice' : previouslyKeptDice}
 
    statusCode = 200
    initResponse = {'body' : body, 'statusCode': statusCode}
    
    return jsonify(initResponse)

#@application.route('/roll_dice/<keep1>/<keep2>/<keep3>', methods=['GET', 'POST'])
#def roll_dice(keep1,keep2,keep3):
@application.route('/roll_dice', methods=['GET', 'POST'])
def roll_dice():
    global NDICE, NPlayers, player, previouslyKeptDice, diceVals, turnScore, totals
    
    # GET code is obsolete and no longer works
    # For GET invocations
    if request.method == 'GET':
        logging.info(f"roll_dice GET called")
        # Parse the input parameters
        # Example ?gameID=1&playerID=1&keep1=true&keep2=false&keep3=false
        gID = request.args.get('gameID')
        playerID = request.args.get('playerID')
        logging.info(f"roll_dice GET received: playerID={playerID}")
        # Need to convert string on command line to Boolean
        keep_str = ['false' for x in range(NDICE)]
        keep_str[0] = request.args.get('keep1')
        keep_str[1] = request.args.get('keep2')
        keep_str[2] = request.args.get('keep3')
        logging.info(f"roll_dice GET received: keep1={keep_str[0]} keep2={keep_str[1]} keep3={keep_str[2]}")

        # Convert string values to Boolean
        keptDice = [False for x in range(NDICE)]
        for i in range(NDICE):
            if keep_str[i] == 'true':
                keptDice[i] = True
            else:
                keptDice[i] = False
        logging.info(f"Dice to keep: keep1={keptDice[0]} keep2={keptDice[1]} keep3={keptDice[2]}")

    elif request.method == 'POST':
        logging.info(f"roll_dice POST called")
        data = request.get_json()
        logging.info(f"roll_dice POST received json {data}")

        gID = data['gameID']
        playerID = data['playerID']
        keptDice = data['keptDice']
        logging.info(f"[playerID is {playerID} keptDice is {keptDice}")
    
    else:
        logging.info(f"ERROR in roll_dice, unhandled {request.method} called")

    game = FarkleBots()
    # Check to see if it is the calling clients turn
    if playerID == player:
        # Score the dice that were kept
        if any(keptDice):
            score, scoringDice = game.score_dice(diceVals,keptDice)
            logging.info(f"Scoring the dice that were kept: score is {score} count is {scoringDice}")
            turnScore += score
        # if no dice were kept then it must be the first roll of the turn
        else:
            turnScore = 0

        # Determine which dice to roll
        diceToRoll = [True for x in range(NDICE)]
        for i in range(NDICE):
            diceToRoll[i] = not (previouslyKeptDice[i] or keptDice[i])
        # If all dice have scored, clear flags and roll all dice
        if not any(diceToRoll):
            keptDice = [False for x in range(NDICE)]
            previouslyKeptDice = [False for x in range(NDICE)]
            diceToRoll = [True for x in range(NDICE)]

        for i in range(NDICE):
            if diceToRoll[i] == True:
                diceVals[i] = random.randint(1,6)
                logging.info(f"rolling die {i} value is {diceVals[i]}")
            
        body = { 'gameID' : gID, 'valid' : True, 'diceVals' : diceVals}
            
        # Check for Farkle
        score, scoringDice = game.score_dice(diceVals, diceToRoll)
        logging.info(f"Checking for Farkle: score is {score} count is {scoringDice}")
        if score > 0:
            body['Farkled'] = False;
            for i in range(NDICE):
                previouslyKeptDice[i] = previouslyKeptDice[i] or keptDice[i]
            body['previouslyKeptDice'] = previouslyKeptDice
        else: # Farkled, zero out turn score and pass dice to next player 
            body['Farkled'] = True;  
            turnScore = 0
            keptDice = [False for x in range(NDICE)]
            previouslyKeptDice = [False for x in range(NDICE)]
            player += 1
            if player > NPlayers:
                player = 1
        
        body['player'] = player
        body['turnScore'] = turnScore
        body['previouslyKeptDice'] = previouslyKeptDice

    else:
        logging.info(f"ERROR in roll_dice, playerID is {playerID}, but current player is {player}")
        body = {  'gameID' : gID, 'valid' : False}

    statusCode = 200
    #diceResponse = {**status, **body}
    diceResponse = {'body' : body, 'statusCode': statusCode}

    return jsonify(diceResponse)

@application.route('/bank_score', methods=['GET', 'POST'])
def bank_score():
    global NDICE, NPlayers, player, previouslyKeptDice, diceVals, turnScore, totals

    # For GET invocations
    if request.method == 'GET':
        logging.info(f"bank_score GET called")
        # Parse the input parameters
        # Example ?gameID=1&playerID=2
        gID = request.args.get('gameID')
        playerID = request.args.get('playerID')
        logging.info(f"bank_score GET gameID is {gID} playerID is {playerID}")
        
    elif request.method == 'POST':
        logging.info(f"bank_score POST called")
        data = request.get_json()
        logging.info(f"bank_score POST received json {data}")
        gID = data['gameID']
        playerID = data['playerID']
    
    else:
        logging.info(f"ERROR in bank_score, unhandled {request.method} request")
    
    logging.info(f"Player number {playerID} has ended their turn.  Current Player number is {player}")
    
    game = FarkleBots()
    body = {'gameID' : gID}
    # Check to see if it is the calling clients turn
    if playerID == player:
        # Compute player's total score
        diceToScore = [True for x in range(NDICE)]
        for i in range(NDICE):
            diceToScore[i] = not previouslyKeptDice[i]
        score, scoringDice = game.score_dice(diceVals,diceToScore)
        logging.info(f"Determining points that were banked: score is {score} count is {scoringDice}")

        turnScore += score
        totals[player] += turnScore

        # Next Players turn
        player += 1
        if player > NPlayers:
            player = 1

        # Clear all kept dice
        previouslyKeptDice = [False for x in range(NDICE)]
        
        body['valid'] = True
        body['player'] = player
        body['turnScore'] = turnScore
        body['totals'] = totals
        body['previouslyKeptDice'] = previouslyKeptDice
    
    else:
        body['valid'] = False

    statusCode = 200
    bankResponse = {'body' : body, 'statusCode': statusCode}
    
    return jsonify(bankResponse)

@application.route('/get_game_state', methods=['GET'])
def get_game_state():
    # For GET invocations
    if request.method == 'GET':
        logging.info(f"get_game_state GET called")
        # Parse the input parameters
        # Example ?gameID=1
        gID = request.args.get('gameID')
    else:
        logging.info(f"ERROR in get_game_state, unhandled {request.method} request")
       
    global NDICE, NPlayers, playerNames, player, previouslyKeptDice, diceVals, turnScore, totals
    
    body = { 'gameID' : gID, 'playerNames' : playerNames, 'player' : player, 'totals' : totals, 'turnScore' : turnScore, 'diceVals' : diceVals, 'previouslyKeptDice' : previouslyKeptDice }
    
    statusCode = 200
    gameStateResponse = {'body' : body, 'statusCode': statusCode}
    
    return jsonify(gameStateResponse)

if __name__ == "__main__":
    # Flask defaults to localhost:5000
    # nginx defaults to port 8000
    doFlaskLogging.set_up_logger()
    application.run()
    doFlaskLogging.clean_up_logger()
