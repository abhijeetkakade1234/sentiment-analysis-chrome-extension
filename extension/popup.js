document.getElementById('openPanel').addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  await chrome.sidePanel.open({ tabId: tab.id });

  // trigger extraction via message (not DOM event!)
  chrome.tabs.sendMessage(tab.id, { type: 'TRIGGER_EXTRACTION' }, async (response) => {
  if (chrome.runtime.lastError) {
    console.warn('Content script not found, injecting it...');

    // Inject contentScript manually
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ['contentScript.js']
    });

    // Try sending the message again
    chrome.tabs.sendMessage(tab.id, { type: 'TRIGGER_EXTRACTION' });
  }
});

});
