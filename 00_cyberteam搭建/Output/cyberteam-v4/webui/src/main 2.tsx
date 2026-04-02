import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import ErrorBoundary, { PageErrorFallback } from './components/ErrorBoundary';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary fallback={<PageErrorFallback />}>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);
