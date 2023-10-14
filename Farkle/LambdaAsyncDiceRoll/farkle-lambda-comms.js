async function lambdaCall(lambdaBody) {
    // instantiate a headers object
    var myHeaders = new Headers();
    // add content type header to object
    myHeaders.append("Content-Type", "application/json");
    var requestOptions = {
        method: 'POST',
//	mode: 'no-cors',
        headers: myHeaders,
        body: JSON.stringify(lambdaBody),
        redirect: 'follow'
    };
    console.log('lambdaCall input: ', lambdaBody);
    // make API call with parameters and use promises to get response
    //let jsObject = await fetch("https://gfkcm1eej6.execute-api.us-west-2.amazonaws.com/dev", requestOptions) //Prod Lambda (helloWorld //Prod Lambda (helloWorldFunction)	
    let jsObject = await fetch ("https://joj0qaxn6c.execute-api.us-west-2.amazonaws.com/dev", requestOptions) // FarkleTestBed
    .then(function (response) { 
    //    console.log('lambdaCall: Return status ', response.status); // 200
    //    console.log(response.statusText); // OK
        return response.json();  // parses JSON response into native JavaScript objects
    })
    .catch(function(error) {
        console.log('ERROR in serverCall fetch ', error);
    })

  //  console.log('lambdaCall: jsObject ', jsObject)
    mybody = jsObject.body;
  console.log('lambdaCall: mybody ', mybody)

    return mybody;
}

// Init game for two people one browser
function initGame(){
    console.log("Initing game");
    // create a JSON object with parameters for API call and store in a variable
    var lambdaBody = {"action":"init_game"};
    var lResult;
    var plResult;
    lambdaCall(lambdaBody)
    .then(updateGameState);

  // Start long polling
  getGameState();
}

 // Function to roll the dice
 function rollDice() {

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
      var lambdaBody = {"action":"roll_dice", "playerID":playerID, "gameID": gameID, "keptDice": keep};
      lambdaCall(lambdaBody)
	    .then(updateRoll);
  }


// Long Poll the server every two second to get the game state
async function getGameState(){
  // create a JSON object with parameters for API call and store in a variable
//What is gameID here?
  var lambdaBody = {"action":"get_game_state", "gameID": gameID};
  console.log("getGameState lambdabody:" + lambdaBody);
  var lResult;
  var plResult;
 
  // Make this a blocking call
  let jsObject = await lambdaCall(lambdaBody);
  let gameStateDict = updateGameState(jsObject);
  //console.log('getGameState returned player is ', gameStateDict.player, " XXX");
 
  // check to see if it is the bots turn and if so, do one step in a bot turn
  if (gameStateDict.player == 2) {
  //if (true) {
  //    doOneBotStep(gameStateDict);
  }     
 
  setTimeout(function (){
      getGameState();
  }, 500);
}

// Call the Server to end players turn and bank score
function bankScore(){
  // create a JSON object with parameters for API call and store in a variable
  var lambdaBody = {"action":"bank", "playerID":playerID, "gameID": gameID};
  console.log("bankscore lambdabody:" + lambdaBody);
  var lResult;
  var plResult;
  lambdaCall(lambdaBody)
  .then(updateTurn);
}

// Call the Server to determine whether to roll or bank and which dice to keep
// Returns a Java Script policy dictionary
function doBotPolicy(gameStateDict) {
  // Get parametes from gameStateDict
  let diceVals = gameStateDict.diceVals;
  let prevKeptDice = gameStateDict.previouslyKeptDice;
  let score = gameStateDict.turnScore;
  let totals = gameStateDict.totals;
  
  console.log('In doBotPolicy prevKeptDice ', prevKeptDice);

   // create a JSON object with parameters for API call and store in a variable
   var lambdaBody = {"action":"do_bot_policy", 'diceVals' : diceVals, 'previouslyKeptDice' : prevKeptDice, 'turnScore' : score, 'totals' : totals, 'playerID' : playerID, 'whichPolicy' : playerID};
   console.log("bankscore lambdabody:" + lambdaBody);
   
   lambdaCall(lambdaBody)
   .then(implementPolicy);
}
