import request from '@/utils/request'

export function saveShortTermMemory(content, tags = []) {
  return request({
    url: '/api/v1/memory/short-term/save',
    method: 'post',
    data: { content, tags }
  })
}

export function fetchRecentShortTermMemory(limit = 10) {
  return request({
    url: '/api/v1/memory/short-term/recent',
    method: 'get',
    params: { limit }
  })
}

export function queryMemory(query, tags = [], memory_type = null) {
  return request({
    url: '/api/v1/memory/query',
    method: 'post',
    data: { query, tags, memory_type }
  })
}
