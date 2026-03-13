<template>
  <v-container class="admin-container" fluid>
    <div class="admin-content">
      <!-- Header -->
      <div class="d-flex align-center justify-space-between mb-6">
        <div>
          <h1 class="text-h5 font-weight-bold">Metrics Dashboard</h1>
          <span v-if="lastUpdated" class="text-body-2 text-medium-emphasis">
            Last updated: {{ timeAgo }}
          </span>
        </div>
        <v-btn
          variant="outlined"
          prepend-icon="mdi-refresh"
          :loading="loading"
          @click="fetchData"
        >
          Refresh
        </v-btn>
      </div>

      <!-- Loading -->
      <div v-if="loading && !metrics" class="text-center py-12">
        <v-progress-circular indeterminate color="primary" size="48" />
        <p class="mt-4 text-body-2 text-medium-emphasis">Loading metrics...</p>
      </div>

      <!-- Error -->
      <v-alert v-if="error" type="error" class="mb-6" closable @click:close="error = null">
        {{ error }}
      </v-alert>

      <!-- Metrics Content -->
      <template v-if="metrics && health">
        <!-- KPI Cards -->
        <v-row class="mb-6">
          <v-col cols="6" md="3">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.growth.total_users }}</div>
                <div class="text-body-2 text-medium-emphasis">Total Users</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" md="3">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.engagement.dau }}</div>
                <div class="kpi-meta">
                  <span class="text-body-2 text-medium-emphasis">DAU</span>
                  <span v-if="trends" :class="trendClass(trends.comparisons.dau)" class="trend-chip">
                    {{ trendIndicator(trends.comparisons.dau) }}
                  </span>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" md="3">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.engagement.wau }}</div>
                <div class="kpi-meta">
                  <span class="text-body-2 text-medium-emphasis">WAU</span>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" md="3">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.volume.total_transactions }}</div>
                <div class="kpi-meta">
                  <span class="text-body-2 text-medium-emphasis">Transactions</span>
                  <span v-if="trends" :class="trendClass(trends.comparisons.transactions)" class="trend-chip">
                    {{ trendIndicator(trends.comparisons.transactions) }}
                  </span>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Trend Charts -->
        <h2 class="text-h6 mb-3">Trends (30 days)</h2>
        <v-row class="mb-6" v-if="trends">
          <v-col cols="12" md="6">
            <v-card variant="outlined" class="metric-card pa-4">
              <div class="text-subtitle-2 font-weight-medium mb-2">Daily Active Users</div>
              <div class="chart-wrapper">
                <TrendChart
                  :labels="trendLabels"
                  :data="trends.daily_active_users.map(d => d.value)"
                  label="DAU"
                  color="#87986a"
                />
              </div>
            </v-card>
          </v-col>
          <v-col cols="12" md="6">
            <v-card variant="outlined" class="metric-card pa-4">
              <div class="text-subtitle-2 font-weight-medium mb-2">Daily Signups</div>
              <div class="chart-wrapper">
                <TrendChart
                  :labels="trendLabels"
                  :data="trends.daily_signups.map(d => d.value)"
                  label="Signups"
                  color="#c4704b"
                />
              </div>
            </v-card>
          </v-col>
        </v-row>

        <!-- Feature Adoption -->
        <h2 class="text-h6 mb-3">Feature Adoption</h2>
        <v-row class="mb-6">
          <v-col cols="6" md="3">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.depth.budget_configured_pct }}%</div>
                <div class="text-body-2 text-medium-emphasis">Budget Config</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" md="3">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.depth.paycheck_mode_count }}</div>
                <div class="text-body-2 text-medium-emphasis">Paycheck Mode</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" md="3">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.depth.fixed_pool_mode_count }}</div>
                <div class="text-body-2 text-medium-emphasis">Fixed Pool</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" md="3">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.depth.pool_enabled_count }}</div>
                <div class="text-body-2 text-medium-emphasis">Pool Enabled</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- System Health -->
        <h2 class="text-h6 mb-3">System Health</h2>
        <v-row class="mb-6">
          <v-col cols="12" sm="6">
            <v-card variant="outlined" class="metric-card">
              <v-card-text>
                <div class="text-subtitle-1 font-weight-bold mb-2">Database</div>
                <div class="text-body-2 mb-1">Size: {{ health.database.size_mb }} MB</div>
                <div v-for="(count, table) in health.database.row_counts" :key="table" class="text-body-2 text-medium-emphasis">
                  {{ table }}: {{ count.toLocaleString() }} rows
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6">
            <v-card variant="outlined" class="metric-card">
              <v-card-text>
                <div class="text-subtitle-1 font-weight-bold mb-2">Disk Volume</div>
                <v-progress-linear
                  :model-value="health.disk.used_pct"
                  :color="health.disk.used_pct > 80 ? 'error' : 'primary'"
                  height="8"
                  rounded
                  class="mb-2"
                />
                <div class="text-body-2">{{ health.disk.used_pct }}% used</div>
                <div class="text-body-2 text-medium-emphasis">
                  {{ formatBytes(health.disk.free_bytes) }} free of {{ formatBytes(health.disk.total_bytes) }}
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </template>
    </div>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { format } from 'date-fns'
import { adminApi, type AdminMetrics, type AdminHealth, type AdminTrends } from '@/services/api'
import TrendChart from '@/components/TrendChart.vue'

const metrics = ref<AdminMetrics | null>(null)
const health = ref<AdminHealth | null>(null)
const trends = ref<AdminTrends | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const lastUpdated = ref<Date | null>(null)
const now = ref(new Date())

let refreshInterval: ReturnType<typeof setInterval> | null = null
let tickInterval: ReturnType<typeof setInterval> | null = null

const timeAgo = computed(() => {
  if (!lastUpdated.value) return ''
  const seconds = Math.floor((now.value.getTime() - lastUpdated.value.getTime()) / 1000)
  if (seconds < 5) return 'just now'
  if (seconds < 60) return `${seconds}s ago`
  return `${Math.floor(seconds / 60)}m ago`
})

const trendLabels = computed(() => {
  if (!trends.value) return []
  return trends.value.daily_active_users.map(d => format(new Date(d.date + 'T00:00:00'), 'MMM d'))
})

function trendIndicator(pct: number): string {
  if (pct > 0) return `▲ ${pct}%`
  if (pct < 0) return `▼ ${Math.abs(pct)}%`
  return '— 0%'
}

function trendClass(pct: number): string {
  if (pct > 0) return 'trend-up'
  if (pct < 0) return 'trend-down'
  return 'trend-flat'
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB'
}

async function fetchData() {
  loading.value = true
  error.value = null
  try {
    const [metricsRes, healthRes, trendsRes] = await Promise.all([
      adminApi.getMetrics(),
      adminApi.getHealth(),
      adminApi.getTrends(),
    ])
    metrics.value = metricsRes.data
    health.value = healthRes.data
    trends.value = trendsRes.data
    lastUpdated.value = new Date()
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load metrics'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
  refreshInterval = setInterval(fetchData, 60_000)
  tickInterval = setInterval(() => { now.value = new Date() }, 1_000)
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
  if (tickInterval) clearInterval(tickInterval)
})
</script>

<style scoped>
.admin-container {
  display: flex;
  justify-content: center;
  padding-top: 24px;
}

.admin-content {
  width: 100%;
  max-width: 1000px;
}

.metric-card {
  border-color: var(--color-sage-green);
}

.chart-wrapper {
  height: 200px;
  position: relative;
}

.kpi-meta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.trend-chip {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 4px;
}

.trend-up {
  color: #2e7d32;
  background: #e8f5e9;
}

.trend-down {
  color: #c62828;
  background: #ffebee;
}

.trend-flat {
  color: #757575;
  background: #f5f5f5;
}
</style>
