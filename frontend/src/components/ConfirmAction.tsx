import { Modal } from 'antd';

export const confirmAction = (title: string, message: string, onOk: () => void) => {
  Modal.confirm({
    title,
    content: message,
    okText: 'Confirm',
    cancelText: 'Cancel',
    onOk,
  });
};
