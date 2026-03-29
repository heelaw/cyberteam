const API_BASE = '/api';

/**
 * API错误类 - 包含状态码和友好消息
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public isNetworkError: boolean = false
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * 友好的错误消息映射
 */
const FRIENDLY_MESSAGES: Record<number, string> = {
  400: '请求参数错误，请检查输入内容',
  401: '未登录或登录已过期，请重新登录',
  403: '没有权限执行此操作',
  404: '请求的资源不存在',
  408: '请求超时，请稍后重试',
  429: '请求过于频繁，请稍后重试',
  500: '服务器内部错误，请稍后重试',
  502: '网关错误，请稍后重试',
  503: '服务暂时不可用，请稍后重试',
  504: '网关超时，请稍后重试',
};

/**
 * 获取友好的错误消息
 */
function getFriendlyMessage(statusCode: number, isNetworkError: boolean): string {
  if (isNetworkError) {
    return '无法连接到服务器，请检查网络连接或确认后端服务是否启动';
  }
  return FRIENDLY_MESSAGES[statusCode] || `请求失败 (${statusCode})`;
}

/**
 * 带容错能力的API请求函数
 * @param path API路径
 * @param options 请求选项
 * @returns Promise<T>
 * @throws ApiError 网络错误或服务器错误时抛出友好错误
 */
export async function apiRequest<T = any>(path: string, options: RequestInit = {}): Promise<T> {
  const { method = 'GET', body, ...rest } = options;

  try {
    const resp = await fetch(API_BASE + path, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
      ...rest,
    });

    // 尝试解析响应体（即使失败也要读取错误信息）
    let errorMessage: string;
    try {
      const data = await resp.json();
      errorMessage = data.message || data.error || await resp.text();
    } catch {
      errorMessage = await resp.text();
    }

    if (!resp.ok) {
      throw new ApiError(
        getFriendlyMessage(resp.status, false),
        resp.status,
        false
      );
    }

    // 处理204 No Content响应
    if (resp.status === 204) {
      return undefined as T;
    }

    return resp.json();
  } catch (error) {
    // 如果已经是ApiError，直接重新抛出
    if (error instanceof ApiError) {
      throw error;
    }

    // 处理网络错误（断网、服务器不可达等）
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new ApiError(
        getFriendlyMessage(0, true),
        0,
        true
      );
    }

    // 其他未知错误
    throw new ApiError(
      error instanceof Error ? error.message : '未知错误，请稍后重试',
      0,
      true
    );
  }
}

/**
 * 带自动重试的API请求
 * @param path API路径
 * @param options 请求选项
 * @param retries 最大重试次数
 */
export async function apiRequestWithRetry<T = any>(
  path: string,
  options: RequestInit = {},
  retries: number = 2
): Promise<T> {
  let lastError: ApiError;

  for (let i = 0; i <= retries; i++) {
    try {
      return await apiRequest<T>(path, options);
    } catch (error) {
      lastError = error as ApiError;

      // 网络错误或5xx服务器错误时重试
      if (lastError.isNetworkError || (lastError.statusCode >= 500 && i < retries)) {
        // 指数退避等待
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 500));
        continue;
      }

      // 其他错误直接抛出
      throw error;
    }
  }

  throw lastError!;
}

/**
 * 检查API服务是否可用
 */
export async function checkApiHealth(): Promise<boolean> {
  try {
    const resp = await fetch(API_BASE + '/health', {
      method: 'GET',
      // 设置较短的超时时间
      signal: AbortSignal.timeout(3000),
    });
    return resp.ok;
  } catch {
    return false;
  }
}
