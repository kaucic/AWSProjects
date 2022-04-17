import json
import boto3

import random

import logging

from Farkle import Farkle


# create a DynamoDB object using the AWS SDK
dynamodb = boto3.resource('dynamodb')

# use the DynamoDB object to select our table
table = dynamodb.Table('farkle_game_state')

game_id = 'test_game'
NDICE = 6
NPlayers = 2
# Note: Index 0 is not used, so Player 1 is index 1
player = 1
previouslyKeptDice = [False for x in range(NDICE)]
diceVals = [1 for x in range(NDICE)]
turnScore = 0
totals = [0 for x in range(NPlayers+1)]
playerNames = ['nobody' for x in range(NPlayers+1)]
game = Farkle()


# define the handler function that the Lambda service will use as an entry point
def lambda_handler(event, context):
    

    global game_id, NDICE, NPlayers, playerNames, player, diceVals, previouslyKeptDice, turnScore, totals
    
    action = event.get('action','none')

    
    # extract values from the event object we got from the Lambda service and store in a variable
    if action == 'init_game':
        
        game_body = init_game()
        print(f"getting gameState: {game_body}")

        response = table.put_item(
                Item = game_body
        )
        
        print(f"inited into DDB: {game_body}");
        # Return new gamestate after die roll
        return {
          'statusCode': 200,
          'body': game_body
    }


    elif action == 'roll_dice':
        print("rolling dice")
        response = table.get_item(
            Key={
                'game_id': game_id 
            }
        )
        rollState = response.get('Item','none')
        if rollState == 'none':
            print('no rollState')
            # do some error or init thing
        
        # copy rollstate into global vars
        player = rollState['player']
        previouslyKeptDice = rollState['previouslyKeptDice']
        diceVals = rollState['diceVals']
        turnScore = rollState['turnScore']
        totals = rollState['totals']
        playerNames = rollState['playerNames']

        
        roll_response = roll_dice(event)

        if roll_response['valid']:
            # write new gamestate back to game_id key
            response = table.put_item(
              Item = roll_response
            )

        # Return new rollState after die roll
        return {
          'statusCode': 200,
          'body': roll_response
    }

    elif action == 'bank':
        print("banking")
        response = table.get_item(
            Key={
                'game_id': game_id
            }
        )
        gameState = response.get('Item','none')
        print(f" gameState at start of bank {gameState}")
        if gameState == 'none':
            print('no gamestate')
            # do some error or init thing
        
        #Copy gamestate params into global vars
        player = int(gameState['player'])
        previouslyKeptDice = gameState['previouslyKeptDice']
        diceVals = gameState['diceVals']
        turnScore = gameState['turnScore']
        totals = gameState['totals']
        playerNames = gameState['playerNames']

        bank_response = bank_score(event)
        print(f"bank_response: {bank_response}")


        # write new gamestate back to game_id key
        if bank_response['valid']:
            response = table.put_item(
              Item = bank_response
            )

        # Return new gamestate after die roll
        return {
          'statusCode': 200,
          'body': bank_response
    }

    elif action == 'get_game_state':
        print("getting gameState")
        response = table.get_item(
            Key={
                'game_id': game_id
            }
        )
        gamestate = response.get('Item','none')
        if GameState == 'none':
            print('no gamestate')
            # do some error or init thing
        
        # Return new gamestate after die roll
        return {
          'statusCode': 200,
          'body': gameState
    }

def init_game():
    print("init GET called")

    global game_id, NDICE, NPlayers, playerNames, player, diceVals, previouslyKeptDice, turnScore, totals
    #game_id += 1
    player = 1
    previouslyKeptDice = [False for x in range(NDICE)]
    diceVals = [1 for x in range(NDICE)]
    turnScore = 0
    totals = [0 for x in range(NPlayers+1)]
    playerNames[1] = 'Bob'
    playerNames[2] = 'Ron'

    body = {'game_id' : game_id,
            'playerNames' : playerNames,
            'player' : player,
            'totals' : totals, 
            'turnScore' : turnScore,
            'diceVals' : diceVals,
            'valid' : 'true',
            'previouslyKeptDice' : previouslyKeptDice}
 
    return body


def roll_dice(input_data):
    global game, NDICE, NPlayers, player, previouslyKeptDice, diceVals, turnScore, totals
    

    gID = input_data['game_id']
    playerID = int(input_data['playerID'])
    keptDice = input_data['keptDice']
    print(f"[playerID is {playerID} keptDice is {keptDice}")
    

    # Check to see if it is the calling clients turn
    if playerID == player:
        # Score the dice that were kept
        if any(keptDice):
            score, scoringDice = game.score_dice(diceVals,keptDice)
            print(f"Scoring the dice that were kept: score is {score} count is {scoringDice}")
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
                print(f"rolling die {i} value is {diceVals[i]}")
            
        body = { 'game_id' : gID, 'valid' : True, 'diceVals' : diceVals}
            
        # Check for Farkle
        score, scoringDice = game.score_dice(diceVals, diceToRoll)
        print(f"Checking for Farkle: score is {score} count is {scoringDice}")
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
        
        body['diceVals'] = diceVals
        body['player'] = player
        body['playerNames'] = playerNames
        body['valid'] = True
        body['turnScore'] = turnScore
        body['totals'] = totals
        body['previouslyKeptDice'] = previouslyKeptDice
        print(f"roll_dice return body: {body}")

    else:
        print(f"ERROR in roll_dice, playerID is {playerID}, but current player is {player}")
        body = {  'game_id' : gID, 'valid' : False}
    return body

def bank_score(input_data):
    global game, NDICE, NPlayers, player, previouslyKeptDice, diceVals, turnScore, totals

    print(f"bank_score Lambda received json {input_data}")
    gID = input_data['game_id']
    playerID = int(input_data['playerID'])
    
    print(f"Player number {playerID} has ended their turn.  Current Player number is {player}")
    
    body = {'game_id' : gID}
    # Check to see if it is the calling clients turn
    print(f"type: {type(playerID)} playerID: {playerID}; type: {type(player)} player: {player}")
    if playerID == player:
        # Compute player's total score
        diceToScore = [True for x in range(NDICE)]
        for i in range(NDICE):
            diceToScore[i] = not previouslyKeptDice[i]
        score, scoringDice = game.score_dice(diceVals,diceToScore)
        print(f"Determining points that were banked: score is {score} count is {scoringDice}")

        turnScore += score
        totals[player] += turnScore
        turnScore = 0

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
        body['diceVals'] = diceVals
        body['playerNames'] = playerNames


    
    else:
        body['valid'] = False

    statusCode = 200

    #For reference: body returned from getGameState - Not quite the same as for bank_score
    #body = { 'game_id' : gID, 'playerNames' : playerNames, 'player' : player, 'totals' : totals, 'turnScore' : turnScore, 'diceVals' : diceVals, 'previouslyKeptDice' : previouslyKeptDice }

    #return json.dumps(body)
    return (body)


#  Is this needed?
def get_game_state(input_data):
    print(f"get_game_state GET called")
    gID = input_data['game_id']
       
    global NDICE, NPlayers, playerNames, player, previouslyKeptDice, diceVals, turnScore, totals
    
    body = { 'game_id' : gID, 'playerNames' : playerNames, 'player' : player, 'totals' : totals, 'turnScore' : turnScore, 'diceVals' : diceVals, 'previouslyKeptDice' : previouslyKeptDice }
    
    statusCode = 200
    gameStateResponse = {'body' : body, 'statusCode': statusCode}
    
    return json.dumps(gameStateResponse)