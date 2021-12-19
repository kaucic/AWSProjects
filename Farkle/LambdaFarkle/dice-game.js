// Initialize game
var NDICE = 6;
var NPlayers = 2;
var game_id = "test_game";
var playerID = 1;

// Note: Index 0 is not used and is a special case representing a tie
var playerNames = Array(NPlayers+1);
playerNames[1] = "Player 1";
playerNames[2] = "Player 2";
previouslyKeptDice = Array(NDICE).fill(false);


// Update the HTML DOM to broadcast message
function updateMessage(msg) {
    document.querySelector("h1").innerHTML = msg;
}

// Update the names of the players
function updatePlayerNamesView(names) {
    document.querySelector("span.Player1").innerHTML = playerNames[1];
    document.querySelector("span.Player2").innerHTML = playerNames[2];
}

// Update the HTML DOM totals
function updateTurnScoreAndTotalsView(turnScore,totals) {
    document.querySelector("span.TurnScore").innerHTML  = turnScore;   
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
function updateRoll(dice) {
    let b = dice;
    console.log('b :  ', b);
    let gID = b.game_id;
    let valid = b.valid;
    console.log('updateRoll validity is ', valid);

    if (valid ) {
        playerID = b.player; // Global variable, will be removed when game logins work
        let player = b.player;
        console.log('Returned Player is ',player);

        let Farkled = b.Farkled;
        console.log('Farkled is ',Farkled);
        let die = b.diceVals;
        previouslyKeptDice = b.previouslyKeptDice; // Update Global variable for dice that are set aside
        let turnScore = b.turnScore;
        console.log('Returned die are ',die);
        console.log('Returned dice kept are ', previouslyKeptDice);
        console.log('Returned turnScore is ',turnScore);

        updateDiceView(player,die,turnScore);
        updateCheckboxes(previouslyKeptDice);
        if (Farkled == true) {
            updateMessage("Farkle!");
        }
        setTimeout(function () {
            updateTurnView(player);
            }, 2000);

    } else {
        console.log('updateRoll validity is ', valid);
        alert("It is not your turn to roll.");
        console.log('Screwed updateRoll validity is ', valid);
    }
}

// Function to parse json returned after a player completes their turn and update the HTML
function updateTurn(turn) {
    var b = turn;
    let gID = b.game_id;
    let valid = b.valid;
    console.log('updateTurn validity is ', valid);

    if (valid == true) {
        playerID = b.player; // Global variable, will be removed when game logins work
        let player = b.player;
        console.log('Turn complete.  Returned new Player number is ', player);

        let turnScore = b.turnScore;
        let totals = b.totals;
        console.log('turnScore: ', turnScore, 'totals: ', totals);
        updateTurnScoreAndTotalsView(turnScore,totals);

        previouslyKeptDice = b.previouslyKeptDice; // update Global variable, which should be zeroed out
        console.log('Returned dice kept are ', previouslyKeptDice);
        updateCheckboxes(previouslyKeptDice);

        // Inform next Player that it is their turn
        updateTurnView(player);
    } else {
        alert ('It is not your turn.  You are not allowed to bank your score');
    }
}

// Function to parse json returned after a change in the game state and update the HTML
function updateGameState(state) {
    console.log('in upateGateSate State: ', state);
    var b = state;
    let gID = b.game_id;
    playerID = b.player; // Global variable, will be removed when game logins work
    let player = b.player;
    console.log('State Update returned Player number ', player);

    playerNames = b.playerNames;  // Global variable
    //console.log('State Update playerNames ',playerNames);

    let totals = b.totals;
    let turnScore = b.turnScore;
    //console.log('State Update Totals',totals);

    let die = b.diceVals;
    previouslyKeptDice = b.previouslyKeptDice; // Global variable
    //console.log('Returned die are ',die);
    //console.log('Returned dice kept are ', previouslyKeptDice);

    updatePlayerNamesView(playerNames);
    updateTurnView(player);
    updateDiceView(player,die,totals[player]);
    updateTurnScoreAndTotalsView(turnScore,totals);
    // Only update the check boxes when you are not the player to not interfere with selections being made
    if (playerID != player) {
        //updateCheckboxes(previouslyKeptDice);
    }
}
