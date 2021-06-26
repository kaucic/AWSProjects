var gameEndpoint = 'http://localhost:5000'; // example: 'http://mythi-publi-abcd12345-01234567890123.elb.us-east-1.amazonaws.com'
//var diceAPI = "https://ghibliapi.herokuapp.com/people";    

// Initialize game
var NDICE = 3;
var NPlayers = 2;
var player = 1;
// Note: Index 0 is not used and is a special case representing a tie
var players = new Array(NPlayers+1);
players[1] = "Player 1";
players[2] = "Player 2";

// Function to change the player name
function editNames() {
    players[1] = prompt("Change Player1 name");
    players[2] = prompt("Change player2 name");

    document.querySelector("p.Player1").innerHTML = players[1];
    document.querySelector("p.Player2").innerHTML = players[2];
}

// Update the HTML DOM to announce the winner
function updateWinnerView(winner) {
    if (winner == 0) {
        document.querySelector("h1").innerHTML = "Draw!";
    }
    else if (winner == 1) {
        document.querySelector("h1").innerHTML 	= (players[1] + " WINS!");
    }
    else {
        document.querySelector("h1").innerHTML = (players[2] + " WINS!");    
    }
}

// Update the HTML DOM wins and totals
function updateWinsTotalsView(wins,totals) {
    document.querySelector("span.Points1").innerHTML 	= wins[1];
    document.querySelector("span.Points2").innerHTML 	= wins[2];
    document.querySelector("span.Total1").innerHTML 	= totals[1];
    document.querySelector("span.Total2").innerHTML 	= totals[2];
}    

// Update the HTML DOM for players turn
function updateTurnView(player) {
    document.querySelector("h1").innerHTML = (players[player] + "\'s turn");
}
 
// Update the HTML DOM for dice
function updateDiceView(which_player,die,total) {
    document.querySelector(".img1").setAttribute("src","dice" + die[0] + ".png");
    document.querySelector(".img2").setAttribute("src","dice" + die[1] + ".png");
    document.querySelector(".img3").setAttribute("src","dice" + die[2] + ".png");

    if (which_player == 1) {
        document.querySelector("span.Total1").innerHTML 	= total;
    } else {
        document.querySelector("span.Total2").innerHTML 	= total;
    }
}

// Update all of the check boxes after every turn based on what the server sent back
function updateCheckboxes(keep) {
    document.getElementById('check1').checked = keep[0];
    document.getElementById('check2').checked = keep[1];
    document.getElementById('check3').checked = keep[2];
}

// Get which dice the Player has selected to keep
function getCheckboxValues() {
    let keep = new Array(NDICE);
    keep[0] = document.getElementById('check1').checked;
    keep[1] = document.getElementById('check2').checked;
    keep[2] = document.getElementById('check3').checked;

    return keep;
}

// Function to parse dice json returned from server and update the HTML
function updateRoll(dice) {
    let b = dice.body;
    player = b.player; // Global variable
    console.log('Returned Player is ',player);

    let die = b.die;
    let keep = b.keep;
    let total = b.total;
    console.log('Returned die are ',die);
    console.log('Returned dice kept are ', keep);
    console.log('Returned total is ',total);

    updateDiceView(player,die,total);
    updateCheckboxes(keep);
    updateTurnView(player);
}

// Function to parse json returned after a player completes their turn and update the HTML
function updateTurn(turn) {
    var b = turn.body;
    player = b.player; // Global variable
    console.log('Turn complete.  Returned new Player number is ', player);

    let keep = b.keep;
    console.log('Returned dice kept are ', keep);
    updateCheckboxes(keep);
    
    // Check to see if all players have completed their turn
    if ('winner' in b) {
        console.log('Everyone has completed their turn');
     
        let winner = b.winner;
        let wins = b.wins;
        let totals = b.totals;
        console.log('Winner',winner);
        console.log('Wins',wins)
        console.log('Totals',totals)
     
        updateWinnerView(winner);
        updateWinsTotalsView(wins,totals);

    } else {
        // Otherwise inform next Player that it is their turn
        updateTurnView(player);
    }
}

// Function to parse json returned after a change in the game state and update the HTML
function updateGameState(state) {
    var b = state.body;
    var which_player = b.player;
    console.log('State Update returned Player number ', player);

    let wins = b.wins;
    let totals = b.totals;
    console.log('State Update Wins',wins);
    console.log('State Update Totals',totals);

    let die = b.die;
    let keep = b.keep;
    console.log('Returned die are ',die);
    console.log('Returned dice kept are ', keep);

    updateTurnView(which_player);
    updateDiceView(which_player,die,totals[which_player]);
    updateWinsTotalsView(wins,totals);
    //updateCheckboxes(keep);
}

// Call the Server to roll the dice
function rollTheDice() {
    var baseAPI = gameEndpoint + "/roll_dice";

    // Get which dice the customer wants to keep
    let keep = getCheckboxValues();
    console.log('Checkbox values are ', keep);
   
    var diceAPI;
    var requestOptions = {};
    setTimeout(function () {

        if (false) {
            // For HTTP GET, Append the parameters to the URL
            diceAPI = baseAPI + "?keep1=" + keep[0] + "&keep2=" + keep[1] + "&keep3=" + keep[2];
            console.log('GET URL is ',diceAPI);
            // Pass as Array of Booleans
            //diceAPI = baseAPI + "?keep=" + keep;
            //console.log('GET URL is ',diceAPI);
         } else {
            // For HTTP POST, Put params in body
            diceAPI = baseAPI;    
            //var raw = {'keep1': keep[0], 'keep2': keep[1], 'keep3': keep[2]}
            let raw = {'keep': keep}
            requestOptions = {
                method: 'POST',
                mode: 'cors',
                headers: { 'Content-Type' : 'application/json'},
                body: JSON.stringify(raw)
            };
            console.log('POST options are',requestOptions);
        }

        fetch(diceAPI,requestOptions)
            .then(function (response) { 
                console.log('diceAPI Return status ', response.status); // 200
                //console.log(response.statusText); // OK
                return response.json();  // parses JSON response into native JavaScript objects
            })
            .then(function (json) {
                console.log(json);
                updateRoll(json);
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
            bankAPI = baseAPI + "?player=" + player;
            console.log('GET URL is ',bankAPI);
         } else {
            // For HTTP POST, Put params in body
            bankAPI = baseAPI;    
            let raw = {'player': player}           
            requestOptions = {
                method: 'POST',
                mode: 'cors',
                headers: { 'Content-Type' : 'application/json'},
                body: JSON.stringify(raw)
            };
            console.log('POST options are',requestOptions);
        }
           
        fetch(bankAPI,requestOptions)
            .then(function (response) { 
                console.log('bankAPI Return status ', response.status); // 200
                //console.log(response.statusText); // OK
                return response.json(); // parses JSON response into native JavaScript objects
            })
            .then(function (json) {
                console.log(json);
                updateTurn(json);
            })
            .catch(function(error) {
                console.log('ERROR in bankAPI fetch ', error);
            });       

    }, 100 );
}

// Long Poll the server every one second to get the game state
async function getGameState() {
    var gameStateAPI = gameEndpoint + "/get_game_state";
    var requestOptions = {};

    setTimeout(function () {      
        fetch(gameStateAPI,requestOptions)
            .then(function (response) { 
                console.log('gameStateAPI Return status ', response.status); // 200
                console.log(response.statusText); // OK
                return response.json(); // parses JSON response into native JavaScript objects
            })
            .then(function (json) {
                console.log(json);
                updateGameState(json);
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
                    console.log('ERROR in gemaeStateAPI fetch ', error);
                }                                  
            });
    }, 5000);
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

    total[1] = 0;
    for (i=0; i < NDICE; i++) {
        total[1] += die[i];
    }
    
    updateDiceView(1,die,total[1]);
 
    // Player 2 roll the dice
    die[0] = Math.floor(Math.random() * 6) + 1;
    die[1] = Math.floor(Math.random() * 6) + 1;
    die[2] = Math.floor(Math.random() * 6) + 1;

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