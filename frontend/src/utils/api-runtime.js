const PLATFORM_NAMES = {
  1: '\u5c0f\u7ea2\u4e66',
  2: '\u89c6\u9891\u53f7',
  3: '\u6296\u97f3',
  4: '\u5feb\u624b',
  5: 'B\u7ad9',
  6: '\u767e\u5bb6\u53f7',
  7: 'TikTok',
  8: 'YouTube',
  9: '\u5c0f\u9ed1\u76d2'
}

const STATUS_LABELS = {
  [-1]: '\u9a8c\u8bc1\u4e2d',
  0: '\u5f02\u5e38',
  1: '\u6b63\u5e38'
}

const DEFAULT_API_BASE_URL =
  typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_BASE_URL
    ? import.meta.env.VITE_API_BASE_URL
    : ''

const RUNTIME_PORT_STORAGE_KEY = 'sau-backend-port'

export const getRuntimeBackendBaseUrl = () => {
  if (typeof window === 'undefined') return ''

  const savedPort = window.localStorage.getItem(RUNTIME_PORT_STORAGE_KEY)
  if (!savedPort) return ''

  const port = String(savedPort).trim()
  if (!/^\d+$/.test(port)) return ''

  return `${window.location.protocol}//${window.location.hostname}:${port}`
}

export const setRuntimeBackendPort = (port) => {
  if (typeof window === 'undefined') return

  const normalized = String(port || '').trim()
  if (!/^\d+$/.test(normalized)) return

  window.localStorage.setItem(RUNTIME_PORT_STORAGE_KEY, normalized)
}

const trimTrailingSlash = (value) => String(value || '').replace(/\/+$/, '')

const normalizePath = (path) => {
  if (!path) return ''
  return path.startsWith('/') ? path : `/${path}`
}

export const resolveApiUrl = (path, baseUrl = DEFAULT_API_BASE_URL || '') => {
  const normalizedBase = trimTrailingSlash(baseUrl)
  const normalizedPath = normalizePath(path)

  if (!normalizedPath) {
    return normalizedBase
  }

  return normalizedBase ? `${normalizedBase}${normalizedPath}` : normalizedPath
}

export const normalizeAccount = (item) => {
  const row = Array.isArray(item)
    ? {
        id: item[0],
        type: item[1],
        filePath: item[2],
        userName: item[3],
        status: item[4],
        avatar: item[5] || ''
      }
    : {
        id: item?.id,
        type: item?.type,
        filePath: item?.filePath,
        userName: item?.userName ?? item?.name ?? '',
        status: item?.status,
        avatar: item?.avatar || ''
      }

  return {
    id: row.id,
    type: row.type,
    filePath: row.filePath,
    name: row.userName,
    status: STATUS_LABELS[row.status] ?? '\u5f02\u5e38',
    platform: PLATFORM_NAMES[row.type] || '\u672a\u77e5',
    avatar: row.avatar
  }
}
