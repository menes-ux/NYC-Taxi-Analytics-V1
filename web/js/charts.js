const COLORS = {
    primary: '#ffd60a',
    secondary: '#ff6b35',
    tertiary: '#00d4ff',
    text: '#94a3b8',
    grid: '#2a3650'
};

const commonOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
        legend: { labels: { color: COLORS.text } }
    },
    scales: {
        x: { grid: { color: COLORS.grid }, ticks: { color: COLORS.text } },
        y: { grid: { color: COLORS.grid }, ticks: { color: COLORS.text } }
    }
};

let charts = {};

function createChart(id, type, labels, datasets) {
    const ctx = document.getElementById(id);
    if (!ctx) return;
    
    if (charts[id]) charts[id].destroy();
    
    charts[id] = new Chart(ctx, {
        type: type,
        data: { labels, datasets },
        options: commonOptions
    });
}

const ChartBuilder = {
    bar: (id, label, labels, data, color = COLORS.primary) => {
        createChart(id, 'bar', labels, [{
            label, data, backgroundColor: color, borderRadius: 4
        }]);
    },
    
    line: (id, label, labels, data, color = COLORS.secondary) => {
        createChart(id, 'line', labels, [{
            label, data, borderColor: color, tension: 0.4, fill: false
        }]);
    },
    
    doughnut: (id, labels, data) => {
        createChart(id, 'doughnut', labels, [{
            data,
            backgroundColor: [COLORS.primary, COLORS.secondary, COLORS.tertiary, '#a855f7', '#10b981'],
            borderColor: '#111827'
        }]);
    }
};