import React, { useState } from 'react';
import { 
  Upload, 
  Button, 
  Card, 
  Typography, 
  Alert, 
  Progress,
  List,
  Tag,
  Space,
  message
} from 'antd';
import { 
  UploadOutlined, 
  FileTextOutlined, 
  CheckCircleOutlined,
  ExclamationCircleOutlined 
} from '@ant-design/icons';
import { ragAPI } from '../services/api';

const { Dragger } = Upload;
const { Title, Paragraph, Text } = Typography;

const UploadPage = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadResults, setUploadResults] = useState([]);
  const [error, setError] = useState(null);

  const handleUpload = async (file) => {
    try {
      setUploading(true);
      setError(null);
      
      const response = await ragAPI.upload(file);
      
      if (response.success) {
        const result = {
          filename: file.name,
          status: 'success',
          message: response.message,
          chunks: response.chunks_created || 0,
          timestamp: new Date().toLocaleString()
        };
        
        setUploadResults(prev => [result, ...prev]);
        message.success(`文件 "${file.name}" 上传成功！`);
      } else {
        const result = {
          filename: file.name,
          status: 'error',
          message: response.message || '上传失败',
          timestamp: new Date().toLocaleString()
        };
        
        setUploadResults(prev => [result, ...prev]);
        message.error(`文件 "${file.name}" 上传失败：${response.message}`);
      }
    } catch (err) {
      const result = {
        filename: file.name,
        status: 'error',
        message: err.message || '上传请求失败',
        timestamp: new Date().toLocaleString()
      };
      
      setUploadResults(prev => [result, ...prev]);
      setError(err.message || '上传请求失败');
      message.error(`文件 "${file.name}" 上传失败：${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const uploadProps = {
    name: 'file',
    multiple: false,
    accept: '.txt,.pdf,.doc,.docx,.md',
    beforeUpload: (file) => {
      // 检查文件大小 (限制为 10MB)
      const isLt10M = file.size / 1024 / 1024 < 10;
      if (!isLt10M) {
        message.error('文件大小不能超过 10MB!');
        return false;
      }
      
      // 检查文件类型
      const allowedTypes = ['text/plain', 'application/pdf', 'application/msword', 
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                           'text/markdown'];
      const isAllowedType = allowedTypes.includes(file.type) || 
                           file.name.endsWith('.txt') || 
                           file.name.endsWith('.md');
      
      if (!isAllowedType) {
        message.error('只支持 TXT、PDF、DOC、DOCX、MD 格式的文件!');
        return false;
      }
      
      handleUpload(file);
      return false; // 阻止默认上传行为
    },
    showUploadList: false,
  };

  return (
    <div>
      <Title level={2}>文档上传</Title>
      <Paragraph>
        上传文档到知识库中。支持的格式包括：TXT、PDF、DOC、DOCX、Markdown。
        文件将被自动处理并分割成小块，以便进行高效的语义搜索。
      </Paragraph>

      <Card style={{ marginBottom: 24 }}>
        <Dragger {...uploadProps} style={{ padding: '40px' }}>
          <p className="ant-upload-drag-icon">
            <UploadOutlined style={{ fontSize: '48px', color: '#1890ff' }} />
          </p>
          <p className="ant-upload-text">
            点击或拖拽文件到此区域上传
          </p>
          <p className="ant-upload-hint">
            支持单个文件上传。文件大小限制：10MB
            <br />
            支持格式：TXT、PDF、DOC、DOCX、Markdown
          </p>
        </Dragger>
        
        {uploading && (
          <div style={{ marginTop: 16, textAlign: 'center' }}>
            <Progress type="circle" percent={100} status="active" />
            <div style={{ marginTop: 8 }}>
              <Text>正在处理文件...</Text>
            </div>
          </div>
        )}
      </Card>

      {error && (
        <Alert
          message="上传失败"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {uploadResults.length > 0 && (
        <Card title="上传历史">
          <List
            itemLayout="horizontal"
            dataSource={uploadResults}
            renderItem={(item) => (
              <List.Item>
                <List.Item.Meta
                  avatar={
                    item.status === 'success' ? (
                      <CheckCircleOutlined style={{ color: '#52c41a', fontSize: '20px' }} />
                    ) : (
                      <ExclamationCircleOutlined style={{ color: '#ff4d4f', fontSize: '20px' }} />
                    )
                  }
                  title={
                    <Space>
                      <FileTextOutlined />
                      <Text strong>{item.filename}</Text>
                      <Tag color={item.status === 'success' ? 'success' : 'error'}>
                        {item.status === 'success' ? '成功' : '失败'}
                      </Tag>
                    </Space>
                  }
                  description={
                    <div>
                      <div>{item.message}</div>
                      {item.chunks && (
                        <Text type="secondary">创建了 {item.chunks} 个文档块</Text>
                      )}
                      <br />
                      <Text type="secondary">{item.timestamp}</Text>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        </Card>
      )}
    </div>
  );
};

export default UploadPage;