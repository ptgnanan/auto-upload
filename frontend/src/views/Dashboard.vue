<template>
  <section class="page-shell dashboard">
    <header class="page-header">
      <div class="page-header__main">
        <h1 class="page-title">仪表盘</h1>
        <p class="page-subtitle">数据概览与快捷操作</p>
      </div>
    </header>

    <section v-if="savedDraftInfo" class="section-card draft-banner">
      <div class="section-card__body draft-banner__body">
        <div class="draft-banner__copy">
          <strong class="draft-banner__title">检测到未完成草稿</strong>
          <div class="draft-banner__meta">
            <span>上次保存：{{ savedDraftInfo.savedAtText }}</span>
            <span v-if="savedDraftInfo.accountCount > 0">已选账号：{{ savedDraftInfo.accountCount }} 个</span>
          </div>
        </div>
        <button class="draft-banner__action" @click="openSavedDraft">继续编辑草稿</button>
      </div>
    </section>

    <div class="page-content">
      <section class="metric-grid">
        <article class="metric-card metric-card--accent">
          <div class="metric-card__head">
            <div class="metric-card__icon metric-card__icon--primary">
              <el-icon><User /></el-icon>
            </div>
            <button class="metric-card__button" @click="handleBatchCheck" :disabled="isChecking">
              <el-icon v-if="isChecking" class="is-loading"><Loading /></el-icon>
              <template v-else>
                <el-icon><Refresh /></el-icon>
                批量检查
              </template>
            </button>
          </div>
          <div class="metric-card__value">{{ accountStats.total }}</div>
          <div class="metric-card__label">账号总数</div>
          <div class="metric-card__meta">
            <span>正常 {{ accountStats.normal }}</span>
            <span class="metric-card__divider"></span>
            <span>异常 {{ accountStats.abnormal }}</span>
          </div>
        </article>

        <article class="metric-card">
          <div class="metric-card__head">
            <div class="metric-card__icon metric-card__icon--info">
              <el-icon><Platform /></el-icon>
            </div>
          </div>
          <div class="metric-card__value">{{ platformStats.total }}</div>
          <div class="metric-card__label">已接入平台</div>
          <div class="metric-card__tags">
            <span v-for="p in platformList" :key="p.id" :class="['platform-pill', p.cssClass]">
              {{ p.name }} {{ platformStats[p.cssClass] || 0 }}
            </span>
          </div>
        </article>

        <article class="metric-card">
          <div class="metric-card__head">
            <div class="metric-card__icon metric-card__icon--teal">
              <el-icon><Document /></el-icon>
            </div>
          </div>
          <div class="metric-card__value">{{ contentStats.total }}</div>
          <div class="metric-card__label">素材总数</div>
          <div class="metric-card__meta">
            <span>视频 {{ contentStats.videos }}</span>
            <span class="metric-card__divider"></span>
            <span>图片 {{ contentStats.images }}</span>
            <span class="metric-card__divider"></span>
            <span>其他 {{ contentStats.others }}</span>
          </div>
        </article>

        <article class="metric-card">
          <div class="metric-card__head">
            <div class="metric-card__icon metric-card__icon--success">
              <el-icon><Upload /></el-icon>
            </div>
          </div>
          <div class="metric-card__value">-</div>
          <div class="metric-card__label">今日发布</div>
          <div class="metric-card__meta">
            <span>成功率 -</span>
          </div>
        </article>
      </section>

      <section class="action-grid">
        <button class="action-card" @click="openPublishCenter">
          <span class="action-card__icon action-card__icon--primary"><el-icon><Upload /></el-icon></span>
          <strong class="action-card__title">快速发布</strong>
          <span class="action-card__desc">新建发布内容</span>
        </button>
        <button v-if="savedDraftInfo" class="action-card" @click="openSavedDraft">
          <span class="action-card__icon action-card__icon--warning"><el-icon><Timer /></el-icon></span>
          <strong class="action-card__title">继续草稿</strong>
          <span class="action-card__desc">恢复上次保存的发布草稿</span>
        </button>
        <button class="action-card" @click="navigateTo('/material-management')">
          <span class="action-card__icon action-card__icon--info"><el-icon><Document /></el-icon></span>
          <strong class="action-card__title">上传素材</strong>
          <span class="action-card__desc">上传和管理视频素材</span>
        </button>
        <button class="action-card" @click="navigateTo('/settings')">
          <span class="action-card__icon action-card__icon--teal"><el-icon><Setting /></el-icon></span>
          <strong class="action-card__title">系统设置</strong>
          <span class="action-card__desc">配置系统参数和选项</span>
        </button>
        <button class="action-card" @click="navigateTo('/account-management')">
          <span class="action-card__icon action-card__icon--success"><el-icon><UserFilled /></el-icon></span>
          <strong class="action-card__title">账号管理</strong>
          <span class="action-card__desc">管理所有平台账号</span>
        </button>
      </section>

      <section class="section-card">
        <div class="section-card__header dashboard-section__header">
          <div>
            <h2 class="section-title">最近素材</h2>
            <p class="section-subtitle">查看最近上传的媒体文件</p>
          </div>
          <button class="dashboard-link" @click="navigateTo('/material-management')">查看全部</button>
        </div>
        <div class="section-card__body">
          <el-table :data="recentMaterials" style="width: 100%" v-loading="loading">
            <el-table-column prop="filename" label="文件名" min-width="260">
              <template #default="scope">
                <span class="filename-cell">{{ scope.row.filename }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="filesize" label="大小" width="120">
              <template #default="scope">
                <span class="meta-cell">{{ scope.row.filesize }} MB</span>
              </template>
            </el-table-column>
            <el-table-column label="类型" width="100">
              <template #default="scope">
                <span
                  class="type-tag"
                  :class="{
                    'type-video': getFileType(scope.row.filename) === '视频',
                    'type-image': getFileType(scope.row.filename) === '图片',
                    'type-other': getFileType(scope.row.filename) === '其他'
                  }"
                >
                  {{ getFileType(scope.row.filename) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="upload_time" label="上传时间" width="200">
              <template #default="scope">
                <span class="meta-cell">{{ scope.row.upload_time }}</span>
              </template>
            </el-table-column>
          </el-table>

          <div v-if="!loading && recentMaterials.length === 0" class="empty-state">
            <div class="empty-state__inner">
              <strong class="empty-state__title">暂无素材数据</strong>
              <p class="empty-state__text">上传素材后会在这里显示最近记录。</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  User,
  UserFilled,
  Platform,
  Document,
  Upload,
  Timer,
  Loading,
  Refresh,
  Setting,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { accountApi } from '@/api/account'
import { materialApi } from '@/api/material'
import { useAccountStore } from '@/stores/account'
import { useAppStore } from '@/stores/app'
import { platformList } from '@/config/platforms'

const router = useRouter()
const accountStore = useAccountStore()
const appStore = useAppStore()
const loading = ref(false)
const isChecking = ref(false)
const savedDraftInfo = ref(null)

function formatDraftSavedAt(value) {
  if (!value) return '未知'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '未知'
  return date.toLocaleString('zh-CN', { hour12: false })
}

function syncSavedDraftInfo() {
  const rawDraft = localStorage.getItem('publishDraft')
  if (!rawDraft) {
    savedDraftInfo.value = null
    return
  }

  try {
    const draftData = JSON.parse(rawDraft)
    savedDraftInfo.value = {
      savedAtText: formatDraftSavedAt(draftData.savedAt),
      accountCount: Array.isArray(draftData.publishAccountIds) ? draftData.publishAccountIds.length : 0,
    }
  } catch (error) {
    console.error('读取草稿信息失败:', error)
    savedDraftInfo.value = null
  }
}

const handleBatchCheck = async () => {
  if (isChecking.value) return
  isChecking.value = true
  try {
    const res = await accountApi.getValidAccounts()
    if (res.code === 200 && res.data) {
      accountStore.setAccounts(res.data)
      ElMessage.success('账号检查完成')
    } else {
      ElMessage.error(res.msg || '检查失败')
    }
  } catch (error) {
    console.error('批量检查失败:', error)
    ElMessage.error('批量检查失败')
  } finally {
    isChecking.value = false
  }
}

const accountStats = computed(() => {
  const accounts = accountStore.accounts
  const normal = accounts.filter(account => account.status === '正常').length
  const abnormal = accounts.filter(account => account.status !== '正常' && account.status !== '验证中').length
  return {
    total: accounts.length,
    normal,
    abnormal,
  }
})

const platformStats = computed(() => {
  const counts = {}
  platformList.forEach(platform => {
    counts[platform.cssClass] = accountStore.accounts.filter(account => account.platform === platform.name).length
  })
  return {
    total: platformList.filter(platform => counts[platform.cssClass] > 0).length,
    ...counts,
  }
})

const videoExtensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv']
const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']

const contentStats = computed(() => {
  const videos = appStore.materials.filter(material => videoExtensions.some(ext => material.filename.toLowerCase().endsWith(ext))).length
  const images = appStore.materials.filter(material => imageExtensions.some(ext => material.filename.toLowerCase().endsWith(ext))).length
  return {
    total: appStore.materials.length,
    videos,
    images,
    others: appStore.materials.length - videos - images,
  }
})

const recentMaterials = computed(() =>
  [...appStore.materials]
    .sort((a, b) => new Date(b.upload_time) - new Date(a.upload_time))
    .slice(0, 5),
)

const getFileType = filename => {
  if (videoExtensions.some(ext => filename.toLowerCase().endsWith(ext))) return '视频'
  if (imageExtensions.some(ext => filename.toLowerCase().endsWith(ext))) return '图片'
  return '其他'
}

function openPublishCenter() {
  router.push('/publish-center')
}

function openSavedDraft() {
  router.push({ path: '/publish-center', query: { draft: 'latest' } })
}

const navigateTo = path => {
  router.push(path)
}

const fetchDashboardData = async () => {
  loading.value = true
  try {
    const [accountRes, materialRes] = await Promise.allSettled([
      accountApi.getAccounts(),
      materialApi.getAllMaterials(),
    ])

    if (accountRes.status === 'fulfilled' && accountRes.value.code === 200) {
      accountStore.setAccounts(accountRes.value.data)
    }
    if (materialRes.status === 'fulfilled' && materialRes.value.code === 200) {
      appStore.setMaterials(materialRes.value.data)
    }
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  syncSavedDraftInfo()
  fetchDashboardData()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.dashboard {
  .draft-banner {
    background: linear-gradient(135deg, rgba($brand-start, 0.08), rgba($brand-end, 0.04));
    border-color: $border-active;
  }

  .draft-banner__body {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: $spacing-lg;
  }

  .draft-banner__copy {
    display: flex;
    flex-direction: column;
    gap: $spacing-xs;
  }

  .draft-banner__title {
    font-size: 16px;
    color: $text-primary;
  }

  .draft-banner__meta {
    display: flex;
    flex-wrap: wrap;
    gap: $spacing-md;
    font-size: 13px;
    color: $text-secondary;
  }

  .draft-banner__action {
    min-height: var(--button-height);
    padding: 0 $spacing-lg;
    border-radius: $radius-base;
    background: $gradient-brand;
    color: var(--color-text-inverse);
    font-weight: 600;
  }

  .metric-card {
    display: flex;
    flex-direction: column;
    gap: $spacing-md;
  }

  .metric-card__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: $spacing-sm;
  }

  .metric-card__icon {
    width: 48px;
    height: 48px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: $radius-base;

    .el-icon {
      font-size: 22px;
    }

    &--primary {
      background: rgba($brand-start, 0.12);
      color: $brand-start;
    }

    &--info {
      background: rgba($info-color, 0.12);
      color: $info-color;
    }

    &--teal {
      background: rgba($brand-end, 0.16);
      color: $brand-start;
    }

    &--success {
      background: rgba($success-color, 0.12);
      color: $success-color;
    }
  }

  .metric-card__button {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    min-height: 32px;
    padding: 0 12px;
    border-radius: $radius-sm;
    background: rgba($success-color, 0.1);
    color: $success-color;
    border: 1px solid rgba($success-color, 0.24);
    font-size: 12px;
    font-weight: 600;

    &:disabled {
      opacity: 0.55;
      cursor: not-allowed;
    }
  }

  .metric-card__value {
    font-size: 32px;
    line-height: 1;
    font-weight: 700;
    color: $text-primary;
  }

  .metric-card__label {
    font-size: 13px;
    color: $text-secondary;
  }

  .metric-card__meta,
  .metric-card__tags {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    padding-top: $spacing-sm;
    border-top: 1px solid $border-light;
    color: $text-secondary;
    font-size: 13px;
  }

  .metric-card__divider {
    width: 1px;
    height: 12px;
    background: $border;
  }

  .platform-pill,
  .type-tag {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 24px;
    padding: 0 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
  }

  .platform-pill.douyin {
    color: $platform-douyin;
    background: $platform-douyin-bg;
  }

  .platform-pill.kuaishou {
    color: $platform-kuaishou;
    background: $platform-kuaishou-bg;
  }

  .platform-pill.channels {
    color: $platform-channels;
    background: $platform-channels-bg;
  }

  .platform-pill.xiaohongshu {
    color: $platform-xiaohongshu;
    background: $platform-xiaohongshu-bg;
  }

  .platform-pill.bilibili {
    color: $platform-bilibili;
    background: $platform-bilibili-bg;
  }

  .platform-pill.baijiahao {
    color: $platform-baijiahao;
    background: $platform-baijiahao-bg;
  }

  .platform-pill.tiktok {
    color: $platform-tiktok;
    background: $platform-tiktok-bg;
  }

  .platform-pill.youtube {
    color: $platform-youtube;
    background: $platform-youtube-bg;
  }

  .action-card {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: $spacing-sm;
    text-align: left;
  }

  .action-card__icon {
    width: 48px;
    height: 48px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: $radius-base;
    color: var(--color-text-inverse);

    .el-icon {
      font-size: 22px;
    }

    &--primary {
      background: $gradient-brand;
    }

    &--warning {
      background: linear-gradient(135deg, rgba($warning-color, 0.92), rgba($brand-start, 0.88));
    }

    &--info {
      background: $gradient-info;
    }

    &--teal {
      background: $gradient-cyan;
    }

    &--success {
      background: $gradient-success;
    }
  }

  .action-card__title {
    font-size: 15px;
    color: $text-primary;
  }

  .action-card__desc {
    font-size: 13px;
    color: $text-secondary;
    line-height: 1.6;
  }

  .dashboard-section__header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: $spacing-md;
  }

  .dashboard-link {
    color: $brand-start;
    font-size: 13px;
    font-weight: 600;
  }

  .filename-cell {
    color: $text-primary;
    font-weight: 500;
  }

  .meta-cell {
    color: $text-secondary;
  }

  .type-tag.type-video {
    color: $success-color;
    background: rgba($success-color, 0.12);
  }

  .type-tag.type-image {
    color: $warning-color;
    background: rgba($warning-color, 0.12);
  }

  .type-tag.type-other {
    color: $text-secondary;
    background: $bg-surface;
  }

  @media (max-width: 1024px) {
    .draft-banner__body {
      flex-direction: column;
      align-items: flex-start;
    }
  }
}
</style>
