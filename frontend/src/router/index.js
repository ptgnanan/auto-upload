import { createRouter, createWebHashHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import AccountManagement from '../views/AccountManagement.vue'
import MaterialManagement from '../views/MaterialManagement.vue'
import PublishCenter from '../views/PublishCenter.vue'
import PublishHistory from '../views/PublishHistory.vue'
import TaskCenter from '../views/TaskCenter.vue'
import Settings from '../views/Settings.vue'
import Author from '../views/Author.vue'
import About from '../views/About.vue'

const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard, meta: { icon: 'HomeFilled', title: '仪表盘' } },
  { path: '/account-management', name: 'AccountManagement', component: AccountManagement, meta: { icon: 'User', title: '账号管理' } },
  { path: '/material-management', name: 'MaterialManagement', component: MaterialManagement, meta: { icon: 'Picture', title: '素材管理' } },
  { path: '/publish-center', name: 'PublishCenter', component: PublishCenter, meta: { icon: 'Upload', title: '发布中心', keepAlive: true } },
  { path: '/publish-history', name: 'PublishHistory', component: PublishHistory, meta: { icon: 'Clock', title: '发布历史' } },
  { path: '/task-center', name: 'TaskCenter', component: TaskCenter, meta: { icon: 'List', title: '任务中心' } },
  { path: '/settings', name: 'Settings', component: Settings, meta: { icon: 'Setting', title: '系统设置', isBottom: true } },
  { path: '/author', name: 'Author', component: Author, meta: { icon: 'UserFilled', title: '关于作者', isBottom: true } },
  { path: '/about', name: 'About', component: About, meta: { icon: 'InfoFilled', title: '关于项目', isBottom: true } }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
