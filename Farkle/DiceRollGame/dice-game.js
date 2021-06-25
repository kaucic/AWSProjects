var gameEndpoint = 'http://localhost:5000'; // example: 'http://mythi-publi-abcd12345-01234567890123.elb.us-east-1.amazonaws.com'
//var diceAPI = "https://ghibliapi.herokuapp.com/people";    

// Initialize game
var NDICE = 3;
var NPlayers = 2;
var player = 1;
// Note: Index 0 is not used and is a special case representing a tie
var players = new Array(NPlayers+1);
var wins = new Array(NPlayers+1);
players[1] = "Player 1";
players[2] = "Player 2";

// Used only for the client javascript solution
wins[1] = 0;
wins[2] = 0;

// Function to change the player name
function editNames() {
    players[1] = prompt("Change Player1 name");
    players[2] = prompt("Change player2 name");

    document.querySelector("p.Player1").innerHTML = players[1];
    document.querySelector("p.Player2").innerHTML = players[2];
}

// Update the HTML DOM for winner
function updateWinnerView(winner,wins1,wins2) {
    if (winner == 0) {
        document.querySelector("h1").innerHTML = "Draw!";
    }
    else if (winner == 1) {
        document.querySelector("h1").innerHTML 	= (players[1] + " WINS!");
    }
    else {
        document.querySelector("h1").innerHTML = (players[2] + " WINS!");    
    }

    document.querySelector("span.Points1").innerHTML 	= wins1;
    document.querySelector("span.Points2").innerHTML 	= wins2;
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
    console.log("updateCheckboxes keep is", keep);

    document.getElementById('check1').checked = keep[0];
    document.getElementById('check2').checked = keep[1];
    document.getElementById('check3').checked = keep[2];

    var new_keep = getCheckboxValues();
    console.log("new_keep is", new_keep);
}

// Get which dice the Player has selected to keep
function getCheckboxValues() {
    var keep = new Array(NDICE);
    keep[0] = document.getElementById('check1').checked;
    keep[1] = document.getElementById('check2').checked;
    keep[2] = document.getElementById('check3').checked;

    return keep;
}

// Function to parse json returned after a player completes their turn and update the HTML
function updateTurn(turn) {
    var b = turn.body;
    player = b.player; // Global variable
    console.log('Turn complete.  New Player number is ', player);

    var keep = new Array(NDICE);
    keep[0] = b.keep1;
    keep[1] = b.keep2;
    keep[2] = b.keep3;
    console.log('Dice kept are ', keep);

    updateCheckboxes(keep);
    
    // Check to see if all players have completed their turn
    if ('winner' in b) {
        console.log('Everyone has completed their turn');
        var winner = b.winner;
        var wins1 = b.wins1;
        var wins2 = b.wins2;
        var total1 = b.total1;
        var total2 = b.total2;

        console.log('Winner',winner);
        console.log('Wins1',wins1)
        console.log('Wins2',wins2)
        console.log('Total1',total1)
        console.log('Total2',total2)

        updateWinnerView(winner,wins1,wins2);

    // Otherwise inform next Player that it is their turn
    } else {
        updateTurnView(player)
    }
}

// Function to parse dice json returned from server and update the HTML
function updateRoll(dice) {
    var b = dice.body;
    player = b.player; // Global variable
    console.log('Player',player);

    var die = new Array(NDICE);
    die[0] = b.die1;
    die[1] = b.die2;
    die[2] = b.die3;

    console.log('Die are ',die);
   
    var keep = new Array(NDICE);
    keep[0] = b.keep1;
    keep[1] = b.keep2;
    keep[2] = b.keep3;
    console.log('Dice kept are ', keep);

    var total = b.total;
    console.log('Total',total);

    updateDiceView(player,die,total);
    updateCheckboxes(keep);
    updateTurnView(player);
}

// Call the Server to roll the dice
function rollTheDice() {
    var baseAPI = gameEndpoint + "/roll_dice";

    // Get which dice the customer wants to keep
    var keep = getCheckboxValues();
    console.log('Keep values are ', keep);
   
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
            var raw = {'keep1': keep[0], 'keep2': keep[1], 'keep3': keep[2]}
            var raw_array = {'keep': keep}
            requestOptions = {
                method: 'POST',
                mode: 'cors',
                headers: { 'Content-Type' : 'application/json'},
                body: JSON.stringify(raw_array)
            };
            console.log('POST options are',requestOptions);
        }

        fetch(diceAPI,requestOptions)
            .then(function (response) { 
                console.log('Return status ', response.status); // 200
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
            var raw = {'player': player}           
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
                console.log('Return status ', response.status); // 200
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

// Client side only solution that rolls the dice in javascript
function js_rollTheDice() {
    // Player 1 roll the dice
    var die1 = Math.floor(Math.random() * 6) + 1;
    var die2 = Math.floor(Math.random() * 6) + 1;
    var die3 = Math.floor(Math.random() * 6) + 1;

    var total1 = die1 + die2 + die3;

    updateDiceView(1,die1,die2,die3,total1);

    // Player 2 roll the dice
    var die1 = Math.floor(Math.random() * 6) + 1;
    var die2 = Math.floor(Math.random() * 6) + 1;
    var die3 = Math.floor(Math.random() * 6) + 1;

    var total2 = die1 + die2 + die3;
  
    updateDiceView(2,die1,die2,die3,total2);

    var winner;
    if (total1 > total2) {
        winner = 1
        wins[1] += 1;
    }
    else if (total2 > total1) {
        winner = 2;
        wins[2] += 1;
    }
    else {
        winner = 0
    }   

    updateWinnerView(winner,wins[1],wins[2])
}