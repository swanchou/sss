<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  sheets: { type: Array, default: () => [] },
  fileName: { type: String, default: '' },
})

const emit = defineEmits(['confirm', 'cancel'])

const activeSheetIdx = ref(0)
const selected = ref({})

function initSelections() {
  const map = {}
  for (const sheet of props.sheets) {
    map[sheet.name] = sheet.columns.filter((c) => c.hasPhones).map((c) => c.index)
  }
  selected.value = map
}

watch(() => props.sheets, initSelections, { immediate: true })

const activeSheet = computed(() => props.sheets[activeSheetIdx.value])
const activeSelected = computed(() => selected.value[activeSheet.value?.name] || [])

function isChecked(colIndex) {
  return activeSelected.value.includes(colIndex)
}

function toggle(colIndex) {
  const name = activeSheet.value.name
  const arr = selected.value[name]
  const idx = arr.indexOf(colIndex)
  if (idx >= 0) {
    arr.splice(idx, 1)
  } else {
    arr.push(colIndex)
  }
}

function selectAll() {
  const sheet = activeSheet.value
  selected.value[sheet.name] = sheet.columns.map((c) => c.index)
}

function deselectAll() {
  selected.value[activeSheet.value.name] = []
}

function selectDetected() {
  const sheet = activeSheet.value
  selected.value[sheet.name] = sheet.columns.filter((c) => c.hasPhones).map((c) => c.index)
}

const totalSelected = computed(() => {
  let count = 0
  for (const sheet of props.sheets) {
    count += (selected.value[sheet.name] || []).length
  }
  return count
})

function handleConfirm() {
  const result = {}
  for (const sheet of props.sheets) {
    const cols = selected.value[sheet.name] || []
    if (cols.length > 0) {
      result[sheet.name] = [...cols]
    }
  }
  emit('confirm', result)
}

function formatSample(text) {
  if (text.length > 60) return text.slice(0, 60) + '...'
  return text
}
</script>

<template>
  <div class="column-selector">
    <div class="selector-header">
      <div class="header-info">
        <h3>📋 选择要识别的列</h3>
        <p class="header-desc">
          文件: <strong>{{ fileName }}</strong> · 已选 {{ totalSelected }} 列
        </p>
      </div>
    </div>

    <div v-if="props.sheets.length > 1" class="sheet-tabs">
      <button
        v-for="(sheet, idx) in props.sheets"
        :key="sheet.name"
        class="tab-btn"
        :class="{ active: activeSheetIdx === idx }"
        @click="activeSheetIdx = idx"
      >
        {{ sheet.name }}
        <span class="tab-count">({{ sheet.columns.length }}列)</span>
      </button>
    </div>

    <div v-if="!activeSheet || activeSheet.columns.length === 0" class="empty-columns">
      <p>该 Sheet 没有检测到数据列，请检查 Excel 文件格式</p>
    </div>

    <template v-else>
    <div class="toolbar">
      <button class="btn btn-sm" @click="selectAll">全选</button>
      <button class="btn btn-sm" @click="deselectAll">全不选</button>
      <button class="btn btn-sm btn-detected" @click="selectDetected">
        🔍 仅选识别到的列
      </button>
    </div>

    <div class="table-wrapper">
      <table class="col-table">
        <thead>
          <tr>
            <th class="col-check">选择</th>
            <th class="col-letter">列号</th>
            <th class="col-header">表头</th>
            <th class="col-preview">数据预览</th>
            <th class="col-hint">智能识别</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="col in activeSheet?.columns || []"
            :key="col.index"
            :class="{ 'detected-row': col.hasPhones, selected: isChecked(col.index) }"
            @click="toggle(col.index)"
          >
            <td class="col-check">
              <input
                type="checkbox"
                :checked="isChecked(col.index)"
                @click.stop
                @change="toggle(col.index)"
              />
            </td>
            <td class="col-letter">
              <span class="letter-badge">{{ col.letter }}</span>
            </td>
            <td class="col-header">{{ col.header }}</td>
            <td class="col-preview">
              <div v-if="col.samples.length > 0" class="samples">
                <div v-for="(s, i) in col.samples.slice(0, 3)" :key="i" class="sample-line">
                  {{ formatSample(s) }}
                </div>
                <div v-if="col.samples.length > 3" class="sample-more">
                  还有 {{ col.samples.length - 3 }} 条...
                </div>
              </div>
              <span v-else class="empty-hint">（空）</span>
            </td>
            <td class="col-hint">
              <span v-if="col.hasPhones" class="hint-badge found">✓ 疑似含手机号</span>
              <span v-else class="hint-badge none">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="actions">
      <button class="btn btn-cancel" @click="emit('cancel')">返回上传</button>
      <button
        class="btn btn-confirm"
        :disabled="totalSelected === 0"
        @click="handleConfirm"
      >
        开始识别 ({{ totalSelected }} 列)
      </button>
    </div>
    </template>
  </div>
</template>

<style scoped>
.column-selector {
  margin-top: 24px;
}

.selector-header {
  margin-bottom: 16px;
}

.selector-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 4px;
}

.header-desc {
  font-size: 13px;
  color: #667085;
  margin: 0;
}

.sheet-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0;
}

.tab-btn {
  padding: 8px 16px;
  border: none;
  background: transparent;
  font-size: 14px;
  color: #667085;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #4096ff;
}

.tab-btn.active {
  color: #4096ff;
  border-bottom-color: #4096ff;
  font-weight: 600;
}

.tab-count {
  font-size: 12px;
  color: #98a2b3;
}

.toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.btn {
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  border: 1px solid #d0d5dd;
  background: #fff;
  color: #344054;
  transition: all 0.2s;
}

.btn:hover {
  border-color: #4096ff;
  color: #4096ff;
}

.btn-sm {
  padding: 4px 10px;
  font-size: 12px;
}

.btn-detected {
  background: #f0f5ff;
  border-color: #4096ff;
  color: #4096ff;
}

.table-wrapper {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: auto;
  max-height: 420px;
}

.col-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.col-table th {
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

.col-table td {
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
  vertical-align: top;
}

.col-table tbody tr {
  cursor: pointer;
  transition: background 0.15s;
}

.col-table tbody tr:hover {
  background: #f0f5ff;
}

.col-table tbody tr.selected {
  background: #e6f4ff;
}

.col-table tbody tr.detected-row {
  background: #fffbf0;
}

.col-table tbody tr.detected-row:hover {
  background: #fff7e6;
}

.col-check {
  width: 48px;
  text-align: center;
}

.col-check input[type='checkbox'] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #4096ff;
}

.col-letter {
  width: 60px;
}

.letter-badge {
  display: inline-block;
  background: #f3f0ff;
  color: #722ed1;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'SF Mono', 'Menlo', monospace;
  font-size: 12px;
  font-weight: 600;
}

.col-header {
  min-width: 120px;
  font-weight: 500;
}

.col-preview {
  min-width: 200px;
  max-width: 400px;
}

.samples {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sample-line {
  font-size: 12px;
  color: #667085;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sample-more {
  font-size: 11px;
  color: #98a2b3;
}

.empty-hint {
  font-size: 12px;
  color: #d0d5dd;
}

.col-hint {
  width: 120px;
  text-align: center;
}

.hint-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.hint-badge.found {
  background: #d4edda;
  color: #155724;
}

.hint-badge.none {
  background: #f8f9fa;
  color: #98a2b3;
}

.actions {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
}

.btn-cancel {
  background: #fff;
  color: #667085;
}

.btn-confirm {
  background: #4096ff;
  color: #fff;
  border-color: #4096ff;
  font-weight: 600;
  padding: 8px 24px;
  font-size: 14px;
}

.btn-confirm:hover:not(:disabled) {
  background: #1677ff;
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-columns {
  text-align: center;
  padding: 40px 20px;
  color: #98a2b3;
  font-size: 14px;
  background: #fafbfc;
  border-radius: 8px;
  border: 1px dashed #d0d5dd;
}
</style>
