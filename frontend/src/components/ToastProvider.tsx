import { notification } from 'antd';
import { createContext, useContext, useMemo } from 'react';

interface ToastContextValue {
  error: (message: string, title?: string) => void;
  info: (message: string, title?: string) => void;
  success: (message: string, title?: string) => void;
  warning: (message: string, title?: string) => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

export const ToastProvider = ({ children }: { children: React.ReactNode }) => {
  const [notificationApi, contextHolder] = notification.useNotification({
    duration: 1,
    maxCount: 4,
    placement: 'topRight',
  });

  const toast = useMemo<ToastContextValue>(
    () => ({
      error: (message, title = 'Action failed') => notificationApi.error({ message: title, description: message }),
      info: (message, title = 'Information') => notificationApi.info({ message: title, description: message }),
      success: (message, title = 'Success') => notificationApi.success({ message: title, description: message }),
      warning: (message, title = 'Attention') => notificationApi.warning({ message: title, description: message }),
    }),
    [notificationApi],
  );

  return (
    <ToastContext.Provider value={toast}>
      {contextHolder}
      {children}
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const toast = useContext(ToastContext);
  if (!toast) throw new Error('useToast must be used within ToastProvider');
  return toast;
};
