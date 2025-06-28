// Initialize game
var NDICE = 6;
var NPlayers = 3;
var gameID = "none";
// Note: A PlayerID value of 0 is not used and is a special case representing a game that hasn't started or a tie
var thisPlayer = 0;
var activePlayer = 0;  //Whose turn is it?
var playerNames = Array(NPlayers+1);
var vSI = 0;
playerNames[1] = "Player1";
playerNames[2] = "Player2";
playerNames[3] = "Player3";
previouslyKeptDice = Array(NDICE).fill(false);

// Update the HTML DOM to broadcast message
function updateMessage(msg) {
    document.querySelector("h1").innerHTML = msg;
}

// Update the names of the players
function updatePlayerNamesView(names) {
    if (thisPlayer == 1){
        document.querySelector("span.Player1").style.backgroundColor = "red";}  
    if (thisPlayer == 2){
        document.querySelector("span.Player2").style.backgroundColor = "red";}
    document.querySelector("span.Player1").innerHTML = ("Player 1: " + playerNames[1]);
    document.querySelector("span.Player2").innerHTML = ("Player 2: " + playerNames[2]);
    document.querySelector("span.Player3").innerHTML = ("Player 3: " + playerNames[3]);

}

// Update the HTML DOM totals
function updateTurnScoreAndTotalsView(turnScore,totals) {
    document.querySelector("span.TurnScore").innerHTML  = turnScore; 
    document.querySelector("span.gameID").innerHTML = gameID;  
    document.querySelector("span.Total1").innerHTML 	= totals[1];
    document.querySelector("span.Total2").innerHTML 	= totals[2];
    document.querySelector("span.Total3").innerHTML 	= totals[3];
}    

// Update the HTML DOM for players turn
function updateTurnView(state) {
    if (state.whoWon) {
       document.querySelector("h1").innerHTML = (playerNames[state.whoWon] + " Won!");
    }
    else {
       document.querySelector("h1").innerHTML = (playerNames[state.player] + "\'s turn");
    }
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
function updateRoll(roll) {
    let b = roll;
    let gID = b.gameID;
    let valid = b.valid;

    if (valid == true) {
        let player = b.player;
        console.log('updateRoll Returned Player is ',player);

        let farkled = b.farkled;
        console.log('farkled is ',farkled);
        //console.log('rolledOnceOrMore is', b.rolledOnceOrMore)
        let die = b.diceVals;
        let turnScore = b.turnScore;
        
        console.log('updateRoll die are ',die);
        console.log('updateRoll dice kept are ', previouslyKeptDice);
        console.log('updateRoll turnScore is ',turnScore);
        
        updateDiceView(player,die,turnScore);
        if (farkled == true) {
            console.log('Displaying Farkle!');
            updateMessage("Farkle!");
            setTimeout(function() {
                updateTurn(roll);
            }, 3000);  
        }
        else {
          vSI++;
        }
        previouslyKeptDice = b.previouslyKeptDice; // Update Global variable for dice that are set aside
        updateCheckboxes(previouslyKeptDice);
    }

    else {
     console.log('alert in updateRoll b is',b);
        alert(b.errMsg);
    }

    return b;
}

// Function to parse json returned after a player completes their turn and update the HTML
// Input is the body of the Java Script object returned from the server
function updateTurn(turn) {
    var b = turn;
    let valid = b.valid;
 
    if (valid == true) {
        let gID = b.gameID;

        activePlayer = b.player;
        console.log('updateTurn complete.  Returned new Player number is ', activePlayer);

        let turnScore = b.turnScore;
        let totals = b.totals;
        vSI++;
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
            updateTurnView(turn);       
        }    
    }
    else {
        console.log('alert in updateTurn b is',b);
        alert (b.errMsg);
    }
        
    if (b.player == 3){
        doBotTurn();
    }
}

// Function to parse json returned after a change in the game state and update the HTML
// Input is the body of the Java Script object returned from the server
function updateGameState(state,doNextMove) {
    var b = state;
    var totals = [];
    var turnscore;
    gameID = b.gameID;
    console.log('updateGameState returned gameID ', gameID);
    console.log('uGS-state: ', state);
    console.log('uSG-doNextMove: ', doNextMove);
 
   if (vSI <= b.viewStateIndex){ 
      playerNames = b.playerNames;  // Global variable
      //console.log('State Update playerNames ',playerNames);
      console.log('uGS-vSI:', vSI);
      totals = b.viewStateList[vSI].totals;
      turnScore = b.viewStateList[vSI].turnScore;
      //console.log('State Update Totals',totals);

      die = b.viewStateList[vSI].diceVals;    
      activePlayer = b.viewStateList[vSI].player;
      previouslyKeptDice = b.viewStateList[vSI].previouslyKeptDice; // Update Global variable
      updateTurnView(b.viewStateList[vSI]);
      updatePlayerNamesView(playerNames);
    
      updateDiceView(activePlayer,die,totals[activePlayer]);
      updateTurnScoreAndTotalsView(turnScore,totals);
       if (b.viewStateList[vSI].farkled == true) {
            console.log('Displaying oppenent Farkle!');
            updateMessage("Farkle!");
            FarkleVSI = vSI;
            setTimeout(function() {
                updateTurnView(b.viewStateList[FarkleVSI]);
            }, 3000); 
       }
      // Only update the check boxes when you are not the active player to not interfere with selections being made
      if (thisPlayer != activePlayer) {
        updateCheckboxes(previouslyKeptDice);
      }
      vSI++;
    }
    return b;
}


// Function to change the player name for this client and start the game
function editName() {
    yourName = prompt("Enter your name");
    playerNames[thisPlayer] = yourName;
    updatePlayerNamesView(playerNames);
}
