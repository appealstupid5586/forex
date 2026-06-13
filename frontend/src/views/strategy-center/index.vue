<template>
  <div class="strategy-center" :class="{ 'theme-dark': isDarkTheme }">
    <!-- 顶栏：标题 + 快捷操作 -->
    <header class="sc-header">
      <div class="sc-header-main">
        <div class="sc-header-badge">
          <a-icon type="cluster" />
          {{ $t('strategyCenter.header.badge') }}
        </div>
        <h1 class="sc-header-title">{{ $t('strategyCenter.title') }}</h1>
        <p class="sc-header-sub">{{ $t('strategyCenter.subtitle') }}</p>
      </div>
      <div class="sc-header-actions">
        <a-button type="primary" class="sc-action-btn sc-action-btn--primary" @click="go('/strategy-live?tab=strategy&mode=create')">
          <a-icon type="plus" /> {{ $t('strategyCenter.header.createIndicatorStrategy') }}
        </a-button>
        <a-button class="sc-action-btn" @click="go('/strategy-script?tab=strategy&mode=create')">
          <a-icon type="code" /> {{ $t('strategyCenter.header.createScriptStrategy') }}
        </a-button>
        <a-button class="sc-action-btn" @click="go('/trading-bot')">
          <a-icon type="robot" /> {{ $t('strategyCenter.header.createBot') }}
        </a-button>
      </div>
    </header>

    <!-- 迷你统计条（与概览 KPI 互补，展示库内资产） -->
    <div class="sc-mini-stats">
      <div v-for="item in miniStatItems" :key="item.key" class="sc-mini-stat" @click="item.path && go(item.path)">
        <span class="sc-mini-stat-icon" :class="`sc-mini-stat-icon--${item.key}`">
          <a-icon :type="item.icon" />
        </span>
        <div class="sc-mini-stat-body">
          <span class="sc-mini-stat-num">{{ item.value }}</span>
          <span class="sc-mini-stat-label">{{ item.label }}</span>
        </div>
        <a-icon v-if="item.path" type="right" class="sc-mini-stat-arrow" />
      </div>
    </div>

    <!-- 主 Tab -->
    <a-tabs v-model="activeTab" class="sc-tabs" :animated="false">
      <a-tab-pane key="overview" :tab="$t('strategyCenter.tabs.overview')">
        <div class="sc-dashboard-wrap">
          <dashboard-overview v-if="activeTab === 'overview'" hide-setup-guide embedded />
        </div>
      </a-tab-pane>

      <a-tab-pane key="workspace" :tab="$t('strategyCenter.tabs.workspace')">
        <div class="sc-workspace">
          <div class="sc-entry-grid">
            <div
              v-for="card in entryCards"
              :key="card.key"
              class="sc-entry-card"
              :class="`sc-entry-card--${card.key}`"
              @click="go(card.path)"
            >
              <div class="sc-entry-card-glow" />
              <span v-if="card.badge" class="sc-entry-card-badge">{{ card.badge }}</span>
              <div class="sc-entry-card-icon">
                <a-icon :type="card.icon" />
              </div>
              <div class="sc-entry-card-body">
                <h3>{{ card.title }}</h3>
                <p>{{ card.desc }}</p>
                <p v-if="card.suit" class="sc-entry-card-suit">{{ card.suit }}</p>
              </div>
              <div class="sc-entry-card-footer">
                <span>{{ card.action }}</span>
                <a-icon type="arrow-right" />
              </div>
              <button
                v-if="card.secondaryPath"
                type="button"
                class="sc-entry-card-secondary"
                @click.stop="go(card.secondaryPath)"
              >
                {{ card.secondaryLabel }}
              </button>
            </div>
          </div>

          <div class="sc-manage-section">
            <h3 class="sc-section-title">{{ $t('strategyCenter.workspace.manageTitle') }}</h3>
            <div class="sc-manage-grid">
              <div
                v-for="link in manageLinks"
                :key="link.path"
                class="sc-manage-tile"
                @click="go(link.path)"
              >
                <a-icon :type="link.icon" />
                <span>{{ link.label }}</span>
              </div>
            </div>
          </div>

          <div class="sc-flow-banner">
            <div class="sc-flow-banner-icon"><a-icon type="bulb" theme="filled" /></div>
            <div class="sc-flow-banner-text">
              <strong>{{ $t('strategyCenter.flowHintTitle') }}</strong>
              <span>{{ $t('strategyCenter.flowHintDesc') }}</span>
            </div>
          </div>
        </div>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import request from '@/utils/request'
import { getStrategyList } from '@/api/strategy'
import DashboardOverview from '@/views/dashboard/index.vue'

export default {
  name: 'StrategyCenter',
  components: { DashboardOverview },
  data () {
    return {
      activeTab: 'overview',
      loadingStats: false,
      stats: { indicator: 0, signal: 0, script: 0, bot: 0, running: 0 }
    }
  },
  computed: {
    ...mapState({
      navTheme: state => state.app.theme
    }),
    isDarkTheme () {
      return this.navTheme === 'dark' || this.navTheme === 'realdark'
    },
    miniStatItems () {
      return [
        { key: 'running', icon: 'thunderbolt', value: this.stats.running, label: this.$t('strategyCenter.stats.running'), path: '/strategy-center?tab=workspace' },
        { key: 'signal', icon: 'deployment-unit', value: this.stats.signal, label: this.$t('strategyCenter.stats.indicatorStrategy'), path: '/strategy-live?tab=strategy' },
        { key: 'script', icon: 'code-sandbox', value: this.stats.script, label: this.$t('strategyCenter.stats.script'), path: '/strategy-script?tab=strategy' },
        { key: 'bot', icon: 'robot', value: this.stats.bot, label: this.$t('strategyCenter.stats.bot'), path: '/trading-bot' },
        { key: 'indicator', icon: 'line-chart', value: this.stats.indicator, label: this.$t('strategyCenter.stats.ownIndicators'), path: '/indicator-ide' }
      ]
    },
    entryCards () {
      return [
        {
          key: 'signal',
          icon: 'deployment-unit',
          badge: this.$t('strategyCenter.card.signal.badge'),
          title: this.$t('strategyCenter.card.signal.title'),
          desc: this.$t('strategyCenter.card.signal.desc'),
          suit: this.$t('strategyCenter.card.signal.suit'),
          action: this.$t('strategyCenter.card.signal.action'),
          path: '/strategy-live?tab=strategy&mode=create',
          secondaryLabel: this.$t('strategyCenter.card.signal.secondary'),
          secondaryPath: '/indicator-ide'
        },
        {
          key: 'script',
          icon: 'code',
          badge: this.$t('strategyCenter.card.script.badge'),
          title: this.$t('strategyCenter.card.script.title'),
          desc: this.$t('strategyCenter.card.script.desc'),
          suit: this.$t('strategyCenter.card.script.suit'),
          action: this.$t('strategyCenter.card.script.action'),
          path: '/strategy-script?tab=strategy&mode=create'
        },
        {
          key: 'bot',
          icon: 'robot',
          badge: this.$t('strategyCenter.card.bot.badge'),
          title: this.$t('strategyCenter.card.bot.title'),
          desc: this.$t('strategyCenter.card.bot.desc'),
          suit: this.$t('strategyCenter.card.bot.suit'),
          action: this.$t('strategyCenter.card.bot.action'),
          path: '/trading-bot'
        }
      ]
    },
    manageLinks () {
      return [
        { icon: 'deployment-unit', label: this.$t('strategyCenter.library.indicatorStrategies'), path: '/strategy-live?tab=strategy' },
        { icon: 'code-sandbox', label: this.$t('strategyCenter.library.scriptStrategies'), path: '/strategy-script?tab=strategy' },
        { icon: 'robot', label: this.$t('strategyCenter.library.bots'), path: '/trading-bot' },
        { icon: 'shop', label: this.$t('strategyCenter.library.marketplace'), path: '/indicator-community' },
        { icon: 'bank', label: this.$t('menu.dashboard.brokerAccounts'), path: '/broker-accounts' },
        { icon: 'code', label: this.$t('menu.dashboard.indicatorIde'), path: '/indicator-ide' }
      ]
    }
  },
  watch: {
    '$route.query.tab' (tab) {
      this.syncTabFromRoute(tab)
    }
  },
  mounted () {
    this.syncTabFromRoute(this.$route.query.tab)
    this.loadStats()
  },
  methods: {
    syncTabFromRoute (tab) {
      const t = String(tab || '').toLowerCase()
      if (t === 'history') {
        this.activeTab = 'overview'
        this.$router.replace({ path: '/strategy-center', query: { tab: 'overview' } }).catch(() => {})
        return
      }
      if (t === 'workspace' || t === 'library') this.activeTab = 'workspace'
      else if (t === 'overview' || !t) this.activeTab = 'overview'
    },
    go (path) {
      if (!path) return
      const qIdx = path.indexOf('?')
      if (qIdx > -1) {
        const routePath = path.slice(0, qIdx)
        const qs = new URLSearchParams(path.slice(qIdx + 1))
        const query = {}
        qs.forEach((v, k) => { query[k] = v })
        this.$router.push({ path: routePath, query }).catch(() => {})
      } else {
        this.$router.push(path).catch(() => {})
      }
    },
    strategyModeBucket (s) {
      const mode = String((s && s.strategy_mode) || '').trim().toLowerCase()
      if (mode === 'bot') return 'bot'
      if (mode === 'script') return 'script'
      return 'signal'
    },
    isRunningStrategy (s) {
      return String((s && s.status) || '').trim().toLowerCase() === 'running'
    },
    parseStrategyList (res) {
      if (!res || res.code !== 1 || !res.data) return []
      if (Array.isArray(res.data)) return res.data
      if (Array.isArray(res.data.strategies)) return res.data.strategies
      return []
    },
    async loadStats () {
      this.loadingStats = true
      try {
        const [strRes, indRes] = await Promise.all([
          getStrategyList(),
          request({ url: '/api/indicator/getIndicators', method: 'get' }).catch(() => ({ code: 0, data: [] }))
        ])
        const list = this.parseStrategyList(strRes)
        this.stats.signal = list.filter(s => this.strategyModeBucket(s) === 'signal').length
        this.stats.script = list.filter(s => this.strategyModeBucket(s) === 'script').length
        this.stats.bot = list.filter(s => this.strategyModeBucket(s) === 'bot').length
        this.stats.running = list.filter(s => this.isRunningStrategy(s)).length
        const inds = (indRes.code === 1 && Array.isArray(indRes.data)) ? indRes.data : []
        this.stats.indicator = inds.filter(i => Number(i.is_buy || 0) !== 1).length
      } finally {
        this.loadingStats = false
      }
    }
  }
}
</script>

<style lang="less" scoped>
@sc-blue: #1677ff;
@sc-purple: #722ed1;
@sc-teal: #13c2c2;
@sc-radius: 14px;
@sc-shadow: 0 4px 24px rgba(15, 23, 42, 0.06);

.strategy-center {
  min-height: calc(100vh - 120px);
  padding: 20px 24px 32px;
  background: linear-gradient(180deg, #f0f5ff 0%, #f5f7fa 38%, #f8fafc 100%);
}

.sc-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.sc-header-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  color: @sc-blue;
  background: rgba(22, 119, 255, 0.1);
  border: 1px solid rgba(22, 119, 255, 0.18);
  margin-bottom: 10px;
}

.sc-header-title {
  margin: 0 0 6px;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #0f172a;
}

.sc-header-sub {
  margin: 0;
  max-width: 560px;
  font-size: 14px;
  line-height: 1.6;
  color: #64748b;
}

.sc-header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.sc-action-btn {
  height: 38px;
  border-radius: 10px;
  font-weight: 500;
  box-shadow: @sc-shadow;

  &--primary {
    background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);
    border: none;
  }
}

.sc-mini-stats {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 20px;

  @media (max-width: 1100px) {
    grid-template-columns: repeat(3, 1fr);
  }
  @media (max-width: 640px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.sc-mini-stat {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: #fff;
  border-radius: @sc-radius;
  border: 1px solid rgba(226, 232, 240, 0.9);
  box-shadow: @sc-shadow;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(15, 23, 42, 0.08);
    border-color: rgba(22, 119, 255, 0.25);
  }
}

.sc-mini-stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;

  &--running { background: rgba(82, 196, 26, 0.12); color: #52c41a; }
  &--signal { background: rgba(22, 119, 255, 0.12); color: @sc-blue; }
  &--script { background: rgba(114, 46, 209, 0.12); color: @sc-purple; }
  &--bot { background: rgba(19, 194, 194, 0.12); color: @sc-teal; }
  &--indicator { background: rgba(250, 173, 20, 0.12); color: #fa8c16; }
}

.sc-mini-stat-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.sc-mini-stat-num {
  font-size: 22px;
  font-weight: 700;
  line-height: 1.2;
  color: #0f172a;
}

.sc-mini-stat-label {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}

.sc-mini-stat-arrow {
  color: #cbd5e1;
  font-size: 12px;
}

.sc-tabs {
  ::v-deep .ant-tabs-bar {
    margin-bottom: 16px;
    border-bottom: 1px solid #e2e8f0;
  }
  ::v-deep .ant-tabs-tab {
    font-size: 14px;
    font-weight: 500;
    padding: 10px 4px;
    margin-right: 28px;
  }
  ::v-deep .ant-tabs-tab-active {
    font-weight: 600;
  }
  ::v-deep .ant-tabs-ink-bar {
    height: 3px;
    border-radius: 3px 3px 0 0;
  }
}

.sc-dashboard-wrap {
  margin: 0 -8px;
  border-radius: @sc-radius;
  overflow: hidden;

  ::v-deep .dashboard-pro.dashboard-pro--embedded {
    min-height: auto;
    padding: 0 8px 8px;
    background: transparent;
  }
}

.sc-workspace {
  padding-top: 4px;
}

.sc-entry-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 28px;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
}

.sc-entry-card {
  position: relative;
  padding: 24px;
  border-radius: 16px;
  background: #fff;
  border: 1px solid #e8ecf1;
  cursor: pointer;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(15, 23, 42, 0.1);

    .sc-entry-card-footer .anticon {
      transform: translateX(4px);
    }
  }

  &--signal .sc-entry-card-icon { background: linear-gradient(135deg, #1677ff, #69b1ff); }
  &--script .sc-entry-card-icon { background: linear-gradient(135deg, #722ed1, #b37feb); }
  &--bot .sc-entry-card-icon { background: linear-gradient(135deg, #13c2c2, #5cdbd3); }
}

.sc-entry-card-glow {
  position: absolute;
  top: -40%;
  right: -20%;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  opacity: 0.08;
  pointer-events: none;
}

.sc-entry-card--signal .sc-entry-card-glow { background: @sc-blue; }
.sc-entry-card--script .sc-entry-card-glow { background: @sc-purple; }
.sc-entry-card--bot .sc-entry-card-glow { background: @sc-teal; }

.sc-entry-card-badge {
  display: inline-block;
  margin-bottom: 12px;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
  background: rgba(22, 119, 255, 0.08);
  color: @sc-blue;
}

.sc-entry-card--script .sc-entry-card-badge {
  background: rgba(114, 46, 209, 0.08);
  color: @sc-purple;
}

.sc-entry-card--bot .sc-entry-card-badge {
  background: rgba(19, 194, 194, 0.1);
  color: @sc-teal;
}

.sc-entry-card-suit {
  margin-top: 8px !important;
  min-height: auto !important;
  font-size: 12px !important;
  color: #94a3b8 !important;
}

.sc-entry-card-secondary {
  display: block;
  width: 100%;
  margin-top: 10px;
  padding: 0;
  border: none;
  background: none;
  text-align: left;
  font-size: 12px;
  color: #64748b;
  cursor: pointer;
  transition: color 0.15s;

  &:hover {
    color: @sc-blue;
    text-decoration: underline;
  }
}

.sc-entry-card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 22px;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.sc-entry-card-body {
  h3 {
    margin: 0 0 8px;
    font-size: 17px;
    font-weight: 600;
    color: #0f172a;
  }
  p {
    margin: 0;
    font-size: 13px;
    line-height: 1.55;
    color: #64748b;
    min-height: 40px;
  }
}

.sc-entry-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
  font-size: 13px;
  font-weight: 600;
  color: @sc-blue;

  .anticon {
    transition: transform 0.2s;
  }
}

.sc-section-title {
  margin: 0 0 14px;
  font-size: 15px;
  font-weight: 600;
  color: #334155;
}

.sc-manage-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 10px;
  margin-bottom: 24px;
}

.sc-manage-tile {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  background: #fff;
  border: 1px solid #e8ecf1;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s;

  .anticon {
    font-size: 16px;
    color: @sc-blue;
  }

  &:hover {
    border-color: rgba(22, 119, 255, 0.35);
    color: @sc-blue;
    background: rgba(22, 119, 255, 0.04);
  }
}

.sc-flow-banner {
  display: flex;
  gap: 14px;
  padding: 16px 20px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(22, 119, 255, 0.06) 0%, rgba(114, 46, 209, 0.05) 100%);
  border: 1px solid rgba(22, 119, 255, 0.12);
}

.sc-flow-banner-icon {
  font-size: 22px;
  color: #faad14;
  flex-shrink: 0;
}

.sc-flow-banner-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
  line-height: 1.6;
  color: #64748b;

  strong {
    color: #334155;
    font-size: 14px;
  }
}

.theme-dark {
  background: linear-gradient(180deg, #141414 0%, #1a1a1a 100%);

  .sc-header-title { color: rgba(255, 255, 255, 0.92); }
  .sc-header-sub { color: rgba(255, 255, 255, 0.45); }
  .sc-mini-stat,
  .sc-entry-card,
  .sc-manage-tile {
    background: #1f1f1f;
    border-color: #303030;
  }
  .sc-mini-stat-num { color: rgba(255, 255, 255, 0.92); }
  .sc-entry-card-body h3 { color: rgba(255, 255, 255, 0.92); }
  .sc-entry-card-body p,
  .sc-mini-stat-label,
  .sc-flow-banner-text,
  .sc-entry-card-suit { color: rgba(255, 255, 255, 0.45); }
  .sc-section-title,
  .sc-flow-banner-text strong { color: rgba(255, 255, 255, 0.75); }
  .sc-tabs ::v-deep .ant-tabs-bar { border-color: #303030; }
}
</style>
