// chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
//     if( request.message === "clicked_browser_action" ) {
//       chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
//         var activeTab = tabs[0];
//         // chrome.tabs.sendMessage(activeTab.id, {"message": "clicked_browser_action"});
//         console.log(activeTab.url)
//       });
//     }
//   }
// );