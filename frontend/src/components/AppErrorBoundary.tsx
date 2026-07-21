import { Alert, Button, Result } from 'antd';
import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props { children: ReactNode }
interface State { error: Error | null }

export class AppErrorBoundary extends Component<Props, State> {
  state: State = { error: null };
  static getDerivedStateFromError(error: Error): State { return { error }; }
  componentDidCatch(error: Error, info: ErrorInfo) { console.error('Unhandled application error', error, info); }
  render() {
    if (!this.state.error) return this.props.children;
    return <Result status="500" title="Something went wrong" subTitle="The application encountered an unexpected error."
      extra={<Button type="primary" onClick={() => window.location.reload()}>Reload application</Button>}>
      {import.meta.env.DEV ? <Alert type="error" message={this.state.error.message} /> : null}
    </Result>;
  }
}
