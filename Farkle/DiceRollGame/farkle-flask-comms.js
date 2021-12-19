var gameEndpoint = 'http://localhost:5000'; // example: 'http://mythi-publi-abcd12345-01234567890123.elb.us-east-1.amazonaws.com' 

// Make GET or POST call to backend Flask server
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
        console.log('POST Endpoint ' + endPoint + ' options are ' + requestOptions);
    }
    // GET
    else {
        console.log('GET Endpoint ' + endPoint); 
    }

    let jsObject = await fetch(endPoint,requestOptions)
        .then(function (response) { 
            console.log('serverCall: Return status ', response.status); // 200
            console.log(response.statusText); // OK
            return response.json();  // parses JSON response into native JavaScript objects
        })
        .catch(function(error) {
            console.log('ERROR in serverCall fetch ', error);
        })

    return jsObject;
}

// Initialize the game for two people to play using one browswer
function initGame() {
    var initGameAPI = gameEndpoint + "/init";
    console.log('GET URL is ',initGameAPI);

    // Make this a blocking call
    serverCall('get',initGameAPI).then(updateGameState);
}

// Call the Server to roll the dice
function rollDice() {
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
    if (false) {
        // HTTP Get is obsolote and no longer works
        // For HTTP GET, Append the parameters to the URL
        diceAPI = baseAPI + "?gameID=" + gameID + "&playerID=" + playerID + "&keep1=" + keptDice[0] + "&keep2=" + keptDice[1] + "&keep3=" + keptDice[2];
        // Pass as Array of Booleans
        //diceAPI = baseAPI + "?gameID=" + gameID + "&playerID=" + playerID + "&keep=" + keptDice;
        console.log('GET URL is ',diceAPI);
    } else {
        // For HTTP POST, Put params in body
        diceAPI = baseAPI;    
        let raw = {'gameID' : gameID, 'playerID': playerID, 'keptDice': keptDice};
        // Make this a blocking call
        serverCall('post',diceAPI,raw).then(updateRoll)
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
        serverCall('post',bankAPI,raw).then(updateTurn);
    }
}

// Long Poll the server every one second to get the game state
async function getGameState() {
    // For HTTP GET, Append the parameters to the URL
    var gameStateAPI = gameEndpoint + "/get_game_state" + "?gameID=" + gameID;
    console.log('GET URL is ',gameStateAPI);
    
    setTimeout(function () {
        // Make this a blocking call
        serverCall('get',gameStateAPI).then(updateGameState);
        getGameState();
    }, 1000);
}

// Long Poll the server to get the game state
//getGameState();