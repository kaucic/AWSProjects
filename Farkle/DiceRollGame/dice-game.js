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

// Used only for the client javascript solution
var wins = new Array(NPlayers+1);
wins[0] = -1;
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
function updateWinnerView(winner,wins) {
    if (winner == 0) {
        document.querySelector("h1").innerHTML = "Draw!";
    }
    else if (winner == 1) {
        document.querySelector("h1").innerHTML 	= (players[1] + " WINS!");
    }
    else {
        document.querySelector("h1").innerHTML = (players[2] + " WINS!");    
    }

    document.querySelector("span.Points1").innerHTML 	= wins[1];
    document.querySelector("span.Points2").innerHTML 	= wins[2];
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
    var keep = new Array(NDICE);
    keep[0] = document.getElementById('check1').checked;
    keep[1] = document.getElementById('check2').checked;
    keep[2] = document.getElementById('check3').checked;

    return keep;
}

// Function to parse dice json returned from server and update the HTML
function updateRoll(dice) {
    var b = dice.body;
    player = b.player; // Global variable
    console.log('Returned Player is ',player);

    var die = b.die;
    var keep = b.keep;
    var total = b.total;
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

    var keep = b.keep;
    console.log('Returned dice kept are ', keep);
    updateCheckboxes(keep);
    
    // Check to see if all players have completed their turn
    if ('winner' in b) {
        console.log('Everyone has completed their turn');
        var winner = b.winner;
        var wins = b.wins;
        var total = b.total;

        console.log('Winner',winner);
        console.log('Wins',wins)
        console.log('Total',total)
        updateWinnerView(winner,wins);

    // Otherwise inform next Player that it is their turn
    } else {
        updateTurnView(player)
    }
}

// Call the Server to roll the dice
function rollTheDice() {
    var baseAPI = gameEndpoint + "/roll_dice";

    // Get which dice the customer wants to keep
    var keep = getCheckboxValues();
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
            var raw = {'keep': keep}
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