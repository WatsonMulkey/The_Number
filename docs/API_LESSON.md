# API Lesson: Understanding REST APIs

## What is an API?

An **API** (Application Programming Interface) is a way for different software applications to talk to each other. Think of it like a menu at a restaurant:

- The **menu** (API documentation) tells you what you can order
- You make a **request** (order food)
- The kitchen prepares it
- You get a **response** (your food arrives)

## REST APIs

**REST** (Representational State Transfer) is a popular style of API that uses HTTP - the same protocol your web browser uses. REST APIs work with **resources** (like expenses, transactions, users) and use standard HTTP methods to interact with them.

---

## The Four Main HTTP Methods

Using our "The Number" budgeting API as an example:

### 1. GET - Read Data

**Purpose:** Retrieve information without changing anything

**Example: Get your daily spending limit**

```bash
# Request
GET http://localhost:8000/api/number

# Response (200 OK)
{
  "the_number": 38.50,
  "mode": "paycheck",
  "total_income": 4000.00,
  "total_expenses": 2500.00,
  "remaining_money": 1500.00,
  "days_remaining": 14,
  "today_spending": 12.00,
  "remaining_today": 26.50,
  "is_over_budget": false
}
```

**Example: Get all expenses**

```bash
# Request
GET http://localhost:8000/api/expenses

# Response (200 OK)
[
  {
    "id": 1,
    "name": "Rent",
    "amount": 1500.00,
    "is_fixed": true,
    "created_at": "2025-01-15T10:30:00",
    "updated_at": "2025-01-15T10:30:00"
  },
  {
    "id": 2,
    "name": "Groceries",
    "amount": 400.00,
    "is_fixed": false,
    "created_at": "2025-01-15T10:31:00",
    "updated_at": "2025-01-15T10:31:00"
  }
]
```

### 2. POST - Create New Data

**Purpose:** Send data to create a new resource

**Example: Add a new expense**

```bash
# Request
POST http://localhost:8000/api/expenses
Content-Type: application/json

{
  "name": "Internet",
  "amount": 60.00,
  "is_fixed": true
}

# Response (201 Created)
{
  "id": 3,
  "name": "Internet",
  "amount": 60.00,
  "is_fixed": true,
  "created_at": "2025-01-15T14:20:00",
  "updated_at": "2025-01-15T14:20:00"
}
```

**Example: Record a spending transaction**

```bash
# Request
POST http://localhost:8000/api/transactions
Content-Type: application/json

{
  "amount": 15.50,
  "description": "Coffee and snack",
  "category": "Food"
}

# Response (201 Created)
{
  "id": 42,
  "date": "2025-01-15T14:25:00",
  "amount": 15.50,
  "description": "Coffee and snack",
  "category": "Food",
  "created_at": "2025-01-15T14:25:00"
}
```

### 3. PUT/PATCH - Update Existing Data

**Purpose:** Modify existing resources

*Note: Our current API doesn't have update endpoints, but here's how they would work:*

```bash
# Request (if we had it)
PATCH http://localhost:8000/api/expenses/3
Content-Type: application/json

{
  "amount": 65.00
}

# Response (200 OK)
{
  "id": 3,
  "name": "Internet",
  "amount": 65.00,  # Updated!
  "is_fixed": true,
  "created_at": "2025-01-15T14:20:00",
  "updated_at": "2025-01-15T15:00:00"  # Timestamp changed
}
```

### 4. DELETE - Remove Data

**Purpose:** Delete a resource

**Example: Delete an expense**

```bash
# Request
DELETE http://localhost:8000/api/expenses/3

# Response (204 No Content)
# No body - just confirms deletion succeeded
```

---

## HTTP Status Codes

APIs use status codes to tell you what happened:

### Success Codes (2xx)

- **200 OK** - Request succeeded, here's your data
- **201 Created** - New resource created successfully
- **204 No Content** - Request succeeded, no data to return (common for DELETE)

### Client Error Codes (4xx)

- **400 Bad Request** - Your data is invalid
  ```json
  {
    "detail": "Paycheck mode requires monthly_income and days_until_paycheck"
  }
  ```

- **404 Not Found** - Resource doesn't exist
  ```json
  {
    "detail": "Expense with id 999 not found"
  }
  ```

### Server Error Codes (5xx)

- **500 Internal Server Error** - Something went wrong on the server
  ```json
  {
    "detail": "Database encryption key not configured"
  }
  ```

---

## Request Structure

Every API request has these parts:

### 1. URL (Endpoint)

The address of the resource:

```
http://localhost:8000/api/expenses/42
│                    │  │         │  │
└─ Protocol         │  │         │  └─ Resource ID
                    │  │         └──── Resource type
                    │  └────────────── API prefix
                    └───────────────── Server address
```

### 2. HTTP Method

What action to perform: GET, POST, DELETE, etc.

### 3. Headers

Metadata about the request:

```http
Content-Type: application/json
Accept: application/json
```

### 4. Body (for POST/PUT/PATCH)

The data you're sending:

```json
{
  "name": "Rent",
  "amount": 1500.00,
  "is_fixed": true
}
```

---

## Response Structure

API responses include:

### 1. Status Code

```http
HTTP/1.1 200 OK
```

### 2. Headers

```http
Content-Type: application/json
Content-Length: 245
```

### 3. Body

```json
{
  "id": 1,
  "name": "Rent",
  "amount": 1500.00,
  "is_fixed": true
}
```

---

## Hands-On Practice

Let's use our "The Number" API! Make sure the server is running:

```bash
cd /c/Users/watso/Dev
python -m uvicorn api.main:app --reload --port 8000
```

### Exercise 1: Check API Health

```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{"status": "healthy"}
```

### Exercise 2: Configure Budget (POST)

```bash
curl -X POST http://localhost:8000/api/budget/configure \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "paycheck",
    "monthly_income": 4000.00,
    "days_until_paycheck": 14
  }'
```

**Expected response:**
```json
{"message": "Budget configured successfully in paycheck mode"}
```

### Exercise 3: Add an Expense (POST)

```bash
curl -X POST http://localhost:8000/api/expenses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rent",
    "amount": 1500.00,
    "is_fixed": true
  }'
```

**Expected response:**
```json
{
  "id": 1,
  "name": "Rent",
  "amount": 1500.00,
  "is_fixed": true,
  "created_at": "2025-01-15T...",
  "updated_at": "2025-01-15T..."
}
```

### Exercise 4: Get "The Number" (GET)

```bash
curl http://localhost:8000/api/number
```

**Expected response:**
```json
{
  "the_number": 178.57,
  "mode": "paycheck",
  "total_income": 4000.00,
  "total_expenses": 1500.00,
  "remaining_money": 2500.00,
  "days_remaining": 14.0,
  "today_spending": 0.0,
  "remaining_today": 178.57,
  "is_over_budget": false
}
```

### Exercise 5: Record Spending (POST)

```bash
curl -X POST http://localhost:8000/api/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 25.50,
    "description": "Lunch",
    "category": "Food"
  }'
```

### Exercise 6: View Transactions (GET)

```bash
curl http://localhost:8000/api/transactions?limit=5
```

### Exercise 7: Delete an Expense (DELETE)

```bash
curl -X DELETE http://localhost:8000/api/expenses/1
```

**Expected response:** 204 No Content (empty body)

---

## Interactive API Documentation

FastAPI automatically generates interactive documentation!

Visit these URLs in your browser:

1. **Swagger UI**: http://localhost:8000/api/docs
   - Try out endpoints directly in your browser
   - See request/response examples
   - No command line needed!

2. **ReDoc**: http://localhost:8000/api/redoc
   - Beautiful, organized documentation
   - Great for reading and understanding

---

## CORS (Cross-Origin Resource Sharing)

When building web apps, your frontend (Vue.js on port 5173) needs to call your backend API (FastAPI on port 8000). This is called a "cross-origin request."

Browsers block these by default for security. Our API allows it with CORS middleware:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vue.js dev server
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, DELETE, etc.
    allow_headers=["*"],  # Content-Type, etc.
)
```

This tells the browser: "Yes, requests from port 5173 are allowed."

---

## Using APIs from JavaScript (Frontend)

Here's how the Vue.js frontend will call our API:

### With Axios (recommended)

```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
})

// GET request
const response = await api.get('/api/number')
console.log(response.data.the_number)  // 178.57

// POST request
const newExpense = await api.post('/api/expenses', {
  name: 'Internet',
  amount: 60.00,
  is_fixed: true
})

// DELETE request
await api.delete('/api/expenses/1')
```

### With Fetch (built-in)

```javascript
// GET request
const response = await fetch('http://localhost:8000/api/number')
const data = await response.json()
console.log(data.the_number)

// POST request
const response = await fetch('http://localhost:8000/api/expenses', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'Internet',
    amount: 60.00,
    is_fixed: true
  })
})
```

---

## API Design Best Practices

Our "The Number" API follows these principles:

### 1. RESTful Resource Naming

✅ **Good:** `/api/expenses` (plural nouns)
❌ **Bad:** `/api/getExpense` (verbs in URL)

### 2. HTTP Methods Match Actions

- `GET /api/expenses` - List all
- `GET /api/expenses/1` - Get one
- `POST /api/expenses` - Create new
- `DELETE /api/expenses/1` - Delete one

### 3. Meaningful Status Codes

- 200 OK - Successfully got data
- 201 Created - Successfully created resource
- 204 No Content - Successfully deleted
- 400 Bad Request - Invalid input
- 404 Not Found - Resource doesn't exist
- 500 Internal Server Error - Server problem

### 4. Consistent Response Format

All endpoints return JSON with predictable structures:

```json
{
  "id": 1,
  "name": "Rent",
  "amount": 1500.00,
  "is_fixed": true,
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:30:00"
}
```

### 5. Error Messages Are Helpful

```json
{
  "detail": "Paycheck mode requires monthly_income and days_until_paycheck"
}
```

Not just: `{"error": "Bad request"}`

---

## Common Patterns

### Pagination

For large lists, use query parameters:

```bash
GET /api/transactions?limit=20&offset=0
```

Our API supports this on the transactions endpoint.

### Filtering

```bash
GET /api/expenses?is_fixed=true
```

*Note: Our current API doesn't filter, but this is common.*

### Sorting

```bash
GET /api/transactions?sort=date&order=desc
```

---

## Summary

**Key Concepts:**

1. **APIs** let applications communicate over HTTP
2. **REST** uses standard HTTP methods (GET, POST, DELETE)
3. **Endpoints** are URLs representing resources
4. **Status codes** tell you what happened
5. **JSON** is the data format
6. **CORS** allows cross-origin requests

**Our API Endpoints:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/number` | Get daily spending limit |
| GET | `/api/expenses` | List all expenses |
| POST | `/api/expenses` | Add new expense |
| DELETE | `/api/expenses/{id}` | Remove expense |
| GET | `/api/transactions` | List transactions |
| POST | `/api/transactions` | Record spending |
| POST | `/api/budget/configure` | Set budget mode |

**Try It Yourself:**

1. Start the server: `python -m uvicorn api.main:app --reload --port 8000`
2. Visit http://localhost:8000/api/docs
3. Click "Try it out" on any endpoint
4. Fill in the parameters
5. Click "Execute"
6. See the response!

---

## Next Steps

- Read the [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- Explore the Swagger docs at http://localhost:8000/api/docs
- Build a simple frontend that calls these endpoints
- Learn about authentication (JWT tokens)
- Study API versioning (`/api/v1/`, `/api/v2/`)

Happy learning! 🚀
