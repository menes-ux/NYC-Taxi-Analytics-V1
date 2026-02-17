# NYC Taxi API Documentation

Base URL

```
http://127.0.0.1:5001/api

```


JSON Responses

---

## Health Check

### GET /health

Response
{
"status": "ok"
}

---

## Boroughs

### GET /boroughs

Returns list of available boroughs.

Response
[
"Manhattan",
"Queens",
"Brooklyn"
]

---

## Dashboard Statistics

### GET /stats

Params
/stats?start_date=2019-01-01&end_date=2019-01-10&borough=Manhattan

Response
{
"total_trips": 15234,
"revenue": 89234.50,
"avg_speed": 18.7,
"avg_distance": 3.2
}

---

## Hourly Trip Pattern

### GET /hourly

Response
[
{"hour": 0, "count": 120},
{"hour": 1, "count": 98}
]

---

## Borough Distribution

### GET /patterns-borough

Response
[
{"borough": "Manhattan", "count": 2300},
{"borough": "Queens", "count": 900}
]

---

## Daily Trend

### GET /patterns-daily

Response
[
{"date": "2019-01-01", "count": 3200},
{"date": "2019-01-02", "count": 3500}
]

---

## Trip Table

### GET /trips

Returns raw trip data with pagination.

Response
```json
{
  "trips": [
    {
      "trip_id": 0,
      "pickup": "2019-01-01T00:46:40",
      "dropoff": "2019-01-01T00:53:20",
      "distance": 1.5,
      "amount": 9.96
    }
  ],
  "total": 7667792,
  "page": 1,
  "per_page": 50
}
```

