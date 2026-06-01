<template>
  <div class="album-detail">
    <main class="main">
      <div class="container">
        <!-- 加载状态 -->
        <LoadingSpinner v-if="loading" />

        <template v-else-if="album">
          <!-- 面包屑 / 返回 -->
          <div class="breadcrumb">
            <router-link to="/" class="back-link">← 返回首页</router-link>
          </div>

          <div class="album-wrap">
            <!-- ========== 左侧：封面 + 信息 ========== -->
            <div class="left">
              <!-- 顶部行：封面 + 社团信息 -->
              <div class="top-row">
                <div class="cover">
                  <img v-if="album.cover_url" :src="album.cover_url" :alt="album.title" />
                  <div v-else class="cover-placeholder"><i class="fas fa-compact-disc"></i></div>
                </div>

                <!-- 社团信息卡片 -->
                <div class="circle-card" v-if="circleDetail">
                  <div class="circle-header" @click="goToCircle(circleDetail)">
                    <img :src="circleDetail.logo_url" :alt="circleDetail.name" class="circle-logo" />
                    <h3 class="circle-name">{{ circleDetail.name }}</h3>
                  </div>
                  <p class="circle-desc" v-if="circleDetail.description">{{ circleDetail.description }}</p>
                  <div class="circle-stats">
                    <span><i class="fas fa-compact-disc"></i> {{ circleDetail.albums.length }} 张专辑</span>
                    <span><i class="fas fa-user-friends"></i> {{ circleDetail.members.length }} 名成员</span>
                  </div>
                  <div class="circle-card-actions">
                    <button class="circle-link-btn" @click.stop="goToCircle(circleDetail)">查看社团 →</button>
                    <button
                      class="circle-follow-btn"
                      :class="{ followed: isCircleFollowed }"
                      @click.stop="toggleCircleFollow"
                    >{{ isCircleFollowed ? '已关注' : '关注社团' }}</button>
                  </div>
                </div>
              </div>

              <div class="info">
                <h1 class="title">{{ album.title }}</h1>
                <p class="artist" @click="goToCircle(album.circle)">@{{ album.circle?.name || '未知社团' }}</p>

                <div class="stats-row">
                  <span class="price-tag" v-if="album.price > 0">¥ {{ album.price }}</span>
                  <span class="price-tag free" v-else>免费</span>
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
              <!-- 试听卡片 -->
              <div class="side-card buy-card">
                <div class="price-row">
                  <span class="price-num" v-if="album.price > 0">¥ {{ album.price }}</span>
                  <span class="price-label free" v-else>免费下载</span>
                </div>
                <button class="buy-btn" @click="handleBuy">
                  {{ album.price > 0 ? '立即试听' : '免费试听' }}
                </button>
                <button
                  class="purchase-btn"
                  :class="{ owned: isPurchased }"
                  :disabled="isPurchased"
                  @click="handlePurchase"
                >
                  {{ isPurchased ? '已拥有' : (album.price > 0 ? `¥${album.price} 购买` : '免费领取') }}
                </button>
                <ul class="buy-info">
                  <li>全曲在线串流试听</li>
                  <li v-if="!isPurchased">购买后永久拥有</li>
                </ul>
              </div>

              <!-- 评论卡片 -->
              <div class="side-card comment-card" ref="commentCard">
                <CommentSection
                  :comments="comments"
                  :total="commentsTotal"
                  :loading="commentsLoading"
                  :is-logged-in="userStore.isLoggedIn"
                  :user-id="userStore.user?.user_id"
                  @load-more="loadMoreComments"
                  @add-comment="handleAddComment"
                  @edit-comment="handleEditComment"
                  @delete-comment="handleDeleteComment"
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
                <p class="rec-artist">@{{ item.circle_name || '未知' }}</p>
              </div>
            </div>
          </div>
        </template>
      </div>
    </main>

    <!-- 购买确认浮窗 -->
    <PurchaseModal
      :album="album"
      :visible="showPurchaseModal"
      :purchasing="purchasing"
      @close="showPurchaseModal = false"
      @confirm="handlePurchaseConfirm"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { fetchAlbum, fetchRecommendations, fetchCircle, fetchComments, addComment, updateComment, deleteComment, checkCircleFollow, followCircle, unfollowCircle, purchaseAlbum, checkPurchased } from '../api'
import { usePlayerStore } from '../stores/player.js'
import { useFavoriteStore } from '../stores/favorite.js'
import { useUserStore } from '../stores/user.js'
import { useNavigation } from '../composables/navigation.js'
import { useAuthGuard } from '../composables/authGuard.js'
import { cleanText } from '../utils/text.js'
import TrackList from '../components/organisms/TrackList.vue'
import CommentSection from '../components/organisms/CommentSection.vue'
import LoadingSpinner from '../components/atoms/LoadingSpinner.vue'
import PurchaseModal from '../components/molecules/PurchaseModal.vue'

const route = useRoute()
const player = usePlayerStore()
const favorite = useFavoriteStore()
const userStore = useUserStore()
const { goToAlbum, goToCircle, goToTag } = useNavigation()
const { guard: guardAsync } = useAuthGuard()

const album = ref(null)
const loading = ref(true)
const recommendList = ref([])
const circleDetail = ref(null)
const isPurchased = ref(false)
const showPurchaseModal = ref(false)
const purchasing = ref(false)
const isCircleFollowed = ref(false)
const comments = ref([])
const commentsTotal = ref(0)
const commentsPage = ref(1)
const commentsLoading = ref(false)

// 收藏状态
const isFavorited = computed(() => album.value ? favorite.isFavorite(album.value.album_id) : false)

async function toggleFavorite() {
  if (!album.value) return
  await guardAsync(() => favorite.toggleFavorite(album.value.album_id), () => alert('请先登录'))
}

async function loadAlbum() {
  try {
    const id = route.params.id
    album.value = await fetchAlbum(id)

    // 检查收藏状态
    if (userStore.isLoggedIn) {
      await favorite.check(album.value.album_id)
      // 检查购买状态
      try {
        const purchaseStatus = await checkPurchased(album.value.album_id)
        isPurchased.value = purchaseStatus.owned
      } catch { /* ignore */ }
    }

    // 初始化评论（详情页返回前 5 条）
    comments.value = album.value.comments || []
    commentsTotal.value = comments.value.length
    commentsPage.value = 1
    if (comments.value.length === 5) {
      try {
        const res = await fetchComments(id, 1, 5)
        commentsTotal.value = res.total
      } catch { /* ignore */ }
    }

    // 加载社团详情 + 关注状态
    if (album.value?.circle?.circle_id) {
      try {
        circleDetail.value = await fetchCircle(album.value.circle.circle_id)
        if (userStore.isLoggedIn) {
          const s = await checkCircleFollow(album.value.circle.circle_id)
          isCircleFollowed.value = s.followed
        }
      } catch {
        circleDetail.value = null
      }
    }

    // 加载推荐作品（随机抽取 5 张）
    try {
      const result = await fetchRecommendations(album.value.album_id)
      recommendList.value = result || []
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
    const res = await fetchComments(album.value.album_id, commentsPage.value, 5)
    comments.value.push(...res.data)
    commentsTotal.value = res.total
  } catch (e) {
    console.error('加载评论失败:', e)
    commentsPage.value--
  } finally {
    commentsLoading.value = false
  }
}

async function toggleCircleFollow() {
  await guardAsync(async () => {
    const circleId = album.value?.circle?.circle_id
    if (!circleId) return
    if (isCircleFollowed.value) {
      await unfollowCircle(circleId)
      isCircleFollowed.value = false
    } else {
      await followCircle(circleId)
      isCircleFollowed.value = true
    }
  }, () => alert('请先登录'))
}

async function handleAddComment(content) {
  try {
    const res = await addComment(album.value.album_id, content)
    comments.value = res.data
    commentsTotal.value = res.total
    commentsPage.value = 1
  } catch (e) {
    console.error('发表评论失败:', e)
  }
}

async function handleEditComment(comment) {
  const newContent = prompt('编辑评论:', comment.content)
  if (!newContent || newContent === comment.content) return
  try {
    await updateComment(comment.comment_id, newContent)
    comment.content = newContent
  } catch (e) {
    console.error('编辑评论失败:', e)
  }
}

async function handleDeleteComment(commentId) {
  if (!confirm('确定删除这条评论？')) return
  try {
    await deleteComment(commentId)
    comments.value = comments.value.filter(c => c.comment_id !== commentId)
    commentsTotal.value--
  } catch (e) {
    console.error('删除评论失败:', e)
  }
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
  if (album.value.tracks?.length > 0) {
    player.playAlbumTracks(album.value.tracks, 0)
  }
}

function handlePurchase() {
  if (isPurchased.value) return
  if (!userStore.isLoggedIn) {
    alert('请先登录')
    return
  }
  showPurchaseModal.value = true
}

async function handlePurchaseConfirm() {
  purchasing.value = true
  try {
    await purchaseAlbum(album.value.album_id)
    isPurchased.value = true
    showPurchaseModal.value = false
  } catch (e) {
    console.error('购买失败:', e)
    alert('购买失败，请重试')
  } finally {
    purchasing.value = false
  }
}

onMounted(() => {
  loadAlbum()
})
</script>

<style scoped>
.album-detail {
  background: var(--color-bg-primary);
  min-height: 100vh;
}

.breadcrumb {
  padding: 1.5rem 0 0.5rem;
}
.back-link {
  color: var(--color-text-muted);
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;
}
.back-link:hover {
  color: var(--color-accent);
}

.main {
  padding: 0 0 4rem;
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

/* 顶部行：封面 + 社团信息 */
.top-row {
  display: flex;
  gap: 32px;
  align-items: flex-start;
  margin-bottom: 24px;
}

.cover {
  position: relative;
  width: 100%;
  max-width: 400px;
  aspect-ratio: 1 / 1;
  border: 1px solid var(--color-border);
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
  background: var(--color-bg-secondary);
  color: var(--color-text-dim);
  font-size: 4rem;
}

/* 社团信息卡片 */
.circle-card {
  flex: 1;
  min-width: 0;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
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
  color: var(--color-accent);
}

.circle-logo {
  width: 64px;
  height: 64px;
  object-fit: cover;
  border: 1px solid var(--color-border);
  flex-shrink: 0;
  transition: transform 0.25s;
}
.circle-header:hover .circle-logo {
  transform: scale(1.15);
}

.circle-name {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.circle-desc {
  font-size: 13px;
  color: var(--color-text-muted);
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
  color: var(--color-text-dim);
  margin-bottom: 18px;
}
.circle-stats i {
  margin-right: 5px;
  color: var(--color-accent);
  width: 16px;
}

.circle-card-actions {
  display: flex;
  gap: 10px;
}
.circle-link-btn {
  background: none;
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  padding: 8px 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.circle-link-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}
.circle-follow-btn {
  background: var(--color-accent);
  border: 1px solid var(--color-accent);
  color: var(--color-text-primary);
  padding: 8px 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.circle-follow-btn.followed {
  background: transparent;
  border-color: var(--color-border);
  color: var(--color-text-muted);
}

/* 信息区 */
.title {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}
.artist {
  font-size: 15px;
  color: var(--color-text-muted);
  margin-bottom: 10px;
  cursor: pointer;
  transition: color 0.2s;
}
.artist:hover {
  color: var(--color-accent);
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
  color: var(--color-accent);
  background: var(--color-bg-secondary);
  padding: 2px 10px;
}
.price-tag.free {
  color: #4caf50;
}

.detail-fav-btn {
  background: none;
  border: none;
  color: var(--color-text-dim);
  font-size: 1.3rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  transition: color 0.2s;
}
.detail-fav-btn:hover {
  color: var(--color-accent);
}
.detail-fav-btn.favorited {
  color: var(--color-accent);
}

.desc {
  margin-bottom: 18px;
}
.desc-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.8;
  margin-bottom: 8px;
  white-space: pre-line;
}
.desc-content {
  font-size: 14px;
  font-weight: 300;
  color: var(--color-text-muted);
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
  background: var(--color-bg-tertiary);
  color: var(--color-text-muted);
  padding: 3px 10px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
}
.tag:hover {
  background: rgba(255, 107, 107, 0.15);
  color: var(--color-accent);
}

.section {
  margin-bottom: 32px;
}

.meta {
  font-size: 12px;
  color: var(--color-text-dim);
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
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  padding: 20px;
  margin-bottom: 16px;
  flex-shrink: 0;
}

.comment-card {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: transparent;
  border: none;
  padding: 0;
  max-height: 60vh;
}

/* 试听卡片 */
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
  color: var(--color-text-primary);
}
.price-label {
  font-size: 12px;
  color: var(--color-accent);
}
.price-label.free {
  color: #4caf50;
}

.buy-btn {
  display: block;
  width: 100%;
  padding: 11px 0;
  background: var(--color-accent);
  color: var(--color-text-primary);
  border: none;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 16px;
  transition: background 0.2s;
}
.buy-btn:hover {
  background: var(--color-accent-hover);
}

.purchase-btn {
  display: block;
  width: 100%;
  padding: 11px 0;
  background: transparent;
  color: var(--color-accent);
  border: 1px solid var(--color-accent);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 16px;
  transition: all 0.2s;
}
.purchase-btn:hover:not(:disabled) {
  background: rgba(255, 107, 107, 0.1);
}
.purchase-btn.owned {
  background: transparent;
  border-color: var(--color-border);
  color: var(--color-text-dim);
  cursor: not-allowed;
}

.buy-info {
  list-style: none;
  font-size: 12px;
  color: var(--color-text-muted);
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
  border-top: 1px solid var(--color-border);
}
.recommend h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
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
  background: var(--color-border);
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
  border: 1px solid var(--color-border);
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
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.rec-artist {
  font-size: 11px;
  color: var(--color-text-dim);
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
  .cover {
    max-width: 100%;
  }
}
</style>
