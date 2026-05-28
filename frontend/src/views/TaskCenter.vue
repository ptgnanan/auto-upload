<template>
  <section class="page-shell task-center-page">
    <header class="page-header">
      <div class="page-header__main">
        <h1 class="page-title">任务中心</h1>
        <p class="page-subtitle">查看和管理发布任务</p>
      </div>
    </header>

    <div class="page-content">
      <section class="section-card queue-overview">
        <div class="section-card__body queue-overview__body">
          <div class="queue-item">
            <span class="queue-item__label">活跃 Worker</span>
            <strong class="queue-item__value queue-item__value--success">{{ queueStatus.active || 0 }}</strong>
          </div>
          <div class="queue-item">
            <span class="queue-item__label">等待中</span>
            <strong class="queue-item__value queue-item__value--info">{{ queueStatus.waiting || 0 }}</strong>
          </div>
        </div>
      </section>

      <div class="page-toolbar">
        <div class="page-toolbar__group page-toolbar__group--grow">
          <div class="status-filters">
            <button
              v-for="f in filterOptions"
              :key="f.value"
              :class="['filter-chip', { active: activeFilter === f.value }]"
              @click="activeFilter = f.value"
            >
              {{ f.label }}
            </button>
          </div>
        </div>

        <div class="page-toolbar__group">
          <el-input v-model="searchKeyword" placeholder="搜索标题或账号" clearable class="task-search" />
          <el-button @click="handleRefresh" :loading="loading">
            <el-icon v-if="!loading"><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>

      <section class="section-card">
        <div class="section-card__body">
          <div v-if="filteredTasks.length > 0" class="task-table-wrap">
            <el-table :data="paginatedTasks" style="width: 100%">
              <el-table-column label="任务ID" width="120">
                <template #default="scope">
                  <span class="task-id">{{ shortId(scope.row.id) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="platform" label="平台" width="110">
                <template #default="scope">
                  <span :class="['platform-tag', getPlatformClass(scope.row.platform)]">{{ scope.row.platform }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="account_name" label="账号" width="140">
                <template #default="scope">
                  <span class="primary-cell">{{ scope.row.account_name || '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="title" label="标题" min-width="220">
                <template #default="scope">
                  <span class="task-title" :title="scope.row.title">{{ scope.row.title || '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="110">
                <template #default="scope">
                  <span :class="['status-tag', getStatusClass(scope.row.status)]">{{ scope.row.status }}</span>
                </template>
              </el-table-column>
              <el-table-column label="创建时间" width="170">
                <template #default="scope">
                  <span class="muted-cell">{{ formatTime(scope.row.created_at) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="scope">
                  <div class="action-cell">
                    <button
                      v-if="scope.row.status === '排队中' || scope.row.status === '发布中'"
                      class="action-btn action-btn--danger"
                      @click="handleCancel(scope.row)"
                    >
                      取消
                    </button>
                    <button
                      v-else-if="scope.row.status === '失败'"
                      class="action-btn action-btn--primary"
                      @click="handleRetry(scope.row)"
                    >
                      重试
                    </button>
                    <button v-else class="action-btn action-btn--disabled" disabled>查看</button>
                  </div>
                </template>
              </el-table-column>
            </el-table>

            <div class="table-footer" v-if="totalPages > 1">
              <el-pagination
                v-model:current-page="currentPage"
                :page-size="pageSize"
                :total="filteredTasks.length"
                layout="prev, pager, next"
                background
                small
              />
            </div>
          </div>

          <div v-else class="empty-state">
            <div class="empty-state__inner">
              <el-icon class="empty-state__icon"><List /></el-icon>
              <strong class="empty-state__title">{{ searchKeyword || activeFilter !== 'all' ? '未找到匹配的任务' : '暂无任务数据' }}</strong>
              <p class="empty-state__text">任务创建后会在这里展示实时状态和操作入口。</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { Refresh, List } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { taskApi } from '@/api/v2'
import { platformCssMap } from '@/config/platforms'
import { resolveApiUrl } from '@/utils/api-runtime'

const tasks = ref([])
const loading = ref(false)
const activeFilter = ref('all')
const searchKeyword = ref('')
const queueStatus = ref({ active: 0, waiting: 0 })
const currentPage = ref(1)
const pageSize = 15

const filterOptions = [
  { label: '全部', value: 'all' },
  { label: '排队中', value: '排队中' },
  { label: '发布中', value: '发布中' },
  { label: '成功', value: '成功' },
  { label: '失败', value: '失败' },
]

const fetchTasks = async () => {
  loading.value = true
  try {
    const res = await taskApi.getTasks()
    if (res.code === 200) tasks.value = res.data || []
  } catch (error) {
    console.error('获取任务列表失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchQueueStatus = async () => {
  try {
    const res = await taskApi.getQueueStatus()
    if (res.code === 200) queueStatus.value = res.data || { active: 0, waiting: 0 }
  } catch (error) {
    console.error('获取队列状态失败:', error)
  }
}

let eventSource = null
const connectSSE = () => {
  eventSource = new EventSource(resolveApiUrl('/api/v2/tasks/stream'))
  eventSource.onmessage = event => {
    try {
      const data = JSON.parse(event.data)
      const index = tasks.value.findIndex(task => task.id === data.id)
      if (index !== -1) {
        tasks.value[index] = { ...tasks.value[index], ...data }
      } else {
        tasks.value.unshift(data)
      }
      fetchQueueStatus()
    } catch {}
  }
  eventSource.onerror = () => {
    eventSource?.close()
    eventSource = null
  }
}

const filteredTasks = computed(() => {
  let result = tasks.value
  if (activeFilter.value !== 'all') {
    result = result.filter(task => task.status === activeFilter.value)
  }
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(task =>
      (task.title || '').toLowerCase().includes(keyword) ||
      (task.account_name || '').toLowerCase().includes(keyword),
    )
  }
  return result
})

const totalPages = computed(() => Math.ceil(filteredTasks.value.length / pageSize))
const paginatedTasks = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredTasks.value.slice(start, start + pageSize)
})

const handleCancel = async task => {
  try {
    await taskApi.cancelTask(task.id)
    ElMessage.success('任务已取消')
    fetchTasks()
    fetchQueueStatus()
  } catch (error) {
    console.error('取消任务失败:', error)
    ElMessage.error('取消任务失败')
  }
}

const handleRetry = async task => {
  try {
    await taskApi.retryTask(task.id)
    ElMessage.success('任务已重新提交')
    fetchTasks()
    fetchQueueStatus()
  } catch (error) {
    console.error('重试任务失败:', error)
    ElMessage.error('重试任务失败')
  }
}

const handleRefresh = () => {
  fetchTasks()
  fetchQueueStatus()
}

const shortId = id => {
  if (!id) return '-'
  const str = String(id)
  return str.length > 8 ? str.slice(0, 8) : str
}

const getPlatformClass = platform => platformCssMap[platform] || ''

const getStatusClass = status => {
  const classMap = {
    排队中: 'pending',
    发布中: 'running',
    成功: 'success',
    失败: 'failed',
  }
  return classMap[status] || ''
}

const formatTime = time => {
  if (!time) return '-'
  try {
    const d = new Date(time)
    const pad = n => String(n).padStart(2, '0')
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
  } catch {
    return time
  }
}

onMounted(() => {
  fetchTasks()
  fetchQueueStatus()
  connectSSE()
})

onBeforeUnmount(() => {
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.task-center-page {
  .queue-overview {
    background: linear-gradient(135deg, rgba($brand-start, 0.08), rgba($info-color, 0.04));
    border-color: $border-active;
  }

  .queue-overview__body {
    display: flex;
    align-items: center;
    gap: $spacing-xl;
  }

  .queue-item {
    display: flex;
    flex-direction: column;
    gap: $spacing-xs;
  }

  .queue-item__label {
    font-size: 13px;
    color: $text-secondary;
  }

  .queue-item__value {
    font-size: 28px;
    line-height: 1;
    color: $text-primary;

    &--success {
      color: $success-color;
    }

    &--info {
      color: $info-color;
    }
  }

  .status-filters {
    display: flex;
    flex-wrap: wrap;
    gap: $spacing-sm;
  }

  .filter-chip {
    min-height: 34px;
    padding: 0 14px;
    border-radius: 999px;
    border: 1px solid $border;
    background: $bg-elevated;
    color: $text-secondary;
    font-size: 13px;
    font-weight: 600;

    &.active {
      border-color: $border-active;
      background: rgba($brand-start, 0.08);
      color: $brand-start;
    }
  }

  .task-search {
    width: 240px;
  }

  .task-table-wrap {
    display: flex;
    flex-direction: column;
    gap: $spacing-md;
  }

  .task-id {
    display: inline-flex;
    min-height: 24px;
    align-items: center;
    padding: 0 8px;
    border-radius: $radius-sm;
    background: $bg-surface;
    color: $text-secondary;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 12px;
  }

  .primary-cell,
  .task-title {
    color: $text-primary;
    font-weight: 500;
  }

  .task-title {
    display: -webkit-box;
    overflow: hidden;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
  }

  .muted-cell {
    color: $text-secondary;
  }

  .platform-tag,
  .status-tag {
    display: inline-flex;
    align-items: center;
    min-height: 24px;
    padding: 0 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
  }

  .platform-tag.douyin {
    color: $platform-douyin;
    background: $platform-douyin-bg;
  }

  .platform-tag.kuaishou {
    color: $platform-kuaishou;
    background: $platform-kuaishou-bg;
  }

  .platform-tag.channels {
    color: $platform-channels;
    background: $platform-channels-bg;
  }

  .platform-tag.xiaohongshu {
    color: $platform-xiaohongshu;
    background: $platform-xiaohongshu-bg;
  }

  .platform-tag.bilibili {
    color: $platform-bilibili;
    background: $platform-bilibili-bg;
  }

  .status-tag.pending {
    color: $info-color;
    background: rgba($info-color, 0.12);
  }

  .status-tag.running {
    color: $brand-start;
    background: rgba($brand-start, 0.12);
  }

  .status-tag.success {
    color: $success-color;
    background: rgba($success-color, 0.12);
  }

  .status-tag.failed {
    color: $danger-color;
    background: rgba($danger-color, 0.12);
  }

  .action-cell {
    display: flex;
    align-items: center;
    gap: $spacing-xs;
  }

  .action-btn {
    min-height: 30px;
    padding: 0 10px;
    border-radius: $radius-sm;
    font-size: 12px;
    font-weight: 600;

    &--primary {
      background: rgba($info-color, 0.1);
      color: $info-color;
    }

    &--danger {
      background: rgba($danger-color, 0.1);
      color: $danger-color;
    }

    &--disabled {
      background: $bg-surface;
      color: $text-muted;
      cursor: not-allowed;
    }
  }

  @media (max-width: 1024px) {
    .queue-overview__body {
      flex-direction: column;
      align-items: flex-start;
      gap: $spacing-md;
    }
  }
}
</style>
