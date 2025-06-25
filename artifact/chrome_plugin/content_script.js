var s = document.createElement('script');
s.src = chrome.runtime.getURL('injected.js');
s.onload = function() {
    this.remove();
};
(document.head || document.documentElement).appendChild(s);

window.addEventListener('mafuzzmessage', (message) => {
    console.log(message)
    
    chrome.runtime.sendMessage(message.detail)
})
