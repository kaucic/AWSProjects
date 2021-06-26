from flask import Flask, jsonify, json, Response, request
from flask_cors import CORS

import random

import logging
import doFlaskLogging

application = Flask(__name__)
CORS(application)

NDICE = 3
NPlayers = 2
# Note: Index 0 is not used, so Player 1 is index 1
player = 1
keep = [False for x in range(NDICE)]
keptDie = [x+1 for x in range(NDICE)]
wins = [0 for x in range(NPlayers+1)]
totals = [0 for x in range(NPlayers+1)]

@application.route("/")
def health_check():
    return jsonify({"message" : "Health check is good.  Try /roll_dice instead."})
    #return "<h1>Health Check is good</h1>"

@application.route('/init')
def init():
    logging.info(f"init GET called")

    global NDICE, NPlayers, player, keep, keptDie, wins, totals
    player = 1
    keep = [False for x in range(NDICE)]
    keptDie = [x+1 for x in range(3)]
    wins = [0 for x in range(NPlayers+1)]
    totals = [0 for x in range(NPlayers+1)]

    initResponse = {'body' : {'player' : player, 'wins' : wins}}

    return jsonify(initResponse)

#@application.route('/roll_dice/<keep1>/<keep2>/<keep3>', methods=['GET', 'POST'])
#def roll_dice(keep1,keep2,keep3):
@application.route('/roll_dice', methods=['GET', 'POST'])
def roll_dice():
    global NDICE, NPlayers, player, keep, keptDie, totals
    
    # For GET invocations
    if request.method == 'GET':
        logging.info(f"roll_dice GET called")
        # Parse the input parameters
        # Example ?keep1=true&keep2=false&keep3=false
        # Need to convert string on command line to Boolean
        keep_str = ['false' for x in range(NDICE)]
        keep_str[0] = request.args.get('keep1')
        keep_str[1] = request.args.get('keep2')
        keep_str[2] = request.args.get('keep3')
        logging.info(f"roll_dice GET received: keep1={keep_str[0]} keep2={keep_str[1]} keep3={keep_str[2]}")

        # Convert string values to Boolean
        for i in range(NDICE):
            if keep_str[i] == 'true':
                keep[i] = True
            else:
                keep[i] = False
        logging.info(f"Dice to keep: keep1={keep[0]} keep2={keep[1]} keep3={keep[2]}")

    elif request.method == 'POST':
        logging.info(f"roll_dice POST called")
        data = request.get_json()
        logging.info(f"roll_dice POST received json {data}")

        keep = data['keep']
        logging.info(f"keep is {keep}")
    
    else:
        logging.info(f"ERROR in roll_dice, unhandled {request.method} called")

    totals[player] = 0
    # Determine which dice to roll
    die = [10 for x in range(NDICE)]
    for i in range(NDICE):
        if keep[i] == True:
            die[i] = keptDie[i]
            logging.info(f"keeping die {i} value is {die[i]}")
        else:
            die[i] = random.randint(1,6)
            keptDie[i] = die[i]
            logging.info(f"rolling die {i} value is {die[i]}")
        totals[player] += die[i]
    logging.info(f"player = {player} total = {totals[player]}")

    body = { 'player' : player, 'die' : die, 'keep' : keep, 'total' : totals[player] }

    statusCode = 200
    #diceResponse = {**status, **body}
    diceResponse = {'body' : body, 'statusCode': statusCode}

    return jsonify(diceResponse)

@application.route('/bank_score', methods=['GET', 'POST'])
def bank_score():
    global NDICE, NPlayers, player, wins, totals, keep

    # For GET invocations
    if request.method == 'GET':
        logging.info(f"bank_score GET called")
        # Parse the input parameters
        # Example ?player=2
        which_player = request.args.get('player')
        logging.info(f"Player number {which_player} has ended their turn.  Global Player number is {player}")
    
    elif request.method == 'POST':
        logging.info(f"bank_score POST called")
        data = request.get_json()
        logging.info(f"bank_score POST received json {data}")
        which_player = data['player']
        logging.info(f"Player number {which_player} has ended their turn.  Global Player number is {player}")
    
    else:
        logging.info(f"ERROR in bank_score, unhandled {request.method} request")
    
    # Next Players turn
    player += 1

    # Clear all kept dice
    keep = [False for x in range(NDICE)]
    
    # Return which dice the Player has kept
    body = {'keep' : keep}

    # If all players have finished their turns then determine who won
    if player > NPlayers:
        if totals[1] > totals[2]:
            winner = 1
            wins[1] += 1
        elif totals[2] > totals[1]:
            winner = 2
            wins[2] += 1
        else: # Set winning player to 0 for a tie
            winner = 0
        logging.info(f"winner is {winner} totals is {totals}")
   
        body['winner'] = winner
        body['totals'] = totals
        body['wins']  = wins
        
        # Reset back to Player1s turn
        player = 1

    body['player'] = player        
    statusCode = 200
    #bankResponse = {**status, **body}
    bankResponse = {'body' : body, 'statusCode': statusCode}
    
    return jsonify(bankResponse)

@application.route('/get_game_state', methods=['GET'])
def get_game_state():
    logging.info(f"get_game_state GET called")

    global NDICE, NPlayers, player, wins, totals, keep, keptDie
    
    body = { 'player' : player, 'wins' : wins, 'totals' : totals, 'die' : keptDie, 'keep' : keep }
    
    statusCode = 200
    gameStateResponse = {'body' : body, 'statusCode': statusCode}
    
    return jsonify(gameStateResponse)

if __name__ == "__main__":
    # Flask defaults to localhost:5000
    # nginx defaults to port 8000
    doFlaskLogging.set_up_logger()
    application.run()
    doFlaskLogging.clean_up_logger()
