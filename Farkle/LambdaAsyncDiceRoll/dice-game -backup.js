// Initialize game
var NDICE = 6;
var NPlayers = 2;
var gameID = "notSet";
// Note: A PlayerID value of 0 is not used and is a special case representing a game that hasn't started or a tie
var playerID = 1;
var playerNames = Array(NPlayers+1);
var vSI = 0;
playerNames[1] = "Player1";
playerNames[2] = "Player2";
previouslyKeptDice = Array(NDICE).fill(false);

// Update the HTML DOM to broadcast message
function updateMessage(msg) {
    document.querySelector("h1").innerHTML = msg;
}

// Update the names of the players
function updatePlayerNamesView(names) {
    document.querySelector("span.Player1").innerHTML = ("Player 1: " + playerNames[1]);
    document.querySelector("span.Player2").innerHTML = ("Player 2: " + playerNames[2]);
}

// Update the HTML DOM totals
function updateTurnScoreAndTotalsView(turnScore,totals) {
    document.querySelector("span.TurnScore").innerHTML  = turnScore; 
    document.querySelector("span.gameID").innerHTML = gameID;  
    document.querySelector("span.Total1").innerHTML 	= totals[1];
    document.querySelector("span.Total2").innerHTML 	= totals[2];
}    

// Update the HTML DOM for players turn
function updateTurnView(player) {
    document.querySelector("h1").innerHTML = (playerNames[player] + "\'s turn");
}
 
// Update the HTML DOM for dice
function updateDiceView(player,die,turnScore) {
    document.querySelector(".img1").setAttribute("src","dice" + die[0] + ".png");
    document.querySelector(".img2").setAttribute("src","dice" + die[1] + ".png");
    document.querySelector(".img3").setAttribute("src","dice" + die[2] + ".png");
    document.querySelector(".img4").setAttribute("src","dice" + die[3] + ".png");
    document.querySelector(".img5").setAttribute("src","dice" + die[4] + ".png");
    document.querySelector(".img6").setAttribute("src","dice" + die[5] + ".png");

    document.querySelector("span.TurnScore").innerHTML = turnScore;   
}

// Update all of the check boxes after every turn based on what the server sent back
function updateCheckboxes(keep) {
    document.getElementById('check1').checked = keep[0];
    document.getElementById('check2').checked = keep[1];
    document.getElementById('check3').checked = keep[2];
    document.getElementById('check4').checked = keep[3];
    document.getElementById('check5').checked = keep[4];
    document.getElementById('check6').checked = keep[5];
}

// Get which dice the Player has selected to keep
function getCheckboxValues() {
    let keep = new Array(NDICE);
    keep[0] = document.getElementById('check1').checked;
    keep[1] = document.getElementById('check2').checked;
    keep[2] = document.getElementById('check3').checked;
    keep[3] = document.getElementById('check4').checked;
    keep[4] = document.getElementById('check5').checked;
    keep[5] = document.getElementById('check6').checked;

    return keep;
}

// Function to parse dice json returned from server and update the HTML
// Input is the body of the Java Script object returned from the server
function updateRoll(dice) {
    let b = dice;
    let gID = b.gameID;
    let valid = b.valid;

    if (valid == true) {
        let player = b.player;
        console.log('updateRoll Returned Player is ',player);

        let Farkled = b.Farkled;
        console.log('Farkled is ',Farkled);
        //console.log('rolledOnceOrMore is', b.rolledOnceOrMore)
        let die = b.diceVals;
        let turnScore = b.turnScore;
        console.log('updateRoll die are ',die);
        console.log('updateRoll dice kept are ', previouslyKeptDice);
        console.log('updateRoll turnScore is ',turnScore);
        
        updateDiceView(player,die,turnScore);
        if (Farkled == true) {
            updateMessage("Farkle!");
            setTimeout(function() {
                updateTurnView(player);
            }, 2000);
        }

        previouslyKeptDice = b.previouslyKeptDice; // Update Global variable for dice that are set aside
        updateCheckboxes(previouslyKeptDice);
      
        playerID = b.player; // Global variable, will be removed when game logins work
    }

    else {
        alert(b.errMsg);
    }

    return b;
}

// Function to parse json returned after a player completes their turn and update the HTML
// Input is the body of the Java Script object returned from the server
function updateTurn(turn) {
    var b = turn;
    let gID = b.gameID;
    let valid = b.valid;

    if (valid == true) {
        let player = b.player;
        console.log('updateTurn complete.  Returned new Player number is ', player);

        let turnScore = b.turnScore;
        let totals = b.totals;
        console.log('turnScore: ', turnScore, 'totals: ', totals);
        updateTurnScoreAndTotalsView(turnScore,totals);

        previouslyKeptDice = b.previouslyKeptDice; // update Global variable, which should be zeroed out
        console.log('Returned dice kept are ', previouslyKeptDice);
        updateCheckboxes(previouslyKeptDice);

        if (b.whoWon) {
           alert('the Winner is ' + b.playerNames[b.whoWon]);
        }
        else {
            // Inform next Player that it is their turn
            updateTurnView(player);
            playerID = b.player; // Global variable, will be removed when game logins work
        }    
    }
    else {
        alert (b.errMsg);
    }

    return b;
}

// Function to parse json returned after a change in the game state and update the HTML
// Input is the body of the Java Script object returned from the server
function updateGameState(state,doNextMove) {
    var b = state;
    gameID = b.gameID;
    let player = b.player;
    //console.log('updateGameState returned Player number ', player);
    //alert('In updateGameState, player is ' + b.player + ' XXX');
    console.log('updateGameState returned gameID ', gameID);
    
    if (doNextMove){
        playerNames = b.playerNames;  // Global variable
        //console.log('State Update playerNames ',playerNames);

        totals = b.viewStateList[vsI].totals;
        turnScore = b.viewStateList[vsI].turnScore;
        //console.log('State Update Totals',totals);

        die = b.viewStateList[vsI].diceVals;
        previouslyKeptDice = b.viewStateList[vsI].previouslyKeptDice; // Update Global variable
        vsI++;
    }else{
        playerNames = b.playerNames;  // Global variable
        //console.log('State Update playerNames ',playerNames);

        totals = b.totals;
        turnScore = b.turnScore;
        //console.log('State Update Totals',totals);

        die = b.diceVals;
        previouslyKeptDice = b.previouslyKeptDice; // Update Global variable
    }
    updatePlayerNamesView(playerNames);
    updateTurnView(player);
    updateDiceView(player,die,totals[player]);
    updateTurnScoreAndTotalsView(turnScore,totals);

    playerID = b.player; // Global variable, will be removed when game logins work

    // Only update the check boxes when you are not the player whose turn it is to not interfere with selections being made
    if (playerID != player) {
        updateCheckboxes(previouslyKeptDice);
    }

    return b;
}


// Function to change the player name for this client and start the game
function editName() {
    yourName = prompt("Enter your name");
    playerNames[playerID] = yourName;
    updatePlayerNamesView(playerNames);
}