<template>
  <div class="position-records strategy-tab-pane-inner" :class="{ 'theme-dark': isDark }">
    <div class="positions-section">
      <div v-if="positions.length === 0 && !loading" class="empty-state strategy-tab-empty">
        <a-empty :description="$t('trading-assistant.table.noPositions')" />
      </div>
      <a-table
        v-else
        :columns="columns"
        :data-source="positions"
        :loading="loading"
        :pagination="false"
        size="small"
        rowKey="id"
        :scroll="{ x: 800 }"
      >
        <template slot="symbol" slot-scope="text, record">
          <strong>{{ record.symbol || text }}</strong>
        </template>
        <template slot="side" slot-scope="text, record">
          <a-tag :color="(record.side || text) === 'long' ? 'green' : 'red'">
            {{ (record.side || text) === 'long' ? $t('trading-assistant.table.long') : $t('trading-assistant.table.short') }}
          </a-tag>
        </template>
        <template slot="entryPrice" slot-scope="text, record">
          <span v-if="hasValidPrice(record.entry_price || text)">
            ${{ parseFloat(record.entry_price || text).toFixed(4) }}
          </span>
          <span v-else>--</span>
        </template>
        <template slot="currentPrice" slot-scope="text, record">
          ${{ parseFloat(record.current_price || text || 0).toFixed(4) }}
        </template>
        <template slot="size" slot-scope="text, record">
          {{ parseFloat(record.size || text || 0).toFixed(4) }}
        </template>
        <template slot="notional" slot-scope="text, record">
          <span v-if="getNotional(record) > 0">${{ getNotional(record).toFixed(2) }}</span>
          <span v-else>--</span>
        </template>
        <template slot="unrealizedPnl" slot-scope="text, record">
          <span :class="{ 'profit': parseFloat(record.unrealized_pnl || text || 0) > 0, 'loss': parseFloat(record.unrealized_pnl || text || 0) < 0 }">
            ${{ parseFloat(record.unrealized_pnl || text || 0).toFixed(2) }}
          </span>
        </template>
        <template slot="pnlPercent" slot-scope="text, record">
          <span :class="{ 'profit': parseFloat(record.pnl_percent || text || 0) > 0, 'loss': parseFloat(record.pnl_percent || text || 0) < 0 }">
            {{ parseFloat(record.pnl_percent || text || 0).toFixed(2) }}%
          </span>
        </template>
      </a-table>
    </div>
  </div>
</template>

<script>
import { getStrategyPositions } from '@/api/strategy'

export default {
  name: 'PositionRecords',
  props: {
    strategyId: {
      type: Number,
      required: true
    },
    executionMode: {
      type: String,
      default: 'signal'
    },
    marketType: {
      type: String,
      default: 'swap'
    },
    leverage: {
      type: [Number, String],
      default: 1
    },
    loading: {
      type: Boolean,
      default: false
    },
    isDark: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      positions: []
    }
  },
  computed: {
    columns () {
      return [
        {
          title: this.$t('trading-assistant.table.symbol'),
          dataIndex: 'symbol',
          key: 'symbol',
          width: 120,
          scopedSlots: { customRender: 'symbol' }
        },
        {
          title: this.$t('trading-assistant.table.side'),
          dataIndex: 'side',
          key: 'side',
          width: 80,
          scopedSlots: { customRender: 'side' }
        },
        {
          title: this.$t('trading-assistant.table.size'),
          dataIndex: 'size',
          key: 'size',
          width: 120,
          scopedSlots: { customRender: 'size' }
        },
        {
          title: this.$t('trading-assistant.table.notional') || 'Value (USDT)',
          dataIndex: 'notional',
          key: 'notional',
          width: 130,
          scopedSlots: { customRender: 'notional' }
        },
        {
          title: this.$t('trading-assistant.table.entryPrice'),
          dataIndex: 'entry_price',
          key: 'entry_price',
          width: 120,
          scopedSlots: { customRender: 'entryPrice' }
        },
        {
          title: this.$t('trading-assistant.table.currentPrice'),
          dataIndex: 'current_price',
          key: 'current_price',
          width: 120,
          scopedSlots: { customRender: 'currentPrice' }
        },
        {
          title: this.$t('trading-assistant.table.unrealizedPnl'),
          dataIndex: 'unrealized_pnl',
          key: 'unrealized_pnl',
          width: 120,
          scopedSlots: { customRender: 'unrealizedPnl' }
        },
        {
          title: this.$t('trading-assistant.table.pnlPercent'),
          dataIndex: 'pnl_percent',
          key: 'pnl_percent',
          width: 100,
          scopedSlots: { customRender: 'pnlPercent' }
        }
      ]
    }
  },
  watch: {
    strategyId: {
      handler (val) {
        if (val) {
          this.loadPositions()
          this.startPolling()
        } else {
          this.stopPolling()
        }
      },
      immediate: true
    }
  },
  beforeDestroy () {
    this.stopPolling()
  },
  methods: {
    async loadPositions () {
      if (!this.strategyId) return

      try {
        const res = await getStrategyPositions(this.strategyId)
        if (res.code === 1) {
          const rawPositions = res.data.positions || res.data.items || []

          this.positions = rawPositions.map((position, index) => {
            const mt = String(this.marketType || 'swap').toLowerCase()
            let lev = parseFloat(this.leverage)
            if (!isFinite(lev) || lev <= 0) lev = 1
            if (mt === 'spot') lev = 1

            const entryPrice = parseFloat(position.entry_price || position.entryPrice || 0)
            const size = parseFloat(position.size || '0') || 0
            const pnl = parseFloat(position.unrealized_pnl || position.unrealizedPnl || '0') || 0
            let pnlPercent = parseFloat(position.pnl_percent || position.pnlPercent || '0') || 0

            if (entryPrice > 0 && size > 0) {
              pnlPercent = (pnl / (entryPrice * size)) * 100 * lev
            } else if (mt !== 'spot') {
              pnlPercent = pnlPercent * lev
            }

            return {
              id: position.id || index,
              symbol: position.symbol || '',
              side: position.side || 'long',
              size: size > 0 ? size.toString() : '0',
              entry_price: entryPrice > 0 ? entryPrice.toString() : '0',
              current_price: position.current_price || position.currentPrice || '0',
              unrealized_pnl: position.unrealized_pnl || position.unrealizedPnl || '0',
              pnl_percent: pnlPercent,
              updated_at: position.updated_at || position.updatedAt || ''
            }
          })
        } else {
          this.positions = []
        }
      } catch (error) {
        this.positions = []
      }
    },
    hasValidPrice (price) {
      const value = parseFloat(price)
      return Number.isFinite(value) && value > 0
    },
    getNotional (record) {
      const size = parseFloat(record.size || 0)
      const cp = parseFloat(record.current_price || 0)
      if (size > 0 && cp > 0) return size * cp
      const ep = parseFloat(record.entry_price || 0)
      if (size > 0 && ep > 0) return size * ep
      return 0
    },
    startPolling () {
      this.stopPolling()
      this.pollingTimer = setInterval(() => {
        this.loadPositions()
      }, 5000)
    },
    stopPolling () {
      if (this.pollingTimer) {
        clearInterval(this.pollingTimer)
        this.pollingTimer = null
      }
    }
  }
}
</script>

<style lang="less" scoped>
@primary-color: #1890ff;
@success-color: #0ecb81;
@danger-color: #f6465d;

.position-records {
  width: 100%;
  min-height: 300px;
  padding: 0;

  .empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 220px;
    padding: 40px 16px;
    border-radius: 8px;
    background: #fafafa;
    border: 1px solid #f0f0f0;
  }

  &.theme-dark .empty-state {
    background: #141414;
    border-color: rgba(255, 255, 255, 0.08);
  }

  ::v-deep .ant-table {
    font-size: 13px;
    color: #333;
  }

  ::v-deep .ant-table-body {
    overflow-x: auto;
    scrollbar-width: thin;
    scrollbar-color: rgba(0, 0, 0, 0.2) transparent;
  }

  ::v-deep .ant-table-thead > tr > th {
    background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    font-weight: 600;
    color: #475569;
    border-bottom: 2px solid #e2e8f0;
    padding: 12px 16px;
    font-size: 13px;
  }

  ::v-deep .ant-table-tbody > tr > td {
    padding: 12px 16px;
    color: #334155;
    border-bottom: 1px solid #f1f5f9;
  }

  ::v-deep .ant-tag {
    border-radius: 6px;
    padding: 2px 10px;
    font-weight: 600;
    font-size: 11px;
    border: none;

    &[color="green"] {
      background: linear-gradient(135deg, rgba(14, 203, 129, 0.15) 0%, rgba(14, 203, 129, 0.08) 100%);
      color: @success-color;
      border: 1px solid rgba(14, 203, 129, 0.3);
    }

    &[color="red"] {
      background: linear-gradient(135deg, rgba(246, 70, 93, 0.15) 0%, rgba(246, 70, 93, 0.08) 100%);
      color: @danger-color;
      border: 1px solid rgba(246, 70, 93, 0.3);
    }
  }

  &.theme-dark {
    ::v-deep .ant-table {
      background: #1c1c1c !important;
      color: #d1d4dc !important;
    }

    ::v-deep .ant-table-thead > tr > th {
      background: #2a2e39 !important;
      color: #d1d4dc !important;
      border-bottom-color: #363c4e !important;
    }

    ::v-deep .ant-table-tbody > tr > td {
      background: #1c1c1c !important;
      color: #d1d4dc !important;
      border-bottom-color: #363c4e !important;
    }
  }

  .profit {
    color: @success-color;
    font-weight: 700;
  }

  .loss {
    color: @danger-color;
    font-weight: 700;
  }
}
</style>
