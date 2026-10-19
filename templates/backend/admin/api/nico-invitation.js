import request from './index'

// ==================== 邀请函管理接口 ====================

// 获取邀请函列表
export function getNicoInvitationList(params) {
  return request.get('/nico_invitations', { params })
}

// 获取邀请函详情（含 HTML 源码）
export function getNicoInvitationDetail(id) {
  return request.get(`/nico_invitations/${id}`)
}

// 新增/上传邀请函 (FormData 或 JSON)
export function createNicoInvitation(data) {
  return request.post('/nico_invitations', data)
}

// 更新邀请函信息或重新上传 HTML 文件
export function updateNicoInvitation(id, data) {
  return request.put(`/nico_invitations/${id}`, data)
}

// 删除邀请函
export function deleteNicoInvitation(id) {
  return request.delete(`/nico_invitations/${id}`)
}

// ==================== 预约报名管理接口 ====================

// 获取预约报名列表与统计
export function getSignupList(params) {
  return request.get('/nico_invitations/signups', { params })
}

// 新增预约记录（管理员手动录入或 H5 提交）
export function createSignup(data) {
  return request.post('/nico_invitations/signup', data)
}

// 更新预约记录（状态、跟进备注、基本信息）
export function updateSignup(id, data) {
  return request.put(`/nico_invitations/signups/${id}`, data)
}

// 删除预约记录
export function deleteSignup(id) {
  return request.delete(`/nico_invitations/signups/${id}`)
}

// 导出预约记录 CSV
export function exportSignups(params) {
  return request.get('/nico_invitations/signups/export', {
    params,
    responseType: 'blob'
  })
}
