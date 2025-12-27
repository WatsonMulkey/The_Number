# Vue.js Frontend Setup Guide

## Quick Start

### 1. Create Vue Project

```bash
# From the project root directory
npm create vue@latest frontend

# When prompted, select:
✅ TypeScript
✅ Vue Router
✅ Pinia (state management)
❌ JSX Support
❌ Vitest
❌ End-to-End Testing
❌ ESLint
❌ Prettier
```

### 2. Install Dependencies

```bash
cd frontend
npm install

# Install Vuetify 3 (Material Design)
npm install vuetify@^3.0.0

# Install Material Design Icons
npm install @mdi/font

# Install Axios (API client)
npm install axios

# Install date utilities
npm install date-fns
```

### 3. Configure Vuetify

Create `frontend/src/plugins/vuetify.ts`:

```typescript
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'

export default createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'theNumberTheme',
    themes: {
      theNumberTheme: {
        dark: false,
        colors: {
          primary: '#87986A', // Sage green from design
          secondary: '#625B71',
          background: 'rgba(135, 152, 106, 0.83)',
          surface: '#FFFFFF',
          'primary-container': '#EADDFF',
          'on-primary-container': '#4F378A',
          'secondary-container': '#E8DEF8',
          'on-secondary-container': '#4A4459',
          'surface-variant': '#E7E0EC',
          'on-surface-variant': '#49454F',
        },
      },
    },
  },
})
```

### 4. Project Structure

```
frontend/
├── src/
│   ├── assets/              # Static assets
│   ├── components/          # Reusable components
│   │   ├── NavigationRail.vue
│   │   ├── NumberDisplay.vue
│   │   ├── StreakCounter.vue
│   │   └── ExpenseCard.vue
│   ├── views/               # Page components
│   │   ├── Dashboard.vue    # Main "Your Number is..." page
│   │   ├── Expenses.vue     # Manage expenses
│   │   ├── Transactions.vue # View spending history
│   │   └── Settings.vue     # Budget configuration
│   ├── stores/              # Pinia stores
│   │   ├── budget.ts        # Budget state
│   │   └── auth.ts          # Authentication (future)
│   ├── services/            # API client
│   │   └── api.ts           # Axios instance + endpoints
│   ├── router/              # Vue Router
│   │   └── index.ts
│   ├── plugins/             # Plugins
│   │   └── vuetify.ts
│   ├── App.vue
│   └── main.ts
├── public/                  # Public assets
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

### 5. API Client Setup

Create `frontend/src/services/api.ts`:

```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// API endpoints
export const budgetApi = {
  // Get "The Number"
  getNumber: () => api.get('/api/number'),

  // Configure budget
  configureBudget: (config: any) => api.post('/api/budget/configure', config),
  getBudgetConfig: () => api.get('/api/budget/config'),

  // Expenses
  getExpenses: () => api.get('/api/expenses'),
  createExpense: (expense: any) => api.post('/api/expenses', expense),
  deleteExpense: (id: number) => api.delete(`/api/expenses/${id}`),
  importExpenses: (file: File, replace: boolean) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/api/expenses/import?replace=${replace}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  exportExpenses: (format: 'csv' | 'excel') =>
    api.get(`/api/expenses/export/${format}`, { responseType: 'blob' }),

  // Transactions
  getTransactions: (limit?: number) => api.get('/api/transactions', { params: { limit } }),
  createTransaction: (transaction: any) => api.post('/api/transactions', transaction),
  deleteTransaction: (id: number) => api.delete(`/api/transactions/${id}`),
}

export default api
```

### 6. Run Development Servers

```bash
# Terminal 1: FastAPI Backend
cd /c/Users/watso/Dev
python -m uvicorn api.main:app --reload --port 8000

# Terminal 2: Vue Frontend
cd frontend
npm run dev
```

### 7. Access the App

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

## Next Steps

1. Create the Dashboard view with NumberDisplay component
2. Implement NavigationRail for navigation
3. Build Expenses management view
4. Add Transactions view
5. Create Settings view for budget configuration
6. Style with Material Design 3 theme

## Design Reference

Your design specifications:
- **Background**: `rgba(135, 152, 106, 0.83)` - Sage green
- **Typography**:
  - Headlines: Libre Baskerville
  - UI: Roboto
- **Main Number**: 150px font, white with shadow
- **Navigation Rail**: 96px wide, Material Design 3
- **Components**: FAB, avatar, nav items, cards

## Deployment

Once complete:
- **Frontend**: Deploy to Vercel or Netlify
- **Backend**: Deploy to Railway or Render
- **Database**: Migrate from SQLite to PostgreSQL for multi-user support
