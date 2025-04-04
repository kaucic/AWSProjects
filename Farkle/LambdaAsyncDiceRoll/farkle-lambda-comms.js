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
        console.log('lambdaCall: Return status ', response.status); // 200
        //console.log(response.statusText); // OK
        return response.json();  // parses JSON response into native JavaScript objects
    })
    .catch(function(error) {
        console.log('ERROR in serverCall fetch ', error);
    })

    //console.log('lambdaCall: jsObject ', jsObject)
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
    vSI = 0; 
    thisPlayer = 1;
    activePlayer = 1; //Player 1 always goes first.
    // Start long polling
    //getGameState(false);
}

// Function to roll the dice
function rollDice() {

    if (thisPlayer != activePlayer){
      //do alert 'not your turn'
      alert('It is not your turn yet.');
      return;
    }

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
      var lambdaBody = {"action":"roll_dice", "playerID":thisPlayer, "gameID": gameID, "keptDice": keep};
      lambdaCall(lambdaBody)
	    .then(updateRoll);
}

// Long Poll the server every two second to get the game state
async function initPlayer2(){
  // create a JSON object with parameters for API call and store in a variable
  //What is gameID here?
  console.log("gameID :" + gameID);
  var lambdaBody;
  console.log("getGameState lambdabody:" + lambdaBody);
  var lResult;
  var plResult;
  
  // you are starting as Player 2; so get the gameID and init the view State Index.
  lambdaBody = {"action":"get_game_state"}; 
  thisPlayer = 2; 
  vSI = 0; 
  
  // Make this a blocking call
  let jsObject = await lambdaCall(lambdaBody);
  let gameStateDict = updateGameState(jsObject, false);
  //console.log('getGameState returned player is ', gameStateDict.player, " XXX");
 
}

// Long Poll the server every two second to get the game state
async function getGameState(){
  // create a JSON object with parameters for API call and store in a variable
//What is gameID here?
  console.log("gameID :" + gameID);
  var lambdaBody;
  console.log("getGameState lambdabody:" + lambdaBody);
  var lResult;
  var plResult;
  

  lambdaBody = {"action":"get_game_state", "gameID": gameID};

  // Make this a blocking call
  let jsObject = await lambdaCall(lambdaBody);
  let gameStateDict = updateGameState(jsObject, true);
  //console.log('getGameState returned player is ', gameStateDict.player, " XXX");
 
  // check to see if it is the bots turn and if so, do one step in a bot turn
  if (gameStateDict.player == 2) {
  //if (true) {
  //    doOneBotStep(gameStateDict);
  }     
  
  //setTimeout(function (){
  //    getGameState();
  //}, 5000);
}
 
// Call the Server to end players turn and bank score
function bankScore(){

  if (thisPlayer != activePlayer){
      //do alert 'not your turn'
      alert('It is not your turn yet.');
      return;
  }

  // create a JSON object with parameters for API call and store in a variable
  var lambdaBody = {"action":"bank", "playerID":thisPlayer, "gameID": gameID};
  console.log("bankscore lambdabody:" + lambdaBody);
  var lResult;
  var plResult;
  lambdaCall(lambdaBody)
  .then(updateTurn);
}
 
// Call the Server to do a full turn as the bot. The bot is player 2
function doBotTurn(whichPolicy) {
  // Get parametes from gameStateDict
   console.log('In doBotTurn');
   var whichPolicy = 1;

   // create a JSON object with parameters for API call and store in a variable
   var lambdaBody = {"action":"do_bot_turn", "playerID" : 3, "whichPolicy" : whichPolicy, "gameID": gameID};
   console.log("doBotTurn lambdabody:" + lambdaBody);
   
   lambdaCall(lambdaBody)
   .then(updateTurn);
}
