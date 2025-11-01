import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Space,
  message,
  Popconfirm,
  Tag,
  Divider,
  Row,
  Col,
  Typography,
  Tooltip,
  Spin,
  Empty
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  CopyOutlined,
  FileTextOutlined,
  BookOutlined,
  GlobalOutlined,
  ExperimentOutlined
} from '@ant-design/icons';
import { citationAPI } from '../services/api';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const Citations = () => {
  const [citations, setCitations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingCitation, setEditingCitation] = useState(null);
  const [form] = Form.useForm();
  const [formatModalVisible, setFormatModalVisible] = useState(false);
  const [selectedCitations, setSelectedCitations] = useState([]);
  const [formattedCitations, setFormattedCitations] = useState({});
  const [statistics, setStatistics] = useState({});

  // 引用类型图标映射
  const typeIcons = {
    journal: <FileTextOutlined />,
    book: <BookOutlined />,
    website: <GlobalOutlined />,
    conference: <ExperimentOutlined />
  };

  // 引用格式选项
  const citationStyles = [
    { value: 'apa', label: 'APA' },
    { value: 'mla', label: 'MLA' },
    { value: 'chicago', label: 'Chicago' },
    { value: 'ieee', label: 'IEEE' },
    { value: 'harvard', label: 'Harvard' }
  ];

  // 发表类型选项
  const publicationTypes = [
    { value: 'journal', label: '期刊文章' },
    { value: 'book', label: '书籍' },
    { value: 'website', label: '网站' },
    { value: 'conference', label: '会议论文' }
  ];

  useEffect(() => {
    loadCitations();
    loadStatistics();
  }, []);

  const loadCitations = async () => {
    setLoading(true);
    try {
      const response = await citationAPI.getCitations();
      setCitations(response.data);
    } catch (error) {
      message.error('加载引用列表失败');
    } finally {
      setLoading(false);
    }
  };

  const loadStatistics = async () => {
    try {
      const response = await citationAPI.getStatistics();
      setStatistics(response.data);
    } catch (error) {
      console.error('加载统计信息失败:', error);
    }
  };

  const handleAddCitation = () => {
    setEditingCitation(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEditCitation = (citation) => {
    setEditingCitation(citation);
    form.setFieldsValue({
      ...citation,
      authors: citation.authors.map(author => 
        `${author.first_name} ${author.last_name}${author.middle_name ? ' ' + author.middle_name : ''}`
      ).join('; ')
    });
    setModalVisible(true);
  };

  const handleDeleteCitation = async (citationId) => {
    try {
      await citationAPI.deleteCitation(citationId);
      message.success('引用删除成功');
      loadCitations();
      loadStatistics();
    } catch (error) {
      message.error('删除引用失败');
    }
  };

  const handleSubmit = async (values) => {
    try {
      // 解析作者信息
      const authors = values.authors.split(';').map(authorStr => {
        const parts = authorStr.trim().split(' ');
        return {
          first_name: parts[0] || '',
          last_name: parts[parts.length - 1] || '',
          middle_name: parts.length > 2 ? parts.slice(1, -1).join(' ') : null
        };
      });

      const citationData = {
        ...values,
        authors
      };

      if (editingCitation) {
        await citationAPI.updateCitation(editingCitation.id, citationData);
        message.success('引用更新成功');
      } else {
        await citationAPI.createCitation(citationData);
        message.success('引用创建成功');
      }

      setModalVisible(false);
      loadCitations();
      loadStatistics();
    } catch (error) {
      message.error(editingCitation ? '更新引用失败' : '创建引用失败');
    }
  };

  const handleFormatCitations = async (style) => {
    if (selectedCitations.length === 0) {
      message.warning('请先选择要格式化的引用');
      return;
    }

    try {
      const response = await citationAPI.formatCitations(selectedCitations, style);
      setFormattedCitations(response.data.formatted_citations);
      setFormatModalVisible(true);
    } catch (error) {
      message.error('格式化引用失败');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      message.success('已复制到剪贴板');
    });
  };

  const columns = [
    {
      title: '类型',
      dataIndex: 'publication_type',
      key: 'type',
      width: 80,
      render: (type) => (
        <Tooltip title={publicationTypes.find(t => t.value === type)?.label}>
          {typeIcons[type] || <FileTextOutlined />}
        </Tooltip>
      )
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      render: (title) => <Text strong>{title}</Text>
    },
    {
      title: '作者',
      dataIndex: 'authors',
      key: 'authors',
      ellipsis: true,
      render: (authors) => (
        <Text>
          {authors.map(author => `${author.first_name} ${author.last_name}`).join(', ')}
        </Text>
      )
    },
    {
      title: '年份',
      dataIndex: 'year',
      key: 'year',
      width: 80,
      sorter: (a, b) => a.year - b.year
    },
    {
      title: '期刊/出版社',
      key: 'publication',
      ellipsis: true,
      render: (record) => (
        <Text type="secondary">
          {record.journal || record.publisher || record.url || '-'}
        </Text>
      )
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      render: (_, record) => (
        <Space>
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEditCitation(record)}
            size="small"
          />
          <Popconfirm
            title="确定要删除这个引用吗？"
            onConfirm={() => handleDeleteCitation(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              size="small"
            />
          </Popconfirm>
        </Space>
      )
    }
  ];

  const rowSelection = {
    selectedRowKeys: selectedCitations,
    onChange: (selectedRowKeys) => {
      setSelectedCitations(selectedRowKeys);
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card>
            <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
              <Col>
                <Title level={3} style={{ margin: 0 }}>
                  引用管理
                </Title>
              </Col>
              <Col>
                <Space>
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={handleAddCitation}
                  >
                    添加引用
                  </Button>
                  {citationStyles.map(style => (
                    <Button
                      key={style.value}
                      onClick={() => handleFormatCitations(style.value)}
                      disabled={selectedCitations.length === 0}
                    >
                      {style.label}格式
                    </Button>
                  ))}
                </Space>
              </Col>
            </Row>

            {/* 统计信息 */}
            {statistics.total_citations > 0 && (
              <Row gutter={16} style={{ marginBottom: 16 }}>
                <Col span={6}>
                  <Card size="small">
                    <Text type="secondary">总引用数</Text>
                    <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
                      {statistics.total_citations}
                    </div>
                  </Card>
                </Col>
                <Col span={6}>
                  <Card size="small">
                    <Text type="secondary">类型分布</Text>
                    <div>
                      {Object.entries(statistics.by_type || {}).map(([type, count]) => (
                        <Tag key={type} style={{ margin: '2px' }}>
                          {publicationTypes.find(t => t.value === type)?.label}: {count}
                        </Tag>
                      ))}
                    </div>
                  </Card>
                </Col>
                <Col span={6}>
                  <Card size="small">
                    <Text type="secondary">支持格式</Text>
                    <div>
                      {statistics.supported_styles?.map(style => (
                        <Tag key={style} color="blue" style={{ margin: '2px' }}>
                          {style.toUpperCase()}
                        </Tag>
                      ))}
                    </div>
                  </Card>
                </Col>
                <Col span={6}>
                  <Card size="small">
                    <Text type="secondary">已选择</Text>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1890ff' }}>
                      {selectedCitations.length}
                    </div>
                  </Card>
                </Col>
              </Row>
            )}

            <Table
              columns={columns}
              dataSource={citations}
              rowKey="id"
              loading={loading}
              rowSelection={rowSelection}
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total) => `共 ${total} 条记录`
              }}
              locale={{
                emptyText: (
                  <Empty
                    description="暂无引用数据"
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                  />
                )
              }}
            />
          </Card>
        </Col>
      </Row>

      {/* 添加/编辑引用模态框 */}
      <Modal
        title={editingCitation ? '编辑引用' : '添加引用'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={800}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="title"
                label="标题"
                rules={[{ required: true, message: '请输入标题' }]}
              >
                <Input placeholder="请输入文献标题" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="publication_type"
                label="发表类型"
                rules={[{ required: true, message: '请选择发表类型' }]}
              >
                <Select placeholder="请选择发表类型">
                  {publicationTypes.map(type => (
                    <Option key={type.value} value={type.value}>
                      {type.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="authors"
            label="作者"
            rules={[{ required: true, message: '请输入作者信息' }]}
            extra="多个作者请用分号(;)分隔，格式：名 姓"
          >
            <Input placeholder="例如：John Smith; Jane Doe" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="year"
                label="年份"
                rules={[{ required: true, message: '请输入年份' }]}
              >
                <Input type="number" placeholder="例如：2023" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="journal" label="期刊名称">
                <Input placeholder="期刊或会议名称" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="publisher" label="出版社">
                <Input placeholder="出版社名称" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={6}>
              <Form.Item name="volume" label="卷号">
                <Input placeholder="卷号" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="issue" label="期号">
                <Input placeholder="期号" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="pages" label="页码">
                <Input placeholder="例如：1-10" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="doi" label="DOI">
                <Input placeholder="DOI号" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="url" label="网址">
            <Input placeholder="网站链接" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingCitation ? '更新' : '创建'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 格式化结果模态框 */}
      <Modal
        title="格式化结果"
        open={formatModalVisible}
        onCancel={() => setFormatModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setFormatModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        <div>
          {Object.entries(formattedCitations).map(([citationId, formattedText]) => {
            const citation = citations.find(c => c.id === citationId);
            return (
              <Card
                key={citationId}
                size="small"
                title={citation?.title}
                extra={
                  <Button
                    type="text"
                    icon={<CopyOutlined />}
                    onClick={() => copyToClipboard(formattedText)}
                  >
                    复制
                  </Button>
                }
                style={{ marginBottom: 16 }}
              >
                <Paragraph copyable={{ text: formattedText }}>
                  {formattedText}
                </Paragraph>
              </Card>
            );
          })}
        </div>
      </Modal>
    </div>
  );
};

export default Citations;