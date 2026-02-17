let currentTripPage = 1;
let tripCache = {};

document.addEventListener('DOMContentLoaded', init);

async function init() {
    console.log("App starting...");
    
    // This checks the health of the backend
    try {
        const health = await api.health();
        console.log("Health:", health);
    } catch (e) {
        console.error("Health Check Failed:", e);
        alert(`Backend Error: ${e.message}\nCheck console for details.`);
        return;
    }

    document.getElementById('start-date').value = '2019-01-01';
    document.getElementById('end-date').value = '2019-01-31';

    loadDashboard();
    loadDropdowns();
    
    document.getElementById('apply-filters').onclick = () => {
        currentTripPage = 1;
        tripCache = {};
        loadDashboard();
    };
    document.getElementById('start-date').onchange = () => { currentTripPage = 1; tripCache = {}; loadDashboard(); };
    document.getElementById('end-date').onchange = () => { currentTripPage = 1; tripCache = {}; loadDashboard(); };
    document.getElementById('borough-select').onchange = () => { currentTripPage = 1; tripCache = {}; loadDashboard(); };
    
    document.querySelectorAll('.nav-tab').forEach(t => t.onclick = (e) => switchView(e.target.dataset.view));
}

async function loadDropdowns() {
    const boroughs = await api.getBoroughs();
    const sel = document.getElementById('borough-select');
    boroughs.forEach(b => {
        const opt = document.createElement('option');
        opt.value = b;
        opt.textContent = b;
        sel.appendChild(opt);
    });
}

function getFilters() {
    return {
        start_date: document.getElementById('start-date').value,
        end_date: document.getElementById('end-date').value,
        borough: document.getElementById('borough-select').value
    };
}

async function loadDashboard() {
    setLoadingState(true);
    const filters = getFilters();
    
    try {
        const stats = await api.getStats(filters);
        updateStats(stats);
    } catch (e) { console.error(e); } finally { hideCardLoader('stats-metrics'); }
    
    Promise.allSettled([
        api.getHourly(filters).then(data => {
            ChartBuilder.bar('hourly-chart', 'Trips by Hour', data.map(h => h.hour + ':00'), data.map(h => h.count));
            hideCardLoader('hourly-chart-container');
        }),
        api.getBoroughPatterns(filters).then(data => {
            ChartBuilder.doughnut('borough-chart', data.map(b => b.borough), data.map(b => b.count));
            hideCardLoader('borough-chart-container');
        }),
        api.getDailyPatterns(filters).then(data => {
            const formattedDates = data.map(d => {
                const date = new Date(d.date);
                return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            });
            ChartBuilder.line('daily-trend-chart', 'All Trip Trend', formattedDates, data.map(d => d.count));
            hideCardLoader('daily-trend-container');
        })
    ]);

    loadTrips();
}

async function loadTrips() {
    showCardLoader('trips-table-container');
    const filters = getFilters();
    const cacheKey = `${currentTripPage}_${filters.start_date}_${filters.end_date}_${filters.borough}`;
    
    if (tripCache[cacheKey]) {
        console.log("Loading trips from cache...");
        renderTrips(tripCache[cacheKey].trips, tripCache[cacheKey].total);
        hideCardLoader('trips-table-container');
        return;
    }

    filters.page = currentTripPage;
    try {
        const response = await api.getTrips(filters);
        tripCache[cacheKey] = { trips: response.trips, total: response.total };
        renderTrips(response.trips, response.total);
    } catch (e) {
        console.error("Error loading trips:", e);
    } finally {
        hideCardLoader('trips-table-container');
    }
}

function renderTrips(trips, total) {
    const tbody = document.getElementById('trips-table-body');
    tbody.innerHTML = '';
    
    trips.forEach(t => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${t.trip_id}</td>
            <td>${new Date(t.pickup).toLocaleString()}</td>
            <td>${new Date(t.dropoff).toLocaleString()}</td>
            <td>${t.distance.toFixed(2)} mi</td>
            <td>$${t.amount.toFixed(2)}</td>
        `;
        tbody.appendChild(tr);
    });
    
    renderPagination(total);
}

function renderPagination(total) {
    const wrapper = document.getElementById('pagination-wrapper');
    wrapper.innerHTML = '';
    
    const totalPages = Math.ceil(total / 50);
    const maxVisible = 5;
    
    const prev = createPagBtn('<i class="fas fa-chevron-left"></i>', currentTripPage === 1, () => {
        currentTripPage--;
        loadTrips();
    });
    wrapper.appendChild(prev);

    const visiblePages = getVisiblePages(currentTripPage, totalPages);

    visiblePages.forEach(p => {
        if (p === '...') {
            wrapper.appendChild(createEllipsis());
        } else {
            const btn = createPagBtn(p, p === currentTripPage, () => {
                currentTripPage = p;
                loadTrips();
            });
            if (p === currentTripPage) btn.classList.add('active');
            wrapper.appendChild(btn);
        }
    });

    // Next Button
    const next = createPagBtn('<i class="fas fa-chevron-right"></i>', currentTripPage === totalPages, () => {
        currentTripPage++;
        loadTrips();
    });
    wrapper.appendChild(next);

    // Page Info
    const info = document.createElement('span');
    info.id = 'page-info';
    info.textContent = `Total: ${total.toLocaleString()} records`;
    wrapper.appendChild(info);
}

function createPagBtn(text, disabled, callback) {
    const btn = document.createElement('button');
    btn.className = 'pagination-btn';
    btn.innerHTML = text;
    btn.disabled = disabled;
    btn.onclick = callback;
    return btn;
}

function createEllipsis() {
    const span = document.createElement('span');
    span.className = 'pagination-ellipsis';
    span.textContent = '...';
    return span;
}

function setLoadingState(isLoading) {
    const action = isLoading ? 'add' : 'remove';
    document.querySelectorAll('.card-loader').forEach(l => l.classList[action]('active'));
}

function hideCardLoader(idOrGroup) {
    if (idOrGroup === 'stats-metrics') {
        ['trips-metric', 'distance-metric', 'revenue-metric', 'speed-metric'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.querySelector('.card-loader').classList.remove('active');
        });
    } else {
        const el = document.getElementById(idOrGroup);
        if (el) el.querySelector('.card-loader').classList.remove('active');
    }
}

function showCardLoader(id) {
    const el = document.getElementById(id);
    if (el) el.querySelector('.card-loader').classList.add('active');
}

function updateStats(stats) {
    if (!stats) return;
    document.getElementById('total-trips-count').textContent = stats.total_trips.toLocaleString();
    document.getElementById('total-revenue-display').textContent = '$' + stats.revenue.toLocaleString();
    document.getElementById('avg-efficiency').textContent = stats.avg_speed + ' mph';
    document.getElementById('total-distance').textContent = stats.avg_distance + ' mi (avg)';
}

function switchView(view) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById(view + '-view').classList.add('active');
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`[data-view="${view}"]`).classList.add('active');
}


function getVisiblePages(current, total) {
    const delta = 2; 
    const pages = [];

    for (let i = 1; i <= total; i++) {
        if (i === 1 || i === total || (i >= current - delta && i <= current + delta)) {
            pages.push(i);
        } 
        else if (pages.length > 0 && pages[pages.length - 1] !== '...') {
            pages.push('...');
        }
    }
    return pages;
}