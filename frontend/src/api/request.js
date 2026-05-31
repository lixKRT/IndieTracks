import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

// 401 拦截器：未登录时清除用户状态
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // 由各 store 自行处理，这里只做日志
      console.warn('API 401:', error.config?.url);
    }
    return Promise.reject(error);
  }
);

// ===== 专辑 =====
export async function fetchAlbums(params = {}) {
  const { data } = await api.get('/albums', { params });
  return data;
}

export async function fetchAlbum(album_id) {
  const { data } = await api.get(`/albums/${album_id}`);
  return data;
}

// ===== 社团 =====
export async function fetchCircles() {
  const { data } = await api.get('/circles');
  return data;
}

export async function fetchCircle(circle_id) {
  const { data } = await api.get(`/circles/${circle_id}`);
  return data;
}

// ===== 标签 =====
export async function getTags() {
  const { data } = await api.get('/tags');
  return data;
}

// ===== 用户 =====
export async function fetchUser(user_id) {
  const { data } = await api.get(`/users/${user_id}`);
  return data;
}

// ===== 评论 =====
export async function fetchComments(albumId, page = 1, pageSize = 5) {
  const { data } = await api.get(`/albums/${albumId}/comments`, { params: { page, page_size: pageSize } });
  return data;
}

export async function addComment(albumId, content) {
  const { data } = await api.post(`/albums/${albumId}/comments`, { content });
  return data;
}

export async function updateComment(commentId, content) {
  const { data } = await api.put(`/comments/${commentId}`, { content });
  return data;
}

export async function deleteComment(commentId) {
  const { data } = await api.delete(`/comments/${commentId}`);
  return data;
}

// ===== 收藏 =====
export async function getFavorites() {
  const { data } = await api.get('/favorites');
  return data;
}

export async function addFavorite(albumId) {
  const { data } = await api.post(`/favorites/${albumId}`);
  return data;
}

export async function removeFavorite(albumId) {
  const { data } = await api.delete(`/favorites/${albumId}`);
  return data;
}

export async function checkFavorite(albumId) {
  const { data } = await api.get(`/favorites/${albumId}/status`);
  return data;
}

// ===== 关注社团 =====
export async function followCircle(circleId) {
  const { data } = await api.post(`/circle-follows/${circleId}`);
  return data;
}

export async function unfollowCircle(circleId) {
  const { data } = await api.delete(`/circle-follows/${circleId}`);
  return data;
}

export async function checkCircleFollow(circleId) {
  const { data } = await api.get(`/circle-follows/${circleId}/status`);
  return data;
}

// ===== 关注用户 =====
export async function followUser(userId) {
  const { data } = await api.post(`/user-follows/${userId}`);
  return data;
}

export async function unfollowUser(userId) {
  const { data } = await api.delete(`/user-follows/${userId}`);
  return data;
}

export async function checkUserFollow(userId) {
  const { data } = await api.get(`/user-follows/${userId}/status`);
  return data;
}

// ===== 用户主页 =====
export async function getUserFavorites(userId) {
  const { data } = await api.get(`/users/${userId}/favorites`);
  return data;
}

export async function getUserFollowingCircles(userId) {
  const { data } = await api.get(`/users/${userId}/following-circles`);
  return data;
}

export async function getUserFollowingUsers(userId) {
  const { data } = await api.get(`/users/${userId}/following-users`);
  return data;
}

// ===== 认证 =====
export async function register(form) {
  const { data } = await api.post('/auth/register', form);
  return data;
}

export async function login(form) {
  const { data } = await api.post('/auth/login', form);
  return data;
}

export async function logout() {
  const { data } = await api.post('/auth/logout');
  return data;
}

export async function fetchMe() {
  const { data } = await api.get('/auth/me');
  return data;
}

export async function uploadAvatar(file) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/auth/avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return data;
}
