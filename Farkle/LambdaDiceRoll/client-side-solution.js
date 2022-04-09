// Initialize game
var NDICE = 6;
var NPlayers = 2;

// Used only for the client javascript solution
var wins = new Array(NPlayers+1);
wins[0] = -1;
wins[1] = 0;
wins[2] = 0;

// Client side only solution that rolls the dice in javascript
// Obsolete: was written for total score wins rules instead of Farkle rules
function js_rollDice() {
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