// Listen for runtime messages
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('Side panel received message:', message);
    
    if (message.type === 'SUMMARY_SENTIMENT' && message.data) {
        updateResults(message.data);
        updateStatus('Analysis updated: ' + new Date().toLocaleTimeString());
    }
});

function updateStatus(message) {
    const status = document.getElementById('status');
    if (status) {
        status.textContent = message;
    }
}

function updateResults(data) {
    console.log('Updating results with:', data);
    
    const container = document.getElementById("results");
    if (!container) {
        console.error('Results container not found');
        return;
    }

    // Add animation class for updates
    container.innerHTML = `
        <div class="analysis-content">
            <h3>Sentiment Analysis</h3>
            <p><strong>Overall Tone:</strong> <span class="${data.overall_tone.toLowerCase()}">${data.overall_tone}</span></p>
            <p><strong>Top Emotions:</strong> ${data.top_emotions.map(([e, count]) => `<span class="emotion">${e} (${count})</span>`).join(', ')}</p>
            <!-- <div class="summary-text">
                ${data.summary_text}
            </div> -->
        </div>
    `;
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'SUMMARY_SENTIMENT' && message.data) {
        updateResults(message.data);
        updateStatus('Analysis updated: ' + new Date().toLocaleTimeString());
    }
});


// Initialize
updateStatus('Connected and waiting for analysis...');
chrome.runtime.sendMessage({ type: 'REQUEST_LATEST_ANALYSIS' }, response => {
    if (response && response.data) {
        updateResults(response.data);
        updateStatus('Analysis loaded: ' + new Date().toLocaleTimeString());
    } else {
        updateStatus('No analysis yet.');
    }
});


console.log('SidePanel script loaded and ready');
