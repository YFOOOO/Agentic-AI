import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Statistic, 
  Typography, 
  Alert, 
  Spin,
  Descriptions,
  Tag,
  Button,
  Space
} from 'antd';
import { 
  ReloadOutlined,
  DatabaseOutlined,
  FileTextOutlined,
  SettingOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import { ragAPI } from '../services/api';

const { Title, Paragraph } = Typography;

const Statistics = () => {
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchStatistics = async () => {
    try {
      setRefreshing(true);
      setError(null);
      
      const response = await ragAPI.getStatistics();
      
      if (response) {
        setStatistics(response);
      } else {
        setError('获取统计信息失败');
      }
    } catch (err) {
      setError(err.message || '请求失败');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchStatistics();
  }, []);

  const getStatusColor = (status) => {
    return status === 'active' ? 'success' : 'error';
  };

  const getStatusIcon = (status) => {
    return status === 'active' ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />;
  };

  const getStatusText = (status) => {
    return status === 'active' ? '正常' : '异常';
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>加载统计信息...</div>
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <Title level={2}>系统统计</Title>
          <Paragraph>
            查看RAG系统的详细统计信息和运行状态。
          </Paragraph>
        </div>
        <Button 
          type="primary" 
          icon={<ReloadOutlined />} 
          loading={refreshing}
          onClick={fetchStatistics}
        >
          刷新数据
        </Button>
      </div>

      {error && (
        <Alert
          message="获取统计信息失败"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {statistics && (
        <>
          {/* 核心指标 */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} md={8}>
              <Card>
                <Statistic
                  title="文档总数"
                  value={statistics.total_documents || 0}
                  prefix={<FileTextOutlined />}
                  valueStyle={{ color: '#3f8600' }}
                  suffix="个"
                />
              </Card>
            </Col>
            
            <Col xs={24} sm={12} md={8}>
              <Card>
                <Statistic
                  title="知识库名称"
                  value={statistics.collection_name || 'unknown'}
                  prefix={<DatabaseOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            
            <Col xs={24} sm={12} md={8}>
              <Card>
                <Statistic
                  title="嵌入模型"
                  value={statistics.embedding_model || 'N/A'}
                  prefix={<SettingOutlined />}
                  valueStyle={{ color: '#722ed1' }}
                />
              </Card>
            </Col>
          </Row>

          {/* 系统状态 */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} lg={12}>
              <Card title="组件状态" bordered={false}>
                <Space direction="vertical" style={{ width: '100%' }} size="middle">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span><strong>向量存储：</strong></span>
                    <Tag 
                      color={getStatusColor(statistics.vector_store_status)} 
                      icon={getStatusIcon(statistics.vector_store_status)}
                    >
                      {getStatusText(statistics.vector_store_status)}
                    </Tag>
                  </div>
                  
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span><strong>文档处理器：</strong></span>
                    <Tag 
                      color={getStatusColor(statistics.document_processor_status)} 
                      icon={getStatusIcon(statistics.document_processor_status)}
                    >
                      {getStatusText(statistics.document_processor_status)}
                    </Tag>
                  </div>
                  
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span><strong>知识检索器：</strong></span>
                    <Tag 
                      color={getStatusColor(statistics.knowledge_retriever_status)} 
                      icon={getStatusIcon(statistics.knowledge_retriever_status)}
                    >
                      {getStatusText(statistics.knowledge_retriever_status)}
                    </Tag>
                  </div>
                </Space>
              </Card>
            </Col>
            
            <Col xs={24} lg={12}>
              <Card title="系统信息" bordered={false}>
                <Descriptions column={1} size="small">
                  <Descriptions.Item label="知识库集合">
                    {statistics.collection_name || 'unknown'}
                  </Descriptions.Item>
                  <Descriptions.Item label="嵌入模型">
                    {statistics.embedding_model || 'N/A'}
                  </Descriptions.Item>
                  <Descriptions.Item label="文档总数">
                    {statistics.total_documents || 0} 个
                  </Descriptions.Item>
                  <Descriptions.Item label="最后更新">
                    {new Date().toLocaleString()}
                  </Descriptions.Item>
                </Descriptions>
              </Card>
            </Col>
          </Row>

          {/* 详细信息 */}
          <Card title="详细统计信息">
            <Descriptions bordered column={2} size="middle">
              <Descriptions.Item label="向量存储状态" span={1}>
                <Tag 
                  color={getStatusColor(statistics.vector_store_status)} 
                  icon={getStatusIcon(statistics.vector_store_status)}
                >
                  {getStatusText(statistics.vector_store_status)}
                </Tag>
              </Descriptions.Item>
              
              <Descriptions.Item label="文档处理器状态" span={1}>
                <Tag 
                  color={getStatusColor(statistics.document_processor_status)} 
                  icon={getStatusIcon(statistics.document_processor_status)}
                >
                  {getStatusText(statistics.document_processor_status)}
                </Tag>
              </Descriptions.Item>
              
              <Descriptions.Item label="知识检索器状态" span={1}>
                <Tag 
                  color={getStatusColor(statistics.knowledge_retriever_status)} 
                  icon={getStatusIcon(statistics.knowledge_retriever_status)}
                >
                  {getStatusText(statistics.knowledge_retriever_status)}
                </Tag>
              </Descriptions.Item>
              
              <Descriptions.Item label="嵌入模型" span={1}>
                <code>{statistics.embedding_model || 'N/A'}</code>
              </Descriptions.Item>
              
              <Descriptions.Item label="知识库集合名称" span={2}>
                <code>{statistics.collection_name || 'unknown'}</code>
              </Descriptions.Item>
              
              <Descriptions.Item label="文档总数" span={2}>
                <strong style={{ fontSize: '16px', color: '#1890ff' }}>
                  {statistics.total_documents || 0} 个文档
                </strong>
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </>
      )}
    </div>
  );
};

export default Statistics;