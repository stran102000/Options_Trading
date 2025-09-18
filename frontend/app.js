// This JS assumes a backend API endpoint at /api/analyze (to be implemented in Python)
// The backend should accept POST requests with {tickers, expiration} and return analysis results

let lastQuery = null;
const DRAG_KEY = 'chartHeightRatioV1';

// Apply stored ratio if present
window.addEventListener('DOMContentLoaded', () => {
    const ratio = parseFloat(localStorage.getItem(DRAG_KEY));
    if (!isNaN(ratio)) {
        const chartSection = document.getElementById('chart-section');
        if (chartSection) {
            chartSection.style.flex = `0 0 ${Math.min(Math.max(ratio, 0.12), 0.75) * 100}%`;
            if (window.optionsChart) window.optionsChart.resize();
        }
    }
    initQuickActions();
});

document.getElementById('options-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const tickers = document.getElementById('tickers').value.trim();
    const expiration = document.getElementById('expiration').value.trim();
    lastQuery = { tickers, expiration };
    await runAnalysis(tickers, expiration);
});

document.getElementById('refresh-btn').addEventListener('click', async () => {
    if (lastQuery) {
        await runAnalysis(lastQuery.tickers, lastQuery.expiration);
    }
});

document.getElementById('clear-btn').addEventListener('click', () => {
    document.getElementById('results').innerHTML = '';
    if (window.optionsChart) { window.optionsChart.destroy(); }
});

document.getElementById('toggle-chart-btn').addEventListener('click', () => {
    const section = document.getElementById('chart-section');
    if (!section) return;
    const hidden = section.classList.toggle('collapsed');
    if (hidden) {
        section.style.display = 'none';
    } else {
        section.style.display = 'flex';
        if (window.optionsChart) { window.optionsChart.resize(); }
    }
});

// Fullscreen expand logic
document.getElementById('expand-chart-btn').addEventListener('click', () => {
    const section = document.getElementById('chart-section');
    if (!section) return;
    const isFullscreen = section.classList.toggle('fullscreen-overlay');
    if (isFullscreen) {
        // Prevent page scroll behind overlay
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = '';
    }
    if (window.optionsChart) { window.optionsChart.resize(); }
});

// Double click exit fullscreen
document.getElementById('chart-section').addEventListener('dblclick', (e) => {
    const section = e.currentTarget;
    if (section.classList.contains('fullscreen-overlay')) {
        section.classList.remove('fullscreen-overlay');
        document.body.style.overflow = '';
        if (window.optionsChart) { window.optionsChart.resize(); }
    }
});

// Drag resize logic
(function initDragResize(){
    const separator = document.getElementById('drag-separator');
    const chartSection = document.getElementById('chart-section');
    const mainContent = document.querySelector('.main-content');
    if (!separator || !chartSection || !mainContent) return;
    let isDragging = false;
    let startY = 0;
    let startHeight = 0; // in pixels

    const minPct = 0.12; // 12%
    const maxPct = 0.75; // 75%

    function onMouseDown(e){
        if (chartSection.classList.contains('collapsed') || chartSection.classList.contains('fullscreen-overlay')) return;
        isDragging = true;
        startY = e.clientY;
        startHeight = chartSection.getBoundingClientRect().height;
        document.body.style.cursor = 'row-resize';
        separator.classList.add('drag-active');
        e.preventDefault();
    }
    function onMouseMove(e){
        if (!isDragging) return;
        const delta = e.clientY - startY;
        const newHeight = startHeight + delta;
        const containerHeight = mainContent.getBoundingClientRect().height;
        let ratio = newHeight / containerHeight;
        ratio = Math.min(Math.max(ratio, minPct), maxPct);
        chartSection.style.flex = `0 0 ${ratio * 100}%`;
        if (window.optionsChart) window.optionsChart.resize();
    }
    function endDrag(){
        if (!isDragging) return;
        isDragging = false;
        document.body.style.cursor = '';
        separator.classList.remove('drag-active');
        // persist ratio
        const containerHeight = mainContent.getBoundingClientRect().height;
        const currentHeight = chartSection.getBoundingClientRect().height;
        const ratio = currentHeight / containerHeight;
        localStorage.setItem(DRAG_KEY, ratio.toString());
    }
    separator.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', endDrag);
    window.addEventListener('mouseleave', endDrag);
})();

function initQuickActions(){
    const container = document.getElementById('quick-actions');
    if (!container) return;
    const cards = container.querySelectorAll('.qa-card');
    cards.forEach(card => {
        card.addEventListener('click', (e) => {
            const tickers = e.currentTarget.getAttribute('data-tickers');
            const input = document.getElementById('tickers');
            if (input) {
                input.value = tickers;
            }
            // Highlight active
            cards.forEach(c => c.classList.remove('active'));
            e.currentTarget.classList.add('active');
            // Auto submit
            document.getElementById('options-form').dispatchEvent(new Event('submit'));
        });
    });
}

async function runAnalysis(tickers, expiration) {
    const resultsDiv = document.getElementById('results');
    if (!tickers) {
        resultsDiv.innerHTML = '<em>Please enter at least one ticker.</em>';
        return;
    }
    resultsDiv.innerHTML = '<div class="fade-in">Analyzing <span style="opacity:.7">(fetching chain & pricing)...</span></div>';
    document.getElementById('chart').style.display = 'none';
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tickers, expiration })
        });
        if (!response.ok) throw new Error('API error');
        const data = await response.json();
        renderResults(data);
    } catch (err) {
        resultsDiv.innerHTML = `<span style="color:#f87171">Error: ${err.message}</span>`;
    }
}

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
    let html = '<div class="table-wrapper"><table class="option-table"><thead><tr><th>Strike</th><th>Last</th><th>SMA</th><th>S</th><th>MC</th><th>VaR</th><th>Advice</th></tr></thead><tbody>';
    options.forEach(opt => {
        const adviceClass = opt.advice && opt.advice.startsWith('Good') ? 'advice-good' : 'advice-bad';
        html += `<tr>
            <td>${opt.strike}</td>
            <td>${opt.lastPrice}</td>
            <td>${opt.SMA ?? ''}</td>
            <td>${opt.Signal ? '✔️' : ''}</td>
            <td>${opt.mc_price ?? ''}</td>
            <td>${opt.var ?? ''}</td>
            <td class="${adviceClass}">${opt.advice ?? ''}</td>
        </tr>`;
    });
    html += '</tbody></table></div>';
    return html;
}

function plotChart(calls) {
    if (!calls || calls.length === 0) return;
    const chartCanvas = document.getElementById('chart');
    const ctx = chartCanvas.getContext('2d');
    chartCanvas.style.display = 'block';
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
                    borderColor: '#3b82f6',
                    borderWidth: 2,
                    pointRadius: 2,
                    backgroundColor: 'rgba(59,130,246,0.08)',
                    fill: true,
                    tension: 0.25
                },
                {
                    label: 'SMA',
                    data: smas,
                    borderColor: '#10b981',
                    borderWidth: 2,
                    pointRadius: 2,
                    backgroundColor: 'rgba(16,185,129,0.05)',
                    fill: true,
                    tension: 0.25
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true, labels: { color: '#cbd5e1', font: { size: 11 } } },
                tooltip: { mode: 'index', intersect: false }
            },
            scales: {
                x: { title: { display: true, text: 'Strike', color:'#94a3b8' }, ticks:{ color:'#64748b'} , grid:{ color:'rgba(148,163,184,0.1)'} },
                y: { title: { display: true, text: 'Price', color:'#94a3b8' }, ticks:{ color:'#64748b'} , grid:{ color:'rgba(148,163,184,0.1)'} }
            }
        }
    });
}
