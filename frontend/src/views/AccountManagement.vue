<template>
  <section class="page-shell account-management">
    <header class="page-header">
      <div class="page-header__main">
        <h1 class="page-title">账号管理</h1>
        <p class="page-subtitle">管理所有平台账号</p>
      </div>
      <div class="page-header__actions">
        <el-button type="primary" @click="handleAddAccount">
          <el-icon><Plus /></el-icon>
          添加账号
        </el-button>
      </div>
    </header>

    <div class="page-content">
      <section class="section-card">
        <div class="section-card__body filter-panel">
          <div class="platform-tabs">
            <button
              v-for="tab in filterOptions"
              :key="tab.value"
              :class="['tab-item', { active: activeTab === tab.value }]"
              @click="activeTab = tab.value"
            >
              <span>{{ tab.label }}</span>
              <span v-if="tab.count" class="tab-count">{{ tab.count }}</span>
            </button>
          </div>

          <div class="page-toolbar">
            <div class="page-toolbar__group page-toolbar__group--grow">
              <el-input v-model="searchKeyword" placeholder="搜索名称或账号..." clearable class="search-input" />
            </div>
            <div class="page-toolbar__group">
              <el-button @click="fetchAccountsQuick" :loading="appStore.isAccountRefreshing">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
              <el-button @click="fetchAccounts" :loading="appStore.isAccountRefreshing">
                <el-icon v-if="!appStore.isAccountRefreshing"><Loading /></el-icon>
                批量检查
              </el-button>
            </div>
          </div>
        </div>
      </section>

      <section v-if="filteredAccounts.length > 0" class="account-grid">
        <article
          v-for="account in filteredAccounts"
          :key="account.id"
          :class="['account-card', `platform-${getPlatformClass(account.platform)}`]"
        >
          <div class="account-card__main">
            <el-avatar :src="account.avatar || getDefaultAvatar(account.name)" :size="48" class="user-avatar" />
            <div class="account-card__copy">
              <strong class="account-name">{{ account.name }}</strong>
              <div class="account-meta">
                <span class="platform-name">{{ account.platform }}</span>
                <span :class="['status-badge', getStatusClass(account.status)]">
                  <span class="status-dot"></span>
                  {{ account.status }}
                </span>
              </div>
            </div>
            <div class="platform-logo">
              <img v-if="getPlatformLogo(account.platform)" :src="getPlatformLogo(account.platform)" :alt="account.platform" class="platform-icon" />
              <span v-else class="platform-letter" :style="{ color: getPlatformColor(account.platform) }">
                {{ getPlatformLetter(account.platform) }}
              </span>
            </div>
          </div>

          <div class="account-card__actions">
            <button class="action-btn action-btn--success" @click="handleCheckAccount(account)" :disabled="checkingIds.has(account.id)">
              <span class="action-btn__icon">
                <el-icon v-if="checkingIds.has(account.id)" class="is-loading"><Loading /></el-icon>
                <el-icon v-else><Check /></el-icon>
              </span>
              <span class="action-btn__label">检查</span>
            </button>
            <button class="action-btn action-btn--info" @click="handleSyncProfile(account)" :disabled="syncingIds.has(account.id)">
              <span class="action-btn__icon">
                <el-icon v-if="syncingIds.has(account.id)" class="is-loading"><Loading /></el-icon>
                <el-icon v-else><Refresh /></el-icon>
              </span>
              <span class="action-btn__label">同步</span>
            </button>
            <button class="action-btn action-btn--teal" @click="handleOpenCreatorCenter(account)">
              <span class="action-btn__icon">
                <el-icon><Link /></el-icon>
              </span>
              <span class="action-btn__label">创作中心</span>
            </button>
            <button class="action-btn action-btn--danger" @click="handleDelete(account)">
              <span class="action-btn__icon">
                <el-icon><Delete /></el-icon>
              </span>
              <span class="action-btn__label">删除</span>
            </button>
          </div>
        </article>
      </section>

      <div v-else class="empty-state">
        <div class="empty-state__inner">
          <el-icon class="empty-state__icon"><Folder /></el-icon>
          <strong class="empty-state__title">{{ searchKeyword ? '未找到匹配账号' : '暂无账号数据' }}</strong>
          <p class="empty-state__text">{{ searchKeyword ? '请尝试其他关键词搜索。' : '点击上方“添加账号”开始绑定你的第一个平台账号。' }}</p>
          <el-button v-if="!searchKeyword" type="primary" @click="handleAddAccount">
            <el-icon><Plus /></el-icon>
            添加账号
          </el-button>
        </div>
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '添加账号' : '编辑账号'"
      width="560px"
      :close-on-click-modal="false"
      :close-on-press-escape="!sseConnecting"
      :show-close="!sseConnecting"
    >
      <el-form :model="accountForm" label-width="80px" :rules="rules" ref="accountFormRef">
        <el-form-item label="平台" prop="platform">
          <el-select
            v-model="accountForm.platform"
            placeholder="请选择平台"
            :disabled="dialogType === 'edit' || sseConnecting"
            style="width: 100%"
            @change="onPlatformSelect"
          >
            <el-option v-for="p in platformOptions" :key="p.value" :label="p.label" :value="p.label" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="dialogType === 'edit'" label="名称" prop="name">
          <el-input v-model="accountForm.name" placeholder="扫码后自动同步" disabled />
        </el-form-item>

        <div v-if="sseConnecting" class="qrcode-container">
          <div v-if="qrCodeData && !loginStatus" class="qrcode-wrapper">
            <p class="qrcode-tip">请使用对应平台 APP 扫描二维码登录</p>
            <img :src="qrCodeData" alt="登录二维码" class="qrcode-image" />
          </div>
          <div v-else-if="!qrCodeData && !loginStatus" class="loading-wrapper">
            <el-icon class="is-loading"><Refresh /></el-icon>
            <span>请求中...</span>
          </div>
          <div v-else-if="loginStatus === '200'" class="status-wrapper success">
            <el-icon><CircleCheckFilled /></el-icon>
            <span>添加成功</span>
          </div>
          <div v-else-if="loginStatus === '500'" class="status-wrapper error">
            <el-icon><CircleCloseFilled /></el-icon>
            <span>添加失败，请稍后再试</span>
          </div>
        </div>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitAccountForm" :loading="sseConnecting" :disabled="sseConnecting">
            {{ sseConnecting ? '请求中' : '确认' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { Refresh, CircleCheckFilled, CircleCloseFilled, Loading, Link, Plus, Delete, Check, Folder } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { accountApi } from '@/api/account'
import { useAccountStore } from '@/stores/account'
import { useAppStore } from '@/stores/app'
import { http } from '@/utils/request'
import { resolveApiUrl } from '@/utils/api-runtime'
import { platformList, platformNameToId, platformCssMap, getPlatformByName } from '@/config/platforms'

const accountStore = useAccountStore()
const appStore = useAppStore()

const activeTab = ref('all')
const searchKeyword = ref('')

const filterOptions = computed(() => {
  const counts = {}
  accountStore.accounts.forEach(account => {
    counts[account.platform] = (counts[account.platform] || 0) + 1
  })
  return [
    { label: '全部', value: 'all', count: accountStore.accounts.length },
    ...platformList.map(platform => ({ label: platform.name, value: platform.name, count: counts[platform.name] || 0 })),
  ].filter(option => option.value === 'all' || (option.count && option.count > 0))
})

const platformOptions = platformList.map(platform => ({
  label: platform.name,
  value: String(platform.id),
  logo: platform.logo,
  color: platform.color,
  bg: platform.bgColor,
}))

const fetchAccountsQuick = async () => {
  try {
    const res = await accountApi.getAccounts()
    if (res.code === 200 && res.data) {
      accountStore.setAccounts(res.data)
    }
  } catch (error) {
    console.error('快速获取账号数据失败:', error)
  }
}

const fetchAccounts = async () => {
  if (appStore.isAccountRefreshing) return
  appStore.setAccountRefreshing(true)
  try {
    const res = await accountApi.getValidAccounts()
    if (res.code === 200 && res.data) {
      accountStore.setAccounts(res.data)
      ElMessage.success('账号数据获取成功')
      if (appStore.isFirstTimeAccountManagement) {
        appStore.setAccountManagementVisited()
      }
    } else {
      ElMessage.error('获取账号数据失败')
    }
  } catch (error) {
    console.error('获取账号数据失败:', error)
    ElMessage.error('获取账号数据失败')
  } finally {
    appStore.setAccountRefreshing(false)
  }
}

onMounted(() => {
  fetchAccountsQuick()
})

const getPlatformClass = platform => platformCssMap[platform] || ''
const getPlatformColor = platform => getPlatformByName(platform)?.color || '#14937c'
const getPlatformLogo = platform => getPlatformByName(platform)?.logo || null
const getPlatformLetter = platform => getPlatformByName(platform)?.letter || platform?.charAt(0) || '?'

const getStatusClass = status => {
  if (status === '验证中') return 'pending'
  if (status === '正常') return 'normal'
  return 'error'
}

const filteredAccounts = computed(() => {
  let accounts = accountStore.accounts
  if (activeTab.value !== 'all') {
    accounts = accounts.filter(account => account.platform === activeTab.value)
  }
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    accounts = accounts.filter(account => account.name.toLowerCase().includes(keyword))
  }
  return accounts
})

watch([activeTab, searchKeyword], () => {})

const dialogVisible = ref(false)
const dialogType = ref('add')
const accountFormRef = ref(null)
const accountForm = reactive({ id: null, name: '', platform: '', status: '正常' })
const rules = {
  platform: [{ required: true, message: '请选择平台', trigger: 'change' }],
}

const sseConnecting = ref(false)
const checkingIds = ref(new Set())

const handleCheckAccount = async row => {
  checkingIds.value.add(row.id)
  try {
    const res = await http.get('/checkAccount', { id: row.id })
    if (res.code === 200 && res.data) {
      const { valid } = res.data
      accountStore.updateAccount(row.id, { ...row, status: valid ? '正常' : '失效' })
      ElMessage({ type: valid ? 'success' : 'warning', message: res.msg })
    } else {
      ElMessage.error(res.msg || '检查失败')
    }
  } catch (error) {
    ElMessage.error('检查请求失败')
  } finally {
    checkingIds.value.delete(row.id)
  }
}

const qrCodeData = ref('')
const loginStatus = ref('')

const onPlatformSelect = () => {
  accountFormRef.value?.validateField('platform')
}

const handleAddAccount = () => {
  dialogType.value = 'add'
  Object.assign(accountForm, { id: null, name: '', platform: '', status: '正常' })
  sseConnecting.value = false
  qrCodeData.value = ''
  loginStatus.value = ''
  dialogVisible.value = true
}

const handleDelete = row => {
  ElMessageBox.confirm(`确定要删除账号 ${row.name} 吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      try {
        const response = await accountApi.deleteAccount(row.id)
        if (response.code === 200) {
          accountStore.deleteAccount(row.id)
          ElMessage.success('删除成功')
        } else {
          ElMessage.error(response.msg || '删除失败')
        }
      } catch (error) {
        console.error('删除账号失败:', error)
        ElMessage.error('删除账号失败')
      }
    })
    .catch(() => {})
}

const syncingIds = reactive(new Set())

const handleSyncProfile = async row => {
  if (syncingIds.has(row.id)) return
  syncingIds.add(row.id)
  try {
    const res = await accountApi.syncProfile(row.id)
    if (res.code === 200 && res.data) {
      accountStore.updateAccount(row.id, {
        id: row.id,
        name: res.data.name || row.name,
        avatar: res.data.avatar || row.avatar,
      })
      ElMessage.success('资料同步成功')
    } else {
      ElMessage.error(res.msg || '同步失败')
    }
  } catch (error) {
    console.error('同步资料失败:', error)
    ElMessage.error('同步资料失败')
  } finally {
    syncingIds.delete(row.id)
  }
}

const getDefaultAvatar = name => `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=random`

const handleOpenCreatorCenter = async row => {
  try {
    const res = await http.post('/openCreatorCenter', { id: row.id })
    if (res.code === 200) {
      ElMessage.success('正在打开创作中心...')
    } else {
      ElMessage.error(res.msg || '打开失败')
    }
  } catch (error) {
    console.error('打开创作中心失败:', error)
    ElMessage.error('打开创作中心失败')
  }
}

let eventSource = null

const closeSSEConnection = () => {
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
}

const connectSSE = platform => {
  closeSSEConnection()
  sseConnecting.value = true
  qrCodeData.value = ''
  loginStatus.value = ''

  const type = platformNameToId[platform] ? String(platformNameToId[platform]) : '1'
  const tempId = crypto.randomUUID()
  const url = resolveApiUrl(`/login?type=${type}&id=${encodeURIComponent(tempId)}`)

  eventSource = new EventSource(url)

  eventSource.onmessage = event => {
    const data = event.data

    try {
      const result = JSON.parse(data)
      if (result.status === '200') {
        loginStatus.value = '200'
        setTimeout(() => {
          closeSSEConnection()
          setTimeout(() => {
            dialogVisible.value = false
            sseConnecting.value = false
            ElMessage.success(dialogType.value === 'edit' ? '重新登录成功' : '账号添加成功')
            ElMessage({ type: 'info', message: '正在同步账号信息...', duration: 0 })
            fetchAccountsQuick().then(() => {
              ElMessage.closeAll()
              ElMessage.success('账号信息已更新')
            })
          }, 1000)
        }, 1000)
        return
      }
      if (result.status === '500') {
        loginStatus.value = '500'
        closeSSEConnection()
        sseConnecting.value = false
        qrCodeData.value = ''
        ElMessage.error(result.msg || '登录失败，请稍后再试')
        setTimeout(() => {
          loginStatus.value = ''
        }, 2000)
        return
      }
    } catch {}

    if (data === '500') {
      loginStatus.value = '500'
      closeSSEConnection()
      setTimeout(() => {
        sseConnecting.value = false
        qrCodeData.value = ''
        loginStatus.value = ''
      }, 2000)
    } else if (!qrCodeData.value && data.length > 100) {
      qrCodeData.value = data.startsWith('data:image') ? data : `data:image/png;base64,${data}`
    } else if (data === '200') {
      loginStatus.value = '200'
      setTimeout(() => {
        closeSSEConnection()
        setTimeout(() => {
          dialogVisible.value = false
          sseConnecting.value = false
          ElMessage.success(dialogType.value === 'edit' ? '重新登录成功' : '账号添加成功')
          ElMessage({ type: 'info', message: '正在同步账号信息...', duration: 0 })
          fetchAccountsQuick().then(() => {
            ElMessage.closeAll()
            ElMessage.success('账号信息已更新')
          })
        }, 1000)
      }, 1000)
    }
  }

  eventSource.onerror = error => {
    console.error('SSE连接错误:', error)
    ElMessage.error('连接服务器失败，请稍后再试')
    closeSSEConnection()
    sseConnecting.value = false
  }
}

const submitAccountForm = () => {
  accountFormRef.value.validate(async valid => {
    if (!valid) return

    if (dialogType.value === 'add') {
      connectSSE(accountForm.platform)
    } else {
      try {
        const type = platformNameToId[accountForm.platform] || 1
        const res = await accountApi.updateAccount({ id: accountForm.id, type, userName: accountForm.name })
        if (res.code === 200) {
          accountStore.updateAccount(accountForm.id, {
            id: accountForm.id,
            name: accountForm.name,
            platform: accountForm.platform,
            status: accountForm.status,
          })
          ElMessage.success('更新成功')
          dialogVisible.value = false
          fetchAccountsQuick()
        } else {
          ElMessage.error(res.msg || '更新账号失败')
        }
      } catch (error) {
        console.error('更新账号失败:', error)
        ElMessage.error('更新账号失败')
      }
    }
  })
}

onBeforeUnmount(() => {
  closeSSEConnection()
})
</script>

<style lang="scss" scoped>
@use 'sass:color';
@use '@/styles/variables.scss' as *;

.account-management {
  .filter-panel {
    display: flex;
    flex-direction: column;
    gap: $spacing-md;
  }

  .platform-tabs {
    display: flex;
    flex-wrap: wrap;
    gap: $spacing-sm;
  }

  .tab-item {
    display: inline-flex;
    align-items: center;
    gap: 8px;
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

  .tab-count {
    display: inline-flex;
    min-width: 22px;
    min-height: 22px;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    background: rgba($text-primary, 0.06);
    font-size: 12px;
  }

  .search-input {
    max-width: 320px;
  }

  .account-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: $spacing-lg;
  }

  .account-card {
    display: flex;
    flex-direction: column;
    gap: $spacing-md;
    padding: $spacing-lg;
    border-radius: $radius-card;
    border: 1px solid $border;
    background: $bg-elevated;
    box-shadow: $shadow-xs;
    transition:
      transform $transition-base,
      border-color $transition-base,
      box-shadow $transition-base;

    &:hover {
      transform: translateY(-2px);
      box-shadow: $shadow-sm;
      border-color: $border-active;
    }
  }

  .account-card__main {
    display: flex;
    align-items: center;
    gap: $spacing-md;
  }

  .user-avatar {
    border: 1px solid $border;
    flex-shrink: 0;
  }

  .account-card__copy {
    display: flex;
    flex-direction: column;
    gap: $spacing-xs;
    min-width: 0;
    flex: 1;
  }

  .account-name {
    color: $text-primary;
    font-size: 16px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .account-meta {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: $spacing-sm;
  }

  .platform-name {
    color: $text-secondary;
    font-size: 13px;
  }

  .status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    min-height: 24px;
    padding: 0 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;

    &.normal {
      color: $success-color;
      background: rgba($success-color, 0.12);
    }

    &.pending {
      color: $info-color;
      background: rgba($info-color, 0.12);
    }

    &.error {
      color: $danger-color;
      background: rgba($danger-color, 0.12);
    }
  }

  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
  }

  .platform-logo {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .platform-icon {
    width: 40px;
    height: 40px;
    object-fit: contain;
  }

  .platform-letter {
    font-size: 20px;
    font-weight: 700;
  }

  .account-card__actions {
    display: flex;
    flex-wrap: wrap;
    gap: $spacing-sm;
    padding-top: $spacing-md;
    border-top: 1px solid $border-light;
  }

  .action-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    min-height: 38px;
    padding: 0 14px 0 10px;
    border: 1px solid transparent;
    border-radius: 999px;
    background: $bg-elevated;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.72);
    color: $text-secondary;
    font-size: 12px;
    font-weight: 600;
    transition:
      border-color $transition-base,
      background-color $transition-base,
      color $transition-base,
      box-shadow $transition-base,
      transform $transition-base;

    &:hover {
      transform: translateY(-1px);
    }

    &:disabled {
      opacity: 0.55;
      cursor: not-allowed;
      transform: none;
    }

    .action-btn__icon {
      width: 22px;
      height: 22px;
      border-radius: 999px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: rgba($text-primary, 0.06);
      color: inherit;
      flex-shrink: 0;
      transition:
        background-color $transition-base,
        color $transition-base;
    }

    .action-btn__label {
      line-height: 1;
    }

    &--success {
      color: color.adjust($success-color, $lightness: -6%);
      background: rgba($success-color, 0.08);
      border-color: rgba($success-color, 0.16);

      .action-btn__icon {
        background: rgba($success-color, 0.14);
      }

      &:hover {
        background: rgba($success-color, 0.12);
        border-color: rgba($success-color, 0.24);
      }
    }

    &--info {
      color: color.adjust($info-color, $lightness: -4%);
      background: rgba($info-color, 0.08);
      border-color: rgba($info-color, 0.16);

      .action-btn__icon {
        background: rgba($info-color, 0.14);
      }

      &:hover {
        background: rgba($info-color, 0.12);
        border-color: rgba($info-color, 0.24);
      }
    }

    &--teal {
      color: color.adjust($brand-start, $lightness: -4%);
      background: rgba($brand-start, 0.08);
      border-color: rgba($brand-start, 0.16);

      .action-btn__icon {
        background: rgba($brand-start, 0.14);
      }

      &:hover {
        background: rgba($brand-start, 0.12);
        border-color: rgba($brand-start, 0.24);
      }
    }

    &--danger {
      color: color.adjust($danger-color, $lightness: -2%);
      background: rgba($danger-color, 0.08);
      border-color: rgba($danger-color, 0.16);

      .action-btn__icon {
        background: rgba($danger-color, 0.14);
      }

      &:hover {
        background: rgba($danger-color, 0.12);
        border-color: rgba($danger-color, 0.24);
      }
    }
  }

  .qrcode-container {
    margin-top: $spacing-md;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 250px;
  }

  .qrcode-wrapper {
    text-align: center;
  }

  .qrcode-tip {
    margin-bottom: $spacing-md;
    color: $text-secondary;
  }

  .qrcode-image {
    max-width: 200px;
    max-height: 200px;
    border: 1px solid $border;
    background-color: #000;
    border-radius: $radius-sm;
  }

  .loading-wrapper,
  .status-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: $spacing-sm;

    .el-icon {
      font-size: 48px;
    }
  }

  .success .el-icon {
    color: $success-color;
  }

  .error .el-icon {
    color: $danger-color;
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: $spacing-sm;
  }
}
</style>
