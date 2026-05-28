<template>
  <section class="page-shell publish-history-page">
    <header class="page-header">
      <div class="page-header__main">
        <h1 class="page-title">发布历史</h1>
        <p class="page-subtitle">回顾所有发布记录</p>
      </div>
    </header>

    <div class="page-content">
      <section class="metric-grid publish-history-metrics">
        <article class="metric-card metric-card--accent">
          <div class="metric-card__mini">总发布数</div>
          <div class="metric-card__value">{{ stats.total }}</div>
        </article>
        <article class="metric-card">
          <div class="metric-card__mini">成功率</div>
          <div class="metric-card__value">{{ stats.successRate }}%</div>
        </article>
        <article class="metric-card">
          <div class="metric-card__mini">本月发布</div>
          <div class="metric-card__value">{{ stats.monthlyTotal }}</div>
        </article>
      </section>

      <div class="page-toolbar">
        <div class="page-toolbar__group">
          <el-select v-model="timeRange" placeholder="时间范围" @change="handleFilterChange">
            <el-option label="今天" value="today" />
            <el-option label="最近7天" value="7days" />
            <el-option label="最近30天" value="30days" />
            <el-option label="全部" value="all" />
          </el-select>

          <el-select v-model="platformFilter" placeholder="平台" @change="handleFilterChange">
            <el-option label="全部" value="all" />
            <el-option v-for="p in platformList" :key="p.key" :label="p.name" :value="p.key" />
          </el-select>

          <el-select v-model="statusFilter" placeholder="状态" @change="handleFilterChange">
            <el-option label="全部" value="all" />
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
          </el-select>
        </div>

        <div class="page-toolbar__group">
          <el-button @click="fetchHistory" :loading="loading" :icon="Refresh">刷新</el-button>
        </div>
      </div>

      <section class="section-card">
        <div class="section-card__body history-table-wrap">
          <el-table
            :data="history"
            style="width: 100%"
            v-loading="loading"
            row-key="id"
            :row-class-name="tableRowClassName"
            @row-click="row => toggleRowExpansion(row)"
            ref="historyTableRef"
          >
            <el-table-column type="expand">
              <template #default="{ row }">
                <div class="expand-content">
                  <div class="expand-row" v-if="row.description">
                    <span class="expand-label">描述</span>
                    <span class="expand-value">{{ row.description }}</span>
                  </div>
                  <div class="expand-row" v-if="row.tags && row.tags.length">
                    <span class="expand-label">标签</span>
                    <div class="expand-tags">
                      <span class="expand-tag" v-for="tag in row.tags" :key="tag">{{ tag }}</span>
                    </div>
                  </div>
                  <div class="expand-row" v-if="row.status === 'failed' && row.error_message">
                    <span class="expand-label">错误信息</span>
                    <span class="expand-value expand-value--error">{{ row.error_message }}</span>
                  </div>
                  <div class="expand-row" v-if="row.status === 'success' && row.publish_url">
                    <span class="expand-label">发布链接</span>
                    <a :href="row.publish_url" target="_blank" rel="noopener noreferrer" class="expand-link" @click.stop>
                      {{ row.publish_url }}
                    </a>
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="platform" label="平台" width="120">
              <template #default="{ row }">
                <span class="platform-tag" :class="getPlatformClass(row.platform)">{{ getPlatformLabel(row.platform) }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="account" label="账号" min-width="140">
              <template #default="{ row }">
                <span class="primary-cell">{{ row.account || row.account_name || '-' }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="title" label="标题" min-width="220">
              <template #default="{ row }">
                <span class="primary-cell">{{ row.title || '-' }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <span class="status-tag" :class="row.status === 'success' ? 'status-success' : 'status-failed'">
                  {{ row.status === 'success' ? '成功' : '失败' }}
                </span>
              </template>
            </el-table-column>

            <el-table-column prop="publish_time" label="发布时间" width="180">
              <template #default="{ row }">
                <span class="muted-cell">{{ row.publish_time || row.created_at || '-' }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="duration" label="耗时" width="100">
              <template #default="{ row }">
                <span class="muted-cell">{{ formatDuration(row.duration) }}</span>
              </template>
            </el-table-column>
          </el-table>

          <div v-if="!loading && history.length === 0" class="empty-state">
            <div class="empty-state__inner">
              <el-icon class="empty-state__icon"><Clock /></el-icon>
              <strong class="empty-state__title">暂无发布记录</strong>
              <p class="empty-state__text">完成发布后，历史记录会出现在这里。</p>
            </div>
          </div>

          <div class="table-footer" v-if="total > 0">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50]"
              :total="total"
              layout="total, sizes, prev, pager, next"
              @current-change="handlePageChange"
              @size-change="handleSizeChange"
              background
            />
          </div>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { Upload, CircleCheck, Calendar, Refresh, Clock } from '@element-plus/icons-vue'
import { historyApi, statsApi } from '@/api/v2'
import { platformList } from '@/config/platforms'

const history = ref([])
const stats = ref({ total: 0, successRate: 0, monthlyTotal: 0 })
const loading = ref(false)
const historyTableRef = ref(null)

const timeRange = ref('all')
const platformFilter = ref('all')
const statusFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const fetchHistory = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, pageSize: pageSize.value }
    if (timeRange.value !== 'all') params.timeRange = timeRange.value
    if (platformFilter.value !== 'all') params.platform = platformFilter.value
    if (statusFilter.value !== 'all') params.status = statusFilter.value
    const res = await historyApi.getHistory(params)
    if (res.code === 200) {
      const items = res.data?.items || res.data?.list
      history.value = Array.isArray(items) ? items : []
      total.value = res.data?.total || 0
    }
  } catch (error) {
    console.error('Failed to fetch history:', error)
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    const res = await statsApi.getStats()
    if (res.code === 200 && res.data) {
      const data = res.data
      stats.value = {
        total: data.total ?? data.tasks?.total ?? 0,
        successRate: data.successRate ?? data.tasks?.successRate ?? 0,
        monthlyTotal: data.monthlyTotal ?? 0,
      }
    }
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

const handlePageChange = page => {
  currentPage.value = page
  fetchHistory()
}

const handleSizeChange = size => {
  pageSize.value = size
  currentPage.value = 1
  fetchHistory()
}

const handleFilterChange = () => {
  currentPage.value = 1
  fetchHistory()
}

const toggleRowExpansion = row => {
  if (!historyTableRef.value) return
  historyTableRef.value.toggleRowExpansion(row)
}

const tableRowClassName = ({ row }) => {
  if (row.status === 'success') return 'row-success'
  if (row.status === 'failed') return 'row-failed'
  return ''
}

const platformMap = Object.fromEntries(platformList.map(p => [p.key, { label: p.name, class: `tag-${p.cssClass}` }]))

const getPlatformLabel = platform => platformMap[platform]?.label || platform || '-'
const getPlatformClass = platform => platformMap[platform]?.class || ''

const formatDuration = seconds => {
  if (!seconds && seconds !== 0) return '-'
  if (seconds < 60) return `${seconds}s`
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return secs > 0 ? `${mins}m ${secs}s` : `${mins}m`
}

onMounted(() => {
  fetchHistory()
  fetchStats()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.publish-history-page {
  .publish-history-metrics {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .metric-card__mini {
    font-size: 13px;
    color: $text-secondary;
  }

  .history-table-wrap {
    display: flex;
    flex-direction: column;
    gap: $spacing-md;
  }

  .primary-cell {
    color: $text-primary;
    font-weight: 500;
  }

  .muted-cell {
    color: $text-secondary;
  }

  .platform-tag,
  .status-tag,
  .expand-tag {
    display: inline-flex;
    align-items: center;
    min-height: 24px;
    padding: 0 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
  }

  .platform-tag.tag-douyin {
    color: $platform-douyin;
    background: $platform-douyin-bg;
  }

  .platform-tag.tag-kuaishou {
    color: $platform-kuaishou;
    background: $platform-kuaishou-bg;
  }

  .platform-tag.tag-channels {
    color: $platform-channels;
    background: $platform-channels-bg;
  }

  .platform-tag.tag-xiaohongshu {
    color: $platform-xiaohongshu;
    background: $platform-xiaohongshu-bg;
  }

  .platform-tag.tag-bilibili {
    color: $platform-bilibili;
    background: $platform-bilibili-bg;
  }

  .status-success {
    color: $success-color;
    background: rgba($success-color, 0.12);
  }

  .status-failed {
    color: $danger-color;
    background: rgba($danger-color, 0.12);
  }

  .expand-content {
    display: flex;
    flex-direction: column;
    gap: $spacing-sm;
    padding: $spacing-sm 0 $spacing-sm 28px;
  }

  .expand-row {
    display: flex;
    align-items: flex-start;
    gap: $spacing-sm;
    color: $text-secondary;
    line-height: 1.7;
  }

  .expand-label {
    min-width: 70px;
    color: $text-muted;
    font-size: 13px;
  }

  .expand-value {
    color: $text-secondary;
    word-break: break-word;
  }

  .expand-value--error {
    color: $danger-color;
  }

  .expand-tags {
    display: flex;
    flex-wrap: wrap;
    gap: $spacing-xs;
  }

  .expand-tag {
    color: $text-secondary;
    background: $bg-surface;
  }

  .expand-link {
    color: $brand-start;
    word-break: break-all;
  }

  @media (max-width: 1024px) {
    .publish-history-metrics {
      grid-template-columns: 1fr;
    }
  }
}
</style>
