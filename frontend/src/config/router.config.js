// eslint-disable-next-line
import { UserLayout, BasicLayout, BlankLayout } from '@/layouts'

export const asyncRouterMap = [
  {
    path: '/',
    name: 'index',
    component: BasicLayout,
    meta: { title: 'menu.home' },
    redirect: '/ai-asset-analysis',
    children: [
      // 1. AI智能分析（首页）
      // keepAlive: true so the heavy market-data fetches (sentiment / indices /
      // heatmap / calendar / opportunities / watchlist prices) only run on the
      // first visit. The component handles its own "data is stale" refresh in
      // `activated()`. Disabling this again will reintroduce a 1~3s cold start
      // every time the user navigates back here.
      {
        path: '/ai-asset-analysis',
        name: 'AIAssetAnalysis',
        component: () => import('@/views/ai-asset-analysis'),
        meta: { title: 'menu.dashboard.aiAssetAnalysis', keepAlive: true, icon: 'appstore', permission: ['dashboard'] }
      },
      // 2. 数据中心（统一入口：指标 / 脚本 / 机器人 / 回测历史）
      {
        path: '/strategy-center',
        name: 'StrategyCenter',
        component: () => import('@/views/strategy-center'),
        meta: { title: 'menu.dashboard.strategyCenter', keepAlive: true, icon: 'cluster', permission: ['dashboard'] }
      },
      // 3. 指标市场
      {
        path: '/indicator-community',
        name: 'IndicatorCommunity',
        component: () => import('@/views/indicator-community'),
        meta: { title: 'menu.dashboard.community', keepAlive: false, icon: 'shop', permission: ['dashboard'] }
      },
      // 4. 指标 IDE（图表 + 代码编辑 + 回测一体化）
      {
        path: '/indicator-ide',
        name: 'IndicatorIDE',
        component: () => import('@/views/indicator-ide'),
        meta: { title: 'menu.dashboard.indicatorIde', keepAlive: true, icon: 'code', permission: ['dashboard'] }
      },
      // 5. 指标策略 — 概览已合并至数据中心
      {
        path: '/strategy-live',
        name: 'StrategyLive',
        component: () => import('@/views/trading-assistant'),
        meta: {
          title: 'menu.dashboard.tradingAssistant',
          keepAlive: true,
          icon: 'deployment-unit',
          permission: ['dashboard'],
          indicatorSignalOnly: true
        },
        beforeEnter: (to, from, next) => {
          if (to.query.tab === 'overview') {
            next({ path: '/strategy-center', query: { tab: 'overview' }, replace: true })
          } else {
            next()
          }
        }
      },
      // 6. 策略工作室（Python ScriptStrategy）
      {
        path: '/strategy-script',
        name: 'StrategyScript',
        component: () => import('@/views/trading-assistant'),
        meta: {
          title: 'menu.dashboard.scriptStrategies',
          keepAlive: true,
          icon: 'code-sandbox',
          permission: ['dashboard'],
          scriptStrategiesOnly: true
        }
      },
      {
        path: '/strategy-scripts',
        redirect: '/strategy-live',
        hidden: true
      },
      // 7. 交易机器人
      {
        path: '/trading-bot',
        name: 'TradingBot',
        component: () => import('@/views/trading-bot'),
        meta: { title: 'menu.dashboard.tradingBot', keepAlive: true, icon: 'robot', permission: ['dashboard'] }
      },
      {
        path: '/memory',
        name: 'Memory',
        component: () => import('@/views/memory'),
        hidden: true,
        meta: { title: 'menu.memory', keepAlive: true, icon: 'database', permission: ['dashboard'] }
      },
      // 8. 券商账户
      {
        path: '/broker-accounts',
        name: 'BrokerAccounts',
        component: () => import('@/views/broker-accounts'),
        meta: { title: 'menu.dashboard.brokerAccounts', keepAlive: true, icon: 'bank', permission: ['dashboard'] }
      },
      // 旧路由兼容：图表与指标 → 指标 IDE
      {
        path: '/indicator-analysis',
        name: 'Indicator',
        redirect: '/indicator-ide',
        hidden: true,
        meta: { title: 'menu.dashboard.indicator', keepAlive: false, icon: 'line-chart', permission: ['dashboard'] }
      },
      {
        path: '/backtest-center',
        name: 'BacktestCenter',
        redirect: '/indicator-ide',
        hidden: true,
        meta: { title: 'menu.dashboard.backtestCenter', keepAlive: false, icon: 'experiment', permission: ['dashboard'] }
      },
      // 旧路由兼容：交易助手 → 策略与实盘
      {
        path: '/trading-assistant',
        name: 'TradingAssistant',
        redirect: '/strategy-live',
        hidden: true,
        meta: { title: 'menu.dashboard.tradingAssistant', keepAlive: false, icon: 'deployment-unit', permission: ['dashboard'] }
      },
      // 原仪表盘路由保留兼容，重定向到交易助手
      {
        path: '/dashboard',
        name: 'Dashboard',
        redirect: '/trading-bot',
        hidden: true,
        meta: { title: 'menu.dashboard', keepAlive: false, icon: 'dashboard', permission: ['dashboard'] }
      },
      // AI 分析（隐藏）
      {
        path: '/ai-analysis/:pageNo([1-9]\\d*)?',
        name: 'Analysis',
        component: () => import('@/views/ai-analysis'),
        hidden: true,
        meta: { title: 'menu.dashboard.analysis', keepAlive: false, icon: 'thunderbolt', permission: ['dashboard'] }
      },
      // 资产监测（隐藏）
      {
        path: '/portfolio',
        name: 'Portfolio',
        component: () => import('@/views/portfolio'),
        hidden: true,
        meta: { title: 'menu.dashboard.portfolio', keepAlive: true, icon: 'fund', permission: ['dashboard'] }
      },
      // 会员/充值
      {
        path: '/billing',
        name: 'Billing',
        component: () => import('@/views/billing'),
        meta: { title: 'menu.billing', keepAlive: false, icon: 'wallet', permission: ['dashboard'] }
      },
      // 个人中心（下方分隔线后为管理员菜单）
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/profile'),
        meta: { title: 'menu.myProfile', keepAlive: false, icon: 'user', permission: ['dashboard'], menuDividerAfter: true }
      },
      // 用户管理 (admin only)
      {
        path: '/user-manage',
        name: 'UserManage',
        component: () => import('@/views/user-manage'),
        meta: { title: 'menu.userManage', keepAlive: false, icon: 'team', permission: ['admin'] }
      },
      // Agent Tokens (admin only) — issue/revoke tokens for AI agents and view audit log
      {
        path: '/agent-tokens',
        name: 'AgentTokens',
        component: () => import('@/views/agent-tokens'),
        meta: { title: 'menu.agentTokens', keepAlive: false, icon: 'api', permission: ['admin'] }
      },
      // 系统设置 (admin only) - 放在最后
      {
        path: '/settings',
        name: 'Settings',
        component: () => import('@/views/settings'),
        meta: { title: 'menu.settings', keepAlive: false, icon: 'setting', permission: ['admin'] }
      }

      // other
      /*
      {
        path: '/other',
        name: 'otherPage',
        component: PageView,
        meta: { title: '其他组件', icon: 'slack', permission: [ 'dashboard' ] },
        redirect: '/other/icon-selector',
        children: [
          {
            path: '/other/icon-selector',
            name: 'TestIconSelect',
            component: () => import('@/views/other/IconSelectorView'),
            meta: { title: 'IconSelector', icon: 'tool', keepAlive: true, permission: [ 'dashboard' ] }
          },
          {
            path: '/other/list',
            component: RouteView,
            meta: { title: '业务布局', icon: 'layout', permission: [ 'support' ] },
            redirect: '/other/list/tree-list',
            children: [
              {
                path: '/other/list/tree-list',
                name: 'TreeList',
                component: () => import('@/views/other/TreeList'),
                meta: { title: '树目录表格', keepAlive: true }
              },
              {
                path: '/other/list/edit-table',
                name: 'EditList',
                component: () => import('@/views/other/TableInnerEditList'),
                meta: { title: '内联编辑表格', keepAlive: true }
              },
              {
                path: '/other/list/user-list',
                name: 'UserList',
                component: () => import('@/views/other/UserList'),
                meta: { title: '用户列表', keepAlive: true }
              },
              {
                path: '/other/list/role-list',
                name: 'RoleList',
                component: () => import('@/views/other/RoleList'),
                meta: { title: '角色列表', keepAlive: true }
              },
              {
                path: '/other/list/system-role',
                name: 'SystemRole',
                component: () => import('@/views/role/RoleList'),
                meta: { title: '角色列表2', keepAlive: true }
              },
              {
                path: '/other/list/permission-list',
                name: 'PermissionList',
                component: () => import('@/views/other/PermissionList'),
                meta: { title: '权限列表', keepAlive: true }
              }
            ]
          }
        ]
      }
      */
    ]
  },
  {
    path: '*',
    redirect: '/404',
    hidden: true
  }
]

/**
 * 基础路由
 * @type { *[] }
 */
export const constantRouterMap = [
  {
    path: '/user',
    component: UserLayout,
    redirect: '/user/login',
    hidden: true,
    children: [
      {
        path: 'login',
        name: 'login',
        component: () => import(/* webpackChunkName: "user" */ '@/views/user/Login')
      }
    ]
  },

  {
    path: '/404',
    component: () => import(/* webpackChunkName: "fail" */ '@/views/exception/404')
  }
]
