<script setup>
import { ref, useTemplateRef } from 'vue'

const emit = defineEmits(['file-selected'])

const fileInput = useTemplateRef('fileInput')
const isDragging = ref(false)
const error = ref('')

function handleDragOver(e) {
  e.preventDefault()
  isDragging.value = true
}

function handleDragLeave() {
  isDragging.value = false
}

function handleDrop(e) {
  e.preventDefault()
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) processFile(file)
}

function handleFileChange(e) {
  const file = e.target.files[0]
  if (file) processFile(file)
}

function triggerFileInput() {
  fileInput.value?.click()
}

function processFile(file) {
  const validExts = ['.xlsx', '.xls', '.csv']
  const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
  if (!validExts.includes(ext)) {
    error.value = '请上传 Excel 文件 (.xlsx / .xls / .csv)'
    return
  }

  error.value = ''
  emit('file-selected', file)
  if (fileInput.value) fileInput.value.value = ''
}
</script>

<template>
  <div
    class="uploader"
    :class="{ dragging: isDragging }"
    @dragover="handleDragOver"
    @dragleave="handleDragLeave"
    @drop="handleDrop"
    @click="triggerFileInput"
  >
    <input
      ref="fileInput"
      type="file"
      accept=".xlsx,.xls,.csv"
      class="file-input"
      @change="handleFileChange"
    />

    <div class="uploader-content">
      <div class="upload-icon">📁</div>
      <p class="upload-text">拖拽 Excel 文件到此处，或点击选择文件</p>
      <p class="upload-hint">支持 .xlsx / .xls / .csv 格式</p>
    </div>

    <p v-if="error" class="error-text">{{ error }}</p>
  </div>
</template>

<style scoped>
.uploader {
  border: 2px dashed #d0d5dd;
  border-radius: 12px;
  padding: 48px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s ease;
  background: #fafbfc;
  position: relative;
}

.uploader:hover {
  border-color: #4096ff;
  background: #f0f5ff;
}

.uploader.dragging {
  border-color: #4096ff;
  background: #e6f4ff;
  transform: scale(1.01);
}

.file-input {
  display: none;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.upload-text {
  font-size: 16px;
  color: #344054;
  margin: 0 0 8px;
}

.upload-hint {
  font-size: 13px;
  color: #98a2b3;
  margin: 0;
}

.error-text {
  color: #f5222d;
  font-size: 13px;
  margin-top: 12px;
}
</style>
