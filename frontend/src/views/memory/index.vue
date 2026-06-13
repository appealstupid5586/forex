<template>
  <div class="memory-page">
    <a-row gutter="24">
      <a-col :span="12">
        <a-card title="Short-term Memory" bordered>
          <a-form layout="vertical">
            <a-form-item label="Content">
              <a-textarea v-model:value="shortTermContent" rows="4" placeholder="Enter short-term memory content" />
            </a-form-item>
            <a-form-item label="Tags">
              <a-input v-model:value="shortTermTags" placeholder="comma-separated tags" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="saveShortTerm">Save Short-term Memory</a-button>
            </a-form-item>
            <a-form-item v-if="saveResult">
              <a-alert :message="saveResult" type="success" show-icon />
            </a-form-item>
          </a-form>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="Recent Short-term Memory" bordered>
          <a-form layout="inline">
            <a-form-item label="Limit">
              <a-input-number v-model:value="recentLimit" :min="1" :max="50" />
            </a-form-item>
            <a-form-item>
              <a-button type="default" @click="loadRecent">Refresh</a-button>
            </a-form-item>
          </a-form>
          <a-list bordered style="margin-top: 16px">
            <a-list-item v-for="item in recentMemories" :key="item.memory_id">
              <a-list-item-meta
                :title="item.memory_id"
                :description="JSON.stringify(item.content)"
              />
              <div style="margin-top: 8px">Tags: {{ (item.tags || []).join(', ') }}</div>
            </a-list-item>
          </a-list>
        </a-card>
      </a-col>
    </a-row>

    <a-row gutter="24" style="margin-top: 24px;">
      <a-col :span="24">
        <a-card title="Query Memory" bordered>
          <a-form layout="inline">
            <a-form-item label="Query">
              <a-input v-model:value="queryText" placeholder="Search memory text" />
            </a-form-item>
            <a-form-item label="Tags">
              <a-input v-model:value="queryTags" placeholder="comma-separated tags" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="searchMemory">Search</a-button>
            </a-form-item>
          </a-form>
          <a-list bordered style="margin-top: 16px">
            <a-list-item v-for="item in queryResults" :key="item.memory_id">
              <a-list-item-meta
                :title="item.memory_id"
                :description="JSON.stringify(item.content)"
              />
              <div style="margin-top: 8px">Tags: {{ (item.tags || []).join(', ') }}</div>
            </a-list-item>
          </a-list>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script>
import { saveShortTermMemory, fetchRecentShortTermMemory, queryMemory } from '@/api/memory'

export default {
  name: 'MemoryPage',
  data () {
    return {
      shortTermContent: '',
      shortTermTags: '',
      saveResult: '',
      recentLimit: 10,
      recentMemories: [],
      queryText: '',
      queryTags: '',
      queryResults: []
    }
  },
  methods: {
    async saveShortTerm () {
      try {
        const tags = this.shortTermTags
          .split(',')
          .map(tag => tag.trim())
          .filter(Boolean)
        await saveShortTermMemory({ content: { text: this.shortTermContent }, tags })
        this.saveResult = 'Saved successfully'
        this.shortTermContent = ''
        this.shortTermTags = ''
        this.loadRecent()
      } catch (err) {
        this.saveResult = 'Save failed'
        console.error(err)
      }
    },
    async loadRecent () {
      try {
        const data = await fetchRecentShortTermMemory(this.recentLimit)
        this.recentMemories = data.recent_memories || []
      } catch (err) {
        console.error(err)
      }
    },
    async searchMemory () {
      try {
        const tags = this.queryTags
          .split(',')
          .map(tag => tag.trim())
          .filter(Boolean)
        const data = await queryMemory(this.queryText, tags)
        this.queryResults = data.results || []
      } catch (err) {
        console.error(err)
      }
    }
  },
  mounted () {
    this.loadRecent()
  }
}
</script>

<style scoped>
.memory-page {
  padding: 16px;
}
</style>
