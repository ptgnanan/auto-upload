<template>
  <div class="app-shell">
    <aside class="app-sidebar" :class="{ 'is-collapsed': sidebarCollapsed }">
      <div class="app-sidebar__brand">
        <button class="brand-mark" type="button" @click="router.push('/')">SA</button>
        <div v-if="!sidebarCollapsed" class="brand-copy">
          <strong>Social Auto Upload</strong>
          <span>内容分发工作台</span>
        </div>
        <button class="sidebar-toggle" type="button" @click="sidebarCollapsed = !sidebarCollapsed">
          <el-icon><component :is="sidebarCollapsed ? Expand : Fold" /></el-icon>
        </button>
      </div>

      <nav class="sidebar-nav">
        <button
          v-for="item in primaryNavItems"
          :key="item.path"
          class="sidebar-nav__item"
          :class="{ 'is-active': activeMenu === item.path }"
          type="button"
          @click="router.push(item.path)"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span v-if="!sidebarCollapsed">{{ item.title }}</span>
        </button>
      </nav>

      <div class="sidebar-nav sidebar-nav--secondary">
        <button
          v-for="item in secondaryNavItems"
          :key="item.path"
          class="sidebar-nav__item"
          :class="{ 'is-active': activeMenu === item.path }"
          type="button"
          @click="router.push(item.path)"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span v-if="!sidebarCollapsed">{{ item.title }}</span>
        </button>
      </div>
    </aside>

    <div class="app-main">
      <header class="app-topbar">
        <div class="app-topbar__meta">
          <span class="app-topbar__eyebrow">社交媒体自动上传</span>
          <strong class="app-topbar__title">{{ pageTitle }}</strong>
        </div>
      </header>

      <main class="app-content">
        <router-view v-slot="{ Component, route }">
          <keep-alive>
            <component :is="Component" v-if="route.meta?.keepAlive" />
          </keep-alive>
          <component :is="Component" v-if="!route.meta?.keepAlive" />
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  HomeFilled,
  User,
  Picture,
  Upload,
  Clock,
  List,
  Setting,
  UserFilled,
  InfoFilled,
  Expand,
  Fold,
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const sidebarCollapsed = ref(false)

const primaryNavItems = [
  { path: '/', icon: HomeFilled, title: '仪表盘' },
  { path: '/account-management', icon: User, title: '账号管理' },
  { path: '/material-management', icon: Picture, title: '素材管理' },
  { path: '/publish-center', icon: Upload, title: '发布中心' },
  { path: '/publish-history', icon: Clock, title: '发布历史' },
  { path: '/task-center', icon: List, title: '任务中心' },
]

const secondaryNavItems = [
  { path: '/settings', icon: Setting, title: '系统设置' },
  { path: '/author', icon: UserFilled, title: '关于作者' },
  { path: '/about', icon: InfoFilled, title: '关于项目' },
]

const activeMenu = computed(() => route.path)
const pageTitle = computed(() => route.meta?.title || '工作台')
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.app-shell {
  display: flex;
  min-height: 100vh;
  background: transparent;
}

.app-sidebar {
  width: 248px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
  padding: $spacing-lg $spacing-md;
  border-right: 1px solid $border;
  background: rgba(255, 255, 255, 0.62);
  backdrop-filter: blur(18px);
  position: sticky;
  top: 0;
  height: 100vh;

  &.is-collapsed {
    width: 88px;

    .app-sidebar__brand {
      justify-content: center;
      gap: $spacing-sm;
    }

    .sidebar-toggle {
      position: absolute;
      right: 12px;
      top: 18px;
    }

    .sidebar-nav__item {
      justify-content: center;
      padding-inline: 0;
    }
  }
}

.app-sidebar__brand {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  padding: $spacing-sm;
}

.brand-mark {
  width: 44px;
  height: 44px;
  border-radius: $radius-card;
  background: $gradient-brand;
  color: var(--color-text-inverse);
  font-weight: 700;
  letter-spacing: 0.04em;
}

.brand-copy {
  display: flex;
  flex-direction: column;
  min-width: 0;

  strong {
    font-size: 15px;
    color: $text-primary;
  }

  span {
    font-size: 12px;
    color: $text-muted;
  }
}

.sidebar-toggle {
  width: 32px;
  height: 32px;
  margin-left: auto;
  border-radius: $radius-sm;
  color: $text-secondary;
  transition: background-color $transition-base, color $transition-base;

  &:hover {
    background: $bg-surface;
    color: $brand-start;
  }
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;

  &--secondary {
    margin-top: auto;
    padding-top: $spacing-md;
    border-top: 1px solid $border-light;
  }
}

.sidebar-nav__item {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  min-height: 42px;
  padding: 0 $spacing-md;
  border-radius: $radius-base;
  color: $text-secondary;
  font-size: 14px;
  font-weight: 500;
  text-align: left;
  transition:
    background-color $transition-base,
    color $transition-base,
    box-shadow $transition-base;

  &:hover {
    background: rgba($brand-start, 0.08);
    color: $text-primary;
  }

  &.is-active {
    color: $brand-start;
    background: rgba($brand-start, 0.1);
    box-shadow: inset 0 0 0 1px rgba($brand-start, 0.14);
  }

  .el-icon {
    font-size: 18px;
    flex-shrink: 0;
  }
}

.app-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.app-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 72px;
  padding: 0 $spacing-xl;
  border-bottom: 1px solid $border-light;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(14px);
}

.app-topbar__meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.app-topbar__eyebrow {
  font-size: 12px;
  color: $text-muted;
}

.app-topbar__title {
  font-size: 18px;
  color: $text-primary;
}

.app-content {
  flex: 1;
  min-width: 0;
  overflow: auto;
}

@media (max-width: 1024px) {
  .app-shell {
    flex-direction: column;
  }

  .app-sidebar {
    position: static;
    width: 100%;
    height: auto;
    border-right: 0;
    border-bottom: 1px solid $border-light;
  }

  .app-sidebar.is-collapsed {
    width: 100%;

    .sidebar-nav__item {
      justify-content: flex-start;
      padding-inline: $spacing-md;
    }
  }

  .sidebar-nav,
  .sidebar-nav--secondary {
    flex-direction: row;
    flex-wrap: wrap;
    margin-top: 0;
    padding-top: 0;
    border-top: 0;
  }

  .app-topbar {
    padding-inline: $spacing-lg;
  }
}
</style>
