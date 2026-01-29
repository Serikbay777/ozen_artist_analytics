# Analytics API Documentation

Comprehensive REST API endpoints for music catalog analytics, designed for frontend visualization.

## Base URL

```
http://localhost:8002
```

## Table of Contents

1. [Overview](#overview)
2. [Trends](#trends)
3. [Artists](#artists)
4. [Tracks](#tracks)
5. [Platforms](#platforms)
6. [Geography](#geography)
7. [Business Intelligence](#business-intelligence)

---

## Overview

### GET `/analytics/overview`

Get high-level overview statistics.

**Response:**
```json
{
  "total_revenue": 1234567.89,
  "total_streams": 500000000,
  "total_artists": 150,
  "total_tracks": 1200,
  "total_platforms": 45,
  "total_countries": 180,
  "avg_cpm": 2.469,
  "date_range": {
    "from": "2019-01-01T00:00:00",
    "to": "2024-12-31T00:00:00"
  },
  "currency": "EUR"
}
```

**Use cases:**
- Dashboard KPI cards
- Summary statistics
- Date range display

---

## Trends

### GET `/analytics/trends/yearly`

Get year-over-year trends with growth percentages.

**Response:**
```json
{
  "years": [
    {
      "year": 2023,
      "revenue": 456789.12,
      "streams": 180000000,
      "artists": 120,
      "revenue_growth": 25.5,
      "streams_growth": 30.2
    }
  ]
}
```

**Use cases:**
- Line charts showing yearly growth
- YoY comparison cards
- Growth rate indicators

---

### GET `/analytics/trends/monthly`

Get monthly trends, optionally filtered by year.

**Parameters:**
- `year` (optional): Filter by specific year

**Response:**
```json
{
  "months": [
    {
      "year": 2024,
      "month": 1,
      "revenue": 38000.50,
      "streams": 15000000,
      "cpm": 2.533
    }
  ]
}
```

**Use cases:**
- Monthly revenue line chart
- Seasonality analysis
- CPM trends over time

---

### GET `/analytics/trends/quarterly`

Get quarterly trends.

**Response:**
```json
{
  "quarters": [
    {
      "year": 2024,
      "quarter": 1,
      "revenue": 114000.00,
      "streams": 45000000
    }
  ]
}
```

**Use cases:**
- Quarterly performance charts
- Business reporting
- Trend analysis

---

## Artists

### GET `/analytics/artists/top`

Get top artists by revenue or streams.

**Parameters:**
- `limit` (default: 20, max: 100): Number of results
- `metric` (default: "revenue"): Sort by "revenue" or "streams"

**Response:**
```json
{
  "artists": [
    {
      "artist": "Artist Name",
      "revenue": 125000.50,
      "revenue_percentage": 10.5,
      "streams": 50000000,
      "tracks": 25,
      "platforms": 35,
      "countries": 120,
      "cpm": 2.500,
      "revenue_per_track": 5000.02
    }
  ]
}
```

**Use cases:**
- Top artists leaderboard
- Artist performance cards
- Revenue distribution charts

---

### GET `/analytics/artists/growth`

Get artist growth matrix (2023 vs 2024) with categorization.

**Parameters:**
- `limit` (default: 20, max: 100): Number of artists per category

**Categories:**
- `new_star`: New artists in 2024
- `rising_star`: High revenue with >50% growth
- `stable_star`: High revenue with positive growth
- `breakthrough`: Medium revenue with >100% growth
- `growing`: Positive growth
- `declining`: Negative growth

**Response:**
```json
{
  "categories": {
    "new_star": [
      {
        "artist": "New Artist",
        "revenue_2023": 0,
        "revenue_2024": 15000.00,
        "growth_percentage": 0,
        "absolute_growth": 15000.00,
        "streams_2023": 0,
        "streams_2024": 6000000
      }
    ],
    "rising_star": [...]
  },
  "summary": [
    {
      "category": "rising_star",
      "count": 15,
      "total_revenue_2024": 450000.00
    }
  ]
}
```

**Use cases:**
- Growth matrix visualization
- Artist segmentation
- Investment decision support
- A&R insights

---

### GET `/analytics/artists/diversity`

Get artist diversification metrics (platforms, countries, tracks).

**Parameters:**
- `limit` (default: 20, max: 100): Number of artists

**Response:**
```json
{
  "artists": [
    {
      "artist": "Artist Name",
      "revenue": 125000.50,
      "streams": 50000000,
      "tracks": 25,
      "platforms": 35,
      "countries": 120
    }
  ]
}
```

**Use cases:**
- Diversification analysis
- Risk assessment
- Market reach visualization
- Geographic expansion tracking

---

## Tracks

### GET `/analytics/tracks/top`

Get top tracks by revenue or streams.

**Parameters:**
- `limit` (default: 20, max: 100): Number of results
- `metric` (default: "revenue"): Sort by "revenue" or "streams"

**Response:**
```json
{
  "tracks": [
    {
      "artist": "Artist Name",
      "track": "Track Name",
      "revenue": 45000.00,
      "revenue_percentage": 3.8,
      "streams": 18000000,
      "streams_percentage": 3.6,
      "cpm": 2.500
    }
  ]
}
```

**Use cases:**
- Top tracks leaderboard
- Hit identification
- Revenue concentration analysis

---

### GET `/analytics/tracks/lifecycle`

Get track lifecycle analysis (longevity and profitability).

**Parameters:**
- `limit` (default: 15, max: 50): Number of tracks per category

**Response:**
```json
{
  "long_running": [
    {
      "artist": "Artist Name",
      "track": "Track Name",
      "active_months": 48,
      "revenue": 85000.00,
      "revenue_per_month": 1770.83,
      "streams": 34000000
    }
  ],
  "most_profitable_per_month": [
    {
      "artist": "Artist Name",
      "track": "Track Name",
      "active_months": 12,
      "revenue": 65000.00,
      "revenue_per_month": 5416.67,
      "streams": 26000000
    }
  ]
}
```

**Use cases:**
- Evergreen track identification
- Catalog value analysis
- Release strategy insights
- Monthly performance tracking

---

## Platforms

### GET `/analytics/platforms`

Get platform statistics.

**Parameters:**
- `limit` (default: 15, max: 50): Number of platforms

**Response:**
```json
{
  "platforms": [
    {
      "platform": "Spotify",
      "revenue": 450000.00,
      "revenue_percentage": 38.5,
      "streams": 180000000,
      "cpm": 2.500
    }
  ]
}
```

**Use cases:**
- Platform distribution pie chart
- Revenue by platform bar chart
- CPM comparison

---

### GET `/analytics/platforms/growth`

Get platform growth trends (2023 vs 2024).

**Response:**
```json
{
  "platforms": [
    {
      "platform": "Spotify",
      "revenue_2023": 380000.00,
      "revenue_2024": 450000.00,
      "growth_percentage": 18.4,
      "absolute_growth": 70000.00
    }
  ]
}
```

**Use cases:**
- Platform growth charts
- Trend identification
- Strategic platform focus

---

## Geography

### GET `/analytics/countries`

Get country statistics.

**Parameters:**
- `limit` (default: 15, max: 50): Number of countries
- `sort_by` (default: "revenue"): Sort by "revenue" or "cpm"

**Response:**
```json
{
  "countries": [
    {
      "country": "United States",
      "revenue": 285000.00,
      "revenue_percentage": 24.3,
      "streams": 110000000,
      "streams_percentage": 22.0,
      "cpm": 2.591
    }
  ]
}
```

**Use cases:**
- Geographic revenue map
- Market prioritization
- CPM by country analysis
- International expansion planning

---

### GET `/analytics/countries/platform-cpm`

Get CPM by country × platform combination.

**Parameters:**
- `limit` (default: 20, max: 50): Number of combinations

**Response:**
```json
{
  "combinations": [
    {
      "country": "Norway",
      "platform": "Spotify",
      "cpm": 4.250,
      "revenue": 12000.00,
      "streams": 2823529
    }
  ]
}
```

**Use cases:**
- CPM heatmap (country × platform)
- High-value market identification
- Strategic targeting
- Revenue optimization

---

## Business Intelligence

### GET `/analytics/concentration`

Get revenue concentration analysis.

**Response:**
```json
{
  "artists": {
    "top_10": {
      "revenue": 650000.00,
      "percentage": 55.5
    },
    "top_20": {
      "revenue": 850000.00,
      "percentage": 72.6
    },
    "top_50": {
      "revenue": 1050000.00,
      "percentage": 89.7
    },
    "total_artists": 150
  },
  "tracks": {
    "top_10": {
      "revenue": 450000.00,
      "percentage": 38.4
    },
    "top_50": {
      "revenue": 750000.00,
      "percentage": 64.1
    },
    "top_100": {
      "revenue": 950000.00,
      "percentage": 81.2
    },
    "total_tracks": 1200
  }
}
```

**Use cases:**
- Concentration risk analysis
- Portfolio diversification metrics
- Pareto charts (80/20 rule)
- Strategic planning

---

### GET `/analytics/labels`

Get label statistics.

**Parameters:**
- `limit` (default: 10, max: 50): Number of labels

**Response:**
```json
{
  "labels": [
    {
      "label": "Label Name",
      "revenue": 285000.00,
      "revenue_percentage": 24.3,
      "streams": 110000000,
      "artists": 25,
      "tracks": 180,
      "cpm": 2.591,
      "revenue_per_artist": 11400.00
    }
  ]
}
```

**Use cases:**
- Label performance comparison
- Artist roster efficiency
- Label strategy analysis

---

### GET `/analytics/sale-types`

Get sale type statistics (streaming, download, etc.).

**Response:**
```json
{
  "sale_types": [
    {
      "type": "Streaming",
      "revenue": 1150000.00,
      "revenue_percentage": 98.2,
      "streams": 480000000,
      "streams_percentage": 96.0,
      "cpm": 2.396
    }
  ]
}
```

**Use cases:**
- Revenue source breakdown
- Business model analysis
- Trend identification

---

## Frontend Integration Examples

### React Example

```typescript
// API client
const API_BASE = 'http://localhost:8002';

export const analyticsAPI = {
  getOverview: () => 
    fetch(`${API_BASE}/analytics/overview`).then(r => r.json()),
  
  getTopArtists: (limit = 20, metric = 'revenue') =>
    fetch(`${API_BASE}/analytics/artists/top?limit=${limit}&metric=${metric}`)
      .then(r => r.json()),
  
  getYearlyTrends: () =>
    fetch(`${API_BASE}/analytics/trends/yearly`).then(r => r.json()),
};

// Component usage
function Dashboard() {
  const [overview, setOverview] = useState(null);
  
  useEffect(() => {
    analyticsAPI.getOverview().then(setOverview);
  }, []);
  
  return (
    <div>
      <h1>Total Revenue: €{overview?.total_revenue.toLocaleString()}</h1>
      <p>Total Streams: {overview?.total_streams.toLocaleString()}</p>
    </div>
  );
}
```

### Chart.js Integration

```typescript
// Yearly trends line chart
const yearlyData = await analyticsAPI.getYearlyTrends();

const chartData = {
  labels: yearlyData.years.map(y => y.year),
  datasets: [{
    label: 'Revenue (EUR)',
    data: yearlyData.years.map(y => y.revenue),
    borderColor: 'rgb(75, 192, 192)',
    tension: 0.1
  }]
};
```

### Recharts Integration

```tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

function RevenueChart() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    analyticsAPI.getMonthlyTrends(2024).then(res => {
      setData(res.months);
    });
  }, []);
  
  return (
    <LineChart width={800} height={400} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="month" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="revenue" stroke="#8884d8" />
    </LineChart>
  );
}
```

---

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "detail": "Error message here"
}
```

---

## Performance Notes

- Data is loaded once on service initialization
- All queries run in-memory on pandas DataFrames
- Response times: typically < 100ms
- Recommended to implement caching on frontend for dashboard views

---

## Development

### Running the API

```bash
cd /Users/nuraliserikbay/Desktop/codes/music_analyzer_agent
python -m uvicorn app.main:app --reload --port 8002
```

### API Documentation

Interactive API docs available at:
- Swagger UI: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc

---

## Data Source

All analytics are based on Believe distribution data:
- Period: 2019 Q2 - 2024 Q4
- 8+ million rows
- 23 data fields
- Processed and aggregated for optimal performance

---

## Support

For questions or issues, check the logs or API documentation at `/docs`.

