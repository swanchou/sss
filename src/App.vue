<script setup>
import { ref } from 'vue'
import ResultTable from './components/ResultTable.vue'

const showModal = ref(true)
const error = ref('')
const isLoading = ref(false)
const resultData = ref(null)

const selectedFile = ref(null)
const targetCol = ref('')
const displayCol = ref('')
const fileName = ref('')

function handleFileChange(e) {
  const file = e.target.files[0]
  if (file) {
    selectedFile.value = file
    fileName.value = file.name
  }
}

function handleDrop(e) {
  e.preventDefault()
  const file = e.dataTransfer.files[0]
  if (file) {
    selectedFile.value = file
    fileName.value = file.name
  }
}

function handleDragOver(e) {
  e.preventDefault()
}

async function handleSubmit() {
  error.value = ''
  if (!selectedFile.value) {
    error.value = '请上传 Excel 文件'
    return
  }
  if (!targetCol.value.trim()) {
    error.value = '请填写识别目标列号'
    return
  }
  if (!displayCol.value.trim()) {
    error.value = '请填写返回数据列号'
    return
  }

  isLoading.value = true
  resultData.value = null

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('target_col', targetCol.value.trim())
    formData.append('display_col', displayCol.value.trim())

    const resp = await fetch('/api/extract', {
      method: 'POST',
      body: formData,
    })

    const json = await resp.json()

    if (!resp.ok) {
      throw new Error(json.error || '服务端返回错误')
    }

    resultData.value = json
    showModal.value = false
  } catch (err) {
    error.value = err.message
  } finally {
    isLoading.value = false
  }
}

function handleReset() {
  resultData.value = null
  selectedFile.value = null
  fileName.value = ''
  targetCol.value = ''
  displayCol.value = ''
  error.value = ''
  showModal.value = true
}
</script>

<template>
  <div class="app">
    <header class="header">
      <div class="header-inner">
        <h1 class="title">📱 Excel 手机号识别工具</h1>
        <p class="subtitle">上传 Excel，指定识别列，自动提取手机号</p>
      </div>
    </header>

    <main class="main">
      <div class="container">
        <div v-if="isLoading" class="loading-overlay">
          <div class="spinner"></div>
          <p>正在识别手机号...</p>
        </div>

        <template v-if="resultData && !showModal">
          <div class="info-bar">
            <span>📄 文件: <strong>{{ resultData.fileName }}</strong></span>
            <span>🎯 识别列: <strong>{{ resultData.targetCol }}</strong></span>
            <span>📋 返回列: <strong>{{ resultData.displayCol }}</strong></span>
            <span>📞 找到 <strong>{{ resultData.totalPhones }}</strong> 个手机号</span>
            <button class="btn-reset" @click="handleReset">🔄 重新识别</button>
          </div>

          <ResultTable :data="resultData" />
        </template>
      </div>
    </main>

    <div v-if="showModal && !isLoading" class="modal-overlay">
      <div class="modal" @drop="handleDrop" @dragover="handleDragOver">
        <h2 class="modal-title">上传 Excel 并配置识别参数</h2>

        <p v-if="error" class="modal-error">{{ error }}</p>

        <div class="form-group">
          <label class="form-label">① 上传 Excel 文件</label>
          <div class="upload-area" @click="$refs.fileInput.click()">
            <input ref="fileInput" type="file" accept=".xlsx,.xls,.csv" class="file-input" @change="handleFileChange" />
            <div v-if="!fileName" class="upload-placeholder">
              <span class="upload-icon">📁</span>
              <span>点击或拖拽文件到此处</span>
            </div>
            <div v-else class="upload-file">
              <span>📎 {{ fileName }}</span>
              <button class="btn-clear" @click.stop="selectedFile = null; fileName = ''">×</button>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">② 识别目标列号（从此列提取手机号）</label>
          <input v-model="targetCol" type="text" class="form-input" placeholder="例如：B" />
        </div>

        <div class="form-group">
          <label class="form-label">③ 返回数据列号（展示此列的内容）</label>
          <input v-model="displayCol" type="text" class="form-input" placeholder="例如：A" />
        </div>

        <button class="btn-submit" @click="handleSubmit">开始识别</button>
      </div>
    </div>

    <footer class="footer">
      <p>Excel 手机号识别工具 · 自动从文本中提取中国大陆手机号</p>
    </footer>
  </div>
</template>

<style>
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial,
    sans-serif;
  background: #f5f5f5;
  color: #1d2939;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}
</style>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: linear-gradient(135deg, #4096ff 0%, #1677ff 100%);
  color: #fff;
  padding: 32px 0;
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 4px;
}

.subtitle {
  font-size: 14px;
  opacity: 0.85;
  margin: 0;
}

.main {
  flex: 1;
  padding: 32px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #4096ff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.info-bar {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 16px;
  font-size: 14px;
  color: #344054;
  flex-wrap: wrap;
}

.btn-reset {
  margin-left: auto;
  padding: 6px 16px;
  border: 1px solid #d0d5dd;
  border-radius: 8px;
  background: #fff;
  color: #344054;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-reset:hover {
  border-color: #4096ff;
  color: #4096ff;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  width: 480px;
  max-width: 90vw;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.modal-title {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 24px;
  color: #1d2939;
}

.modal-error {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  color: #f5222d;
  padding: 10px 14px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 13px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #344054;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #d0d5dd;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.form-input:focus {
  border-color: #4096ff;
}

.upload-area {
  border: 2px dashed #d0d5dd;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #fafbfc;
}

.upload-area:hover {
  border-color: #4096ff;
  background: #f0f5ff;
}

.file-input {
  display: none;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #667085;
  font-size: 14px;
}

.upload-icon {
  font-size: 32px;
}

.upload-file {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 14px;
  color: #344054;
}

.btn-clear {
  background: none;
  border: none;
  font-size: 20px;
  color: #98a2b3;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
}

.btn-clear:hover {
  color: #f5222d;
}

.btn-submit {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #4096ff 0%, #1677ff 100%);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-submit:hover {
  opacity: 0.9;
}

.footer {
  text-align: center;
  padding: 20px;
  color: #98a2b3;
  font-size: 13px;
}
</style>
