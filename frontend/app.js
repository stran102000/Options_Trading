// This JS assumes a backend API endpoint at /api/analyze (to be implemented in Python)
// The backend should accept POST requests with {tickers, expiration} and return analysis results

document.getElementById('options-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const tickers = document.getElementById('tickers').value.trim();
    const expiration = document.getElementById('expiration').value.trim();
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<em>Analyzing, please wait...</em>';
    document.getElementById('chart').style.display = 'none';

    try {
        // Example API call (replace URL as needed)
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tickers, expiration })
        });
        if (!response.ok) throw new Error('API error');
        const data = await response.json();
        renderResults(data);
    } catch (err) {
        resultsDiv.innerHTML = `<span style="color:red">Error: ${err.message}</span>`;
    }
});

function renderResults(data) {
    const resultsDiv = document.getElementById('results');
    if (!data || !data.results || data.results.length === 0) {
        resultsDiv.innerHTML = '<em>No results found.</em>';
        return;
    }
    resultsDiv.innerHTML = '';
    data.results.forEach(tickerResult => {
        const div = document.createElement('div');
        div.className = 'ticker-result';
        div.innerHTML = `
            <h2>${tickerResult.ticker} (${tickerResult.expiration})</h2>
            <div><strong>Underlying Price:</strong> $${tickerResult.underlying_price}</div>
            <div style="margin-top:10px;">
                <strong>Calls:</strong>
                ${renderOptionTable(tickerResult.calls)}
            </div>
            <div style="margin-top:10px;">
                <strong>Puts:</strong>
                ${renderOptionTable(tickerResult.puts)}
            </div>
        `;
        resultsDiv.appendChild(div);
        // Optionally, plot chart for the first ticker
        if (tickerResult.calls && tickerResult.calls.length > 0) {
            plotChart(tickerResult.calls);
        }
    });
}

function renderOptionTable(options) {
    if (!options || options.length === 0) return '<em>No data</em>';
    let html = '<table class="option-table"><tr><th>Strike</th><th>Last Price</th><th>SMA</th><th>Signal</th><th>MC Price</th><th>VaR</th><th>Advice</th></tr>';
    options.forEach(opt => {
        html += `<tr>
            <td>${opt.strike}</td>
            <td>${opt.lastPrice}</td>
            <td>${opt.SMA ?? ''}</td>
            <td>${opt.Signal ? '✔️' : ''}</td>
            <td>${opt.mc_price ?? ''}</td>
            <td>${opt.var ?? ''}</td>
            <td>${opt.advice ?? ''}</td>
        </tr>`;
    });
    html += '</table>';
    return html;
}

function plotChart(calls) {
    if (!calls || calls.length === 0) return;
    const ctx = document.getElementById('chart').getContext('2d');
    document.getElementById('chart').style.display = 'block';
    const labels = calls.map((c, i) => c.strike);
    const lastPrices = calls.map(c => c.lastPrice);
    const smas = calls.map(c => c.SMA);
    if (window.optionsChart) window.optionsChart.destroy();
    window.optionsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [
                {
                    label: 'Last Price',
                    data: lastPrices,
                    borderColor: '#1976d2',
                    backgroundColor: 'rgba(25, 118, 210, 0.1)',
                    fill: false,
                    tension: 0.2
                },
                {
                    label: 'SMA',
                    data: smas,
                    borderColor: '#43a047',
                    backgroundColor: 'rgba(67, 160, 71, 0.1)',
                    fill: false,
                    tension: 0.2
                }
            ]
        },
        options: {
            responsive: false,
            plugins: {
                legend: { display: true }
            },
            scales: {
                x: { title: { display: true, text: 'Strike Price' } },
                y: { title: { display: true, text: 'Price' } }
            }
        }
    });
}
