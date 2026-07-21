import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import 'antd/dist/reset.css';
import { AuthProvider } from './auth/AuthContext';
import { AppRoutes } from './routes/AppRoutes';
import { ToastProvider } from './components/ToastProvider';
import { AppErrorBoundary } from './components/AppErrorBoundary';
import './styles/app.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider theme={{ token: { borderRadius: 6 } }}>
      <AppErrorBoundary><ToastProvider>
        <BrowserRouter>
          <AuthProvider>
            <AppRoutes />
          </AuthProvider>
        </BrowserRouter>
      </ToastProvider></AppErrorBoundary>
    </ConfigProvider>
  </React.StrictMode>,
);
