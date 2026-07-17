import { useMemo, useState } from 'react';
import { Avatar, Dropdown, Layout, Menu, Space, Typography } from 'antd';
import { BookOutlined, ClockCircleOutlined, DashboardOutlined, LogoutOutlined, MenuFoldOutlined, MenuUnfoldOutlined, SwapOutlined, TeamOutlined } from '@ant-design/icons';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

const { Header, Sider, Content } = Layout;

export const AppLayout = () => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const items = useMemo(
    () => [
      { key: '/', icon: <DashboardOutlined />, label: <Link to="/">Dashboard</Link> },
      { key: '/members', icon: <TeamOutlined />, label: <Link to="/members">Members</Link> },
      { key: '/books', icon: <BookOutlined />, label: <Link to="/books">Books</Link> },
      { key: '/borrow', icon: <SwapOutlined />, label: <Link to="/borrow">Borrow Book</Link> },
      { key: '/lendings', icon: <ClockCircleOutlined />, label: <Link to="/lendings">Lending Records</Link> },
      { key: '/overdue', icon: <ClockCircleOutlined />, label: <Link to="/overdue">Overdue Books</Link> },
    ],
    [],
  );

  const onLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed} theme="light">
        <div
          title="Society Connect"
          style={{
            alignItems: 'center',
            display: 'flex',
            fontWeight: 700,
            height: 64,
            justifyContent: collapsed ? 'center' : 'flex-start',
            lineHeight: 1.2,
            overflow: 'hidden',
            padding: collapsed ? '0 8px' : '0 16px',
            whiteSpace: collapsed ? 'nowrap' : 'normal',
          }}
        >
          {collapsed ? 'SC' : 'Society Connect'}
        </div>
        <Menu selectedKeys={[location.pathname]} mode="inline" items={items} />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div onClick={() => setCollapsed(!collapsed)} style={{ cursor: 'pointer' }}>
            {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          </div>
          <Dropdown
            menu={{
              items: [{ key: 'logout', icon: <LogoutOutlined />, label: 'Logout', onClick: onLogout }],
            }}
          >
            <Space>
              <Avatar>{user?.username?.[0]?.toUpperCase() || 'U'}</Avatar>
              <Typography.Text>{user?.username}</Typography.Text>
            </Space>
          </Dropdown>
        </Header>
        <Content style={{ margin: 16, background: '#fff', padding: 24 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};
