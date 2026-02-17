const API_URL = 'http://127.0.0.1:5001/api';

async function fetchAPI(endpoint, params = {}) {
    const url = new URL(API_URL + endpoint);
    Object.keys(params).forEach(key => {
        if (params[key]) url.searchParams.append(key, params[key]);
    });
    
    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(res.statusText);
        return await res.json();
    } catch (e) {
        console.error(`API Error ${endpoint}:`, e);
        throw e;
    }
}

const api = {
    health: () => fetchAPI('/health'),
    getTrips: (params) => fetchAPI('/trips', params),
    getStats: (params) => fetchAPI('/stats', params),
    getHourly: (params) => fetchAPI('/hourly', params),
    getBoroughPatterns: (params) => fetchAPI('/patterns-borough', params),
    getDailyPatterns: (params) => fetchAPI('/patterns-daily', params),
    getBoroughs: () => fetchAPI('/boroughs'),
};