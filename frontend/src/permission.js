import router, {
  resetRouter
} from './router'
import store from './store'
import storage from 'store'
import NProgress from 'nprogress' // progress bar
import '@/components/NProgress/nprogress.less' // progress bar custom style
import {
  setDocumentTitle,
  domTitle
} from '@/utils/domUtil'
import {
  ACCESS_TOKEN,
  USER_INFO,
  USER_ROLES
} from '@/store/mutation-types'
import {
  i18nRender
} from '@/locales'
import { promptChangeInitialPassword } from '@/utils/initialPasswordReminder'

NProgress.configure({
  showSpinner: false
}) // NProgress Configuration

const allowList = ['login'] // no redirect allowList
const loginRoutePath = '/user/login'
const defaultRoutePath = '/ai-asset-analysis'

router.beforeEach((to, from, next) => {
  NProgress.start() // start progress bar
  to.meta && typeof to.meta.title !== 'undefined' && setDocumentTitle(`${i18nRender(to.meta.title)} - ${domTitle}`)

  // Check whether we have a token (local-only auth).
  // 处理 token 可能是字符串或对象的情况
  let token = storage.get(ACCESS_TOKEN)
  if (token && typeof token !== 'string') {
    token = token.token || token.value || (typeof token === 'object' ? null : token)
  }
  token = typeof token === 'string' ? token : null

  // Create demo token if missing (for demo/dev mode without auth backend)
  if (!token) {
    token = 'demo-token-' + Date.now()
    storage.set(ACCESS_TOKEN, token)
    store.commit('SET_TOKEN', token)
  }

  // 有 token，允许访问所有页面
  if (to.path === loginRoutePath) {
    next({ path: defaultRoutePath })
    NProgress.done()
  } else {
    // 检查用户信息是否已加载
    if (store.getters.roles.length === 0) {
      // 如果没有用户信息，设置默认用户
      const defaultUser = {
        username: 'Demo User',
        nickname: 'Demo User',
        avatar: '/avatar2.jpg',
        is_demo: true,
        must_change_initial_password: false,
        role: { id: 'default', permissionList: [] }
      }
      store.commit('SET_INFO', defaultUser)
      store.commit('SET_NAME', { name: defaultUser.username, welcome: 'Welcome' })
      store.commit('SET_ROLES', [{ id: 'default', permissionList: [] }])
      storage.set(USER_INFO, defaultUser, new Date().getTime() + 7 * 24 * 60 * 60 * 1000)
      storage.set(USER_ROLES, [{ id: 'default', permissionList: [] }], new Date().getTime() + 7 * 24 * 60 * 60 * 1000)

      // 生成路由
      store.dispatch('GenerateRoutes', { token }).then(() => {
        // 动态添加可访问路由表
        resetRouter()
        store.getters.addRouters.forEach(r => {
          router.addRoute(r)
        })
        // 重新进入当前路由
        next({ ...to, replace: true })
      }).catch(() => {
        next()
      })
    } else {
      // 检查路由是否已初始化
      const addRouters = store.getters.addRouters
      if (!addRouters || addRouters.length === 0) {
        store.dispatch('GenerateRoutes', { token }).then(() => {
          resetRouter()
          store.getters.addRouters.forEach(r => {
            router.addRoute(r)
          })
          next({ ...to, replace: true })
        }).catch(() => {
          next()
        })
      } else {
        next()
      }
    }
  }
})

router.afterEach(() => {
  NProgress.done() // finish progress bar
})
