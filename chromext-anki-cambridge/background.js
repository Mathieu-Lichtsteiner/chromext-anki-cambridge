chrome.runtime.onInstalled.addListener(() => {
  chrome.action.disable();

  chrome.declarativeContent.onPageChanged.removeRules(undefined, () => {
    chrome.declarativeContent.onPageChanged.addRules([{
      conditions: [
        new chrome.declarativeContent.PageStateMatcher({
          pageUrl: {
            hostEquals: 'dictionary.cambridge.org',
            pathPrefix: '/dictionary/'
          }
        })
      ],
      actions: [new chrome.declarativeContent.ShowAction()]
    }]);
  });
});
