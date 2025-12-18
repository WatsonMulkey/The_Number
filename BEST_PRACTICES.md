# Comprehensive Development Best Practices Guide

**Document Version:** 1.0
**Last Updated:** December 18, 2025
**Projects Covered:** resume-tailor, The Number web app, API development, Frontend architecture
**Author:** Research Orchestrator / Watson Mulkey development sessions

---

## Executive Summary

This document consolidates lessons learned, architectural decisions, and best practices from multiple development sessions involving:
- **resume-tailor**: AI-powered CLI tool for resume/cover letter generation
- **The Number**: Vue 3 + Vuetify budget tracking web application
- **FastAPI backend**: RESTful API with encrypted database
- **Frontend architecture**: Vue 3, Pinia, TypeScript patterns

These insights form an institutional knowledge base for future development work.

---

## Table of Contents

1. [AI Integration Best Practices](#1-ai-integration-best-practices)
2. [API Design Principles](#2-api-design-principles)
3. [Frontend Architecture Patterns](#3-frontend-architecture-patterns)
4. [Testing Strategy](#4-testing-strategy)
5. [Security Practices](#5-security-practices)
6. [State Management](#6-state-management)
7. [Error Handling Patterns](#7-error-handling-patterns)
8. [Performance Optimization](#8-performance-optimization)
9. [Development Workflow](#9-development-workflow)
10. [Common Pitfalls and Solutions](#10-common-pitfalls-and-solutions)

---

## 1. AI Integration Best Practices

### 1.1 Zero-Hallucination Architecture

**Pattern: Factual Data Injection**

The resume-tailor project implements a critical pattern for preventing AI hallucinations:

```python
# CRITICAL: Post-processing injection to guarantee factual data
def inject_correct_contact_info(content: str, job_title: str) -> str:
    """
    Removes AI-generated contact block and injects correct one.
    Runs AFTER AI generation to guarantee factual contact info.
    """
    # Remove any AI-generated contact info
    # Inject verified contact information
    correct_header = f"""# {CONTACT_INFO['name']}
{CONTACT_INFO['email']} | {CONTACT_INFO['phone']} | {CONTACT_INFO['linkedin']}
"""
    return correct_header + content_without_header
```

**Key Principles:**
1. **Never trust AI for factual data** - Always inject verified facts post-generation
2. **Validate generated content** - Check for placeholder patterns, fake data markers
3. **Hardcode critical info** - Contact details, dates, metrics should come from verified sources
4. **Context-aware personal anecdotes** - Only use personal stories when domain-appropriate

### 1.2 Anti-Hallucination Validation

```python
def validate_generated_content(content: str, job_info: Dict) -> List[str]:
    """Post-generation validation to catch hallucinations."""
    warnings = []

    hallucination_patterns = {
        '555-555': 'Fake phone number pattern detected',
        '@email.com': 'Generic email address detected',
        'Lorem ipsum': 'Placeholder text detected',
        '[Your ': 'Template placeholder detected',
    }

    # Check for bracket placeholders
    bracket_placeholders = re.findall(r'\[[A-Z][^\]]{3,50}\]', content)
    if bracket_placeholders:
        warnings.append(f"CRITICAL: Template placeholder detected")
```

### 1.3 Retry Logic with Exponential Backoff

**Proven Pattern from resume-tailor:**

```python
def call_claude_with_retry(
    client: anthropic.Anthropic,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    **api_kwargs
) -> anthropic.types.Message:
    """Call Claude API with exponential backoff retry logic."""
    delay = initial_delay

    for attempt in range(max_retries + 1):
        try:
            return client.messages.create(**api_kwargs)
        except anthropic.RateLimitError as e:
            wait_time = delay * (2 ** attempt)
            print(f"Rate limit hit. Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
        except anthropic.AuthenticationError:
            raise  # Don't retry auth errors
```

### 1.4 Prompt Engineering Patterns

**Effective Prompt Structure:**
1. Clear role definition
2. Explicit contact/factual info with "USE EXACTLY AS PROVIDED"
3. Structured context sections (achievements, skills, job history)
4. CRITICAL rules in capitals
5. Specific output format requirements
6. Anti-hallucination instructions

---

## 2. API Design Principles

### 2.1 RESTful Resource Design

**Learned from The Number API implementation:**

| Method | Endpoint | Purpose | Status Code |
|--------|----------|---------|-------------|
| GET | `/api/expenses` | List all | 200 OK |
| GET | `/api/expenses/{id}` | Get one | 200 OK / 404 Not Found |
| POST | `/api/expenses` | Create new | 201 Created |
| DELETE | `/api/expenses/{id}` | Remove | 204 No Content |
| PATCH | `/api/expenses/{id}` | Update | 200 OK |

**Best Practices:**
- Use plural nouns for resources (`/expenses` not `/expense`)
- Never use verbs in URLs (`/api/expenses` not `/api/getExpense`)
- Consistent response format with predictable structures
- Helpful error messages with context

### 2.2 CORS Configuration

**Critical Issue Discovered:** Frontend running on different port than expected.

```python
# ALWAYS include all development ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5176",  # Often missed!
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5176",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production Checklist:**
- Configure CORS from environment variables
- Whitelist only production domains
- Consider removing wildcard methods/headers

### 2.3 API Documentation

**FastAPI provides automatic documentation - leverage it:**
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

---

## 3. Frontend Architecture Patterns

### 3.1 Vue 3 Composition API Structure

**Recommended Project Structure:**

```
frontend/
├── src/
│   ├── components/          # Reusable components
│   │   ├── NavigationRail.vue
│   │   ├── NumberDisplay.vue
│   │   └── Onboarding.vue
│   ├── views/               # Page components
│   │   ├── Dashboard.vue
│   │   ├── Expenses.vue
│   │   └── Settings.vue
│   ├── stores/              # Pinia stores
│   │   └── budget.ts
│   ├── services/            # API client
│   │   └── api.ts
│   ├── router/
│   │   └── index.ts
│   └── plugins/
│       └── vuetify.ts
```

### 3.2 API Client Pattern

**Centralized API Configuration:**

```typescript
import axios from 'axios'

const api = axios.create({
  // CRITICAL: Use environment variable, not hardcoded URL
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const budgetApi = {
  getNumber: () => api.get('/api/number'),
  getExpenses: () => api.get('/api/expenses'),
  createExpense: (expense: any) => api.post('/api/expenses', expense),
  deleteExpense: (id: number) => api.delete(`/api/expenses/${id}`),
}
```

### 3.3 Router Configuration

**Critical Bug Found:** Using wrong history base path.

```typescript
// WRONG - Causes navigation failure in production
const router = createRouter({
  history: createWebHistory(import.meta.url),  // INCORRECT!
  routes: [...]
})

// CORRECT
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),  // CORRECT
  routes: [...]
})
```

### 3.4 Props with Defaults

**Always use withDefaults for optional props:**

```typescript
// Without defaults - potential runtime errors
const props = defineProps<{
  theNumber: number
  todaySpending?: number  // Could be undefined!
}>()

// With defaults - safer
const props = withDefaults(defineProps<{
  theNumber: number
  todaySpending?: number
}>(), {
  todaySpending: 0
})
```

---

## 4. Testing Strategy

### 4.1 Testing Pyramid

**Recommended Coverage by Type:**

| Test Type | Coverage Target | Tools |
|-----------|----------------|-------|
| Unit Tests | 90%+ | Vitest, Vue Test Utils |
| Integration Tests | Critical paths | Vitest |
| E2E Tests | Happy paths | Playwright |

### 4.2 Critical Testing Gaps Identified

From The Number QA review, these areas commonly lack tests:

1. **Onboarding/Wizard flows** - Multi-step navigation, validation, data persistence
2. **Error recovery** - Network failures, API errors, timeout handling
3. **Edge cases** - Negative numbers, zero values, very large numbers
4. **Accessibility** - Keyboard navigation, screen reader, focus management
5. **Race conditions** - Concurrent operations, stale data

### 4.3 Test Quality Markers

**Meaningful Tests Should:**
- Verify user-facing behavior, not implementation details
- Test unhappy paths, not just happy paths
- Use proper async handling (`flushPromises()`)
- Mock external dependencies (API calls)
- Include edge case coverage

**Example: Proper Test Structure**

```typescript
describe('Onboarding Component', () => {
  let pinia: any

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    vi.clearAllMocks()
  })

  it('should reject negative income', async () => {
    const wrapper = mount(Onboarding, {
      global: { plugins: [pinia] },
    })
    wrapper.vm.currentStep = 2
    wrapper.vm.budgetMode = 'paycheck'
    wrapper.vm.monthlyIncome = -100

    expect(wrapper.vm.canProceed).toBe(false)
  })
})
```

### 4.4 Test Naming Convention

- **File names**: `ComponentName.spec.ts`
- **Describe blocks**: Feature or component name
- **Test names**: Start with "should" + describe behavior
- **Good**: `should disable button when form is invalid`
- **Bad**: `test button disabled`

---

## 5. Security Practices

### 5.1 Critical Security Issues Found

| Issue | Severity | Solution |
|-------|----------|----------|
| XSS in error handler | CRITICAL | Use `textContent` not `innerHTML` |
| Hardcoded API URL | CRITICAL | Use environment variables |
| No authentication | CRITICAL | Implement auth before production |
| Arbitrary file upload | CRITICAL | Validate file type, size, content |
| No rate limiting | MAJOR | Implement API rate limits |
| Verbose error messages | MEDIUM | Sanitize for production |

### 5.2 Input Sanitization

**All user inputs should be sanitized:**

```typescript
// Client-side validation (defense in depth)
const sanitizedInput = input
  .replace(/<script>/gi, '')
  .replace(/javascript:/gi, '')
  .trim()
```

**Plus server-side Pydantic validation:**

```python
class ExpenseCreate(BaseModel):
    name: str = Field(..., max_length=255, min_length=1)
    amount: float = Field(..., gt=0, le=999999.99)
    is_fixed: bool = True
```

### 5.3 Environment Configuration

**Never commit secrets to version control:**

```bash
# .env (never committed)
ANTHROPIC_API_KEY=sk-ant-xxxxx
VITE_API_URL=http://localhost:8000
DATABASE_ENCRYPTION_KEY=xxxxx

# .env.example (committed)
ANTHROPIC_API_KEY=your-key-here
VITE_API_URL=http://localhost:8000
```

---

## 6. State Management

### 6.1 Pinia Store Pattern

**Effective Store Structure:**

```typescript
export const useBudgetStore = defineStore('budget', () => {
  // State
  const budgetNumber = ref<BudgetNumber | null>(null)
  const expenses = ref<Expense[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const totalExpenses = computed(() =>
    expenses.value.reduce((sum, e) => sum + e.amount, 0)
  )

  // Actions
  async function fetchNumber() {
    loading.value = true
    error.value = null
    try {
      const response = await budgetApi.getNumber()
      budgetNumber.value = response.data
    } catch (e) {
      error.value = extractErrorMessage(e)
    } finally {
      loading.value = false
    }
  }

  return { budgetNumber, expenses, loading, error, totalExpenses, fetchNumber }
})
```

### 6.2 Race Condition Prevention

**Critical Issue Found:** Shared loading state causes race conditions.

```typescript
// WRONG - Single shared loading state
async function addExpense(expense) {
  loading.value = true  // Global loading
  await budgetApi.createExpense(expense)
  await fetchExpenses()  // Also sets loading!
  await fetchNumber()    // Also sets loading!
  loading.value = false  // Race condition!
}

// BETTER - Per-operation loading states
const loadingStates = ref({
  expenses: false,
  number: false,
  saving: false,
})
```

### 6.3 Optimistic Updates with Rollback

```typescript
async function deleteExpense(id: number) {
  const original = [...expenses.value]

  // Optimistic update
  expenses.value = expenses.value.filter(e => e.id !== id)

  try {
    await budgetApi.deleteExpense(id)
  } catch (e) {
    // Rollback on failure
    expenses.value = original
    throw e
  }
}
```

---

## 7. Error Handling Patterns

### 7.1 Consistent Error Extraction

```typescript
function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    return error.response?.data?.detail ||
           error.response?.data?.message ||
           error.message
  }
  if (error instanceof Error) {
    return error.message
  }
  return 'An unexpected error occurred'
}
```

### 7.2 Error Display Patterns

**Use consistent UI patterns:**
- **Snackbars**: For action results (success/failure)
- **Inline errors**: For form validation
- **Error states**: For page-level failures

```vue
<v-snackbar v-model="showError" color="error">
  {{ errorMessage }}
</v-snackbar>
```

### 7.3 Global Error Boundary

```typescript
// main.ts
app.config.errorHandler = (err, vm, info) => {
  console.error('Global error:', err, info)
  // Log to error tracking service (Sentry, etc.)
}
```

---

## 8. Performance Optimization

### 8.1 Bundle Size Optimization

**Issues Found:**
- Vuetify not tree-shaken (imports all components)
- @mdi/font includes 7000+ icons (only using ~10)
- No code splitting for routes

**Solutions:**

```typescript
// Lazy load routes
const routes = [
  {
    path: '/expenses',
    component: () => import('@/views/Expenses.vue')  // Lazy loaded
  }
]

// Use specific icon imports
import { mdiDelete, mdiPlus } from '@mdi/js'
```

### 8.2 Request Optimization

**Avoid N+1 API Calls:**

```typescript
// WRONG - N+1 calls during onboarding
for (const expense of expenses) {
  await budgetApi.createExpense(expense)  // N separate calls
}

// BETTER - Batch endpoint
await budgetApi.createExpenses(expenses)  // Single call
```

### 8.3 Request Caching

```typescript
// Simple caching pattern
const cache = new Map<string, { data: any, timestamp: number }>()
const CACHE_TTL = 60000 // 1 minute

async function getCachedData(key: string, fetcher: () => Promise<any>) {
  const cached = cache.get(key)
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data
  }
  const data = await fetcher()
  cache.set(key, { data, timestamp: Date.now() })
  return data
}
```

---

## 9. Development Workflow

### 9.1 Recommended Tooling

| Purpose | Tool | Why |
|---------|------|-----|
| Unit Tests | Vitest | Fast, Vite-native |
| Component Tests | Vue Test Utils | Official Vue testing |
| E2E Tests | Playwright | Cross-browser, modern |
| Linting | ESLint + Prettier | Consistent code style |
| Type Checking | TypeScript strict | Catch errors early |

### 9.2 Git Workflow

**Commit Message Format:**
```
<type>(<scope>): <description>

<body>

<footer>
```

**Types:** feat, fix, docs, style, refactor, test, chore

### 9.3 Code Review Checklist

- [ ] No hardcoded values (use env vars)
- [ ] Error handling for all API calls
- [ ] Loading states for async operations
- [ ] TypeScript types (avoid `any`)
- [ ] Tests for new functionality
- [ ] Accessibility considerations
- [ ] Security review for user inputs

---

## 10. Common Pitfalls and Solutions

### 10.1 Discovered Issues Summary

| Issue | Where Found | Impact | Solution |
|-------|-------------|--------|----------|
| Fake transaction delete | Transactions.vue | Data not persisted | Uncomment API call |
| Router history bug | router/index.ts | Navigation broken | Use `BASE_URL` |
| CORS port mismatch | api/main.py | API calls blocked | Add all dev ports |
| XSS in error handler | main.ts | Security vulnerability | Use textContent |
| Race conditions | budget.ts store | Data corruption | Per-operation loading |
| Missing import | Transactions.vue | Runtime error | Import budgetApi |

### 10.2 Anti-Pattern Catalog

**DON'T:**
- Use `any` type in TypeScript
- Hardcode API URLs
- Use `confirm()` for deletions (use Vuetify dialogs)
- Trust AI-generated factual data
- Share loading state across operations
- Skip error handling for API calls
- Use native alerts instead of framework components

**DO:**
- Define TypeScript interfaces for all data
- Use environment variables
- Implement proper confirmation dialogs
- Validate and inject factual data post-AI-generation
- Use per-operation loading states
- Handle all error cases with user feedback
- Use consistent UI component library

### 10.3 Production Readiness Checklist

Before any production deployment:

- [ ] All CRITICAL issues resolved
- [ ] Authentication implemented
- [ ] CORS configured for production only
- [ ] Environment variables for all secrets
- [ ] Error tracking (Sentry) configured
- [ ] Rate limiting on API endpoints
- [ ] Database backups configured
- [ ] HTTPS enforced
- [ ] Accessibility audit passed
- [ ] Performance benchmarks met

---

## Appendix A: File Reference

### Resume-Tailor Project Files

| File | Purpose |
|------|---------|
| `resume_tailor.py` | CLI entry point |
| `generator.py` | Core generation logic, AI integration |
| `conflict_detector.py` | Data conflict detection |
| `import_career_data.py` | Career data structure |
| `html_template.py` | HTML resume generation |
| `pdf_generator.py` | PDF output generation |
| `docx_generator.py` | Word document generation |

### The Number Web App Files

| File | Purpose |
|------|---------|
| `frontend/src/views/Dashboard.vue` | Main dashboard |
| `frontend/src/views/Transactions.vue` | Transaction management |
| `frontend/src/stores/budget.ts` | State management |
| `frontend/src/services/api.ts` | API client |
| `frontend/src/router/index.ts` | Route configuration |
| `api/main.py` | FastAPI backend |

---

## Appendix B: Quick Reference Commands

```bash
# Start Vue development server
cd frontend && npm run dev

# Start FastAPI backend
python -m uvicorn api.main:app --reload --port 8000

# Run unit tests
npm run test

# Run E2E tests
npm run test:e2e

# Generate resume
python resume_tailor.py --job job_description.txt --format all
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-18 | Research Orchestrator | Initial comprehensive guide |

---

**IMPORTANT:** This document should be reviewed and updated as new learnings emerge. It serves as the institutional memory for development best practices across all related projects.
