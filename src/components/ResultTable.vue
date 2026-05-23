<script setup>
import { ref, computed } from 'vue'
import { highlightPhones, formatPhone } from '../utils/phone.js'

const { data } = defineProps({
  data: {
    type: Object,
    default: null,
  },
})

const searchText = ref('')
const filterRisk = ref('')
const filterType = ref('')

const highlightCache = new Map()
function cachedHighlight(text) {
  if (highlightCache.has(text)) return highlightCache.get(text)
  const result = highlightPhones(text)
  highlightCache.set(text, result)
  return result
}

const filteredResults = computed(() => {
  if (!data) return []
  let list = data.results

  if (filterRisk.value) {
    list = list.filter((r) => r.riskLevel === filterRisk.value)
  }

  if (filterType.value) {
    list = list.filter((r) => r.dataType === filterType.value)
  }

  if (searchText.value.trim()) {
    const q = searchText.value.trim().toLowerCase()
    list = list.filter(
      (r) =>
        r.displayValue.toLowerCase().includes(q) ||
        r.originalText.toLowerCase().includes(q) ||
        r.phones.some((p) => p.includes(q)) ||
        r.sns.some((s) => s.toLowerCase().includes(q))
    )
  }

  return list
})

const allPhones = computed(() => {
  if (!data) return []
  const set = new Set()
  data.results.forEach((r) => r.phones.forEach((p) => set.add(p)))
  return [...set]
})

const allSNs = computed(() => {
  if (!data) return []
  const set = new Set()
  data.results.forEach((r) => r.sns.forEach((s) => set.add(s)))
  return [...set]
})

function copyAllPhones() {
  navigator.clipboard.writeText(allPhones.value.join('\n'))
}

function copyAllSNs() {
  navigator.clipboard.writeText(allSNs.value.join('\n'))
}

async function handleExport() {
  const { exportResults } = await import('../utils/excel.js')
  exportResults(filteredResults.value, data.displayCol, '识别结果')
}
</script>

<template>
  <div v-if="data" class="result-panel">
    <div class="stats-bar">
      <div class="stat-item">
        <span class="stat-label">识别列</span>
        <span class="stat-value">{{ data.targetCol }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">返回列</span>
        <span class="stat-value">{{ data.displayCol }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">匹配行数</span>
        <span class="stat-value highlight">{{ data.results.length }}</span>
      </div>
      <div class="stat-item type-phone">
        <span class="stat-label">电话</span>
        <span class="stat-value">{{ data.typeCounts?.['电话'] || 0 }}</span>
      </div>
      <div class="stat-item type-sn">
        <span class="stat-label">SN</span>
        <span class="stat-value">{{ data.typeCounts?.['SN'] || 0 }}</span>
      </div>
      <div class="stat-item risk-normal">
        <span class="stat-label">普通</span>
        <span class="stat-value">{{ data.riskCounts?.['普通'] || 0 }}</span>
      </div>
      <div class="stat-item risk-low">
        <span class="stat-label">低风险</span>
        <span class="stat-value">{{ data.riskCounts?.['低风险'] || 0 }}</span>
      </div>
      <div class="stat-item risk-high">
        <span class="stat-label">重危</span>
        <span class="stat-value">{{ data.riskCounts?.['重危'] || 0 }}</span>
      </div>
    </div>

    <div class="toolbar">
      <div class="filter-group">
        <button
          class="filter-btn"
          :class="{ active: filterType === '' }"
          @click="filterType = ''"
        >全部</button>
        <button
          class="filter-btn filter-phone"
          :class="{ active: filterType === '电话' }"
          @click="filterType = '电话'"
        >电话</button>
        <button
          class="filter-btn filter-sn"
          :class="{ active: filterType === 'SN' }"
          @click="filterType = 'SN'"
        >SN</button>
      </div>

      <div class="filter-group">
        <button
          class="filter-btn"
          :class="{ active: filterRisk === '' }"
          @click="filterRisk = ''"
        >全部风险</button>
        <button
          class="filter-btn filter-normal"
          :class="{ active: filterRisk === '普通' }"
          @click="filterRisk = '普通'"
        >普通</button>
        <button
          class="filter-btn filter-low"
          :class="{ active: filterRisk === '低风险' }"
          @click="filterRisk = '低风险'"
        >低风险</button>
        <button
          class="filter-btn filter-high"
          :class="{ active: filterRisk === '重危' }"
          @click="filterRisk = '重危'"
        >重危</button>
      </div>

      <input
        v-model="searchText"
        type="text"
        class="search-input"
        placeholder="搜索文本、手机号或SN..."
      />

      <div class="toolbar-actions">
        <button class="btn btn-outline" @click="copyAllPhones">📋 复制手机号</button>
        <button class="btn btn-outline" @click="copyAllSNs">📋 复制SN</button>
        <button class="btn btn-primary" @click="handleExport">📥 导出结果</button>
      </div>
    </div>

    <div class="table-wrapper">
      <table class="result-table">
        <thead>
          <tr>
            <th class="col-idx">#</th>
            <th class="col-display">{{ data.displayCol }} 列数据</th>
            <th class="col-row">原始行号</th>
            <th class="col-type">类型</th>
            <th class="col-value">识别到的值</th>
            <th class="col-text">原文内容</th>
            <th class="col-risk">风险类型</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in filteredResults" :key="index">
            <td class="col-idx">{{ index + 1 }}</td>
            <td class="col-display">{{ item.displayValue }}</td>
            <td class="col-row">{{ item.rowNum }}</td>
            <td class="col-type">
              <span class="type-tag" :class="item.dataType === 'SN' ? 'type-tag-sn' : 'type-tag-phone'">
                {{ item.dataType }}
              </span>
            </td>
            <td class="col-value">
              <template v-if="item.dataType === '电话'">
                <span v-for="phone in item.phones" :key="phone" class="phone-tag">
                  {{ formatPhone(phone) }}
                </span>
              </template>
              <template v-else>
                <span v-for="sn in item.sns" :key="sn" class="sn-tag">
                  {{ sn }}
                </span>
              </template>
            </td>
            <td class="col-text">
              <div class="text-cell" v-html="cachedHighlight(item.originalText)"></div>
            </td>
            <td class="col-risk">
              <span class="risk-tag" :class="item.riskLevel === '重危' ? 'risk-tag-high' : item.riskLevel === '低风险' ? 'risk-tag-low' : 'risk-tag-normal'">
                {{ item.riskLevel }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <p v-if="filteredResults.length === 0" class="empty-text">
        {{ data.results.length === 0 ? '未在指定列中识别到手机号或SN' : '没有匹配的结果' }}
      </p>
    </div>

    <div v-if="allPhones.length > 0" class="phone-summary">
      <h4>全部识别到的手机号 ({{ allPhones.length }} 个)</h4>
      <div class="phone-list">
        <span v-for="phone in allPhones" :key="phone" class="phone-chip">
          {{ formatPhone(phone) }}
        </span>
      </div>
    </div>

    <div v-if="allSNs.length > 0" class="phone-summary">
      <h4>全部识别到的SN ({{ allSNs.length }} 个)</h4>
      <div class="phone-list">
        <span v-for="sn in allSNs" :key="sn" class="sn-chip">
          {{ sn }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.result-panel {
  margin-top: 24px;
}

.stats-bar {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.stat-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px 20px;
  flex: 1;
  min-width: 100px;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #667085;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #1d2939;
}

.stat-value.highlight {
  color: #4096ff;
}

.type-phone {
  background: #e6f4ff;
  border: 1px solid #91caff;
}

.type-phone .stat-value {
  color: #1677ff;
}

.type-sn {
  background: #fff7e6;
  border: 1px solid #ffd591;
}

.type-sn .stat-value {
  color: #fa8c16;
}

.risk-normal {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
}

.risk-normal .stat-value {
  color: #389e0d;
}

.risk-low {
  background: #e6f4ff;
  border: 1px solid #91caff;
}

.risk-low .stat-value {
  color: #1677ff;
}

.risk-high {
  background: #fff2f0;
  border: 1px solid #ffccc7;
}

.risk-high .stat-value {
  color: #f5222d;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-group {
  display: flex;
  gap: 4px;
  background: #f0f0f0;
  border-radius: 8px;
  padding: 3px;
}

.filter-btn {
  padding: 6px 14px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  background: transparent;
  color: #667085;
  transition: all 0.2s;
}

.filter-btn:hover {
  color: #344054;
}

.filter-btn.active {
  background: #fff;
  color: #1d2939;
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filter-btn.filter-phone.active {
  color: #1677ff;
}

.filter-btn.filter-sn.active {
  color: #fa8c16;
}

.filter-btn.filter-normal.active {
  color: #389e0d;
}

.filter-btn.filter-low.active {
  color: #1677ff;
}

.filter-btn.filter-high.active {
  color: #f5222d;
}

.search-input {
  flex: 1;
  min-width: 200px;
  padding: 8px 12px;
  border: 1px solid #d0d5dd;
  border-radius: 8px;
  font-size: 14px;
  background: #fff;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #4096ff;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-primary {
  background: #4096ff;
  color: #fff;
}

.btn-primary:hover {
  background: #1677ff;
}

.btn-outline {
  background: #fff;
  color: #344054;
  border: 1px solid #d0d5dd;
}

.btn-outline:hover {
  background: #f8f9fa;
  border-color: #98a2b3;
}

.table-wrapper {
  overflow-x: auto;
  overflow-y: auto;
  max-height: 600px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.result-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.result-table th {
  background: #f8f9fa;
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  color: #344054;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  z-index: 1;
}

.result-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #f0f0f0;
  vertical-align: top;
}

.result-table tbody tr:hover {
  background: #f0f5ff;
}

.col-idx {
  width: 48px;
  text-align: center;
  color: #98a2b3;
}

.col-display {
  min-width: 150px;
  max-width: 300px;
  word-break: break-all;
}

.col-row {
  width: 80px;
  text-align: center;
  font-family: 'SF Mono', 'Menlo', monospace;
  color: #667085;
}

.col-type {
  width: 70px;
  text-align: center;
}

.col-value {
  min-width: 160px;
}

.col-text {
  min-width: 250px;
  max-width: 400px;
}

.col-risk {
  width: 90px;
  text-align: center;
}

.text-cell {
  word-break: break-all;
  line-height: 1.6;
  max-height: 120px;
  overflow-y: auto;
}

.text-cell :deep(.phone-highlight) {
  background: #fff3cd;
  color: #856404;
  padding: 1px 3px;
  border-radius: 3px;
  font-weight: 600;
}

.type-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.type-tag-phone {
  background: #e6f4ff;
  color: #1677ff;
  border: 1px solid #91caff;
}

.type-tag-sn {
  background: #fff7e6;
  color: #fa8c16;
  border: 1px solid #ffd591;
}

.phone-tag {
  display: inline-block;
  background: #e6f4ff;
  color: #1677ff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 13px;
  margin: 2px 4px 2px 0;
  font-family: 'SF Mono', 'Menlo', monospace;
}

.sn-tag {
  display: inline-block;
  background: #fff7e6;
  color: #fa8c16;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 13px;
  margin: 2px 4px 2px 0;
  font-family: 'SF Mono', 'Menlo', monospace;
}

.risk-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.risk-tag-normal {
  background: #f6ffed;
  color: #389e0d;
  border: 1px solid #b7eb8f;
}

.risk-tag-low {
  background: #e6f4ff;
  color: #1677ff;
  border: 1px solid #91caff;
}

.risk-tag-high {
  background: #fff2f0;
  color: #f5222d;
  border: 1px solid #ffccc7;
}

.empty-text {
  text-align: center;
  color: #98a2b3;
  padding: 32px;
  font-size: 14px;
}

.phone-summary {
  margin-top: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.phone-summary h4 {
  margin: 0 0 12px;
  font-size: 14px;
  color: #344054;
}

.phone-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.phone-chip {
  display: inline-flex;
  align-items: center;
  background: #fff;
  border: 1px solid #4096ff;
  color: #1677ff;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-family: 'SF Mono', 'Menlo', monospace;
}

.sn-chip {
  display: inline-flex;
  align-items: center;
  background: #fff;
  border: 1px solid #fa8c16;
  color: #fa8c16;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-family: 'SF Mono', 'Menlo', monospace;
}
</style>
