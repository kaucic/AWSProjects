

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

	// Player name
  var player1 = "Player 1";
  var player2 = "Player 2";
  var wins1 = 0;
  var wins2 = 0;
  var mybody;
  var pmybody;
  var turn;


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
    let b = dice.body;
    let gID = b.gameID;
    let valid = b.valid;
    console.log('updateRoll validity is ', valid);

    if (valid == true) {
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
        alert("It is not your turn to roll.");
    }
}

// Function to parse json returned after a player completes their turn and update the HTML
function updateTurn(turn) {
    var b = turn.body;
    let gID = b.gameID;
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
    let gID = b.gameID;
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


  function lambdaCall(lambdaBody) {
                // instantiate a headers object
                var myHeaders = new Headers();
                // add content type header to object
                myHeaders.append("Content-Type", "application/json");
                var requestOptions = {
                                method: 'POST',
                                headers: myHeaders,
                                body: lambdaBody,
                                redirect: 'follow'
                            };
                // make API call with parameters and use promises to get response
                setTimeout(function () {
                    fetch("https://gfkcm1eej6.execute-api.us-west-2.amazonaws.com/dev", requestOptions)
		            //.then(response => response.text())
		            //.then(result => alert(JSON.parse(result).body))
		            //.then(result => console.log('result', result))
		            //.then(result => mybody = JSON.parse(result).body)
		            //.catch(error => console.log('error', error));

                    .then(function (response) { 
                        console.log('lambdaCall Return status ', response.status); // 200
                        console.log(response.statusText); // OK
                        return response.json();  // parses JSON response into native JavaScript objects
                    })
                    .then(function (jsObject) {
                        console.log(jsObject);
                        //updateRoll(jsObject);
                        mybody = jsObject;
                    })
                    .catch(function(error) {
                        console.log('ERROR in lambdaCall fetch ', error);
                    })
                    

                }, 3000);

	  return mybody;
  }

// Init game for two people one browser
function initGame(){
    console.log("Initing game");
    // create a JSON object with parameters for API call and store in a variable
    var lambdaBody = JSON.stringify({"action":"init_game"});
    var lResult;
    var plResult;
    lResult = lambdaCall(lambdaBody);
    //document.getElementById("Lambda_result").innerHTML = lResult;
    console.log(lResult);
    var gameId = lResult.game_id;
    console.log("Game Id is:  " + gameId);
  }


  function bankScore(){
    // create a JSON object with parameters for API call and store in a variable
    var lambdaBody = JSON.stringify({"action":"bank"});
    var lResult;
    var plResult;
    lResult = lambdaCall(lambdaBody);
    //document.getElementById("Lambda_result").innerHTML = lResult;
    console.log(lResult);
    var gameId = lResult.game_id;
    console.log("Game Id is:  " + gameId);
  }


// Call the Server to end players turn and bank score
/*
function bankScore() {
    var baseAPI = gameEndpoint + "/bank_score";

    var bankAPI;
    var requestOptions = {};
    setTimeout(function () {

        if (false) {
            // For HTTP GET, Append the parameters to the URL
            bankAPI = baseAPI + "?gameID=" + gameID + "&playerID=" + playerID;
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
*/

// Function to change the player name
  function editNames() {
    player1 = prompt("Change Player1 name");
    player2 = prompt("Change player2 name");
    var lambdaBody = JSON.stringify({"action":"edit_names","player1Name":player1,"player2Name":player2});
    var lResult = lambdaCall(lambdaBody);
    //console.log(lResult);

    document.getElementById("Lambda_result").innerHTML = lResult;

    document.querySelector("p.Player1").innerHTML = player1;
    document.querySelector("p.Player2").innerHTML = player2;
  }

  // Function to roll the dice
  function rollDice(turn) {
    setTimeout(function () {
      //var randomNumber1 = Math.floor(Math.random() * 6) + 1;
      //var randomNumber2 = Math.floor(Math.random() * 6) + 1;

      var lambdaBody = JSON.stringify({"action":"roll"});
      var lResult;
      var plResult;
      plResult = lambdaCall(lambdaBody);
      document.getElementById("Lambda_result").innerHTML = lResult;
      console.log(plResult);
      console.log("first die " + plResult.die1);
      console.log("second die " + plResult.die2);
      var randomNumber1 = plResult.die1;
      var randomNumber2 = plResult.die2;
      var randomNumber3 = plResult.die3;
      
       document.querySelector("p.Die1").innerHTML = randomNumber1;
       document.querySelector("p.Die2").innerHTML = randomNumber2;
       document.querySelector("p.Die3").innerHTML = randomNumber3;
      document.querySelector(".img1").setAttribute("src",
				  "dice" + randomNumber1 + ".png");
  
      document.querySelector(".img2").setAttribute("src",
				  "dice" + randomNumber2 + ".png");
  
      document.querySelector(".img3").setAttribute("src",
				  "dice" + randomNumber3 + ".png");
  
      if (randomNumber1 === randomNumber2) {
	      document.querySelector("h1").innerHTML = "Draw!";
      }
  
     else if (randomNumber1 < randomNumber2) {
      wins2 += 1;
      document.querySelector("h1").innerHTML 	= (player2 + " WINS!");
      document.querySelector("p.Points2").innerHTML 	= wins2;
      }
  
     else {
      wins1 += 1;
      document.querySelector("h1").innerHTML = (player1 + " WINS!");
      document.querySelector("p.Points1").innerHTML 	= wins1;
      }
    }, 2500);
  }
