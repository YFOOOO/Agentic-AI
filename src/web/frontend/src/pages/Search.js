import React, { useState } from 'react';
import { 
  Input, 
  Button, 
  Card, 
  List, 
  Typography, 
  Alert, 
  Spin, 
  Empty,
  Tag,
  Space,
  Slider
} from 'antd';
import { SearchOutlined, BulbOutlined } from '@ant-design/icons';
import { ragAPI } from '../services/api';

const { Search: AntSearch } = Input;
const { Title, Paragraph, Text } = Typography;

const Search = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [nResults, setNResults] = useState(5);

  const handleSearch = async (searchQuery) => {
    if (!searchQuery.trim()) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await ragAPI.search(searchQuery, nResults);
      
      if (response.success) {
        setResults(response.results || []);
        
        // 获取查询建议
        try {
          const suggestionsResponse = await ragAPI.getSuggestions(searchQuery);
          if (suggestionsResponse.success) {
            setSuggestions(suggestionsResponse.suggestions || []);
          }
        } catch (suggErr) {
          console.warn('获取建议失败:', suggErr);
        }
      } else {
        setError(response.message || '搜索失败');
      }
    } catch (err) {
      setError(err.message || '搜索请求失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion);
    handleSearch(suggestion);
  };

  return (
    <div className="search-container">
      <Title level={2}>知识搜索</Title>
      <Paragraph>
        在知识库中搜索相关文档和信息。支持自然语言查询，系统会返回最相关的内容片段。
      </Paragraph>

      <Card style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <AntSearch
            placeholder="输入您的问题或关键词..."
            enterButton={<Button type="primary" icon={<SearchOutlined />}>搜索</Button>}
            size="large"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onSearch={handleSearch}
            loading={loading}
          />
          
          <div>
            <Text strong>返回结果数量：</Text>
            <Slider
              min={1}
              max={20}
              value={nResults}
              onChange={setNResults}
              style={{ width: 200, marginLeft: 16 }}
              tooltip={{ formatter: (value) => `${value} 条` }}
            />
            <Text style={{ marginLeft: 8 }}>{nResults} 条</Text>
          </div>
        </Space>
      </Card>

      {error && (
        <Alert
          message="搜索失败"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {suggestions.length > 0 && (
        <Card 
          title={<><BulbOutlined /> 相关建议</>} 
          style={{ marginBottom: 24 }}
          size="small"
        >
          <Space wrap>
            {suggestions.map((suggestion, index) => (
              <Tag
                key={index}
                color="blue"
                style={{ cursor: 'pointer' }}
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </Tag>
            ))}
          </Space>
        </Card>
      )}

      {loading && (
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>搜索中...</div>
        </div>
      )}

      {!loading && results.length === 0 && query && (
        <Empty
          description="未找到相关结果"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      )}

      {!loading && results.length > 0 && (
        <Card title={`搜索结果 (${results.length} 条)`}>
          <List
            itemLayout="vertical"
            dataSource={results}
            renderItem={(item, index) => (
              <List.Item
                key={index}
                extra={
                  <div style={{ textAlign: 'right' }}>
                    <Text type="secondary">相似度</Text>
                    <br />
                    <Text strong style={{ color: '#1890ff' }}>
                      {((1 - (item.distance || 0)) * 100).toFixed(1)}%
                    </Text>
                  </div>
                }
              >
                <List.Item.Meta
                  title={
                    <div>
                      <Text strong>文档片段 #{index + 1}</Text>
                      {item.metadata?.source && (
                        <Tag color="green" style={{ marginLeft: 8 }}>
                          {item.metadata.source}
                        </Tag>
                      )}
                    </div>
                  }
                  description={
                    <div>
                      {item.metadata?.page && (
                        <Text type="secondary">页码: {item.metadata.page} | </Text>
                      )}
                      {item.metadata?.chunk_id && (
                        <Text type="secondary">片段ID: {item.metadata.chunk_id}</Text>
                      )}
                    </div>
                  }
                />
                <Paragraph
                  ellipsis={{ rows: 4, expandable: true, symbol: '展开' }}
                  style={{ 
                    background: '#f9f9f9', 
                    padding: '12px', 
                    borderRadius: '6px',
                    marginTop: '8px'
                  }}
                >
                  {item.content || item.document || '无内容'}
                </Paragraph>
              </List.Item>
            )}
          />
        </Card>
      )}
    </div>
  );
};

export default Search;