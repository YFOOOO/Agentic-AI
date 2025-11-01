import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Typography, Alert, Spin } from 'antd';
import { 
  FileTextOutlined, 
  SearchOutlined, 
  DatabaseOutlined,
  CheckCircleOutlined 
} from '@ant-design/icons';
import { ragAPI, healthAPI } from '../services/api';

const { Title, Paragraph } = Typography;

const Dashboard = () => {
  const [statistics, setStatistics] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [statsResponse, healthResponse] = await Promise.allSettled([
          ragAPI.getStatistics(),
          healthAPI.check()
        ]);

        if (statsResponse.status === 'fulfilled') {
          setStatistics(statsResponse.value);
        }
        
        if (healthResponse.status === 'fulfilled') {
          setHealth(healthResponse.value);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>加载中...</div>
      </div>
    );
  }

  return (
    <div>
      <Title level={2}>系统仪表板</Title>
      <Paragraph>
        欢迎使用 Agentic AI Dashboard！这是一个智能研究助手系统，
        集成了RAG（检索增强生成）技术，帮助您高效管理和检索知识。
      </Paragraph>

      {error && (
        <Alert
          message="数据加载失败"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="文档总数"
              value={statistics?.total_documents || 0}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="知识库状态"
              value={statistics?.collection_name || 'unknown'}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="向量存储"
              value={statistics?.vector_store_status === 'active' ? '正常' : '异常'}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ 
                color: statistics?.vector_store_status === 'active' ? '#3f8600' : '#cf1322' 
              }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="嵌入模型"
              value={statistics?.embedding_model || 'N/A'}
              prefix={<SearchOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} md={12}>
          <Card title="系统状态" bordered={false}>
            <div style={{ padding: '16px 0' }}>
              <div style={{ marginBottom: 16 }}>
                <strong>RAG系统状态：</strong>
                <span style={{ 
                  color: statistics?.knowledge_retriever_status === 'active' ? '#3f8600' : '#cf1322',
                  marginLeft: 8 
                }}>
                  {statistics?.knowledge_retriever_status === 'active' ? '✓ 正常运行' : '✗ 异常'}
                </span>
              </div>
              <div style={{ marginBottom: 16 }}>
                <strong>文档处理器：</strong>
                <span style={{ 
                  color: statistics?.document_processor_status === 'active' ? '#3f8600' : '#cf1322',
                  marginLeft: 8 
                }}>
                  {statistics?.document_processor_status === 'active' ? '✓ 正常运行' : '✗ 异常'}
                </span>
              </div>
              <div>
                <strong>API服务：</strong>
                <span style={{ 
                  color: health ? '#3f8600' : '#cf1322',
                  marginLeft: 8 
                }}>
                  {health ? '✓ 正常运行' : '✗ 连接失败'}
                </span>
              </div>
            </div>
          </Card>
        </Col>
        
        <Col xs={24} md={12}>
          <Card title="快速操作" bordered={false}>
            <div style={{ padding: '16px 0' }}>
              <Paragraph>
                <a href="/search">🔍 开始搜索知识库</a>
              </Paragraph>
              <Paragraph>
                <a href="/upload">📁 上传新文档</a>
              </Paragraph>
              <Paragraph>
                <a href="/statistics">📊 查看详细统计</a>
              </Paragraph>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;