<template>
  <div class="account-management">
    <div class="page-header">
      <h1>账号管理</h1>
    </div>

    <div class="account-container">
      <div class="account-toolbar">
        <div class="toolbar-left">
          <el-tabs v-model="activeTab" class="account-tabs">
            <el-tab-pane label="全部" name="all" />
            <el-tab-pane label="快手" name="快手" />
            <el-tab-pane label="抖音" name="抖音" />
            <el-tab-pane label="视频号" name="视频号" />
            <el-tab-pane label="小红书" name="小红书" />
          </el-tabs>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索名称或账号"
            prefix-icon="Search"
            clearable
            style="width: 240px"
          />
        </div>
        <div class="toolbar-right">
          <el-button @click="fetchAccounts" :loading="appStore.isAccountRefreshing">
            <el-icon v-if="!appStore.isAccountRefreshing"><Refresh /></el-icon>
            刷新
          </el-button>
          <el-button type="primary" @click="handleAddAccount">添加账号</el-button>
        </div>
      </div>

      <div v-if="filteredAccounts.length > 0" class="account-list">
        <el-table :data="filteredAccounts" style="width: 100%">
          <el-table-column label="头像" width="70">
            <template #default="scope">
              <el-avatar :src="getDefaultAvatar(scope.row.name)" :size="36" />
            </template>
          </el-table-column>
          <el-table-column prop="name" label="名称" width="180">
            <template #default="scope">
              <span class="account-name">{{ scope.row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="platform" label="平台" width="120">
            <template #default="scope">
              <el-tag
                :type="getPlatformTagType(scope.row.platform)"
                effect="plain"
                size="small"
                round
              >
                {{ scope.row.platform }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="120">
            <template #default="scope">
              <el-tag
                :type="getStatusTagType(scope.row.status)"
                effect="plain"
                size="small"
                :class="{'clickable-status': isStatusClickable(scope.row.status)}"
                @click="handleStatusClick(scope.row)"
              >
                <el-icon :class="scope.row.status === '验证中' ? 'is-loading' : ''" v-if="scope.row.status === '验证中'">
                  <Loading />
                </el-icon>
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="260">
            <template #default="scope">
              <div class="action-cell">
                <el-button size="small" text @click="handleEdit(scope.row)">编辑</el-button>
                <el-button size="small" text type="primary" @click="handleDownloadCookie(scope.row)">
                  <el-icon><Download /></el-icon> Cookie
                </el-button>
                <el-button size="small" text type="info" @click="handleUploadCookie(scope.row)">
                  <el-icon><Upload /></el-icon> Cookie
                </el-button>
                <el-button size="small" text type="danger" @click="handleDelete(scope.row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-else class="empty-data">
        <el-empty :description="searchKeyword ? '未找到匹配账号' : '暂无账号数据'" />
      </div>
    </div>

    <!-- 添加/编辑账号对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '添加账号' : '编辑账号'"
      width="500px"
      :close-on-click-modal="false"
      :close-on-press-escape="!sseConnecting"
      :show-close="!sseConnecting"
    >
      <el-form :model="accountForm" label-width="80px" :rules="rules" ref="accountFormRef">
        <el-form-item label="平台" prop="platform">
          <el-select
            v-model="accountForm.platform"
            placeholder="请选择平台"
            style="width: 100%"
            :disabled="dialogType === 'edit' || sseConnecting"
          >
            <el-option label="快手" value="快手" />
            <el-option label="抖音" value="抖音" />
            <el-option label="视频号" value="视频号" />
            <el-option label="小红书" value="小红书" />
          </el-select>
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input
            v-model="accountForm.name"
            placeholder="请输入账号名称"
            :disabled="sseConnecting"
          />
        </el-form-item>

        <!-- 二维码显示区域 -->
        <div v-if="sseConnecting" class="qrcode-container">
          <div v-if="qrCodeData && !loginStatus" class="qrcode-wrapper">
            <p class="qrcode-tip">请使用对应平台APP扫描二维码登录</p>
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
          <el-button
            type="primary"
            @click="submitAccountForm"
            :loading="sseConnecting"
            :disabled="sseConnecting"
          >
            {{ sseConnecting ? '请求中' : '确认' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { Refresh, CircleCheckFilled, CircleCloseFilled, Download, Upload, Loading } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { accountApi } from '@/api/account'
import { useAccountStore } from '@/stores/account'
import { useAppStore } from '@/stores/app'
import { http } from '@/utils/request'

const accountStore = useAccountStore()
const appStore = useAppStore()

const activeTab = ref('all')
const searchKeyword = ref('')

const fetchAccountsQuick = async () => {
  try {
    const res = await accountApi.getAccounts()
    if (res.code === 200 && res.data) {
      const accountsWithPendingStatus = res.data.map(account => {
        const updatedAccount = [...account];
        updatedAccount[4] = -1;
        return updatedAccount;
      });
      accountStore.setAccounts(accountsWithPendingStatus);
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

const validateAllAccountsInBackground = async () => {
  setTimeout(async () => {
    try {
      const res = await accountApi.getValidAccounts()
      if (res.code === 200 && res.data) {
        accountStore.setAccounts(res.data)
      }
    } catch (error) {
      console.error('后台验证账号失败:', error)
    }
  }, 0)
}

onMounted(() => {
  fetchAccountsQuick()
  setTimeout(() => {
    validateAllAccountsInBackground()
  }, 100)
})

const getPlatformTagType = (platform) => {
  const typeMap = { '快手': 'success', '抖音': 'danger', '视频号': 'warning', '小红书': 'info' }
  return typeMap[platform] || 'info'
}

const isStatusClickable = (status) => status === '异常'

const getStatusTagType = (status) => {
  if (status === '验证中') return 'info'
  if (status === '正常') return 'success'
  return 'danger'
}

const handleStatusClick = (row) => {
  if (isStatusClickable(row.status)) handleReLogin(row)
}

const filteredAccounts = computed(() => {
  let accounts = accountStore.accounts
  if (activeTab.value !== 'all') {
    accounts = accounts.filter(a => a.platform === activeTab.value)
  }
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    accounts = accounts.filter(a => a.name.toLowerCase().includes(keyword))
  }
  return accounts
})

const dialogVisible = ref(false)
const dialogType = ref('add')
const accountFormRef = ref(null)

const accountForm = reactive({ id: null, name: '', platform: '', status: '正常' })

const rules = {
  platform: [{ required: true, message: '请选择平台', trigger: 'change' }],
  name: [{ required: true, message: '请输入账号名称', trigger: 'blur' }]
}

const sseConnecting = ref(false)
const qrCodeData = ref('')
const loginStatus = ref('')

const handleAddAccount = () => {
  dialogType.value = 'add'
  Object.assign(accountForm, { id: null, name: '', platform: '', status: '正常' })
  sseConnecting.value = false
  qrCodeData.value = ''
  loginStatus.value = ''
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogType.value = 'edit'
  Object.assign(accountForm, { id: row.id, name: row.name, platform: row.platform, status: row.status })
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除账号 ${row.name} 吗？`, '警告', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning',
  }).then(async () => {
    try {
      const response = await accountApi.deleteAccount(row.id)
      if (response.code === 200) {
        accountStore.deleteAccount(row.id)
        ElMessage({ type: 'success', message: '删除成功' })
      } else {
        ElMessage.error(response.msg || '删除失败')
      }
    } catch (error) {
      console.error('删除账号失败:', error)
      ElMessage.error('删除账号失败')
    }
  }).catch(() => {})
}

const handleDownloadCookie = (row) => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5409'
  const downloadUrl = `${baseUrl}/downloadCookie?filePath=${encodeURIComponent(row.filePath)}`
  const link = document.createElement('a')
  link.href = downloadUrl
  link.download = `${row.name}_cookie.json`
  link.target = '_blank'
  link.style.display = 'none'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const handleUploadCookie = (row) => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.style.display = 'none'
  document.body.appendChild(input)

  input.onchange = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    if (!file.name.endsWith('.json')) {
      ElMessage.error('请选择JSON格式的Cookie文件')
      document.body.removeChild(input)
      return
    }
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('id', row.id)
      formData.append('platform', row.platform)
      await http.upload('/uploadCookie', formData)
      ElMessage.success('Cookie文件上传成功')
      fetchAccounts()
    } catch (error) {
      ElMessage.error('Cookie文件上传失败')
    } finally {
      document.body.removeChild(input)
    }
  }
  input.click()
}

const handleReLogin = (row) => {
  dialogType.value = 'edit'
  Object.assign(accountForm, { id: row.id, name: row.name, platform: row.platform, status: row.status })
  sseConnecting.value = false
  qrCodeData.value = ''
  loginStatus.value = ''
  dialogVisible.value = true
  setTimeout(() => connectSSE(row.platform, row.name), 300)
}

const getDefaultAvatar = (name) => {
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=random`
}

let eventSource = null

const closeSSEConnection = () => {
  if (eventSource) { eventSource.close(); eventSource = null }
}

const connectSSE = (platform, name) => {
  closeSSEConnection()
  sseConnecting.value = true
  qrCodeData.value = ''
  loginStatus.value = ''

  const platformTypeMap = { '小红书': '1', '视频号': '2', '抖音': '3', '快手': '4' }
  const type = platformTypeMap[platform] || '1'
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5409'
  const url = `${baseUrl}/login?type=${type}&id=${encodeURIComponent(name)}`

  eventSource = new EventSource(url)

  eventSource.onmessage = (event) => {
    const data = event.data
    if (!qrCodeData.value && data.length > 100) {
      try {
        qrCodeData.value = data.startsWith('data:image') ? data : `data:image/png;base64,${data}`
      } catch (error) {}
    } else if (data === '200' || data === '500') {
      loginStatus.value = data
      if (data === '200') {
        setTimeout(() => {
          closeSSEConnection()
          setTimeout(() => {
            dialogVisible.value = false
            sseConnecting.value = false
            ElMessage.success(dialogType.value === 'edit' ? '重新登录成功' : '账号添加成功')
            ElMessage({ type: 'info', message: '正在同步账号信息...', duration: 0 })
            fetchAccounts().then(() => { ElMessage.closeAll(); ElMessage.success('账号信息已更新') })
          }, 1000)
        }, 1000)
      } else {
        closeSSEConnection()
        setTimeout(() => { sseConnecting.value = false; qrCodeData.value = ''; loginStatus.value = '' }, 2000)
      }
    }
  }

  eventSource.onerror = (error) => {
    console.error('SSE连接错误:', error)
    ElMessage.error('连接服务器失败，请稍后再试')
    closeSSEConnection()
    sseConnecting.value = false
  }
}

const submitAccountForm = () => {
  accountFormRef.value.validate(async (valid) => {
    if (valid) {
      if (dialogType.value === 'add') {
        connectSSE(accountForm.platform, accountForm.name)
      } else {
        try {
          const platformTypeMap = { '小红书': 1, '视频号': 2, '抖音': 3, '快手': 4 }
          const type = platformTypeMap[accountForm.platform] || 1
          const res = await accountApi.updateAccount({ id: accountForm.id, type, userName: accountForm.name })
          if (res.code === 200) {
            accountStore.updateAccount(accountForm.id, { id: accountForm.id, name: accountForm.name, platform: accountForm.platform, status: accountForm.status })
            ElMessage.success('更新成功')
            dialogVisible.value = false
            fetchAccounts()
          } else {
            ElMessage.error(res.msg || '更新账号失败')
          }
        } catch (error) {
          console.error('更新账号失败:', error)
          ElMessage.error('更新账号失败')
        }
      }
    }
  })
}

onBeforeUnmount(() => { closeSSEConnection() })
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.account-management {
  .page-header {
    margin-bottom: 24px;

    h1 {
      font-size: 26px;
      font-weight: 700;
      color: $text-primary;
      margin: 0;
      letter-spacing: -0.5px;
    }
  }

  .account-container {
    background-color: $bg-color-surface;
    border: 1px solid $border-base;
    border-radius: 12px;
    padding: 4px 24px 24px;

    .account-toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      gap: 16px;

      .toolbar-left {
        display: flex;
        align-items: center;
        gap: 20px;
        flex: 1;
      }

      .toolbar-right {
        display: flex;
        gap: 10px;
        flex-shrink: 0;
      }

      .account-tabs {
        :deep(.el-tabs__header) {
          margin-bottom: 0;
        }
      }
    }

    .account-list {
      margin-bottom: 20px;
    }

    .empty-data {
      padding: 60px 0;
    }

    .account-name {
      font-weight: 500;
      color: $text-primary;
    }

    .action-cell {
      display: flex;
      align-items: center;
      gap: 4px;
    }
  }

  .clickable-status {
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      transform: scale(1.05);
      box-shadow: 0 0 8px rgba(0, 0, 0, 0.2);
    }
  }

  .qrcode-container {
    margin-top: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 250px;

    .qrcode-wrapper {
      text-align: center;

      .qrcode-tip {
        margin-bottom: 16px;
        color: $text-secondary;
      }

      .qrcode-image {
        max-width: 200px;
        max-height: 200px;
        border: 1px solid $border-base;
        background-color: #000;
        border-radius: 8px;
      }
    }

    .loading-wrapper, .status-wrapper {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 12px;

      .el-icon {
        font-size: 48px;
        &.is-loading { animation: rotate 1s linear infinite; }
      }
      span { font-size: 16px; }
    }

    .success .el-icon { color: $success-color; }
    .error .el-icon { color: $danger-color; }
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }
}
</style>
