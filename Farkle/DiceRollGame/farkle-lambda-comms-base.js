async function lambdaCall(lambdaBody) {
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
	
    let response = await fetch("https://gfkcm1eej6.execute-api.us-west-2.amazonaws.com/dev", requestOptions);
    let result = await response.json();
    //console.log("await fetch: ", result.body);
    mybody = result.body;

    return mybody;
}
