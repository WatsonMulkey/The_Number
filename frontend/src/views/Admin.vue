<template>
  <v-container class="admin-container" fluid>
    <div class="admin-content">
      <!-- Header -->
      <div class="d-flex align-center justify-space-between mb-6">
        <h1 class="text-h5 font-weight-bold">Metrics Dashboard</h1>
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
        <!-- Growth -->
        <h2 class="text-h6 mb-3">Growth</h2>
        <v-row class="mb-6">
          <v-col cols="12" sm="4">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.growth.total_users }}</div>
                <div class="text-body-2 text-medium-emphasis">Total Users</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" sm="4">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.growth.signups_this_week }}</div>
                <div class="text-body-2 text-medium-emphasis">Signups This Week</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" sm="4">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.growth.signups_this_month }}</div>
                <div class="text-body-2 text-medium-emphasis">Signups This Month</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Engagement -->
        <h2 class="text-h6 mb-3">Engagement</h2>
        <v-row class="mb-6">
          <v-col cols="6" sm="3">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.engagement.dau }}</div>
                <div class="text-body-2 text-medium-emphasis">DAU</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" sm="3">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.engagement.wau }}</div>
                <div class="text-body-2 text-medium-emphasis">WAU</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" sm="3">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.engagement.mau }}</div>
                <div class="text-body-2 text-medium-emphasis">MAU</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" sm="3">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.engagement.avg_sessions_per_day }}</div>
                <div class="text-body-2 text-medium-emphasis">Avg Sessions/Day</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Feature Adoption -->
        <h2 class="text-h6 mb-3">Feature Adoption</h2>
        <v-row class="mb-6">
          <v-col cols="6" sm="3">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.depth.budget_configured_pct }}%</div>
                <div class="text-body-2 text-medium-emphasis">Budget Config Rate</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" sm="3">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.depth.paycheck_mode_count }}</div>
                <div class="text-body-2 text-medium-emphasis">Paycheck Mode</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" sm="3">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.depth.fixed_pool_mode_count }}</div>
                <div class="text-body-2 text-medium-emphasis">Fixed Pool Mode</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" sm="3">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.depth.pool_enabled_count }}</div>
                <div class="text-body-2 text-medium-emphasis">Pool Enabled</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Volume -->
        <h2 class="text-h6 mb-3">Volume</h2>
        <v-row class="mb-6">
          <v-col cols="6">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.volume.total_transactions }}</div>
                <div class="text-body-2 text-medium-emphasis">Total Transactions</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6">
            <v-card variant="outlined" class="metric-card">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ metrics.volume.total_expenses }}</div>
                <div class="text-body-2 text-medium-emphasis">Total Expenses</div>
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
                  {{ table }}: {{ count }} rows
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
import { ref, onMounted } from 'vue'
import { adminApi, type AdminMetrics, type AdminHealth } from '@/services/api'

const metrics = ref<AdminMetrics | null>(null)
const health = ref<AdminHealth | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

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
    const [metricsRes, healthRes] = await Promise.all([
      adminApi.getMetrics(),
      adminApi.getHealth(),
    ])
    metrics.value = metricsRes.data
    health.value = healthRes.data
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load metrics'
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
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
</style>
