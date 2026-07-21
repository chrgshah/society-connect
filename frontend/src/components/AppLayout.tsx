import { useMemo, useState } from 'react';
import { Avatar, Dropdown, Layout, Menu, Space, Typography } from 'antd';
import { BookOutlined, ClockCircleOutlined, DashboardOutlined, MoneyCollectOutlined, DownCircleOutlined, LogoutOutlined, MenuFoldOutlined, MenuUnfoldOutlined, SwapOutlined, TeamOutlined } from '@ant-design/icons';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { useToast } from './ToastProvider';
import { ROUTES } from '../config/paths';

const { Header, Sider, Content } = Layout;

export const AppLayout = () => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const toast = useToast();

  const items = useMemo(
    () => [
      { key: ROUTES.dashboard, icon: <DashboardOutlined />, label: <Link to={ROUTES.dashboard}>Dashboard</Link> },
      { key: ROUTES.members, icon: <TeamOutlined />, label: <Link to={ROUTES.members}>Members</Link> },
      { key: ROUTES.books, icon: <BookOutlined />, label: <Link to={ROUTES.books}>Books</Link> },
      { key: ROUTES.borrow, icon: <SwapOutlined />, label: <Link to={ROUTES.borrow}>Borrow Book</Link> },
      { key: ROUTES.lendings, icon: <MoneyCollectOutlined />, label: <Link to={ROUTES.lendings}>Lending Records</Link> },
      { key: ROUTES.overdue, icon: <ClockCircleOutlined />, label: <Link to={ROUTES.overdue}>Overdue Books</Link> },
      { key: ROUTES.categories, icon: <DownCircleOutlined />, label: <Link to={ROUTES.categories}>Categories</Link> },
    ],
    [],
  );

  const onLogout = async () => {
    await logout();
    toast.success('You have been signed out.', 'Logged out');
    navigate(ROUTES.login);
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
