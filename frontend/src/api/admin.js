import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

// ===== Dashboard =====
export async function getDashboardStats() {
  const { data } = await api.get('/admin/dashboard/stats');
  return data;
}

export async function getDashboardTrends(period = 'month') {
  const { data } = await api.get('/admin/dashboard/trends', { params: { period } });
  return data;
}

export async function getTopAlbums(period = 'month', limit = 50) {
  const { data } = await api.get('/admin/dashboard/top-albums', { params: { period, limit } });
  return data;
}

export async function getTopCircles(period = 'month', limit = 50) {
  const { data } = await api.get('/admin/dashboard/top-circles', { params: { period, limit } });
  return data;
}

export async function getTagDistribution() {
  const { data } = await api.get('/admin/dashboard/tag-distribution');
  return data;
}

// ===== 专辑管理 =====
export async function getAdminAlbums(params = {}) {
  const { data } = await api.get('/admin/albums', { params });
  return data;
}

export async function createAlbum(albumData) {
  const { data } = await api.post('/admin/albums', albumData);
  return data;
}

export async function updateAlbum(albumId, albumData) {
  const { data } = await api.put(`/admin/albums/${albumId}`, albumData);
  return data;
}

export async function deleteAlbum(albumId) {
  const { data } = await api.delete(`/admin/albums/${albumId}`);
  return data;
}

// ===== 社团管理 =====
export async function getAdminCircles(params = {}) {
  const { data } = await api.get('/admin/circles', { params });
  return data;
}

export async function createCircle(circleData) {
  const { data } = await api.post('/admin/circles', circleData);
  return data;
}

export async function updateCircle(circleId, circleData) {
  const { data } = await api.put(`/admin/circles/${circleId}`, circleData);
  return data;
}

export async function deleteCircle(circleId) {
  const { data } = await api.delete(`/admin/circles/${circleId}`);
  return data;
}

export async function getCircleMembers(circleId) {
  const { data } = await api.get(`/admin/circles/${circleId}/members`);
  return data;
}

export async function addCircleMember(circleId, userId) {
  const { data } = await api.post(`/admin/circles/${circleId}/members`, { user_id: userId });
  return data;
}

export async function removeCircleMember(circleId, userId) {
  const { data } = await api.delete(`/admin/circles/${circleId}/members/${userId}`);
  return data;
}

// ===== 用户管理 =====
export async function getAdminUsers(params = {}) {
  const { data } = await api.get('/admin/users', { params });
  return data;
}

export async function updateUser(userId, userData) {
  const { data } = await api.put(`/admin/users/${userId}`, userData);
  return data;
}

export async function deleteUser(userId) {
  const { data } = await api.delete(`/admin/users/${userId}`);
  return data;
}

// ===== 标签管理 =====
export async function getAdminTags(params = {}) {
  const { data } = await api.get('/admin/tags', { params });
  return data;
}

export async function createTag(tagData) {
  const { data } = await api.post('/admin/tags', tagData);
  return data;
}

export async function updateTag(tagId, tagData) {
  const { data } = await api.put(`/admin/tags/${tagId}`, tagData);
  return data;
}

export async function deleteTag(tagId) {
  const { data } = await api.delete(`/admin/tags/${tagId}`);
  return data;
}

// ===== 评论管理 =====
export async function getAdminComments(params = {}) {
  const { data } = await api.get('/admin/comments', { params });
  return data;
}

export async function deleteComment(commentId) {
  const { data } = await api.delete(`/admin/comments/${commentId}`);
  return data;
}
