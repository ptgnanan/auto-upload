import { defineStore } from 'pinia'
import { ref } from 'vue'
import { normalizeAccount } from '@/utils/api-runtime'

export const useAccountStore = defineStore('account', () => {
  const accounts = ref([])

  const setAccounts = (accountsData) => {
    const list = Array.isArray(accountsData) ? accountsData : []
    accounts.value = list.map(normalizeAccount)
  }

  const addAccount = (account) => {
    accounts.value.push(account)
  }

  const updateAccount = (id, updatedAccount) => {
    const index = accounts.value.findIndex(acc => acc.id === id)
    if (index !== -1) {
      accounts.value[index] = { ...accounts.value[index], ...updatedAccount }
    }
  }

  const deleteAccount = (id) => {
    accounts.value = accounts.value.filter(acc => acc.id !== id)
  }

  const getAccountsByPlatform = (platform) => {
    return accounts.value.filter(acc => acc.platform === platform)
  }

  return {
    accounts,
    setAccounts,
    addAccount,
    updateAccount,
    deleteAccount,
    getAccountsByPlatform
  }
})
