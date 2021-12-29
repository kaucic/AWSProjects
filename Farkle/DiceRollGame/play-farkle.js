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

function implementPolicy(decision) {
    var b = decision.body;
    let gID = b.gameID;
    let banked = b.banked;
    let diceToKeep = b.diceToKeep

    console.log('implementPolicy banked is ', banked);
    console.log('implementPolicy diceToKeep are ', diceToKeep);

    if (banked == true) {
        bankScore(); 
    }
    else if (banked == false) {
        let rollDiceDict = rollDice(diceToKeep);
    }
    else {
        alert('ERROR: In doPolicy with decision ' + decision);
    }

    return b;
}

function doOneBotStep(gameStateDict) {
    // A bot turn is
    // do roll_dice until Farkle or bank_score
    //   if not Farkle
    //     Use policy to bank_score or choose dice to roll
    
    //alert('doOneBotStep rolledOnceOrMore is ' + gameStateDict.rolledOnceOrMore + ' XXX');

    if (gameStateDict.rolledOnceOrMore == false) {
        console.log('doOneBotStep rolling dice');
        let rollDiceDict = rollDice(previouslyKeptDice);
    }    
    else {
        console.log('doOneBotStep doing doBotPolicy');
        let botPolicyDict = doBotPolicy(gameStateDict);
        //console.log('doOneBotStep banked is ', botPolicyDict.banked);
        //console.log('doOneBotStep diceToKeep are ', botPolicyDict.diceToKeep);
    }
}

// Long Poll the server to get the game state
getGameState();
