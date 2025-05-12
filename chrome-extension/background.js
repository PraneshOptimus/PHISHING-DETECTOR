let currentUrl = '';
let currentStatus = '';
let suspiciousLinks = [];

const apiUrl = 'https://phishing-detector-h6c1.onrender.com/predict'; // Updated URL

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.message === 'process_urls') {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            currentUrl = tabs[0].url;
            const pageUrls = request.links || [];

            fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: currentUrl })
            })
            .then(response => response.json())
            .then(data => {
                currentStatus = data.result === 'phishing'
                    ? `⚠️ Phishing Detected (${Math.round(data.confidence * 100)}%)`
                    : `Safe (${Math.round(data.confidence * 100)}%)`;

                const linkPromises = pageUrls.slice(0, 10).map(url =>
                    fetch(apiUrl, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ url })
                    })
                    .then(res => res.json())
                    .then(res => res.result === 'phishing' ? url : null)
                    .catch(() => null)
                );

                Promise.all(linkPromises).then(results => {
                    suspiciousLinks = results.filter(url => url);
                    chrome.action.setBadgeText({ text: suspiciousLinks.length.toString() });
                    chrome.action.setBadgeBackgroundColor({ color: '#FF0000' });
                });
            })
            .catch(err => {
                currentStatus = 'Error checking URL';
                console.error(err);
            });
        });
    } else if (request.message === 'get_results') {
        sendResponse({ currentUrl, currentStatus, suspiciousLinks });
    } else if (request.message === 'report_false_positive') {
        fetch(apiUrl.replace('/predict', '/report'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: request.url, status: currentStatus })
        })
        .then(res => res.json())
        .then(data => sendResponse({ message: data.message }))
        .catch(() => sendResponse({ message: 'Error reporting' }));
        return true;
    }
});
