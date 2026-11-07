document.getElementById('syncBtn').addEventListener('click', async () => {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = "Scraping Blackboard page...";

    // Get active browser tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if(!tab.url || !tab.url.toLowerCase().includes("blackboard")){
        statusDiv.textContent = "Error: Please open a Blackboard course page first.";
        statusDiv.style.color = "red";
        return;
    }

    // Execute script to extract data via content.js
    chrome.tabs.sendMessage(tab.action || tab.id, { action: "scrape_blackboard" }, async (response) => {
        // Fallback if message passing needs scripting injection injection
        if (chrome.runtime.lastError) {
            // Inject content script manually if not loaded
            chrome.scripting.executeScript({
                target: { tabId: tab.id },
                files: ['content.js']
            }, () => {
                sendScrapeMessage(tab.id, statusDiv);
            });
        } else if (response && response.data) {
            await sendDataToDjango(response.data, statusDiv);
        } else {
            statusDiv.textContent = "Error: Could not extract course data.";
            statusDiv.style.color = "red";
        }
    });
});

function sendScrapeMessage(tabId, statusDiv) {
    chrome.tabs.sendMessage(tabId, { action: "scrape_blackboard" }, async (response) => {
        if (response && response.data) {
            await sendDataToDjango(response.data, statusDiv);
        } else {
            statusDiv.textContent = "Error: Failed to scrape data.";
            statusDiv.style.color = "red";
        }
    });
}

async function sendDataToDjango(data, statusDiv) {
    statusDiv.textContent = "Syncing with Django backend...";
    try {
        const res = await fetch('http://127.0.0.1:8000/api/sync/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (res.ok) {
            statusDiv.textContent = "Success! Course synced & study plan generated.";
            statusDiv.style.color = "green";
        } else {
            const err = await res.json();
            statusDiv.textContent = `Server Error: ${err.error || 'Unknown'}`;
            statusDiv.style.color = "red";
        }
    } catch (e) {
        statusDiv.textContent = "Connection Error: Is Django running?";
        statusDiv.style.color = "red";
    }
}