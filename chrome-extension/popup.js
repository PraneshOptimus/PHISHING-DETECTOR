document.addEventListener('DOMContentLoaded', () => {
  const urlSpan = document.getElementById('url');
  const statusSpan = document.getElementById('status');
  const linkList = document.getElementById('link-list');
  const reportBtn = document.getElementById('report-btn');

  chrome.runtime.sendMessage({ message: 'get_results' }, (response) => {
    if (response) {
      urlSpan.textContent = response.currentUrl;
      statusSpan.textContent = response.currentStatus || 'Checking...';
      if (response.suspiciousLinks && response.suspiciousLinks.length > 0) {
        response.suspiciousLinks.forEach(link => {
          const li = document.createElement('li');
          li.textContent = link;
          linkList.appendChild(li);
        });
      } else {
        linkList.innerHTML = '<li>No suspicious links found.</li>';
      }
    }
  });

  reportBtn.addEventListener('click', () => {
    chrome.runtime.sendMessage({ message: 'report_false_positive', url: urlSpan.textContent }, (response) => {
      alert(response.message);
    });
  });
});