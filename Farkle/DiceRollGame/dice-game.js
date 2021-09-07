var gameEndpoint = 'http://localhost:5000'; // example: 'http://mythi-publi-abcd12345-01234567890123.elb.us-east-1.amazonaws.com' 

// Initialize game
var NDICE = 6;
var NPlayers = 2;
var gameID = 0;
var playerID = 1;
// Note: Index 0 is not used and is a special case representing a tie
var playerNames = Array(NPlayers+1);
playerNames[1] = "Player 1";
playerNames[2] = "Player 2";
previouslyKeptDice = Array(NDICE).fill(false);

// Function to change the player name
function editNames() {
    playerNames[1] = prompt("Change Player1 name");
    playerNames[2] = prompt("Change player2 name");

    document.querySelector("p.Player1").innerHTML = playerNames[1];
    document.querySelector("p.Player2").innerHTML = playerNames[2];
}

// Update the HTML DOM to broadcast message
function updateMessage(msg) {
    document.querySelector("h1").innerHTML = msg;
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
    let b = dice.body;
    let valid = b.valid;
    console.log('updateRoll validity is ', valid);

    if (valid == true) {
        playerID = b.player; // Global variable, will be removed when game logins work
        let player = b.player;
        console.log('Returned Player is ',player);

        let Farkled = b.Farkled;
        console.log('Farkled is ',Farkled);
        let die = b.diceVals;
        let keep = b.previouslyKeptDice;
        previouslyKeptDice = keep;  // Update Global variable for dice that are set aside
        let turnScore = b.turnScore;
        console.log('Returned die are ',die);
        console.log('Returned dice kept are ', keep);
        console.log('Returned turnScore is ',turnScore);

        updateDiceView(player,die,turnScore);
        updateCheckboxes(keep);
        if (Farkled == true) {
            setTimeout(function () {
                updateMessage("Farkle!");
            }, 500);
        }
        updateTurnView(player);
    } else {
        alert("It is not your turn to roll.");
    }
}

// Function to parse json returned after a player completes their turn and update the HTML
function updateTurn(turn) {
    var b = turn.body;
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
    var b = state.body;
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

    updateTurnView(player);
    updateDiceView(player,die,totals[player]);
    updateTurnScoreAndTotalsView(turnScore,totals);
    // Only update the check boxes when you are not the player to not interfere with selections being made
    if (playerID != player) {
        //updateCheckboxes(keep);
    }
}

// Call the Server to roll the dice
function rollTheDice() {
    var baseAPI = gameEndpoint + "/roll_dice";

    // Get which dice the customer wants to keep
    let keep = getCheckboxValues();
    console.log('Checkbox values are ', keep);
    
    // Split them into what was previously kept and what is kept this roll
    let keptDice = keep;
    for (i=0; i < NDICE; i++) {
        if (previouslyKeptDice[i] == true) {
            keptDice[i] = false;
        }
    }
   
    var diceAPI;
    var requestOptions = {};
    setTimeout(function () {

        if (false) {
            // For HTTP GET, Append the parameters to the URL
            diceAPI = baseAPI + "?playerID=" + playerID + "&keep1=" + keep[0] + "&keep2=" + keep[1] + "&keep3=" + keep[2];
            console.log('GET URL is ',diceAPI);
            // Pass as Array of Booleans
            //diceAPI = baseAPI + "?playerID=" + playerID + "&keep=" + keep;
            //console.log('GET URL is ',diceAPI);
         } else {
            // For HTTP POST, Put params in body
            diceAPI = baseAPI;    
            let raw = {'gameID' : gameID, 'playerID': playerID, 'keptDice': keptDice, 'previouslyKeptDice' : previouslyKeptDice}
            requestOptions = {
                method: 'POST',
                mode: 'cors',
                headers: { 'Content-Type' : 'application/json'},
                body: JSON.stringify(raw)
            };
            //console.log('POST options are',requestOptions);
        }

        fetch(diceAPI,requestOptions)
            .then(function (response) { 
                console.log('diceAPI Return status ', response.status); // 200
                //console.log(response.statusText); // OK
                return response.json();  // parses JSON response into native JavaScript objects
            })
            .then(function (jsObject) {
                //console.log(jsObject);
                updateRoll(jsObject);
            })
            .catch(function(error) {
                console.log('ERROR in diceAPI fetch ', error);
            });       

    }, 100 );
}

// Call the Server to end players turn and bank score
function bankScore() {
    var baseAPI = gameEndpoint + "/bank_score";

    var bankAPI;
    var requestOptions = {};
    setTimeout(function () {

        if (false) {
            // For HTTP GET, Append the parameters to the URL
            bankAPI = baseAPI + "?playerID=" + playerID;
            console.log('GET URL is ',bankAPI);
         } else {
            // For HTTP POST, Put params in body
            bankAPI = baseAPI;    
            let raw = {'gameID' : gameID, 'playerID': playerID}           
            requestOptions = {
                method: 'POST',
                mode: 'cors',
                headers: { 'Content-Type' : 'application/json'},
                body: JSON.stringify(raw)
            };
            //console.log('POST options are',requestOptions);
        }
           
        fetch(bankAPI,requestOptions)
            .then(function (response) { 
                console.log('bankAPI Return status ', response.status); // 200
                //console.log(response.statusText); // OK
                return response.json(); // parses JSON response into native JavaScript objects
            })
            .then(function (jsObject) {
                //console.log(jsObject);
                updateTurn(jsObject);
            })
            .catch(function(error) {
                console.log('ERROR in bankAPI fetch ', error);
            });       

    }, 100 );
}

// Long Poll the server every one second to get the game state
async function getGameState() {
    // For HTTP GET, Append the parameters to the URL
    var gameStateAPI = gameEndpoint + "/get_game_state" + "?gameID=" + gameID;
    var requestOptions = {};
    console.log('GET URL is ',gameStateAPI);
    
    setTimeout(function () {
        fetch(gameStateAPI,requestOptions)
            .then(function (response) { 
                //console.log('gameStateAPI Return status ', response.status); // 200
                //console.log(response.statusText); // OK
                return response.json(); // parses JSON response into native JavaScript objects
            })
            .then(function (jsObject) {
                //console.log(jsObject);
                updateGameState(jsObject);
                getGameState();
            })
            .catch(function(error) {
                // Status 502 is a connection timeout error, so trap it
                // may happen when the connection was pending for too long and the remote server
                // or a proxy closed it
                if (response.status == 502) {
                    console.log("ERROR 502 in gameStateAPI ", error);
                    getGameState();
                } else {
                    console.log('ERROR in gameStateAPI fetch ', error);
                }                                  
            });
    }, 3000);
}

// Long Poll the server to get the game state
getGameState();

// Used only for the client javascript solution
var wins = new Array(NPlayers+1);
wins[0] = -1;
wins[1] = 0;
wins[2] = 0;

// Client side only solution that rolls the dice in javascript
function js_rollTheDice() {
    var die = new Array(NDICE);
    var total = new Array(NPlayers+1);

    // Player 1 roll the dice
    die[0] = Math.floor(Math.random() * 6) + 1;
    die[1] = Math.floor(Math.random() * 6) + 1;
    die[2] = Math.floor(Math.random() * 6) + 1;
    die[3] = Math.floor(Math.random() * 6) + 1;
    die[4] = Math.floor(Math.random() * 6) + 1;
    die[5] = Math.floor(Math.random() * 6) + 1;

    total[1] = 0;
    for (i=0; i < NDICE; i++) {
        total[1] += die[i];
    }
    
    updateDiceView(1,die,total[1]);
 
    // Player 2 roll the dice
    die[0] = Math.floor(Math.random() * 6) + 1;
    die[1] = Math.floor(Math.random() * 6) + 1;
    die[2] = Math.floor(Math.random() * 6) + 1;
    die[3] = Math.floor(Math.random() * 6) + 1;
    die[4] = Math.floor(Math.random() * 6) + 1;
    die[5] = Math.floor(Math.random() * 6) + 1;

    total[2] = 0;
    for (i=0; i < NDICE; i++) {
        total[2] += die[i];
    }
  
    updateDiceView(2,die,total[2]);

    var winner;
    if (total[1] > total[2]) {
        winner = 1
        wins[1] += 1;
    }
    else if (total[2] > total[1]) {
        winner = 2;
        wins[2] += 1;
    }
    else {
        winner = 0
    }   

    updateWinnerView(winner,wins)
}