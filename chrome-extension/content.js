const links = Array.from(document.getElementsByTagName('a')).map(a => a.href);
chrome.runtime.sendMessage({ message: 'process_urls', links: links });