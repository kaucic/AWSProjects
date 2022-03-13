var gameEndpoint = 'http://localhost:5000'; // example: 'http://mythi-publi-abcd12345-01234567890123.elb.us-east-1.amazonaws.com' 

// Make GET or POST call to backend Flask server
// Returns the extracted body from the Servers json packet
async function serverCall(GetPost,endPoint,rawBody={}) {
    var requestOptions = {};
    // POST
    if (GetPost == 'post') {
        requestOptions = {
            method: 'POST',
            mode: 'cors',
            headers: { 'Content-Type' : 'application/json'},
            body: JSON.stringify(rawBody)
        };
        console.log('POST Endpoint ', endPoint, ' options are ', requestOptions);
    }
    // GET
    else {
        console.log('GET Endpoint ', endPoint); 
    }

    let jsObject = await fetch(endPoint,requestOptions)
    .then(function (response) { 
        console.log('serverCall: Return status ', response.status); // 200
        //console.log(response.statusText); // OK
        return response.json();  // parses JSON response into native JavaScript objects
    })
    .catch(function(error) {
        console.log('ERROR in serverCall fetch ', error);
    })

    // Extract bddy from returned json
    let myBody = jsObject.body;

    return myBody;
}

// Long Poll the server every one second to get the game state and potentially do Bot step
async function getGameState() {
    // For HTTP GET, Append the parameters to the URL
    var gameStateAPI = gameEndpoint + "/get_game_state" + "?gameID=" + gameID;
    
    // Make this a blocking call
    let jsObject = await serverCall('get',gameStateAPI);
    let gameStateDict = updateGameState(jsObject);
    console.log('getGameState returned player is ', gameStateDict.player, " XXX");
   
    // check to see if it is the bots turn and if so, do one step in a bot turn
    //if (gameStateDict.player == 2) {
    if (true) {
        doOneBotStep(gameStateDict);
    }     
    setTimeout(function () {
        getGameState();
    }, 2000);
}

// Initialize the game for two people to play using one browswer
function initGame() {
    var initGameAPI = gameEndpoint + "/init";
    console.log('initGame GET URL is ',initGameAPI);

    // Make this a blocking call
    serverCall('get',initGameAPI).then(updateGameState);

    // Start long polling
    getGameState();
}

// Call the Server to roll the dice
// Returns a Java Script roll dice dictionary
function rollDice(keptDice) {
    var baseAPI = gameEndpoint + "/roll_dice";
    var diceAPI;

    if (false) {
        // HTTP Get is obsolote and no longer works
        // For HTTP GET, Append the parameters to the URL
        diceAPI = baseAPI + "?gameID=" + gameID + "&playerID=" + playerID + "&keep1=" + keptDice[0] + "&keep2=" + keptDice[1] + "&keep3=" + keptDice[2];
        // Pass as Array of Booleans
        //diceAPI = baseAPI + "?gameID=" + gameID + "&playerID=" + playerID + "&keep=" + keptDice;
        console.log('GET URL is ',diceAPI);
    }
    else {
        // For HTTP POST, Put params in body
        diceAPI = baseAPI;    
        let raw = {'gameID' : gameID, 'playerID': playerID, 'keptDice': keptDice};
        // Make this a blocking call
        rollDiceDict = serverCall('post',diceAPI,raw).then(updateRoll)
    }
}

// Call the Server to end players turn and bank score
function bankScore() {
    var baseAPI = gameEndpoint + "/bank_score";
    var bankAPI;
 
    if (false) {
        // For HTTP GET, Append the parameters to the URL
        bankAPI = baseAPI + "?gameID=" + gameID + "&playerID=" + playerID;
        console.log('GET URL is ',bankAPI);
        // Make this a blocking call
        serverCall('get',bankAPI).then(updateTurn);
    }
    else {
        // For HTTP POST, Put params in body
        bankAPI = baseAPI;    
        let raw = {'gameID' : gameID, 'playerID': playerID};
        // Make this a blocking call           
        let bankScoreDict = serverCall('post',bankAPI,raw).then(updateTurn);
    }
}

// Call the Server to determine whether to roll or bank and which dice to keep
// Returns a Java Script policy dictionary
function doBotPolicy(gameStateDict) {
    var botPolicyAPI = gameEndpoint + "/do_bot_policy";

    // Get parametes from gameStateDict
    let diceVals = gameStateDict.diceVals;
    let prevKeptDice = gameStateDict.previouslyKeptDice;
    let score = gameStateDict.turnScore;
    
    console.log('In doBotPolicy prevKeptDice ', prevKeptDice);

    // For HTTP POST, Put params in body   
    let raw = {'gameID' : gameID, 'diceVals' : diceVals, 'previouslyKeptDice' : prevKeptDice, 'turnScore' : score, 'whichPolicy' : playerID};

    // Make this a blocking call           
    let botPolicyDict = serverCall('post',botPolicyAPI,raw).then(implementPolicy);
    //raw['action'] = 'do_bot_policy';
    //foo = JSON.stringify(raw);
    //let botPolicyDict = lambdaCall(foo).then(implementPolicy);
}

