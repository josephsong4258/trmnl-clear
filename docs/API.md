# API Reference

Complete API documentation for the TRMNL James Clear Quotes plugin.

## Base URL

```
https://your-server.com
```

## Endpoints

### Plugin Endpoint

The main endpoint that TRMNL calls to generate screen content.

```http
POST /plugin
```

#### Request

**Headers:**
```
Authorization: Bearer {user_access_token}
Content-Type: application/x-www-form-urlencoded
```

**Body Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_uuid` | string | Yes | Unique identifier for the user's plugin connection |
| `trmnl` | string (JSON) | No | Metadata about the device and user |

**Example Request:**
```bash
curl -X POST https://your-server.com/plugin \
  -H "Authorization: Bearer xxx" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "user_uuid=abc123&trmnl=%7B%22device%22%3A%7B%22width%22%3A800%2C%22height%22%3A480%7D%7D"
```

**TRMNL Metadata Structure:**
```json
{
  "user": {
    "name": "John Doe",
    "first_name": "John",
    "last_name": "Doe",
    "locale": "en",
    "time_zone": "America/New_York",
    "time_zone_iana": "America/New_York",
    "utc_offset": -14400
  },
  "device": {
    "friendly_id": "DEVICE123",
    "percent_charged": 85.5,
    "wifi_strength": 75,
    "height": 480,
    "width": 800
  },
  "system": {
    "timestamp_utc": 1704067200
  },
  "plugin_settings": {
    "instance_name": "Daily Quotes"
  }
}
```

#### Response

**Success Response (200 OK):**

```json
{
  "markup": "<div class=\"view view--full\">...</div>",
  "markup_half_vertical": "<div class=\"view view--half_vertical\">...</div>",
  "markup_half_horizontal": "<div class=\"view view--half_horizontal\">...</div>",
  "markup_quadrant": "<div class=\"view view--quadrant\">...</div>",
  "shared": ""
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `markup` | string (HTML) | Full screen layout markup |
| `markup_half_vertical` | string (HTML) | Half vertical layout markup |
| `markup_half_horizontal` | string (HTML) | Half horizontal layout markup |
| `markup_quadrant` | string (HTML) | Quadrant layout markup |
| `shared` | string | Shared data between layouts (optional) |

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Error message describing what went wrong"
}
```

---

### Newsletter Webhook

Endpoint for receiving new quotes from newsletter automation.

```http
POST /webhook/newsletter
```

#### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "quotes": [
    "First quote from James Clear",
    "Second quote from James Clear",
    "Third quote from James Clear"
  ]
}
```

**Example Request:**
```bash
curl -X POST https://your-server.com/webhook/newsletter \
  -H "Content-Type: application/json" \
  -d '{
    "quotes": [
      "Your outcomes are a lagging measure of your habits.",
      "Every action you take is a vote for the person you wish to become.",
      "You do not rise to the level of your goals. You fall to the level of your systems."
    ]
  }'
```

#### Response

**Success Response (200 OK):**
```json
{
  "status": "success",
  "added": 3
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Error message"
}
```

---

### Stats Endpoint

Get statistics about the quote database.

```http
GET /stats
```

#### Response

```json
{
  "total_quotes": 547,
  "by_length": {
    "short": 156,
    "medium": 234,
    "long": 128,
    "very_long": 29
  },
  "categories": [
    "life",
    "atomic-habits",
    "deep",
    "inspiring",
    "motivational",
    "success",
    "3-2-1-newsletter"
  ]
}
```

**Example Request:**
```bash
curl https://your-server.com/stats
```

---

### Health Check

Check if the server is running properly.

```http
GET /health
```

#### Response

```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "quotes_loaded": 547
}
```

**Example Request:**
```bash
curl https://your-server.com/health
```

---

## Markup Layouts

The plugin generates HTML markup using TRMNL's built-in CSS classes.

### Available CSS Classes

**Container Classes:**
- `.view` - Main container
- `.layout` - Layout wrapper
- `.columns`, `.column` - Column structure
- `.markdown` - Markdown container

**Typography:**
- `.title` - Large title text
- `.subtitle` - Medium subtitle text
- `.label` - Small label text
- `.content` - Body content
- `.content-element` - Content wrapper

**Spacing:**
- `.gap--small` - Small gap
- `.gap--medium` - Medium gap
- `.gap--large` - Large gap
- `.mt-2`, `.mt-4` - Margin top

**Modifiers:**
- `.label--underline` - Underlined label
- `.content--center` - Centered content

### Layout Examples

**Full Screen:**
```html
<div class="view view--full">
  <div class="layout">
    <div class="columns">
      <div class="column">
        <div class="markdown gap--large">
          <span class="title">Daily Wisdom</span>
          <div class="content-element content content--center">
            "Quote text here"
          </div>
          <span class="label label--underline mt-4">— James Clear</span>
        </div>
      </div>
    </div>
  </div>
</div>
```

**Half Vertical:**
```html
<div class="view view--half_vertical">
  <div class="layout">
    <div class="markdown gap--medium">
      <span class="subtitle">Daily Wisdom</span>
      <div class="content-element content">
        "Quote text here"
      </div>
      <span class="label mt-2">— James Clear</span>
    </div>
  </div>
</div>
```

**Quadrant:**
```html
<div class="view view--quadrant">
  <div class="markdown gap--small">
    <span class="label">Wisdom</span>
    <div class="content-element">
      "Quote text here"
    </div>
  </div>
</div>
```

---

## Quote Selection Logic

The plugin uses smart selection based on layout:

### Length Categories

| Category | Character Range | Use Case |
|----------|----------------|----------|
| Short | < 100 | Quadrant, side panels |
| Medium | 100-250 | Half layouts, smaller displays |
| Long | 250-400 | Full screen |
| Very Long | > 400 | Full screen only (truncated if needed) |

### Selection Algorithm

1. **Layout Detection**: Determine which layout is being requested
2. **Length Matching**: Select quotes that fit the layout constraints
3. **Date-Based Seeding**: Use current date to ensure same quote all day
4. **Intelligent Truncation**: If quote is too long, truncate at sentence boundary

### Truncation Rules

- Prefers breaking at sentence boundaries (`. ` `! ` `? `)
- Requires at least 60% of desired length before breaking
- Falls back to word boundaries with ellipsis (`...`)
- Never breaks mid-sentence

---

## Rate Limiting

Currently, there are no rate limits enforced. However, be respectful:

- TRMNL requests occur at user-defined intervals (typically 30-60 minutes)
- Webhook posts should be limited to actual newsletter sends (weekly)
- Stats/health checks can be polled frequently

---

## Error Handling

All endpoints return appropriate HTTP status codes:

| Status Code | Meaning |
|-------------|---------|
| 200 | Success |
| 400 | Bad Request (invalid parameters) |
| 401 | Unauthorized (invalid token) |
| 404 | Not Found |
| 500 | Internal Server Error |

Error responses include a descriptive message:

```json
{
  "error": "Description of what went wrong"
}
```

---

## Integration Examples

### Python

```python
import requests

response = requests.post(
    'https://your-server.com/plugin',
    headers={
        'Authorization': 'Bearer YOUR_TOKEN',
        'Content-Type': 'application/x-www-form-urlencoded'
    },
    data={'user_uuid': 'test'}
)

markup = response.json()
print(markup['markup'])
```

### JavaScript/Node.js

```javascript
const response = await fetch('https://your-server.com/plugin', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/x-www-form-urlencoded'
  },
  body: 'user_uuid=test'
});

const data = await response.json();
console.log(data.markup);
```

### cURL

```bash
curl -X POST https://your-server.com/plugin \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "user_uuid=test"
```

---

## Changelog

### v1.0.0 (Initial Release)
- Plugin endpoint with all 4 layouts
- Newsletter webhook integration
- Stats and health check endpoints
- Smart quote selection based on length
- Date-based daily rotation
