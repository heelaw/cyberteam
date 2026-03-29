import React, { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * ErrorBoundary - React错误边界组件
 * 捕获子组件的JavaScript错误，防止整个应用白屏崩溃
 * 用于保护关键页面区域，在错误时显示友好的错误提示
 */
export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div
          role="alert"
          aria-live="assertive"
          style={{
            padding: '24px',
            margin: '16px',
            borderRadius: '8px',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            color: '#fecaca',
          }}
        >
          <h2 style={{ marginBottom: '12px', fontSize: '18px', fontWeight: '600' }}>
            页面加载失败
          </h2>
          <p style={{ marginBottom: '12px', fontSize: '14px', color: '#fca5a5' }}>
            抱歉，页面发生了一些错误。请尝试刷新页面。
          </p>
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details style={{ whiteSpace: 'pre-wrap', fontSize: '12px', color: '#f87171' }}>
              <summary style={{ cursor: 'pointer', marginBottom: '8px' }}>
                错误详情（开发模式）
              </summary>
              {this.state.error.toString()}
            </details>
          )}
          <button
            onClick={() => window.location.reload()}
            style={{
              marginTop: '16px',
              padding: '8px 16px',
              backgroundColor: '#dc2626',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
            aria-label="刷新页面"
          >
            刷新页面
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * 页面级ErrorBoundary - 用于包裹整个页面组件
 */
export function PageErrorFallback({ title = '页面加载失败' }: { title?: string }) {
  return (
    <div
      role="alert"
      aria-live="assertive"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '400px',
        padding: '24px',
        textAlign: 'center',
      }}
    >
      <div
        style={{
          fontSize: '48px',
          marginBottom: '16px',
        }}
        aria-hidden="true"
      >
        !
      </div>
      <h2 style={{ marginBottom: '12px', fontSize: '20px', fontWeight: '600', color: '#f1f5f9' }}>
        {title}
      </h2>
      <p style={{ marginBottom: '16px', fontSize: '14px', color: '#94a3b8' }}>
        抱歉，页面发生了一些错误。请尝试刷新页面或联系支持人员。
      </p>
      <button
        onClick={() => window.location.reload()}
        style={{
          padding: '10px 20px',
          backgroundColor: '#3b82f6',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer',
          fontSize: '14px',
          fontWeight: '500',
        }}
        aria-label="刷新页面"
      >
        刷新页面
      </button>
    </div>
  );
}
