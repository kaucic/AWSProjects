from flask import Flask, jsonify, json, Response, request
from flask_cors import CORS

import random
from time import sleep

import logging
import doFlaskLogging

from FarkleFuncs import FarkleFuncs
from FarkleBots import FarkleBots

application = Flask(__name__)
CORS(application)

NPlayers = 2 # Global diceObj variable
# Note: Index 0 is not used, so Player 1 is index 1
playerNames = ['nobody' for x in range(NPlayers+1)] # Global diceObj variable
totals = [0 for x in range(NPlayers+1)] # Global diceObj variable indicating everyone's score
gameID = 100 # Global ID for the game with these players

diceObj = FarkleFuncs() # Global Dice variable that contains variables _previouslyKeptDice and _keptDiceVals
# Note: Index 0 is not used, so Player 1 is index 1
player = 1 # Global Turn variable representing whose turn it is
rolledOnceOrMore = False;  # Global Turn variable to indicate whether or not current player has rolled
turnScore = 0 # Global Turn variable indicating how many points the current player has in this turh 

@application.route("/")
def health_check():
    return jsonify({"message" : "Health check is good.  Try /roll_dice instead."})
    #return "<h1>Health Check is good.  Try /roll_dice instead.</h1>"

@application.route('/init', methods=['GET'])
def init():
    logging.info(f"init GET called")

    global gameID, NPlayers, playerNames, player, diceObj, rolledOnceOrMore, turnScore, totals

    gameID += 1
    NPlayers = 2
    playerNames[1] = 'Bot1'
    playerNames[2] = 'Bot2'
    player = 1 # Global variable representing whose turn it is.  Will be replaced with a diceObj_setup API
    diceObj = FarkleFuncs()
    rolledOnceOrMore = False # Global variable to indicate whether or not current player has rolled
    previouslyKeptDice = diceObj.get_previouslyKeptDice()
    diceVals = diceObj.get_keptDiceVals()
    turnScore = 0
    totals = [0 for x in range(NPlayers+1)]
   
    body = {'gameID' : gameID, 'NPlayers' : NPlayers, 'playerNames' : playerNames, 'player' : player,  'rolledOnceOrMore' : rolledOnceOrMore, 'totals' : totals, 'turnScore' : turnScore, 'diceVals' : diceVals, 'previouslyKeptDice' : previouslyKeptDice}
 
    statusCode = 200
    initResponse = {'body' : body, 'statusCode': statusCode}

    return jsonify(initResponse)

#@application.route('/roll_dice/<keep1>/<keep2>/<keep3>', methods=['GET', 'POST'])
#def roll_dice(keep1,keep2,keep3):
@application.route('/roll_dice', methods=['GET', 'POST'])
def roll_dice():
    global player, diceObj, rolledOnceOrMore, turnScore
    errMsg = ""
    
    # GET METHOD CODE IS OBSOLETE AND NO LONGER WORKS
    # For GET invocations
    if request.method == 'GET':
        logging.info(f"roll_dice GET called")
        # Parse the input parameters
        # Example ?diceObjID=1&playerID=1&keep1=true&keep2=false&keep3=false
        gID = request.args.get('gameID')
        playerID = request.args.get('playerID')
        logging.info(f"roll_dice GET received: playerID={playerID}")
        # Need to convert string on command line to Boolean
        NDICE = 6
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
        #logging.info(f"roll_dice POST called")
        data = request.get_json()
        logging.info(f"roll_dice POST received json {data}")

        gID = data['gameID']
        playerID = data['playerID']
        keptDice = data['keptDice']
        logging.info(f"roll_dice gameID {gameID} playerID {playerID} keptDice {keptDice}")
    
    else:
        logging.error(f"ERROR in roll_dice, unhandled {request.method} called")
  
    # Check to see if it is the calling clients turn
    if playerID == player:
        # If the player hasn't yet rolled, clear everything and start turn
        if rolledOnceOrMore == False:
            previouslyKeptDice = diceObj.clear_previouslyKeptDice()
            turnScore = 0
        # Score the dice that were kept
        elif any(keptDice):
            diceVals = diceObj.get_keptDiceVals()
            score, numDiceThatScored, scoringDice = FarkleFuncs.score_dice(diceVals,keptDice)
            # Error Check to ensure that the player only kept dice that scored
            numDiceKept = sum(keptDice)
            if numDiceKept > numDiceThatScored:
                errMsg = f"ERROR in roll_dice, playerID {playerID} kept dice that didn't score"
                logging.error(errMsg)
                body = {'gameID' : gID, 'valid' : False, 'errMsg' : errMsg}
                statusCode = 200
                diceResponse = {'body' : body, 'statusCode': statusCode}
                return jsonify(diceResponse)
            else:
                previouslyKeptDice = diceObj.update_previouslyKeptDice(keptDice)
                logging.info(f"Scoring the dice that were kept: score {score} numDiceThatScored {numDiceThatScored} scoringDice {scoringDice}")
                turnScore += score
                
                # If all dice have scored, clear previouslyKeptDice and roll all dice
                if all(previouslyKeptDice):
                    previousKeptDice = diceObj.clear_previouslyKeptDice()  # clear class variable
        # Error the player did not keep any dice
        else:
            errMsg = f"ERROR in roll_dice, playerID {playerID} did not keep any dice"
            logging.error(errMsg)
            body = {'gameID' : gID, 'valid' : False, 'errMsg' : errMsg}
            statusCode = 200
            diceResponse = {'body' : body, 'statusCode': statusCode}
            return jsonify(diceResponse)
                
        diceVals,previouslyKeptDice,rolledDice = diceObj.roll_dice()
        rolledOnceOrMore = True
        diceObj.set_keptDiceVals(diceVals)  # update class variable
                          
        body = { 'diceObjID' : gID, 'valid' : True, 'diceVals' : diceVals}
            
        # Check for Farkle
        score, numDiceThatScored, scoringDice = diceObj.score_dice(diceVals,rolledDice)
        #logging.info(f"Checking for Farkle: score is {score} numDiceThatScored is {numDiceThatScored}")
        if score > 0:
            body['Farkled'] = False
        else: # Farkled, zero out turn score and pass dice to next player 
            body['Farkled'] = True  
            turnScore = 0
            previouslyKeptDice = diceObj.clear_previouslyKeptDice()  # clear class variable
            rolledOnceOrMore = False # reset global variable when the turn passes to the next player
            player += 1 # Update global variable for whose turn it is
            if player > NPlayers:
                player = 1
        
        body['player'] = player
        body['turnScore'] = turnScore
        body['previouslyKeptDice'] = previouslyKeptDice
        body['rolledOnceOrMore'] = rolledOnceOrMore

    # Error, it is not the player's turn
    else:
        errMsg = f"ERROR in roll_dice, playerID is {playerID}, but current player is {player}"
        logging.error(errMsg)
        body = {'gameID' : gID, 'valid' : False, 'errMsg' : errMsg}

    statusCode = 200
    diceResponse = {'body' : body, 'statusCode': statusCode}

    return jsonify(diceResponse)

@application.route('/bank_score', methods=['GET', 'POST'])
def bank_score():
    global player, diceObj, rolledOnceOrMore, turnScore, totals
    errMsg = ""

    # For GET invocations
    if request.method == 'GET':
        #logging.info(f"bank_score GET called")
        # Parse the input parameters
        # Example ?diceObjID=1&playerID=2
        gID = request.args.get('gameID')
        playerID = request.args.get('playerID')
        logging.info(f"bank_score GET diceObjID is {gID} playerID is {playerID}")
        
    elif request.method == 'POST':
        #logging.info(f"bank_score POST called")
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
            score = diceObj.bank_score()
            turnScore += score
            totals[player] += turnScore

            # Next Players turn
            player += 1
            previouslyKeptDice = diceObj.clear_previouslyKeptDice()  # clear class variable
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

@application.route('/get_game_state', methods=['GET'])
def get_game_state():
    #global gameID, NPlayers, playerNames, player, diceObj, rolledOnceOrMore, turnScore, totals
    errMsg = ""

    # For GET invocations
    if request.method == 'GET':
        logging.info(f"get_game_state GET called")
        # Parse the input parameters
        # Example ?diceObjID=1
        gID = request.args.get('gameID')
    else:
        errMsg = f"ERROR in get_game_state, unhandled {request.method} request"
        logging.error(errMsg)
       
    previouslyKeptDice = diceObj.get_previouslyKeptDice()
    diceVals = diceObj.get_keptDiceVals()

    body = { 'gameID' : gID, 'playerNames' : playerNames, 'player' : player, 'totals' : totals, 'turnScore' : turnScore, 'diceVals' : diceVals, 'rolledOnceOrMore' : rolledOnceOrMore, 'previouslyKeptDice' : previouslyKeptDice}
    
    statusCode = 200
    gameStateResponse = {'body' : body, 'statusCode': statusCode}
    
    return jsonify(gameStateResponse)

@application.route('/do_bot_policy', methods=['POST'])
def do_bot_policy():
    #global totals, player  
    #logging.info(f"do_bot_policy POST called")
    data = request.get_json()
    logging.info(f"do_bot_policy POST received json {data}")

    diceVals = data['diceVals']
    previouslyKeptDice = data['previouslyKeptDice']
    score = data['turnScore']

    # Check to see if the client selected a particular policy
    if 'whichPolicy' in data:
        whichPolicy = data['whichPolicy']
    else:
        whichPolicy = 1
    logging.info(f"do_bot_policy entered with diceVals {diceVals} previouslyKeptDice {previouslyKeptDice} turnScore {score} and whichPolicy {whichPolicy}")    

    bank, diceToKeep = FarkleBots.bot_policy(whichPolicy,diceVals,previouslyKeptDice,score,totals,player)
    
    body = {'banked' : bank, 'diceToKeep' : diceToKeep}
    
    statusCode = 200
    botPolicyResponse = {'body' : body, 'statusCode': statusCode}
    
    return jsonify(botPolicyResponse)
    
if __name__ == "__main__":
    # Flask defaults to localhost:5000
    # nginx defaults to port 8000
    doFlaskLogging.set_up_logger()
    application.run()
    doFlaskLogging.clean_up_logger()
