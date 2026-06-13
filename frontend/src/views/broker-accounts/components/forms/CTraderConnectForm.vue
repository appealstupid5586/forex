<template>
  <a-form layout="vertical" class="broker-form">
    <a-row :gutter="12">
      <a-col :xs="24" :md="12">
        <a-form-item :label="$t('brokerAccounts.ctrader.accessToken')">
          <a-input-password
            v-model="form.accessToken"
            :placeholder="$t('brokerAccounts.ctrader.accessTokenPh')"
            :disabled="disabled"
            autocomplete="new-password"
          />
        </a-form-item>
      </a-col>
      <a-col :xs="24" :md="12">
        <a-form-item :label="$t('brokerAccounts.ctrader.accountOptional')">
          <a-input v-model="form.accountId" :placeholder="$t('brokerAccounts.ctrader.accountPh')" :disabled="disabled" />
        </a-form-item>
      </a-col>
    </a-row>
    <a-row :gutter="12">
      <a-col :span="24">
        <a-form-item :label="$t('brokerAccounts.ctrader.environment')">
          <a-select v-model="form.environment" :disabled="disabled">
            <a-select-option value="demo">Demo</a-select-option>
            <a-select-option value="live">Live</a-select-option>
          </a-select>
        </a-form-item>
      </a-col>
    </a-row>
    <div class="form-actions">
      <a-button type="primary" :loading="loading" :disabled="!canSubmit || disabled" @click="submit">
        <a-icon type="link" /> {{ $t('brokerAccounts.connect') }}
      </a-button>
    </div>
  </a-form>
</template>

<script>
export default {
  name: 'CTraderConnectForm',
  props: {
    broker: { type: Object, required: true },
    disabled: { type: Boolean, default: false },
    loading: { type: Boolean, default: false }
  },
  data () {
    return {
      form: {
        accessToken: '',
        accountId: '',
        environment: 'demo'
      }
    }
  },
  computed: {
    canSubmit () {
      return !!(this.form.accessToken && this.form.accessToken.trim())
    }
  },
  methods: {
    submit () {
      if (!this.canSubmit) return
      this.$emit('submit', {
        access_token: this.form.accessToken.trim(),
        account_id: (this.form.accountId || '').trim() || null,
        environment: this.form.environment || 'demo'
      })
    }
  }
}
</script>

<style lang="less" scoped>
.broker-form {
  ::v-deep .ant-form-item-label > label { font-size: 12px; color: #595959; }
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}
</style>
