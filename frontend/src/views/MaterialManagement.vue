<template>
  <section class="page-shell material-management">
    <header class="page-header">
      <div class="page-header__main">
        <h1 class="page-title">素材管理</h1>
        <p class="page-subtitle">上传和管理视频素材</p>
      </div>
    </header>

    <div class="page-content">
      <div class="page-toolbar">
        <div class="page-toolbar__group page-toolbar__group--grow">
          <el-input
            v-model="searchKeyword"
            placeholder="输入文件名搜索"
            clearable
            @clear="handleSearch"
            @input="handleSearch"
            class="search-input"
          />
        </div>
        <div class="page-toolbar__group">
          <el-button type="primary" @click="handleUploadMaterial">
            <el-icon><Upload /></el-icon>
            上传素材
          </el-button>
          <el-button @click="fetchMaterials">
            <el-icon :class="{ 'is-loading': isRefreshing }"><Refresh /></el-icon>
            {{ isRefreshing ? '刷新中' : '刷新' }}
          </el-button>
        </div>
      </div>

      <section class="section-card">
        <div class="section-card__body">
          <div v-if="filteredMaterials.length > 0" class="material-list">
            <el-table :data="filteredMaterials" style="width: 100%">
              <el-table-column label="缩略图" width="80" align="center">
                <template #default="scope">
                  <div class="thumbnail-cell" v-if="isVideoFile(scope.row.filename)">
                    <span class="play-icon">&#9654;</span>
                  </div>
                  <div class="thumbnail-cell thumbnail-image" v-else-if="isImageFile(scope.row.filename)">
                    <img :src="getPreviewUrl(scope.row.file_path)" alt="" />
                  </div>
                  <div class="thumbnail-cell thumbnail-other" v-else>
                    <el-icon><Document /></el-icon>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="filename" label="文件名" min-width="240" show-overflow-tooltip />
              <el-table-column prop="filesize" label="文件大小" width="120" align="center">
                <template #default="scope">
                  <span class="muted-cell">{{ scope.row.filesize }} MB</span>
                </template>
              </el-table-column>
              <el-table-column prop="upload_time" label="上传时间" width="180" align="center" />
              <el-table-column label="操作" width="160" align="center">
                <template #default="scope">
                  <div class="action-cell">
                    <button class="action-btn action-btn--info" @click="handlePreview(scope.row)" title="预览">
                      <el-icon><View /></el-icon>
                    </button>
                    <button class="action-btn action-btn--danger" @click="handleDelete(scope.row)" title="删除">
                      <el-icon><Delete /></el-icon>
                    </button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div v-else class="empty-state">
            <div class="empty-state__inner">
              <strong class="empty-state__title">暂无素材数据</strong>
              <p class="empty-state__text">上传素材后会在这里集中管理。</p>
            </div>
          </div>
        </div>
      </section>
    </div>

    <el-dialog
      v-model="uploadDialogVisible"
      title="上传素材"
      width="680px"
      @close="handleUploadDialogClose"
      class="upload-dialog"
    >
      <div class="upload-form">
        <el-form label-width="92px">
          <el-form-item label="文件名称">
            <el-input
              v-model="customFilename"
              placeholder="选填，仅单个文件时生效"
              :disabled="customFilenameDisabled"
              clearable
            />
          </el-form-item>
          <el-form-item label="选择文件">
            <el-upload
              class="upload-zone"
              drag
              multiple
              :auto-upload="false"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :file-list="fileList"
            >
              <el-icon class="upload-zone-icon"><Upload /></el-icon>
              <div class="upload-zone-text">
                将文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="upload-zone-tip">支持视频、图片等格式文件，可一次选择多个文件</div>
              </template>
            </el-upload>
          </el-form-item>
          <el-form-item label="上传列表" v-if="fileList.length > 0">
            <div class="upload-file-list">
              <div v-for="file in fileList" :key="file.uid" class="upload-file-item">
                <div class="file-item-header">
                  <span class="file-name">{{ file.name }}</span>
                </div>
                <el-progress
                  :percentage="uploadProgress[file.uid]?.percentage || 0"
                  :text-inside="true"
                  :stroke-width="18"
                  class="upload-progress"
                >
                  <span>{{ uploadProgress[file.uid]?.speed || '' }}</span>
                </el-progress>
              </div>
            </div>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitUpload" :loading="isUploading">
            {{ isUploading ? '上传中' : '确认上传' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="previewDialogVisible" title="素材预览" width="820px" :top="'8vh'" class="preview-dialog">
      <div class="preview-container" v-if="currentMaterial">
        <div class="preview-frame">
          <div v-if="isVideoFile(currentMaterial.filename)" class="video-preview">
            <video controls>
              <source :src="getPreviewUrl(currentMaterial.file_path)" type="video/mp4" />
              您的浏览器不支持视频播放
            </video>
          </div>
          <div v-else-if="isImageFile(currentMaterial.filename)" class="image-preview">
            <img :src="getPreviewUrl(currentMaterial.file_path)" />
          </div>
          <div v-else class="file-info">
            <div class="file-info-icon">
              <el-icon :size="48"><Document /></el-icon>
            </div>
            <p>文件名: {{ currentMaterial.filename }}</p>
            <p>文件大小: {{ currentMaterial.filesize }} MB</p>
            <p>上传时间: {{ currentMaterial.upload_time }}</p>
            <el-button type="primary" @click="downloadFile(currentMaterial)">下载文件</el-button>
          </div>
        </div>
      </div>
    </el-dialog>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { Refresh, Upload, View, Delete, Document } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { materialApi } from '@/api/material'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

const searchKeyword = ref('')
const isRefreshing = ref(false)
const isUploading = ref(false)

const uploadDialogVisible = ref(false)
const previewDialogVisible = ref(false)
const currentMaterial = ref(null)

const fileList = ref([])
const customFilename = ref('')
const customFilenameDisabled = computed(() => fileList.value.length > 1)
const uploadProgress = ref({})

watch(fileList, () => {})

const fetchMaterials = async () => {
  isRefreshing.value = true
  try {
    const response = await materialApi.getAllMaterials()
    if (response.code === 200) {
      appStore.setMaterials(response.data)
      ElMessage.success('刷新成功')
    } else {
      ElMessage.error('获取素材列表失败')
    }
  } catch (error) {
    console.error('获取素材列表出错:', error)
    ElMessage.error('获取素材列表失败')
  } finally {
    isRefreshing.value = false
  }
}

const filteredMaterials = computed(() => {
  if (!searchKeyword.value) return appStore.materials
  const keyword = searchKeyword.value.toLowerCase()
  return appStore.materials.filter(material => material.filename.toLowerCase().includes(keyword))
})

const handleSearch = () => {}

const handleUploadMaterial = () => {
  fileList.value = []
  customFilename.value = ''
  uploadProgress.value = {}
  uploadDialogVisible.value = true
}

const handleUploadDialogClose = () => {
  fileList.value = []
  customFilename.value = ''
  uploadProgress.value = {}
}

const handleFileChange = (file, uploadFileList) => {
  fileList.value = uploadFileList
  const nextProgress = {}
  for (const item of uploadFileList) {
    nextProgress[item.uid] = { percentage: 0, speed: '' }
  }
  uploadProgress.value = nextProgress
}

const handleFileRemove = (file, uploadFileList) => {
  fileList.value = uploadFileList
  const nextProgress = { ...uploadProgress.value }
  delete nextProgress[file.uid]
  uploadProgress.value = nextProgress
}

const submitUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请选择要上传的文件')
    return
  }

  isUploading.value = true

  for (const file of fileList.value) {
    try {
      if (!file || !file.raw) {
        ElMessage.warning(`文件 ${file.name} 对象无效，已跳过`)
        continue
      }

      const formData = new FormData()
      formData.append('file', file.raw)

      if (fileList.value.length === 1 && customFilename.value.trim()) {
        formData.append('filename', customFilename.value.trim())
      }

      let lastLoaded = 0
      let lastTime = Date.now()

      const response = await materialApi.uploadMaterial(formData, progressEvent => {
        const progressData = uploadProgress.value[file.uid]
        if (!progressData) return

        progressData.percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total)

        const currentTime = Date.now()
        const timeDiff = (currentTime - lastTime) / 1000
        const loadedDiff = progressEvent.loaded - lastLoaded

        if (timeDiff > 0.5) {
          const speed = loadedDiff / timeDiff
          progressData.speed = speed > 1024 * 1024
            ? `${(speed / (1024 * 1024)).toFixed(2)} MB/s`
            : `${(speed / 1024).toFixed(2)} KB/s`
          lastLoaded = progressEvent.loaded
          lastTime = currentTime
        }
      })

      if (response.code === 200) {
        ElMessage.success(`文件 ${file.name} 上传成功`)
        const progressData = uploadProgress.value[file.uid]
        if (progressData) progressData.speed = '完成'
      } else {
        ElMessage.error(`文件 ${file.name} 上传失败: ${response.msg || '未知错误'}`)
      }
    } catch (error) {
      console.error(`上传文件 ${file.name} 出错:`, error)
      ElMessage.error(`文件 ${file.name} 上传失败: ${error.message || '未知错误'}`)
    }
  }

  isUploading.value = false
  await fetchMaterials()
}

const handlePreview = async material => {
  currentMaterial.value = null
  previewDialogVisible.value = true
  ElMessage.info('加载中...')
  try {
    await new Promise(resolve => setTimeout(resolve, 100))
    currentMaterial.value = material
  } catch (error) {
    console.error('预览素材出错:', error)
    ElMessage.error('预览加载失败')
    previewDialogVisible.value = false
  }
}

const handleDelete = material => {
  ElMessageBox.confirm(`确定要删除素材 ${material.filename} 吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      try {
        const response = await materialApi.deleteMaterial(material.id)
        if (response.code === 200) {
          appStore.removeMaterial(material.id)
          ElMessage.success('删除成功')
        } else {
          ElMessage.error(response.msg || '删除失败')
        }
      } catch (error) {
        console.error('删除素材出错:', error)
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {})
}

const getPreviewUrl = filePath => {
  const filename = filePath.split('/').pop()
  return materialApi.getMaterialPreviewUrl(filename)
}

const downloadFile = material => {
  const url = materialApi.downloadMaterial(material.file_path)
  window.open(url, '_blank')
}

const isVideoFile = filename => ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv'].some(ext => filename.toLowerCase().endsWith(ext))
const isImageFile = filename => ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'].some(ext => filename.toLowerCase().endsWith(ext))

onMounted(() => {
  if (appStore.materials.length === 0) {
    fetchMaterials()
  }
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.material-management {
  .search-input {
    width: 300px;
  }

  .material-list {
    display: flex;
    flex-direction: column;
    gap: $spacing-md;
  }

  .thumbnail-cell {
    width: 40px;
    height: 40px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: $radius-sm;
    background: $gradient-brand-subtle;
    color: $brand-start;
    overflow: hidden;
  }

  .thumbnail-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .thumbnail-other .el-icon {
    font-size: 18px;
    color: $text-muted;
  }

  .play-icon,
  .muted-cell {
    color: $text-secondary;
  }

  .action-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: $spacing-sm;
  }

  .action-btn {
    width: 32px;
    height: 32px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: $radius-sm;
    border: 1px solid $border;
    background: $bg-elevated;

    &--info {
      color: $info-color;
    }

    &--danger {
      color: $danger-color;
    }
  }

  .upload-zone {
    width: 100%;
  }

  .upload-zone :deep(.el-upload) {
    width: 100%;
  }

  .upload-zone-icon {
    font-size: 40px;
    color: $brand-start;
    margin-bottom: $spacing-sm;
  }

  .upload-zone-text {
    color: $text-secondary;
    font-size: 14px;

    em {
      color: $brand-start;
      font-style: normal;
    }
  }

  .upload-zone-tip {
    margin-top: $spacing-sm;
    color: $text-muted;
    font-size: 12px;
  }

  .upload-file-list {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: $spacing-sm;
  }

  .upload-file-item {
    padding: $spacing-sm $spacing-md;
    border-radius: $radius-base;
    border: 1px solid $border;
    background: $bg-elevated;
  }

  .file-item-header {
    margin-bottom: $spacing-sm;
  }

  .file-name {
    color: $text-primary;
    font-weight: 500;
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: $spacing-sm;
  }

  .preview-container {
    padding: $spacing-md 0;
  }

  .preview-frame {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 320px;
    padding: $spacing-lg;
    border-radius: $radius-card;
    background: $bg-surface;
    border: 1px solid $border;
  }

  .video-preview,
  .image-preview {
    display: flex;
    justify-content: center;

    video,
    img {
      max-width: 100%;
      max-height: 60vh;
      border-radius: $radius-sm;
    }
  }

  .file-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: $spacing-sm;
    text-align: center;
    color: $text-secondary;
  }

  .file-info-icon {
    color: $brand-start;
  }
}
</style>
