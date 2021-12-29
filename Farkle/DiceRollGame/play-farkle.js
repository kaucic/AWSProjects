// Wrapper around rollDice() that first gets which dice are kept 
function humanRollDice() {
    // Get which dice the human player wants to keep
    let keep = getCheckboxValues();
    console.log('Checkbox values are ', keep);
    
    // Split them into what was previously kept and what is kept this roll
    let keptDice = keep;
    for (i=0; i < NDICE; i++) {
        if (previouslyKeptDice[i] == true) {
            keptDice[i] = false;
        }
    }

    let rollDict = rollDice(keptDice);

    return rollDiceDict;
}

function parsePolicy(decision) {
    var b = decision.body;
    let gID = b.gameID;
    let banked = b.banked;
    let diceToKeep = b.diceToKeep

    console.log('parsePolicy banked is ', banked);
    console.log('parsePolicy diceToKeep are ', diceToKeep);

    return b;
}

function doOneBotStep(gameStateDict) {
    // A bot turn is
    // do roll_dice until Farkle or bank_score
    //   if not Farkle
    //     Use policy to bank_score or choose dice to roll
    
    alert('doOneBotStep called gameStateDict is' + gameStateDict + ' XXX');

    if (gameStateDict.rolledOnceOrMore == false) {
        console.log('doOneBotStep rolling dice');
        let rollDiceDict = rollDice(previouslyKeptDice);
    }    
    else {
        let botPolicyDict = doBotPolicy(gameStateDict);
        console.log('doOneBotStep banked is', botPolicyDict.banked);
        console.log('doOneBotStep diceToKeep are', diceToKeep);
        if (botPolicyDict.banked == true) {
            bankScore(); 
        }
        else if (botPolicyDict.banked == false) {
            let diceToKeep = botPolicyDict.diceToKeep;
            updateCheckboxes(diceToKeep);
            let rollDiceDict = rollDice(diceToKeep);
        }
        else {
            alert('ERROR: In doBotStep with botPolicyDict ' + botPolicyDict);
        }
    }
}

// Long Poll the server to get the game state
getGameState();
