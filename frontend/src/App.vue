<template>
  <div id="app">
    <el-container>
      <el-aside :width="isCollapse ? '64px' : '200px'">
        <div class="sidebar">
          <div class="logo">
            <img v-show="isCollapse" src="/vite.svg" alt="Logo" class="logo-img">
            <h2 v-show="!isCollapse">Social Auto Upload</h2>
          </div>
          <el-menu
            :router="true"
            :default-active="activeMenu"
            :collapse="isCollapse"
            class="sidebar-menu"
            background-color="#020617"
            text-color="#94A3B8"
            active-text-color="#22C55E"
          >
            <el-menu-item index="/">
              <el-icon><HomeFilled /></el-icon>
              <span>仪表盘</span>
            </el-menu-item>
            <el-menu-item index="/account-management">
              <el-icon><User /></el-icon>
              <span>账号管理</span>
            </el-menu-item>
            <el-menu-item index="/material-management">
              <el-icon><Picture /></el-icon>
              <span>素材管理</span>
            </el-menu-item>
            <el-menu-item index="/publish-center">
              <el-icon><Upload /></el-icon>
              <span>发布中心</span>
            </el-menu-item>
            <el-menu-item index="/task-center">
              <el-icon><List /></el-icon>
              <span>任务中心</span>
            </el-menu-item>
            <el-menu-item index="/publish-history">
              <el-icon><Clock /></el-icon>
              <span>发布历史</span>
            </el-menu-item>
            <el-menu-item index="/settings">
              <el-icon><Setting /></el-icon>
              <span>系统设置</span>
            </el-menu-item>
          </el-menu>
        </div>
      </el-aside>
      <el-container>
        <el-header>
          <div class="header-content">
            <div class="header-left">
              <el-icon class="toggle-sidebar" @click="toggleSidebar"><Fold /></el-icon>
            </div>
            <div class="header-right">
              <!-- reserved -->
            </div>
          </div>
        </el-header>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  HomeFilled, User, Picture, Upload,
  List, Clock, Setting, Fold
} from '@element-plus/icons-vue'

const route = useRoute()

// 当前激活的菜单项
const activeMenu = computed(() => {
  return route.path
})

// 侧边栏折叠状态
const isCollapse = ref(false)

// 切换侧边栏折叠状态
const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

#app {
  min-height: 100vh;
}

.el-container {
  height: 100vh;
}

.el-aside {
  background-color: #0a0f1e;
  color: $text-primary;
  height: 100vh;
  overflow: hidden;
  transition: width $transition-normal;
  border-right: 1px solid rgba(255, 255, 255, 0.06);

  .sidebar {
    display: flex;
    flex-direction: column;
    height: 100%;

    .logo {
      height: 64px;
      padding: 0 20px;
      display: flex;
      align-items: center;
      overflow: hidden;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);

      .logo-img {
        width: 32px;
        height: 32px;
        margin-right: 12px;
      }

      h2 {
        color: $text-primary;
        font-size: 16px;
        font-weight: 700;
        white-space: nowrap;
        margin: 0;
        letter-spacing: -0.3px;
      }
    }

    .sidebar-menu {
      border-right: none;
      flex: 1;
      padding: 8px;

      .el-menu-item {
        display: flex;
        align-items: center;
        height: 44px;
        line-height: 44px;
        margin-bottom: 2px;
        border-radius: 10px;
        transition: all 0.2s;

        .el-icon {
          margin-right: 12px;
          font-size: 18px;
          transition: color 0.2s;
        }

        span {
          font-size: 14px;
          font-weight: 500;
        }

        &.is-active {
          color: #fff;
          background-color: rgba($primary-color, 0.15);

          .el-icon {
            color: $primary-color;
          }

          span {
            color: #fff;
            font-weight: 600;
          }
        }

        &:hover:not(.is-active) {
          background-color: rgba(255, 255, 255, 0.05);

          .el-icon {
            color: $text-primary;
          }
        }
      }
    }
  }
}

.el-header {
  background-color: $bg-color-overlay;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding: 0;
  height: 56px;

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 100%;
    padding: 0 20px;

    .header-left {
      .toggle-sidebar {
        font-size: 20px;
        cursor: pointer;
        color: $text-secondary;
        padding: 6px;
        border-radius: 6px;
        transition: all 0.2s;

        &:hover {
          color: $primary-color;
          background-color: rgba($primary-color, 0.1);
        }
      }
    }

    .header-right {
      .user-dropdown {
        display: flex;
        align-items: center;
        cursor: pointer;

        .username {
          margin: 0 8px;
          color: $text-secondary;
        }

        .el-icon {
          font-size: 12px;
          color: $text-muted;
        }
      }
    }
  }
}

.el-main {
  background-color: $bg-color-page;
  padding: 24px;
  overflow-y: auto;
}
</style>
