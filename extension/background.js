chrome.runtime.onInstalled.addListener(() => {
    chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: false });
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === "complete") {
        chrome.sidePanel.setOptions({
            tabId,
            path: "sidePanel.html",
            enabled: true
        });
    }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('Background received message:', message);

    try {
        switch (message.type) {
            case 'EXTRACTED_TEXT_BLOCKS':
                fetch('http://localhost:8000/analyze_summary', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ blocks: message.blocks })
                })
                .then(res => res.json())
                .then(data => {
                    chrome.storage.local.set({ latestAnalysis: data }, () => {
                        console.log('Analysis stored in chrome.storage');

                        chrome.tabs.query({}, tabs => {
                            tabs.forEach(tab => {
                                chrome.runtime.sendMessage({
                                    type: 'SUMMARY_SENTIMENT',
                                    data
                                });
                            });
                        });
                    });
                })
                .catch(err => console.error('Backend fetch failed:', err));

                sendResponse({ status: 'fetching' });
                break;

            case 'REQUEST_LATEST_ANALYSIS':
                chrome.storage.local.get('latestAnalysis', result => {
                    if (result.latestAnalysis) {
                        sendResponse({
                            type: 'SUMMARY_SENTIMENT',
                            data: result.latestAnalysis
                        });
                    } else {
                        sendResponse({});
                    }
                });
                return true; // Keep channel open
        }
    } catch (e) {
        console.error('Error handling message:', e);
    }

    return true;
});
