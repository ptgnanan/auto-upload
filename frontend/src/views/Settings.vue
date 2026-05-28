<template>
  <section class="page-shell settings-page" v-loading="loading">
    <header class="page-header">
      <div class="page-header__main">
        <h1 class="page-title">系统设置</h1>
        <p class="page-subtitle">配置应用偏好与运行模式</p>
      </div>
    </header>

    <div class="page-content">
      <section class="section-card">
        <div class="section-card__header">
          <h2 class="section-title">网络代理</h2>
          <p class="section-subtitle">用于海外平台浏览器连接，国内平台无需代理。</p>
        </div>
        <div class="section-card__body">
          <div class="setting-row">
            <div class="setting-copy">
              <strong class="setting-label">HTTP 代理地址</strong>
              <span class="setting-desc">示例：`http://127.0.0.1:7897`</span>
            </div>
            <div class="setting-control">
              <el-input v-model="settings.proxyUrl" placeholder="http://127.0.0.1:7897" clearable />
            </div>
          </div>
          <div class="platform-chip-row">
            <span class="platform-chip" v-for="p in overseasPlatforms" :key="p.key">
              <img :src="p.logo" :alt="p.name" class="platform-chip__logo" />
              {{ p.name }}
            </span>
          </div>
        </div>
      </section>

      <section class="section-card">
        <div class="section-card__header">
          <h2 class="section-title">发布引擎</h2>
          <p class="section-subtitle">新版引擎使用抽象化平台架构，切换后立即生效。</p>
        </div>
        <div class="section-card__body">
          <el-radio-group v-model="settings.engineMode" class="engine-mode-group">
            <el-radio value="old">旧版引擎 (legacy)</el-radio>
            <el-radio value="new">新版引擎 (v2)</el-radio>
          </el-radio-group>
        </div>
      </section>

      <section class="section-card">
        <div class="section-card__header">
          <h2 class="section-title">技术栈</h2>
          <p class="section-subtitle">当前项目前后端与浏览器运行时版本。</p>
        </div>
        <div class="section-card__body tech-grid">
          <div class="tech-section">
            <strong class="tech-section__title">前端</strong>
            <div class="tech-item" v-for="item in frontendStack" :key="item.name">
              <span>{{ item.name }}</span>
              <code>{{ item.version }}</code>
            </div>
          </div>
          <div class="tech-section">
            <strong class="tech-section__title">后端</strong>
            <div class="tech-item" v-for="item in backendStack" :key="item.name">
              <span>{{ item.name }}</span>
              <code>{{ item.version }}</code>
            </div>
          </div>
          <div class="tech-section">
            <strong class="tech-section__title">浏览器引擎</strong>
            <div class="tech-item" v-for="item in browserStack" :key="item.name">
              <span>{{ item.name }}</span>
              <code>{{ item.version }}</code>
            </div>
          </div>
        </div>
      </section>

      <div class="settings-actions">
        <el-button type="primary" :loading="saving" @click="handleSave">
          {{ saving ? '保存中...' : '保存设置' }}
        </el-button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { settingsApi } from '@/api/v2'
import { platformList } from '@/config/platforms'

const loading = ref(false)
const saving = ref(false)

const settings = reactive({
  proxyUrl: '',
  engineMode: 'old',
})

const overseasPlatforms = platformList.filter(platform => ['youtube', 'tiktok'].includes(platform.key))

const frontendStack = [
  { name: 'Vue', version: '3.5.x' },
  { name: 'Element Plus', version: '2.9.x' },
  { name: 'Vite', version: '6.3.x' },
  { name: 'Pinia', version: '3.0.x' },
  { name: 'Axios', version: '1.9.x' },
]

const backendStack = [
  { name: 'Python', version: '3.14' },
  { name: 'Flask', version: '3.1.x' },
  { name: 'SQLite', version: '3.x' },
]

const browserStack = [
  { name: 'Patchright', version: '1.58.x' },
  { name: 'Chromium', version: 'latest' },
]

const fetchSettings = async () => {
  loading.value = true
  try {
    const response = await settingsApi.getSettings()
    if (response.code === 200 && response.data) {
      if (response.data.proxyUrl !== undefined) settings.proxyUrl = response.data.proxyUrl
      if (response.data.engineMode !== undefined) settings.engineMode = response.data.engineMode
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSave = async () => {
  saving.value = true
  try {
    const response = await settingsApi.updateSettings({
      proxyUrl: settings.proxyUrl,
      engineMode: settings.engineMode,
    })
    if (response.code === 200) {
      ElMessage.success('设置已保存')
    } else {
      ElMessage.error(response.msg || '保存失败')
    }
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchSettings()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.settings-page {
  .setting-row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(280px, 360px);
    gap: $spacing-lg;
    align-items: center;
  }

  .setting-copy {
    display: flex;
    flex-direction: column;
    gap: $spacing-xs;
  }

  .setting-label {
    font-size: 15px;
    color: $text-primary;
  }

  .setting-desc {
    font-size: 13px;
    color: $text-secondary;
    line-height: 1.6;
  }

  .platform-chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: $spacing-sm;
    margin-top: $spacing-md;
  }

  .platform-chip {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    min-height: 30px;
    padding: 0 12px;
    border-radius: 999px;
    border: 1px solid $border;
    background: $bg-surface;
    color: $text-secondary;
    font-size: 12px;
    font-weight: 600;
  }

  .platform-chip__logo {
    width: 16px;
    height: 16px;
    object-fit: contain;
  }

  .engine-mode-group {
    display: flex;
    flex-direction: column;
    gap: $spacing-sm;
    align-items: flex-start;
  }

  .tech-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: $spacing-lg;
  }

  .tech-section {
    display: flex;
    flex-direction: column;
    gap: $spacing-sm;
  }

  .tech-section__title {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: $text-muted;
  }

  .tech-item {
    display: flex;
    justify-content: space-between;
    gap: $spacing-md;
    padding: 10px 0;
    border-bottom: 1px solid $border-light;
    color: $text-primary;
    font-size: 14px;

    code {
      color: $text-secondary;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 13px;
    }
  }

  .settings-actions {
    display: flex;
    justify-content: flex-end;
  }

  @media (max-width: 1024px) {
    .setting-row,
    .tech-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
