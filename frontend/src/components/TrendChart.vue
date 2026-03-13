<template>
  <Line :data="chartData" :options="chartOptions" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler)

const props = withDefaults(defineProps<{
  labels: string[]
  data: number[]
  label: string
  color?: string
}>(), {
  color: '#87986a',
})

const chartData = computed(() => ({
  labels: props.labels,
  datasets: [{
    label: props.label,
    data: props.data,
    borderColor: props.color,
    backgroundColor: props.color + '1a',
    fill: true,
    tension: 0.3,
    pointRadius: 0,
    pointHitRadius: 8,
    borderWidth: 2,
  }],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    tooltip: {
      backgroundColor: '#2c2c2c',
      titleFont: { family: 'Inter, sans-serif', size: 12 },
      bodyFont: { family: 'Inter, sans-serif', size: 12 },
      padding: 8,
      cornerRadius: 6,
    },
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: {
        maxTicksLimit: 6,
        font: { family: 'Inter, sans-serif', size: 11 },
        color: '#999',
      },
    },
    y: {
      beginAtZero: true,
      grid: { color: '#f0f0f0' },
      ticks: {
        font: { family: 'Inter, sans-serif', size: 11 },
        color: '#999',
        precision: 0,
      },
    },
  },
}
</script>
