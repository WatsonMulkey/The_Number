# Database Migration Plan: SQLite → PostgreSQL
**Project:** The Number
**Date:** 2025-12-15
**Status:** Monitoring Plan

---

## Current Decision: Start with SQLite

**Rationale:**
- Simple to deploy (no external database service)
- Zero hosting cost for database
- Adequate for initial user base
- Easy local development
- Good performance for read-heavy workloads

---

## Migration Thresholds

We will monitor these metrics and **MUST migrate to PostgreSQL** when we hit ANY of these thresholds:

### 1. Concurrent Users Threshold ⚠️

**Trigger:** 50+ concurrent users regularly

**Why:** SQLite uses file-level locking. While it supports concurrent reads, it only allows ONE write at a time. With 50+ concurrent users creating transactions/expenses, write conflicts will cause:
- `SQLITE_BUSY` errors
- Slow API response times
- User frustration

**Test Plan:**
- Load test with Locust to simulate 50+ concurrent users
- Monitor error rate and response time p95
- If p95 > 500ms or error rate > 1%, migrate immediately

**Monitoring:**
```python
# Track in metrics
concurrent_users = len(active_sessions_in_last_5_minutes)
if concurrent_users > 50:
    alert("Consider PostgreSQL migration")
```

---

### 2. Database Size Threshold ⚠️

**Trigger:** Database file exceeds 1 GB

**Why:** SQLite performs well up to ~1GB. Beyond that:
- Query performance degrades
- Backup/restore becomes slow
- File I/O becomes bottleneck

**Current estimate:**
- 1 user = ~50 KB (expenses + transactions + settings)
- 1 GB = ~20,000 users
- With 100 transactions/user/year + 20 expenses = more conservative

**Realistic threshold:** 10,000-15,000 active users

**Monitoring:**
```python
import os
db_size_mb = os.path.getsize("data/thenumber.db") / (1024 * 1024)
if db_size_mb > 1000:  # 1 GB
    alert("Database size threshold reached - migrate to PostgreSQL")
```

---

### 3. Write Throughput Threshold ⚠️

**Trigger:** >100 writes per second sustained

**Why:** SQLite can handle ~50-100 writes/sec depending on hardware. Beyond that, write queue builds up.

**Calculation:**
- 1000 active users
- Each creates 5 transactions/day = 5000 transactions/day
- Spread over 12 active hours = 5000 / (12 * 3600) = 0.12 writes/sec

Even with 10,000 users, that's only ~1 write/sec average. But peak hours matter:
- If 50% of daily activity happens in 2-hour window
- 10,000 users × 2.5 transactions = 25,000 writes in 2 hours
- = 3.5 writes/sec average, but bursts much higher

**Monitoring:**
```python
writes_per_second = transaction_count_last_minute / 60
if writes_per_second > 100:
    alert("Write throughput threshold - migrate immediately")
if writes_per_second > 50:
    warning("Approaching write threshold - plan migration")
```

---

### 4. Feature Requirements Threshold ⚠️

**Trigger:** Need features SQLite doesn't support well

**Examples:**
- Full-text search across transactions (PostgreSQL has better FTS)
- Advanced analytics queries (PostgreSQL has window functions, CTEs)
- Real-time collaboration (PostgreSQL has LISTEN/NOTIFY)
- JSON fields (both support, but PostgreSQL better)

**Current needs:** None of these yet
**Future needs:** Email receipt parsing might need better FTS

---

### 5. Backup/Disaster Recovery Threshold ⚠️

**Trigger:** Backup time exceeds 5 minutes

**Why:** SQLite backup = copy entire file. As file grows:
- Backup takes longer
- Downtime during backup increases
- Point-in-time recovery harder

PostgreSQL has:
- Streaming replication
- Point-in-time recovery
- No downtime backups

**Monitoring:**
```python
import time
start = time.time()
# Backup database
backup_duration = time.time() - start
if backup_duration > 300:  # 5 minutes
    alert("Backup taking too long - consider PostgreSQL")
```

---

## Concrete Migration Triggers

**MIGRATE IMMEDIATELY if any of these occur:**

1. ✅ **Load test shows:** p95 response time >500ms with 50 concurrent users
2. ✅ **Database size:** >1 GB (approximately 10,000-15,000 users)
3. ✅ **Error rate:** >1% of requests getting SQLITE_BUSY errors
4. ✅ **Write throughput:** Sustained >50 writes/second
5. ✅ **User complaints:** Multiple reports of "slow" or "error saving"

**PLAN MIGRATION (within 2 weeks) if:**

1. ⚠️ 5,000+ active users (approaching concurrent limit)
2. ⚠️ Database size >500 MB (halfway to limit)
3. ⚠️ Write throughput >25 writes/second (halfway to limit)
4. ⚠️ Backup time >2 minutes

---

## Migration Strategy

When we hit a threshold, follow this plan:

### Week 1: Preparation
1. **Set up PostgreSQL:**
   - Railway.app PostgreSQL plan (~$5/month for 1GB)
   - Or Render.com PostgreSQL (~$7/month)
   - Or Supabase free tier (500MB, good for testing)

2. **Create migration script:**
   ```python
   # scripts/migrate_sqlite_to_postgres.py
   import sqlite3
   import psycopg2

   def migrate():
       # Read from SQLite
       sqlite_conn = sqlite3.connect("data/thenumber.db")

       # Write to PostgreSQL
       pg_conn = psycopg2.connect(DATABASE_URL)

       # Migrate users
       # Migrate expenses
       # Migrate transactions
       # Verify data integrity
   ```

3. **Update database.py:**
   - Add PostgreSQL support (SQLAlchemy for abstraction)
   - Keep SQLite for local dev
   - Use environment variable to switch

### Week 2: Testing
1. **Test migration script:**
   - Copy production data to staging
   - Run migration
   - Verify all data present
   - Run all tests against PostgreSQL

2. **Load test PostgreSQL:**
   - Verify it handles 100+ concurrent users
   - Verify write throughput >500/sec
   - Verify response times improved

### Week 3: Migration
1. **Schedule maintenance window** (2 AM on Sunday)
2. **Migration steps:**
   - Put app in read-only mode
   - Run migration script
   - Verify data integrity
   - Switch DATABASE_URL to PostgreSQL
   - Deploy new code
   - Test critical flows
   - Enable writes
   - Monitor for errors

3. **Rollback plan:**
   - Keep SQLite file as backup
   - Can switch back if issues
   - PostgreSQL→SQLite script ready

### Week 4: Monitoring
- Monitor error rate (should be 0%)
- Monitor response times (should improve)
- Monitor user feedback
- Keep SQLite backup for 30 days

---

## Cost Impact of Migration

**Current:** $0/month (SQLite)

**After PostgreSQL Migration:**
- Railway: $5/month (1GB)
- Render: $7/month (1GB)
- Supabase: Free tier (500MB) → $25/month (8GB)

**At 10,000 users (migration point):**
- Assuming $5/user/month revenue (if monetized)
- Revenue: $50,000/month
- Database cost: $5-7/month
- **Cost ratio:** 0.01% of revenue

**Conclusion:** Cost is negligible at migration point.

---

## SQLite Optimization Before Migration

To maximize SQLite performance and delay migration:

### 1. Use WAL Mode (Write-Ahead Logging)
```python
# database.py
conn.execute("PRAGMA journal_mode=WAL")
```

**Benefits:**
- Allows concurrent reads during writes
- Improves write throughput
- Better crash recovery

### 2. Connection Pooling
```python
# Use singleton pattern for database connection
# Reuse connections instead of creating new ones
```

### 3. Batch Writes
```python
# Instead of: 10 individual INSERT statements
# Use: 1 transaction with 10 INSERTs
conn.execute("BEGIN")
for transaction in transactions:
    conn.execute("INSERT...", transaction)
conn.execute("COMMIT")
```

### 4. Indexes
```sql
CREATE INDEX idx_transactions_user_date ON transactions(user_id, date);
CREATE INDEX idx_expenses_user ON expenses(user_id);
CREATE INDEX idx_users_email ON users(email);
```

### 5. VACUUM Regularly
```python
# Weekly maintenance job
conn.execute("VACUUM")  # Defragment database
```

**Expected improvement:** 2-3x better performance → delays migration

---

## Monitoring Dashboard

Track these metrics weekly:

```python
# scripts/database_health_check.py

def check_database_health():
    conn = sqlite3.connect("data/thenumber.db")

    # 1. Database size
    size_mb = os.path.getsize("data/thenumber.db") / (1024 * 1024)
    print(f"Database size: {size_mb:.2f} MB (threshold: 1000 MB)")

    # 2. User count
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    print(f"Total users: {user_count} (threshold: 15,000)")

    # 3. Active users (last 7 days)
    active_users = conn.execute(
        "SELECT COUNT(*) FROM users WHERE last_seen > datetime('now', '-7 days')"
    ).fetchone()[0]
    print(f"Active users (7d): {active_users} (threshold: 5,000)")

    # 4. Write rate (transactions/day)
    transactions_today = conn.execute(
        "SELECT COUNT(*) FROM transactions WHERE date(created_at) = date('now')"
    ).fetchone()[0]
    print(f"Transactions today: {transactions_today}")

    # 5. Table sizes
    for table in ['users', 'expenses', 'transactions']:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count} rows")

    # 6. Recommendations
    if size_mb > 500:
        print("\n⚠️  WARNING: Database >50% of migration threshold")
    if active_users > 2500:
        print("\n⚠️  WARNING: Active users >50% of migration threshold")
    if size_mb > 1000 or active_users > 5000:
        print("\n🚨 ALERT: Migration threshold reached - plan PostgreSQL migration")
```

**Run weekly and log results to track growth trends.**

---

## Decision Matrix

| Metric | Current | Warning | Critical | Action |
|--------|---------|---------|----------|--------|
| Database Size | 0 MB | 500 MB | 1000 MB | Migrate |
| Total Users | 0 | 5,000 | 15,000 | Migrate |
| Active Users (7d) | 0 | 2,500 | 5,000 | Migrate |
| Concurrent Users | 0 | 25 | 50 | Migrate |
| Write Rate | 0/s | 25/s | 50/s | Migrate |
| Error Rate | 0% | 0.5% | 1% | Migrate |
| Response Time p95 | <100ms | 300ms | 500ms | Migrate |
| Backup Time | <10s | 2min | 5min | Migrate |

---

## Summary

**Start with SQLite because:**
- Zero cost
- Simple deployment
- Adequate for 0-10,000 users
- Easy local development

**Migrate to PostgreSQL when:**
- Database >1 GB (~10,000-15,000 users)
- OR concurrent users >50
- OR write rate >50/s
- OR error rate >1%
- OR response time p95 >500ms

**Monitor weekly** and have migration plan ready.

**Expected timeline:** 6-12 months before hitting thresholds (if growth is healthy).

**Cost impact at migration:** <0.01% of revenue (if monetized), or $5-7/month absolute.

---

## Next Steps

1. **Implement SQLite optimizations NOW:**
   - [x] Enable WAL mode
   - [ ] Add proper indexes
   - [ ] Connection pooling
   - [ ] Batch writes where possible

2. **Set up monitoring:**
   - [ ] Create database health check script
   - [ ] Run weekly and log results
   - [ ] Set up alerts for warning thresholds

3. **Plan ahead:**
   - [ ] Document migration script
   - [ ] Test PostgreSQL locally
   - [ ] Have Railway/Render account ready

**Status:** SQLite approved for initial development. Migration thresholds documented and monitored.
