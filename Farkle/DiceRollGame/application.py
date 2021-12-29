from flask import Flask, jsonify, json, Response, request
from flask_cors import CORS

import random
from time import sleep

import logging
import doFlaskLogging

from FarkleBots import FarkleBots

application = Flask(__name__)
CORS(application)

NDICE = 6
gameID = 0
NPlayers = 2
# Note: Index 0 is not used, so Player 1 is index 1
player = 1 # Global variable representing whose turn it is
game = FarkleBots()  # Contains class variables _previouslyKeptDice and _keptDiceVals
rolledOnceOrMore = False;  # Global variable to identify a player's first roll
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

    global gameID, NPlayers, playerNames, player, game, rolledOnceOrMore, turnScore, totals

    gameID += 1
    NPlayers = 2
    playerNames[1] = 'Bob'
    playerNames[2] = 'Ron'
    player = 1 # Global variable representing whose turn it is.  Will be replaced with a game_setup API
    game = FarkleBots()
    rolledOnceOrMore = False # Global variable to identify a player's first roll
    previouslyKeptDice = game.get_previouslyKeptDice()
    diceVals = game.get_keptDiceVals()
    turnScore = 0
    totals = [0 for x in range(NPlayers+1)]
   
    body = {'gameID' : gameID, 'NPlayers' : NPlayers, 'playerNames' : playerNames, 'player' : player,  'rolledOnceOrMore' : rolledOnceOrMore, 'totals' : totals, 'turnScore' : turnScore, 'diceVals' : diceVals, 'previouslyKeptDice' : previouslyKeptDice}
 
    statusCode = 200
    initResponse = {'body' : body, 'statusCode': statusCode}
    
    # Test code to try out the bot
    #logging.info("init calling bot_do_turn")
    #foo = game.bot_do_turn()
    #logging.info("init returned from bot_do_turn")
    #sleep(00)

    return jsonify(initResponse)

#@application.route('/roll_dice/<keep1>/<keep2>/<keep3>', methods=['GET', 'POST'])
#def roll_dice(keep1,keep2,keep3):
@application.route('/roll_dice', methods=['GET', 'POST'])
def roll_dice():
    global player, game, rolledOnceOrMore, turnScore
    errMsg = ""
    
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
  
    # Check to see if it is the calling clients turn
    if playerID == player:
        if rolledOnceOrMore == False:
            previouslyKeptDice = game.clear_previouslyKeptDice();
            turnScore = 0
        # Score the dice that were kept
        elif any(keptDice):
            diceVals = game.get_keptDiceVals()
            score, scoringDice = game.score_dice(diceVals,keptDice)
            previouslyKeptDice = game.update_previouslyKeptDice(keptDice)
            logging.info(f"Scoring the dice that were kept: score is {score} count is {scoringDice}")
            turnScore += score
        # if no dice were kept then the user made an error
        else:
            errMsg = f"ERROR in roll_dice, playerID is {playerID} and no dice were kept"
            logging.error(errMsg)
            previouslyKeptDice = game.get_previouslyKeptDice()
                
        # If all dice have scored, clear previouslyKeptDice and roll all dice
        if all(previouslyKeptDice):
            game.clear_previouslyKeptDice()  # clear class variable

        diceVals,previouslyKeptDice,rolledDice = game.roll_dice()
        rolledOnceOrMore = True
        game.set_keptDiceVals(diceVals)  # update class variable
                          
        body = { 'gameID' : gID, 'valid' : True, 'diceVals' : diceVals}
            
        # Check for Farkle
        score, scoringDice = game.score_dice(diceVals,rolledDice)
        logging.info(f"Checking for Farkle: score is {score} count is {scoringDice}")
        if score > 0:
            body['Farkled'] = False;
            body['previouslyKeptDice'] = previouslyKeptDice
        else: # Farkled, zero out turn score and pass dice to next player 
            body['Farkled'] = True;  
            turnScore = 0
            previouslyKeptDice = game.clear_previouslyKeptDice()  # clear class variable
            rolledOnceOrMore = False # reset global variable when the turn passes to the next player
            player += 1 # Update global variable for whose turn it is
            if player > NPlayers:
                player = 1
        
        body['player'] = player
        body['turnScore'] = turnScore
        body['previouslyKeptDice'] = previouslyKeptDice
        body['rolledOnceOrMore'] = rolledOnceOrMore

    else:
        errMsg = f"ERROR in roll_dice, playerID is {playerID}, but current player is {player}"
        logging.error(errMsg)
        body = {  'gameID' : gID, 'valid' : False, 'errMsg' : errMsg}

    statusCode = 200
    diceResponse = {'body' : body, 'statusCode': statusCode}

    return jsonify(diceResponse)

@application.route('/bank_score', methods=['GET', 'POST'])
def bank_score():
    global player, game, rolledOnceOrMore, turnScore, totals
    errMsg = ""

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
        errMsg = f"ERROR in bank_score, unhandled {request.method} request"
        logging.error(errMsg)
    
    logging.info(f"Player number {playerID} has ended their turn.  Current Player number is {player}")
    
    body = {'gameID' : gID}
    # Check to see if it is the calling clients turn
    if playerID == player:
        # Ensure that the player has rolled before banking their score
        if rolledOnceOrMore == False:
            errMsg = f"You must roll at least once before you bank your score"
            body['valid'] = False
            body['errMsg'] = errMsg
        else:
            # Compute player's total score
            score = game.bank_score()
            turnScore += score
            totals[player] += turnScore

            # Next Players turn
            player += 1
            previouslyKeptDice = game.clear_previouslyKeptDice()  # clear class variable
            rolledOnceOrMore = False # reset global variable when the turn passes to the next player
            if player > NPlayers:
                player = 1
            
            body['valid'] = True
            body['player'] = player
            body['turnScore'] = turnScore
            body['totals'] = totals
            body['previouslyKeptDice'] = previouslyKeptDice
        
    else:
        errMsg = f"ERROR in bank_score, playerID is {playerID}, but current player is {player}"
        body['valid'] = False
        body['errMsg'] = errMsg

    statusCode = 200
    bankResponse = {'body' : body, 'statusCode': statusCode}
    
    return jsonify(bankResponse)

@application.route('/do_bot_policy', methods=['POST'])
def do_bot_policy():
    global gameID, game
    
    logging.info(f"do_bot_policy POST called")
    data = request.get_json()
    logging.info(f"do_bot_policy POST received json {data}")
    gID = data['gameID']
    diceVals = data['diceVals']
    diceToPickFrom = data['diceToPickFrom']
    previouslyKeptDice = data['previouslyKeptDice']
    score = data['turnScore']

    bank, diceToKeep = game.bot1_policy(diceVals,diceToPickFrom,previouslyKeptDice,score)
    
    body = {'gameID' : gID}
    body['banked'] = bank
    body['diceToKeep'] = diceToKeep
    
    statusCode = 200
    botPolicyResponse = {'body' : body, 'statusCode': statusCode}
    
    return jsonify(botPolicyResponse)

@application.route('/get_game_state', methods=['GET'])
def get_game_state():
    global gameID, NPlayers, playerNames, player, game, rolledOnceOrMore, turnScore, totals
    errMsg = ""

    # For GET invocations
    if request.method == 'GET':
        logging.info(f"get_game_state GET called")
        # Parse the input parameters
        # Example ?gameID=1
        gID = request.args.get('gameID')
    else:
        errMsg = f"ERROR in get_game_state, unhandled {request.method} request"
        logging.error(errMsg)
       
    previouslyKeptDice = game.get_previouslyKeptDice()
    diceVals = game.get_keptDiceVals()

    body = { 'gameID' : gID, 'playerNames' : playerNames, 'player' : player, 'totals' : totals, 'turnScore' : turnScore, 'diceVals' : diceVals, 'rolledOnceOrMore' : rolledOnceOrMore, 'previouslyKeptDice' : previouslyKeptDice }
    
    statusCode = 200
    gameStateResponse = {'body' : body, 'statusCode': statusCode}
    
    return jsonify(gameStateResponse)

if __name__ == "__main__":
    # Flask defaults to localhost:5000
    # nginx defaults to port 8000
    doFlaskLogging.set_up_logger()
    application.run()
    doFlaskLogging.clean_up_logger()
