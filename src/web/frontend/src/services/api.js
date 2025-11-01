import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('发送请求:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('请求错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('收到响应:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('响应错误:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

// RAG相关API
export const ragAPI = {
  // 搜索文档
  search: async (query, nResults = 5) => {
    const response = await api.post('/search', {
      query,
      n_results: nResults,
    });
    return response.data;
  },

  // 上传文档
  upload: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // 获取统计信息
  getStatistics: async () => {
    const response = await api.get('/statistics');
    return response.data;
  },

  // 获取查询建议
  getSuggestions: async (query) => {
    const response = await api.post('/suggestions', {
      query,
    });
    return response.data;
  },
};

// 健康检查API
export const healthAPI = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

// 引用管理API
const citationAPI = {
  // 获取所有引用
  getCitations: () => api.get('/citations/'),
  
  // 获取特定引用
  getCitation: (id) => api.get(`/citations/${id}`),
  
  // 创建引用
  createCitation: (data) => api.post('/citations/', data),
  
  // 更新引用
  updateCitation: (id, data) => api.put(`/citations/${id}`, data),
  
  // 删除引用
  deleteCitation: (id) => api.delete(`/citations/${id}`),
  
  // 格式化引用
  formatCitations: (citationIds, style) => api.post('/citations/format', {
    citation_ids: citationIds,
    style: style
  }),
  
  // 解析引用文本
  parseCitation: (text) => api.post('/citations/parse', { text }),
  
  // 获取支持的引用格式
  getSupportedStyles: () => api.get('/citations/styles/supported'),
  
  // 获取引用统计信息
  getStatistics: () => api.get('/citations/statistics/overview')
};

export { citationAPI };
export default api;