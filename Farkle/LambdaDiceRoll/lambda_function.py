import json
import boto3

import random

import logging

from FarkleBots import FarkleBots
from FarkleFuncs import FarkleFuncs


# create a DynamoDB object using the AWS SDK
dynamodb = boto3.resource('dynamodb')

# use the DynamoDB object to select our table
#table = dynamodb.Table('farkle_game_state')
table = dynamodb.Table('Farkle_Game_State_V2')


gameID = 'test_game'
diceObj = FarkleFuncs() # Global Dice variable that contains variables _previouslyKeptDice and _keptDiceVals
NDICE = 6
MINWINNINGSCORE = 1000
NPlayers = 2
# Note: Index 0 is not used, so Player 1 is index 1
player = 1
previouslyKeptDice = [False for x in range(NDICE)]
diceVals = [1 for x in range(NDICE)]
rolledOnceOrMore = False
turnScore = 0
totals = [0 for x in range(NPlayers+1)]
playerNames = ['nobody' for x in range(NPlayers+1)]


# define the handler function that the Lambda service will use as an entry point
def lambda_handler(event, context):
    

    global gameID, NDICE, NPlayers, playerNames, player, diceVals, previouslyKeptDice, turnScore, totals, rolledOnceOrMore
    
    action = event.get('action', 'none')
    
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
                'gameID': gameID 
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
        rolledOnceOrMore = rollState['rolledOnceOrMore']
        
        roll_response = roll_dice(event)

        if roll_response['valid']:
            # write new gamestate back to gameID key
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
                'gameID': gameID
            }
        )
        gameState = response.get('Item','none')
        print(f" gameState at start of bank {gameState}")
        if gameState == 'none':
            print('no gamestate')
            # do some error or init thing
        
        #Copy gamestate params into global vars
        player = gameState['player']
        previouslyKeptDice = gameState['previouslyKeptDice']
        diceVals = gameState['diceVals']
        turnScore = gameState['turnScore']
        totals = gameState['totals']
        playerNames = gameState['playerNames']
        rolledOnceOrMore = gameState['rolledOnceOrMore']


        bank_response = bank_score(event)
        print(f"bank_response: {bank_response}")


        # write new gamestate back to gameID key
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
                'gameID': gameID
            }
        )
        gameState = response.get('Item','none')
        if gameState == 'none':
            print(f"gameID: {gameID}  not found in DDB")
            print('no gamestate')
            # do some error or init thing
        
        # Return new gamestate after die roll
        return {
          'statusCode': 200,
          'body': gameState
    }
    
    elif action == 'do_bot_policy':
        print("doing bot policy")
        
        bot_response = do_bot(event)
        return {
          'statusCode': 200,
          'body': bot_response
    }





#bot Policy stuff
#       bank, diceToKeep = FarkleBots.bot1_policy(diceVals,keptDice, turnScore, totals, botIdx)
def do_bot(input_data):
        diceVals = input_data['diceVals']
        keptDice = input_data['previouslyKeptDice']
        turnScore = input_data['turnScore']
        totals = input_data['totals']
        # Todo: pass in botIdx which is the bots player 
        botIdx = 2
        print(f"diceVals: {diceVals}")
        print(f"keptDice: {keptDice}")
        print(f"turnScore: {turnScore}")
        if 'unitTest' in input_data:
           print("unitTest")
           #FarkleBots.bot1_policy([1,3,4,2,5,6],[False,False,False,False,False,False],0)
           #FarkleBots.bot1_policy([1,3,4,2,5,6],[True,False,False,False,False,False],0)


        bank, diceToKeep = FarkleBots.bot1_policy(diceVals, keptDice, turnScore, totals, botIdx)

        body = {'banked' : bank,
            'diceToKeep' : diceToKeep}
        print(f"bot policy return body: {body}")

        return body

def init_game():

    print("init_ga called")

    global gameID, NDICE, NPlayers, playerNames, player, diceVals, previouslyKeptDice, turnScore, totals
    #gameID += 1
    player = 1
    previouslyKeptDice = [False for x in range(NDICE)]
    diceVals = [1 for x in range(NDICE)]
    turnScore = 0
    totals = [0 for x in range(NPlayers + 1)]
    playerNames[1] = 'Bob'
    playerNames[2] = 'Ron'

    body = {'gameID' : gameID,
            'numPlayers' : NPlayers,
            'whoWon' : 0,
            'playerNames' : playerNames,
            'player' : player,
            'totals' : totals, 
            'rolledOnceOrMore' : False,
            'turnScore' : turnScore,
            'diceVals' : diceVals,
            'valid' : 'true',
            'previouslyKeptDice' : previouslyKeptDice}
 
    return body


def roll_dice(input_data):


    global game, NDICE, NPlayers, player, previouslyKeptDice, diceVals, rolledOnceOrMore, diceObj, turnScore, totals
    print(f"input_data: {input_data}")

    print(f"rolledOnceOrMore: {rolledOnceOrMore}")

    
    #logging.info(f"roll_dice POST called")
    gID = input_data['gameID']
    body = {'gameID' : gID}
    playerID = int(input_data['playerID'])
    keptDice = input_data['keptDice']
    logging.info(f"roll_dice gameID {gID} playerID {playerID} keptDice {keptDice}")
    winner = 0
    
  
    # Check to see if it is the calling clients turn
    if playerID == player:
        # If the player hasn't yet rolled, clear everything and start turn
        #print(f"rolledOnceOrMore: {rolledOnceOrMore}")

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
                return body
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
            return body
                
        diceVals,previouslyKeptDice,rolledDice = diceObj.roll_dice()
        rolledOnceOrMore = True
        diceObj.set_keptDiceVals(diceVals)  # update class variable
                          
        # Check for Farkle
        score, numDiceThatScored, scoringDice = diceObj.score_dice(diceVals,rolledDice)
        #logging.info(f"Checking for Farkle: score is {score} numDiceThatScored is {numDiceThatScored}")
        if score > 0:
            body['Farkled'] = False
        else: # Farkled, zero out turn score and pass dice to next player 
            body['Farkled'] = True  
            turnScore = 0

            #Check to see if there's a winner
            winner = whoWon(totals, player, NPlayers)

            previouslyKeptDice = diceObj.clear_previouslyKeptDice()  # clear class variable
            rolledOnceOrMore = False # reset global variable when the turn passes to the next player
            player += 1 # Update global variable for whose turn it is
            if player > NPlayers:
                player = 1
        
        body['gameID'] = gID
        body['player'] = int(player)
        body['valid'] = True
        body['totals'] = totals
        body['turnScore'] = turnScore
        body['whoWon'] = winner
        body['previouslyKeptDice'] = previouslyKeptDice
        body['rolledOnceOrMore'] = rolledOnceOrMore
        body['diceVals'] = diceVals
        body['playerNames'] = playerNames
        body['previouslyKeptDice'] = previouslyKeptDice
        print(f"roll_dice return body: {body}")


    # Error, it is not the player's turn
    else:
        errMsg = f"ERROR in roll_dice, playerID is {playerID}, but current player is {player}"
        logging.error(errMsg)
        body = {'gameID' : gID, 'valid' : False, 'errMsg' : errMsg}

    return body
    
    # End of roll_dice()
    
    
def bank_score(input_data):
    global game, NDICE, NPlayers, player, previouslyKeptDice, diceVals, turnScore, totals,  diceObj, rolledOnceOrMore
    errMsg = ""

    gID = input_data['gameID']
    playerID = int(input_data['playerID'])
    
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
            totals[int(player)] += turnScore + diceObj.bank_score()
            turnScore = 0
            
            #Check to see if there's a winner
            winner = whoWon(totals, player, NPlayers)

            # Next Players turn
            previouslyKeptDice = diceObj.clear_previouslyKeptDice()  # clear class variable
            rolledOnceOrMore = False # reset global variable when the turn passes to the next player

            player += 1
            if player > NPlayers:
                player = 1
            
            body['valid'] = True
            body['playerNames'] = playerNames
            body['player'] = player
            body['whoWon'] = winner
            body['turnScore'] = turnScore
            body['totals'] = totals
            body['previouslyKeptDice'] = previouslyKeptDice
            body['rolledOnceOrMore'] = False
            body['diceVals'] = diceVals

        
    else:
        errMsg = f"ERROR in bank_score, playerID is {playerID}, but current player is {player}"
        body['valid'] = False
        body['errMsg'] = errMsg

    return body

# returns the player number who won or 0 if nobody has won yet. 
# todo: figure out how to handle ties, currently the lower player number wins ties.
def whoWon(totals, player, numPlayers):
    # if the next player's score is <= MINWINNINGSCORE than somebody has won.
    if player == numPlayers :
        if totals[1] < MINWINNINGSCORE:
            return 0
    else:
        if totals[int(player+1)] < MINWINNINGSCORE:
            return 0
    # Somebody won. Figure out who.
    winning = 1 
    x = 1 
    while ( x <= numPlayers):
        if( totals[winning] < totals[x]):
            winning = x
        x = x+1


    print(f"WINNER: {winning}")
    print(f"WINNER: {winning}")
    print(f"WINNER: {winning}")
    print(f"WINNER: {winning}")
    print(f"WINNER: {winning}")
    print(f"WINNER: {winning}")
    print(f"WINNER: {winning}")
    return winning