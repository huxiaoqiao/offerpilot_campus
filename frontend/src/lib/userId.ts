/**
 * 获取当前用户ID（从localStorage读取）
 * 所有需要 user_id 的 API 调用都应使用此函数
 */
export function getCurrentUserId(): string {
  return localStorage.getItem('offerpilot_profile_id') || 'default'
}
