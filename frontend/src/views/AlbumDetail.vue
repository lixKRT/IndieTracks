<template>
  <div class="album-detail">
    <main class="main">
      <div class="container">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>

        <template v-else-if="album">
          <!-- 面包屑 / 返回 -->
          <div class="breadcrumb">
            <router-link to="/" class="back-link">← 返回首页</router-link>
          </div>

          <div class="album-wrap">
            <!-- ========== 左侧 ========== -->
            <div class="left">
              <!-- 顶部行：封面 + 社团信息 -->
              <div class="top-row">
                <div class="cover">
                  <img v-if="album.cover_url" :src="album.cover_url" :alt="album.title" />
                  <div v-else class="cover-placeholder"><i class="fas fa-compact-disc"></i></div>
                </div>

                <!-- 社团信息卡片 -->
                <div class="circle-card" v-if="circleDetail">
                  <div class="circle-header" @click="goToCircle">
                    <img :src="circleDetail.logo_url" :alt="circleDetail.name" class="circle-logo" />
                    <h3 class="circle-name">{{ circleDetail.name }}</h3>
                  </div>
                  <p class="circle-desc" v-if="circleDetail.description">{{ circleDetail.description }}</p>
                  <div class="circle-stats">
                    <span><i class="fas fa-compact-disc"></i> {{ circleDetail.albums.length }} 张专辑</span>
                    <span><i class="fas fa-user-friends"></i> {{ circleDetail.members.length }} 名成员</span>
                  </div>
                  <button class="circle-link-btn" @click.stop="goToCircle">查看社团 →</button>
                </div>
              </div>

              <!-- 信息区 -->
              <div class="info">
                <h1 class="title">{{ album.title }}</h1>
                <p class="artist" @click="goToCircle">@{{ album.circle?.name || '未知社团' }}</p>

                <div class="stats-row">
                  <span class="price-tag" v-if="album.price > 0">¥ {{ album.price }}</span>
                  <span class="price-tag free" v-else>免费</span>
                  <button
                    class="detail-fav-btn"
                    :class="{ favorited: isFavorited }"
                    @click.stop="toggleFavorite"
                    :title="isFavorited ? '取消收藏' : '收藏'"
                  >{{ isFavorited ? '★' : '☆' }}</button>
                </div>

                <div class="desc" v-if="cleanText(album.info_title) || cleanText(album.info_content)">
                  <p class="desc-title" v-if="cleanText(album.info_title)">{{ cleanText(album.info_title) }}</p>
                  <p class="desc-content" v-if="cleanText(album.info_content)">{{ cleanText(album.info_content) }}</p>
                </div>

                <!-- 标签 -->
                <div class="tags" v-if="album.tags && album.tags.length">
                  <span
                    v-for="tag in album.tags"
                    :key="tag.tag_id"
                    class="tag"
                    @click="goToTag(tag.name)"
                  >#{{ tag.name }}</span>
                </div>

                <!-- 发布信息 -->
                <div class="meta" v-if="album.publish_date">
                  发布于 {{ album.publish_date }}
                </div>

                <!-- 曲目列表（可播放） -->
                <TrackList
                  v-if="album.tracks && album.tracks.length"
                  :tracks="album.tracks"
                  class="section"
                  @preview="handleTrackClick"
                />
              </div>
            </div>

            <!-- ========== 右侧卡片区 ========== -->
            <div class="right">
              <!-- 购买卡片 -->
              <div class="side-card buy-card">
                <div class="price-row">
                  <span class="price-num" v-if="album.price > 0">¥ {{ album.price }}</span>
                  <span class="price-label free" v-else>免费下载</span>
                </div>
                <button class="buy-btn" @click="handleBuy">
                  {{ album.price > 0 ? '立即购买' : '免费下载' }}
                </button>
                <ul class="buy-info">
                  <li>全曲在线串流试听</li>
                </ul>
              </div>

              <!-- 评论卡片 -->
              <div class="side-card comment-card" ref="commentCard">
                <CommentSection
                  :comments="comments"
                  :total="commentsTotal"
                  :loading="commentsLoading"
                  :show-form="false"
                  @load-more="loadMoreComments"
                />
              </div>
            </div>
          </div>

          <!-- ========== 推荐作品 ========== -->
          <div class="recommend" v-if="recommendList.length">
            <h3>推荐作品</h3>
            <div class="rec-list">
              <div
                v-for="item in recommendList"
                :key="item.album_id"
                class="rec-item"
                @click="goToAlbum(item)"
              >
                <div class="rec-cover">
                  <img :src="item.cover_url" :alt="item.title" />
                </div>
                <p class="rec-title">{{ item.title }}</p>
                <p class="rec-artist">@{{ item.circle?.name || '未知' }}</p>
              </div>
            </div>
          </div>
        </template>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchAlbum, fetchAlbums, fetchCircle } from '../api'
import { usePlayerStore } from '../stores/player.js'
import { useFavoriteStore } from '../stores/favorite.js'
import TrackList from '../components/organisms/TrackList.vue'
import CommentSection from '../components/organisms/CommentSection.vue'

// 清洗爬虫抓取的页面噪音
const BOILERPLATE = [
  '提供高品质MP3和无损FLAC格式下载',
  '完整歌曲在线串流',
  '包含实体物品',
  '这个商品需要一个邮寄地址',
  '购买完成后请添加主理人微信',
  '喜欢《',
  '您可以使用BOOST',
  '您可以支付',
  '购买',
  '最少需要',
  '元',
  '在您购买这个商品之后',
  '折扣码',
  '兑换的商品无法使用折扣码',
  '短评',
  '和……相似的作品',
  'OrganicNight',
  '@dizzylab',
  '收件人',
  '手机号',
  '收货地址',
  '附言',
  'BOOST',
  '在声音中寻找本真',
  '粤网文',
  '节目制作经营许可证',
  'Links',
]

function cleanText(text) {
  if (!text) return ''
  // 移除损坏的 Unicode 字符
  let cleaned = text.replace(/[\udc00-\udfff]/g, '')
  // 按行过滤
  const lines = cleaned.split('\n').filter(line => {
    const l = line.trim()
    if (!l) return false
    // 跳过纯数字行、百分比、日期行
    if (/^\d+%$/.test(l)) return false
    if (/^发布于?\d{4}年/.test(l)) return false
    if (/^发布于/.test(l)) return false
    // 跳过包含噪音关键词的行
    for (const bp of BOILERPLATE) {
      if (l.includes(bp)) return false
    }
    return true
  })
  return lines.join('\n').trim()
}

const route = useRoute()
const router = useRouter()
const player = usePlayerStore()
const favorite = useFavoriteStore()

const album = ref(null)
const loading = ref(true)
const recommendList = ref([])
const circleDetail = ref(null)
const comments = ref([])
const commentsTotal = ref(0)
const commentsPage = ref(1)
const commentsLoading = ref(false)

// 收藏状态
const isFavorited = computed(() => album.value ? favorite.isFavorite(album.value.album_id) : false)

function toggleFavorite() {
  if (album.value) {
    favorite.toggleFavorite(album.value.album_id)
  }
}

async function loadAlbum() {
  try {
    const id = route.params.id
    album.value = await fetchAlbum(id)

    // 初始化评论（详情页返回前 5 条）
    comments.value = album.value.comments || []
    commentsTotal.value = comments.value.length // 初始值，后续可能更大
    commentsPage.value = 1
    // 如果返回了 5 条，说明可能还有更多，获取总数
    if (comments.value.length === 5) {
      try {
        const res = await fetch(`/api/albums/${id}/comments?page=1&page_size=5`).then(r => r.json())
        commentsTotal.value = res.total
      } catch { /* ignore */ }
    }

    // 加载社团详情
    if (album.value?.circle?.circle_id) {
      try {
        circleDetail.value = await fetchCircle(album.value.circle.circle_id)
      } catch {
        circleDetail.value = null
      }
    }

    // 加载推荐作品
    try {
      const result = await fetchAlbums({ page_size: 6 })
      recommendList.value = (result.data || []).filter(a => a.album_id !== album.value?.album_id).slice(0, 5)
    } catch {
      recommendList.value = []
    }
  } catch (e) {
    console.error('加载专辑详情失败:', e)
  } finally {
    loading.value = false
  }
}

async function loadMoreComments() {
  if (commentsLoading.value) return
  commentsLoading.value = true
  try {
    commentsPage.value++
    const res = await fetch(`/api/albums/${album.value.album_id}/comments?page=${commentsPage.value}&page_size=5`).then(r => r.json())
    comments.value.push(...res.data)
    commentsTotal.value = res.total
  } catch (e) {
    console.error('加载评论失败:', e)
    commentsPage.value--
  } finally {
    commentsLoading.value = false
  }
}

function goToCircle() {
  if (album.value?.circle) {
    router.push(`/label/${album.value.circle.circle_id}`)
  }
}

function goToTag(name) {
  router.push({ path: '/tag', query: { tag: name } })
}

function goToAlbum(item) {
  router.push(`/album/${item.album_id}`)
}

// 曲目点击播放（TrackList emit 的 preview 事件）
function handleTrackClick(tracks, startIndex) {
  const previewTracks = tracks.filter(t => t.file_type === 'preview')
  if (previewTracks.length === 0) return

  const clickedTrack = tracks[startIndex]
  const previewIndex = previewTracks.findIndex(t => t.file_id === clickedTrack.file_id)

  if (previewIndex >= 0) {
    player.playAlbumTracks(tracks, previewIndex)
  } else {
    const nextPreviewIdx = previewTracks.findIndex(t => {
      const origIdx = tracks.findIndex(tt => tt.file_id === t.file_id)
      return origIdx > startIndex
    })
    if (nextPreviewIdx >= 0) {
      player.playAlbumTracks(tracks, nextPreviewIdx)
    }
  }
}

function handleBuy() {
  if (album.value.price > 0) {
    alert(`正在购买 ${album.value.title} - ¥${album.value.price}`)
  } else {
    alert(`正在下载 ${album.value.title}`)
  }
}

onMounted(() => {
  loadAlbum()
})
</script>

<style scoped>
/* ========================================
   专辑详情页 — 与首页一致的暗黑直角风格
   主色调：#ff6b6b
   ======================================== */

.album-detail {
  background: #0a0a0a;
  min-height: 100vh;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  color: #aaa;
}
.loading-spinner {
  width: 32px;
  height: 32px;
  border: 2px solid #333;
  border-top-color: #ff6b6b;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 面包屑 */
.breadcrumb {
  padding: 1.5rem 0 0.5rem;
}
.back-link {
  color: #aaa;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;
}
.back-link:hover {
  color: #ff6b6b;
}

/* 主体 */
.main {
  padding: 0 0 4rem;
  background: #0a0a0a;
}

.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 左右布局 */
.album-wrap {
  display: flex;
  gap: 48px;
  margin-bottom: 60px;
}

.left {
  flex: 1;
  min-width: 0;
}

/* ==================== 顶部行：封面 + 社团信息 ==================== */
.top-row {
  display: flex;
  gap: 32px;
  align-items: flex-start;
  margin-bottom: 24px;
}

/* 封面 */
.cover {
  position: relative;
  width: 400px;
  max-width: 100%;
  flex-shrink: 0;
  aspect-ratio: 1 / 1;
  border: 1px solid #222;
}
.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a1a1a;
  color: #555;
  font-size: 4rem;
}

/* 社团信息卡片 */
.circle-card {
  flex: 1;
  min-width: 0;
  background: #0a0a0a;
  padding: 24px;
}

.circle-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: opacity 0.2s;
}
.circle-header:hover .circle-name {
  color: #ff6b6b;
}

.circle-logo {
  width: 64px;
  height: 64px;
  object-fit: cover;
  border: 1px solid #333;
  flex-shrink: 0;
  transition: transform 0.25s;
}
.circle-header:hover .circle-logo {
  transform: scale(1.15);
}

.circle-name {
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
}

.circle-desc {
  font-size: 13px;
  color: #999;
  line-height: 1.7;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.circle-stats {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #777;
  margin-bottom: 18px;
}
.circle-stats i {
  margin-right: 5px;
  color: #ff6b6b;
  width: 16px;
}

.circle-link-btn {
  background: none;
  border: 1px solid #444;
  color: #bbb;
  padding: 8px 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.circle-link-btn:hover {
  border-color: #ff6b6b;
  color: #ff6b6b;
}

/* 信息区 */
.title {
  font-size: 28px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 4px;
}
.artist {
  font-size: 15px;
  color: #888;
  margin-bottom: 10px;
  cursor: pointer;
  transition: color 0.2s;
}
.artist:hover {
  color: #ff6b6b;
}

.stats-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 18px;
}
.price-tag {
  font-size: 13px;
  font-weight: 600;
  color: #ff6b6b;
  background: #1a1a1a;
  padding: 2px 10px;
}
.price-tag.free {
  color: #4caf50;
}

.detail-fav-btn {
  background: none;
  border: none;
  color: #666;
  font-size: 1.3rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  transition: color 0.2s;
}
.detail-fav-btn:hover {
  color: #ff6b6b;
}
.detail-fav-btn.favorited {
  color: #ff6b6b;
}

.desc {
  margin-bottom: 18px;
}
.desc-title {
  font-size: 15px;
  font-weight: 600;
  color: #eee;
  line-height: 1.8;
  margin-bottom: 8px;
  white-space: pre-line;
}
.desc-content {
  font-size: 14px;
  font-weight: 300;
  color: #aaa;
  line-height: 1.8;
  white-space: pre-line;
}

/* 标签 */
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 32px;
}
.tag {
  background: #2a2a2a;
  color: #bbb;
  padding: 3px 10px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
}
.tag:hover {
  background: #3a3a3a;
}

/* 分区标题 */
.section {
  margin-bottom: 32px;
}

/* 发布信息 */
.meta {
  font-size: 12px;
  color: #666;
  margin-top: 8px;
}

/* 右侧 */
.right {
  width: 300px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

.side-card {
  background: #1a1a1a;
  border: 1px solid #222;
  padding: 20px;
  margin-bottom: 16px;
  flex-shrink: 0;
}

.comment-card {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 购买卡片 */
.price-row {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 8px;
  margin-bottom: 14px;
}
.price-num {
  font-size: 26px;
  font-weight: 700;
  color: #fff;
}
.price-label {
  font-size: 12px;
  color: #ff6b6b;
}
.price-label.free {
  color: #4caf50;
}

.buy-btn {
  display: block;
  width: 100%;
  padding: 11px 0;
  background: #ff6b6b;
  color: #fff;
  border: none;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 16px;
  transition: background 0.2s;
}
.buy-btn:hover {
  background: #ff8787;
}

.buy-info {
  list-style: none;
  font-size: 12px;
  color: #aaa;
  padding: 0;
}
.buy-info li {
  margin-bottom: 4px;
  padding-left: 8px;
}

/* 推荐作品 */
.recommend {
  margin-top: 20px;
  padding-top: 32px;
  border-top: 1px solid #222;
}
.recommend h3 {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 20px;
}
.rec-list {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 8px;
}
.rec-list::-webkit-scrollbar {
  height: 4px;
}
.rec-list::-webkit-scrollbar-thumb {
  background: #333;
}
.rec-item {
  flex-shrink: 0;
  width: 140px;
  cursor: pointer;
  transition: transform 0.2s;
}
.rec-item:hover {
  transform: translateY(-4px);
}
.rec-cover {
  width: 140px;
  height: 140px;
  border: 1px solid #222;
  margin-bottom: 8px;
  overflow: hidden;
}
.rec-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.rec-title {
  font-size: 13px;
  color: #ddd;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.rec-artist {
  font-size: 11px;
  color: #777;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 响应式 */
@media (max-width: 768px) {
  .album-wrap {
    flex-direction: column;
    gap: 32px;
  }
  .right {
    width: 100%;
  }
  .top-row {
    flex-direction: column;
  }
  .cover {
    width: 100%;
    max-width: 100%;
  }
}
</style>
