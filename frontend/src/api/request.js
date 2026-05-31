import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

/**
 * 专辑列表
 */
export async function fetchAlbums(params = {}) {
  const { data } = await api.get('/albums', { params });
  return data;
}

/**
 * 专辑详情
 */
export async function fetchAlbum(album_id) {
  const { data } = await api.get(`/albums/${album_id}`);
  return data;
}

/**
 * 社团列表（后端已聚合 representative_tags / preview_albums / latest_album_date）
 */
export async function fetchCircles() {
  const { data } = await api.get('/circles');
  return data;
}

/**
 * 社团详情
 */
export async function fetchCircle(circle_id) {
  const { data } = await api.get(`/circles/${circle_id}`);
  return data;
}

/**
 * 标签列表（异步）
 */
export async function getTags() {
  const { data } = await api.get('/tags');
  return data;
}

/**
 * 用户详情
 */
export async function fetchUser(user_id) {
  const { data } = await api.get(`/users/${user_id}`);
  return data;
}
