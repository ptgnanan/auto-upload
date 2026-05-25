import { http } from '@/utils/request'
import { resolveApiUrl } from '@/utils/api-runtime'

export const materialApi = {
  getAllMaterials: () => {
    return http.get('/getFiles')
  },

  uploadMaterial: (formData, onUploadProgress) => {
    return http.upload('/uploadSave', formData, onUploadProgress)
  },

  deleteMaterial: (id) => {
    return http.get(`/deleteFile?id=${id}`)
  },

  downloadMaterial: (filePath) => {
    return resolveApiUrl(`/download/${filePath}`)
  },

  getMaterialPreviewUrl: (filename) => {
    return resolveApiUrl(`/getFile?filename=${filename}`)
  }
}
