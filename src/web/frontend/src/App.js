import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout, Menu, Typography } from 'antd';
import { 
  SearchOutlined, 
  UploadOutlined, 
  BarChartOutlined,
  BookOutlined,
  DashboardOutlined
} from '@ant-design/icons';
import Dashboard from './pages/Dashboard';
import Search from './pages/Search';
import Upload from './pages/Upload';
import Statistics from './pages/Statistics';
import Citations from './pages/Citations';
import './App.css';

const { Header, Content, Sider } = Layout;
const { Title } = Typography;

function App() {
  const menuItems = [
    {
      key: '/',
      icon: <BarChartOutlined />,
      label: '仪表板',
    },
    {
      key: '/search',
      icon: <SearchOutlined />,
      label: '知识检索',
    },
    {
      key: '/upload',
      icon: <UploadOutlined />,
      label: '文档上传',
    },
    {
      key: '/citations',
      icon: <BookOutlined />,
      label: '引用管理',
    },
    {
      key: '/statistics',
      icon: <BarChartOutlined />,
      label: '统计信息',
    },
  ];

  return (
    <Layout className="app-layout">
      <Header className="dashboard-header">
        <Title level={3} style={{ color: 'white', margin: 0 }}>
          Agentic AI Dashboard
        </Title>
        <div style={{ color: 'white' }}>
          智能研究助手
        </div>
      </Header>
      
      <Layout>
        <Sider width={200} theme="light">
          <Menu
            mode="inline"
            defaultSelectedKeys={['/']}
            items={menuItems}
            onClick={({ key }) => {
              window.location.pathname = key;
            }}
          />
        </Sider>
        
        <Layout style={{ padding: '0 24px 24px' }}>
          <Content className="dashboard-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/search" element={<Search />} />
              <Route path="/upload" element={<Upload />} />
              <Route path="/citations" element={<Citations />} />
              <Route path="/statistics" element={<Statistics />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
}

export default App;