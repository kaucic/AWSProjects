import json
import boto3

import random

import logging

from FarkleBots import FarkleBots
from FarkleFuncs import FarkleFuncs
from FarkleFuncs import bank_score_func
from FarkleFuncs import roll_dice_func


from FarkleTests import run_tests

# create a DynamoDB object using the AWS SDK
dynamodb = boto3.resource('dynamodb')

# use the DynamoDB object to select our table
#table = dynamodb.Table('farkle_game_state')
table = dynamodb.Table('Farkle_Game_State_V2')

global gameID

NDICE = 6
MINWINNINGSCORE = 1000
NPlayers = 2

# define the handler function that the Lambda service will use as an entry point
def lambda_handler(event, context):
    

#    global gameID, NDICE, NPlayers, winner, playerNames, player, previouslyKeptDice, turnScore, totals, rolledOnceOrMore
    global gameID, NDICE, NPlayers
    
    action = event.get('action', 'none')
    
    # extract values from the event object we got from the Lambda service and store in a variable
    if action == 'init_game':
        game_body = init_game(event)

        print(f"inited into DDB: {game_body}");
        # Return new gamestate after die roll
        return {
          'statusCode': 200,
          'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
            'Access-Control-Allow-Methods': '*'
          },
          'body': game_body
        }

    elif action == 'roll_dice':
        print("rolling dice")
        newRollState = roll_dice(event)
        if newRollState['valid']:
            # Return new rollState after die roll
            return {
              'statusCode': 200,      
              'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
              },
              'body': newRollState
        }
        #there's an error
        else:
            # Return the error in roll_response
            return {
              'statusCode': 400,
              'body': newRollState
        }

    elif action == 'bank':
        print("banking")

        newBankState = bank_score(event)
        print(f"bank_response: {newBankState}")

        # Return new gamestate after die roll
        return {
          'statusCode': 200,
          'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
          },
          'body': newBankState
    }

    elif action == 'get_game_state':
        print("getting gameState")
        gameID = event.get('gameID', 'none')
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
          'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
          },
          'body': gameState
    }
    
    elif action == 'do_bot_policy':
        print("doing bot policy")
        
        bot_response = do_bot(event)
        return {
          'statusCode': 200,       
          'body': bot_response
    }
    
    elif action == 'run_tests':
        print("running tests")
        
        test_result = run_tests()
        return {
          'statusCode': 200,       
          'body': test_result
    }


def init_game(event):
    print("init_game called")
     
    gameID = event.get('gameID', 'none')
    if gameID != 'none':  # Init the 'test_game' game
        thisGameID = 'test_game'

    else:  #Do normal incrementing of gameID
        response = table.get_item(
            Key={
                'gameID': 'gameIDCounter' 
            }
        )
        counter = response.get('Item','none')
        if counter == 'none':
            print('no counter')
            # do some error or init thing
            thisGameID = '0'
        else:
            thisGameID = counter['nextGameID']
        nextGameID = str(int(thisGameID) + 1)

        response = table.put_item(
            Item = {'gameID' : 'gameIDCounter',
                    'nextGameID' : nextGameID }
        )
      
    player = 1
    previouslyKeptDice = [False for x in range(NDICE)]
    diceVals = [1 for x in range(NDICE)]
    turnScore = 0
    totals = [0 for x in range(NPlayers + 1)]
    playerNames = ['','Bob','Ron']    

    game_state = {'gameID' : thisGameID,
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
 
    tmpVSL = []
    tmpVSL.append(game_state.copy())
    game_state['viewStateList'] = tmpVSL
    game_state['viewStateIndex'] = 0
        
    response = table.put_item(
            Item = game_state
    )

    return game_state


def roll_dice(input_data):
    global NDICE, NPlayers
    
    gameID = input_data.get('gameID', 'none')
    newRollState = {'gameID' : gameID}
    #print(f"input_data: {input_data}")
    #print(f"gameID: {gameID}")
    
    response = table.get_item(
        Key={
            'gameID': gameID 
        }
    )
    rollState = response.get('Item','none')
    if rollState == 'none':
        print('no rollState')
        # do some error or init thing

    # copy rollstate into local vars
    player = rollState['player']
    winner = rollState['whoWon']
    previouslyKeptDice = rollState['previouslyKeptDice']
    diceVals = rollState['diceVals']
    turnScore = rollState['turnScore']
    totals = rollState['totals']
    playerNames = rollState['playerNames']
    rolledOnceOrMore = rollState['rolledOnceOrMore']
    #print(f"rolledOnceOrMore: {rolledOnceOrMore}")

    playerID = int(input_data['playerID'])
    keptDice = input_data['keptDice']
    allKeptDice = [False for x in range(NDICE)]
    
    logging.info(f"roll_dice gameID {gameID} playerID {playerID} keptDice {keptDice}")
    diceObj = FarkleFuncs() # Dice variable that contains variables _previouslyKeptDice and _keptDiceVals
    diceObj.set_diceVals_and_keptDice(diceVals,previouslyKeptDice)
    # diceObj.set_keptDiceVals(keptDice)
    
    if (winner != 0):
        errMsg = f"ERROR in roll_dice, playerID {winner} already won!"
        logging.error(errMsg)
        body = {'gameID' : gameID, 'valid' : False, 'errMsg' : errMsg}
        return body
  
    # Check to see if it is the calling clients turn
    if playerID == player:

        # Error if the player rolled before and did not keep any dice
        if rolledOnceOrMore == True and not any(keptDice):
            errMsg = f"ERROR in roll_dice, playerID {playerID} did not keep any dice"
            logging.error(errMsg)
            body = {'gameID' : gameID, 'valid' : False, 'errMsg' : errMsg}
            return body

        # If the player hasn't yet rolled, clear everything and start turn
        #print(f"rolledOnceOrMore: {rolledOnceOrMore}")
        if rolledOnceOrMore == False:

            previouslyKeptDice = diceObj.clear_previouslyKeptDice()
            turnScore = 0
        # Score the dice that were kept
        elif any(keptDice):
            #diceVals should NOT get overwritten
            #diceVals = diceObj.get_keptDiceVals()
            score, numDiceThatScored, scoringDice = FarkleFuncs.score_dice(diceVals,keptDice)
            # Error Check to ensure that the player only kept dice that scored
            numDiceKept = sum(keptDice)
            if numDiceKept > numDiceThatScored:
                errMsg = f"ERROR in roll_dice, playerID {playerID} kept dice that didn't score"
                logging.error(errMsg)
                body = {'gameID' : gameID, 'valid' : False, 'errMsg' : errMsg}
                return body
            else:
                #previouslyKeptDice = diceObj.update_previouslyKeptDice(keptDice)
                for i in range(NDICE):
                    allKeptDice[i] = previouslyKeptDice[i] or keptDice[i]
        
                print(f"Scoring the dice that were kept: score {score} numDiceThatScored {numDiceThatScored} scoringDice {scoringDice}")
                logging.info(f"Scoring the dice that were kept: score {score} numDiceThatScored {numDiceThatScored} scoringDice {scoringDice}")

                turnScore += score
                
                # If all dice have scored, clear previouslyKeptDice and roll all dice
                if all(allKeptDice):
                    allKeptDice = [False for x in range(NDICE)]
                
        #  DICE ARE ACTUALLY ROLLED HERE
        diceVals,previouslyKeptDice,rolledDice = roll_dice_func(diceVals,allKeptDice)
        rolledOnceOrMore = True
        #diceObj.set_keptDiceVals(diceVals)  # update class variable
                          
        # Check for Farkle
        score, numDiceThatScored, scoringDice = diceObj.score_dice(diceVals,rolledDice)
        #logging.info(f"Checking for Farkle: score is {score} numDiceThatScored is {numDiceThatScored}")
        if score == 0: # Farkled, zero out turn score and pass dice to next player 
            newRollState['Farkled'] = True  
            turnScore = 0

            winner = whoWon(totals, player, NPlayers)
            previouslyKeptDice = [False for x in range(NDICE)]
            rolledOnceOrMore = False # reset global variable when the turn passes to the next player
            player += 1 # Update global variable for whose turn it is
            if player > NPlayers:
                player = 1
        else: 
            newRollState['Farkled'] = False
            
        newRollState['gameID'] = gameID
        newRollState['player'] = int(player)
        newRollState['valid'] = True
        newRollState['totals'] = totals
        newRollState['turnScore'] = turnScore
        newRollState['whoWon'] = winner
        newRollState['previouslyKeptDice'] = previouslyKeptDice
        newRollState['rolledOnceOrMore'] = rolledOnceOrMore
        newRollState['diceVals'] = diceVals
        newRollState['playerNames'] = playerNames
        
        viewStateList = rollState['viewStateList']
        viewStateList.append(newRollState.copy())
        newRollState['viewStateList'] = viewStateList
        newRollState['viewStateIndex'] = rollState['viewStateIndex'] + 1

        # write new gamestate back to gameID key
        response = table.put_item(
            Item = newRollState
        )
        return newRollState

    # Error, it is not the player's turn
    else:
        errMsg = f"ERROR in roll_dice, playerID is {playerID}, but current player is {player}"
        logging.error(errMsg)
        body = {'gameID' : gameID, 'valid' : False, 'errMsg' : errMsg}
    return body
    
    # End of roll_dice()
    
    
def bank_score(input_data):
    global NDICE, NPlayers
    errMsg = ""

    gameID = input_data['gameID']
    playerID = int(input_data['playerID'])

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
        
    #Copy gamestate params into local vars
    player = gameState['player']
    winner = gameState['whoWon']
    previouslyKeptDice = gameState['previouslyKeptDice']
    diceVals = gameState['diceVals']
    turnScore = gameState['turnScore']
    totals = gameState['totals']
    playerNames = gameState['playerNames']
    rolledOnceOrMore = gameState['rolledOnceOrMore']
    
    diceObj = FarkleFuncs() # Dice variable that contains variables _previouslyKeptDice and _keptDiceVals
    diceObj.set_diceVals_and_keptDice(diceVals,previouslyKeptDice)

    logging.info(f"Player number {playerID} has ended their turn.  Current Player number is {player}")
    
    body = {'gameID' : gameID}
    if (winner != 0):
        errMsg = f"ERROR in roll_dice, playerID {winner} already won!"
        logging.error(errMsg)
        body = {'gameID' : gameID, 'valid' : False, 'errMsg' : errMsg}
        return body


    # Check to see if it is the calling clients turn
    if playerID != player:
        errMsg = f"ERROR in bank_score, playerID is {playerID}, but current player is {player}"
        body['valid'] = False
        body['errMsg'] = errMsg
        return body

    # Ensure that the player has rolled before banking their score
    if rolledOnceOrMore == False:
        errMsg = f"You must roll at least once before you bank your score"
        body['valid'] = False
        body['errMsg'] = errMsg
        return body
    # Compute player's total score
    totals[int(player)] += turnScore + bank_score_func(diceVals, previouslyKeptDice)
    turnScore = 0
    
    #Check to see if there's a winner
    winner = whoWon(totals, player, NPlayers)

    # Next Players turn
    #previouslyKeptDice = diceObj.clear_previouslyKeptDice()  # clear class variable
    #Clear previouslyKeptDice
    previouslyKeptDice = [False for x in range(NDICE)]

    rolledOnceOrMore = False # reset global variable when the turn passes to the next player

    player += 1
    if player > NPlayers:
        player = 1
    
    newGameState = {'gameID' : gameID}
    
    newGameState['valid'] = True
    newGameState['playerNames'] = playerNames
    newGameState['player'] = player
    newGameState['whoWon'] = winner
    newGameState['turnScore'] = turnScore
    newGameState['totals'] = totals
    newGameState['previouslyKeptDice'] = previouslyKeptDice
    newGameState['rolledOnceOrMore'] = False
    newGameState['diceVals'] = diceVals

    viewStateList = gameState['viewStateList']
    viewStateList.append(newGameState.copy())
    newGameState['viewStateList'] = viewStateList
    newGameState['viewStateIndex'] = gameState['viewStateIndex'] + 1

    # write new gamestate back to gameID key
    response = table.put_item(
        Item = newGameState
    )
    return newGameState


# returns the player number who won or 0 if nobody has won yet. 
# todo: figure out how to handle ties, currently the lower player number wins ties.
def whoWon(totals, player, numPlayers):
    # if the next player's score is >= MINWINNINGSCORE than somebody has won.
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
    return winning


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
