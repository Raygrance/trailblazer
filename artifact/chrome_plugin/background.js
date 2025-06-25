/*chrome.webRequest.onBeforeRequest.addListener(
  function(details) {
    console.log("Request URL: " + details.url);
    console.log("Request Method: " + details.method);
    console.log("Request Headers: " + details.requestHeaders);
  },
  {urls: ["<all_urls>"]}
);


chrome.webRequest.onCompleted.addListener(
  function(details) {
    console.log("Response URL: " + details.url);
    console.log("Response Headers: " + details.responseHeaders);
    console.log(details)
  },
  {urls: ["<all_urls>"]}
);
*/


chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log(message)
    
    fetch('http://127.0.0.1:8086/record', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(message)
        })
            .then(response => response.json())
            .then(response => sendResponse(response))
            .catch(error => console.log('Error:', error));
})