<template>
  <div class="album-detail">
    <main class="main">
      <div class="container">
        <!-- 面包屑 / 返回 -->
        <div class="breadcrumb">
          <router-link to="/" class="back-link">← 返回首页</router-link>
        </div>

        <div class="album-wrap">
          <!-- ========== 左侧：封面 + 信息 ========== -->
          <div class="left">
            <div class="cover">
              <img :src="album.cover" :alt="album.title" />
              <span v-if="album.isHiRes" class="hi-res">Hi-Res</span>
            </div>

            <div class="info">
              <h1 class="title">{{ album.title }}</h1>
              <p class="artist">@{{ album.artist }}</p>

              <div class="stats-row">
                <span class="like">♥ {{ formatCount(album.likeCount) }}</span>
                <span class="price-tag" v-if="album.price > 0">¥ {{ album.price }}</span>
                <span class="price-tag free" v-else>免费</span>
              </div>

              <div class="desc">
                <p>{{ album.desc }}</p>
              </div>

              <!-- 标签 -->
              <div class="tags">
                <span
                  v-for="tag in album.tags"
                  :key="tag"
                  class="tag"
                  @click="$emit('tag-click', tag)"
                >{{ tag }}</span>
              </div>

              <!-- 曲目列表 -->
              <div class="section">
                <h3>曲目列表</h3>
                <div class="tracks">
                  <div
                    v-for="(item, idx) in album.trackList"
                    :key="idx"
                    class="track"
                  >
                    <div class="track-num">{{ String(idx + 1).padStart(2, '0') }}</div>
                    <div class="track-body">
                      <div class="t-name">{{ item.name }}</div>
                      <div class="t-credit">
                        歌：{{ item.vocal }} / 作詞：{{ item.lyric }} / 作曲：{{ item.compose }}
                      </div>
                    </div>
                    <div class="track-dur">{{ item.duration || '--:--' }}</div>
                  </div>
                </div>
              </div>

              <!-- 制作人员 -->
              <div class="section" v-if="album.creditList.length">
                <h3>制作人员</h3>
                <div class="credits">
                  <p v-for="(line, idx) in album.creditList" :key="idx">{{ line }}</p>
                </div>
              </div>

              <!-- 发布信息 -->
              <div class="meta">
                发布于 {{ album.publishTime }}
              </div>
            </div>
          </div>

          <!-- ========== 右侧卡片区 ========== -->
          <div class="right">
            <!-- 购买卡片 -->
            <div class="side-card buy-card">
              <div class="price-row">
                <span class="price-num">¥ {{ album.price || '免费' }}</span>
                <span class="price-label" v-if="album.price > 0">数字专辑</span>
                <span class="price-label free" v-else>免费下载</span>
              </div>
              <button class="buy-btn" @click="$emit('purchase', album)">
                {{ album.price > 0 ? '立即购买' : '免费下载' }}
              </button>
              <ul class="buy-info">
                <li>高品质 MP3 下载</li>
                <li>无损 FLAC 下载</li>
                <li>全曲在线串流试听</li>
              </ul>
            </div>

            <!-- 试听卡片 -->
            <div class="side-card player-card">
              <h3>试听</h3>
              <div class="player">
                <button class="play-btn" @click="$emit('preview', album)">▶</button>
                <div class="progress-bar">
                  <div class="progress" :style="{ width: playerProgress + '%' }"></div>
                </div>
                <span class="time-label">{{ playerTime }}</span>
              </div>
              <div class="preview-list">
                <div
                  v-for="(p, i) in album.previewList.slice(0, 5)"
                  :key="i"
                  class="preview"
                  @click="$emit('preview-track', p)"
                >
                  <span class="no">{{ String(i + 1).padStart(2, '0') }}</span>
                  <span class="p-name">{{ p.name }}</span>
                  <span class="time">{{ p.time }}</span>
                </div>
              </div>
            </div>

            <!-- 支持者卡片 -->
            <div class="side-card support-card">
              <h3>支持此作品的人</h3>
              <div class="supporters">
                <div
                  v-for="i in supporterCount"
                  :key="i"
                  class="supporter-avatar"
                  :style="{ background: supporterColors[(i - 1) % supporterColors.length] }"
                ></div>
                <span v-if="supporterCount === 0" class="no-supporters">暂无支持者</span>
              </div>
            </div>

            <!-- 短评卡片 -->
            <div class="side-card comment-card">
              <h3>短评</h3>
              <div class="comments">
                <div v-if="comments.length === 0" class="no-comments">暂无评论</div>
                <div v-for="(c, i) in comments" :key="i" class="comment">
                  <div class="comment-header">
                    <span class="comment-user">{{ c.user }}</span>
                    <span class="comment-time">{{ c.time }}</span>
                  </div>
                  <p class="comment-body">{{ c.text }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ========== 推荐作品 ========== -->
        <div class="recommend" v-if="recommendList.length">
          <h3>推荐作品</h3>
          <div class="rec-list">
            <div
              v-for="item in recommendList"
              :key="item.id"
              class="rec-item"
              @click="$emit('album-click', item)"
            >
              <div class="rec-cover">
                <img :src="item.cover" :alt="item.title" />
              </div>
              <p class="rec-title">{{ item.title }}</p>
              <p class="rec-artist">@{{ item.artist }}</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

/* ========================================
   模拟数据 — 接入后端 API 后直接替换
   ======================================== */
const album = ref({
  id: 1,
  cover: 'https://placehold.co/600x600/1a1a1a/ffffff?text=Album+Cover',
  title: 'Emotional Air',
  artist: '優しさの配列',
  likeCount: 1327,
  desc: '这是一张融合了流行、电子与人声的独立音乐专辑。所有曲目均以高解析度录制，力求为听众带来最纯粹的声音体验。专辑封面由知名插画师设计，呈现了梦幻般的视觉世界。',
  price: 50,
  isHiRes: true,
  tags: ['#pops', '#vocal', '#原创', '#同人音乐'],
  publishTime: '2026-03-15',
  trackList: [
    { name: 'intro', vocal: '—', lyric: '—', compose: '優しさの配列', duration: '1:42' },
    { name: '空気の重さ', vocal: '初音ミク', lyric: '佐藤', compose: '優しさの配列', duration: '4:18' },
    { name: 'Float', vocal: 'IA', lyric: 'Tanaka', compose: '優しさの配列', duration: '3:55' },
    { name: 'エモーショナル', vocal: '巡音ルカ', lyric: '山田', compose: '優しさの配列', duration: '4:30' },
    { name: 'Afterglow', vocal: '初音ミク', lyric: 'Suzuki', compose: '優しさの配列', duration: '5:02' },
    { name: 'outro', vocal: '—', lyric: '—', compose: '優しさの配列', duration: '2:10' }
  ],
  creditList: [
    'Produced by: 優しさの配列',
    'Mixed & Mastered by: Studio ECHO',
    'Artwork: 佐藤花子',
    'Special Thanks: All listeners'
  ],
  previewList: [
    { name: '空気の重さ', time: '1:30' },
    { name: 'Float', time: '1:30' },
    { name: 'エモーショナル', time: '1:30' },
    { name: 'Afterglow', time: '1:30' }
  ]
})

const recommendList = ref([
  { id: 2, title: '78+13=91', artist: '78Records', cover: 'https://placehold.co/300x300/1a1a1a/ffffff?text=78%2B13%3D91' },
  { id: 3, title: '山越し独り', artist: 'Kirisame Records', cover: 'https://placehold.co/300x300/1a1a1a/ffffff?text=Yamagoshi' },
  { id: 4, title: '非对称集：2026冬', artist: 'T^T Dynamics', cover: 'https://placehold.co/300x300/1a1a1a/ffffff?text=Asymmetry' },
  { id: 5, title: '78+91=13²', artist: '78Records', cover: 'https://placehold.co/300x300/1a1a1a/ffffff?text=78%2B91' },
  { id: 6, title: 'IONOSPHERE', artist: 'project:2000x', cover: 'https://placehold.co/300x300/1a1a1a/ffffff?text=IONO' }
])

const comments = ref([
  { user: '音乐爱好者', time: '2026-04-01', text: '非常棒的专辑，编曲层次感很强！' },
  { user: '电子羊', time: '2026-03-28', text: '封面太好看了，音乐也很抓耳。' },
  { user: '深夜听众', time: '2026-03-20', text: '第二首单曲循环中…' }
])

const playerProgress = ref(30)
const playerTime = ref('1:24 / 4:18')
const supporterCount = ref(8)
const supporterColors = ['#ff6b6b', '#4ecdc4', '#ffe66d', '#a29bfe', '#fd79a8', '#00cec9', '#fab1a0', '#81ecec']

function formatCount(n) {
  if (n >= 1000) return (n / 1000).toFixed(1) + 'k'
  return String(n)
}

onMounted(() => {
  const albumId = route.params.id
  console.log('当前专辑ID：', albumId)
  // TODO: 根据 albumId 请求后端 API，赋值 album / recommendList / comments
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

/* 封面 */
.cover {
  position: relative;
  width: 100%;
  max-width: 400px;
  aspect-ratio: 1 / 1;
  margin-bottom: 24px;
  border: 1px solid #222;
}
.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.hi-res {
  position: absolute;
  top: 0;
  left: 0;
  background: #1a1a1a;
  color: #ff6b6b;
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  letter-spacing: 1px;
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
}

.stats-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 18px;
}
.like {
  font-size: 14px;
  color: #ff6b6b;
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

.desc {
  font-size: 14px;
  color: #bbb;
  line-height: 1.8;
  margin-bottom: 18px;
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
.section h3 {
  font-size: 15px;
  font-weight: 600;
  color: #ff6b6b;
  margin-bottom: 12px;
  padding-bottom: 6px;
  border-bottom: 1px solid #222;
}

/* 曲目列表 */
.track {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #1a1a1a;
  transition: background 0.15s;
}
.track:hover {
  background: #111;
}
.track:last-child {
  border-bottom: none;
}
.track-num {
  flex-shrink: 0;
  width: 28px;
  font-size: 12px;
  color: #555;
  text-align: right;
}
.track-body {
  flex: 1;
  min-width: 0;
}
.t-name {
  font-size: 14px;
  font-weight: 500;
  color: #eee;
}
.t-credit {
  font-size: 11px;
  color: #777;
  margin-top: 2px;
}
.track-dur {
  flex-shrink: 0;
  font-size: 12px;
  color: #555;
}

/* 制作人员 */
.credits {
  font-size: 13px;
  color: #bbb;
  line-height: 1.7;
}
.credits p {
  margin-bottom: 3px;
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
}

.side-card {
  background: #1a1a1a;
  border: 1px solid #222;
  padding: 20px;
  margin-bottom: 16px;
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

/* 试听卡片 */
.player-card h3 {
  font-size: 14px;
  font-weight: 600;
  color: #ff6b6b;
  margin-bottom: 14px;
}
.player {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}
.play-btn {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  background: #ff6b6b;
  color: #fff;
  border: none;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}
.play-btn:hover {
  background: #ff8787;
}
.progress-bar {
  flex: 1;
  height: 4px;
  background: #333;
}
.progress {
  height: 100%;
  background: #ff6b6b;
  transition: width 0.3s;
}
.time-label {
  flex-shrink: 0;
  font-size: 11px;
  color: #555;
}

.preview-list {
  border-top: 1px solid #222;
  padding-top: 8px;
}
.preview {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 4px;
  cursor: pointer;
  transition: background 0.15s;
}
.preview:hover {
  background: #222;
}
.preview .no {
  width: 22px;
  font-size: 11px;
  color: #555;
}
.preview .p-name {
  flex: 1;
  font-size: 12px;
  color: #ddd;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.preview .time {
  font-size: 11px;
  color: #555;
}

/* 支持者卡片 */
.support-card h3,
.comment-card h3 {
  font-size: 14px;
  font-weight: 600;
  color: #ff6b6b;
  margin-bottom: 12px;
}
.supporters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.supporter-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}
.no-supporters {
  font-size: 12px;
  color: #666;
}

/* 短评卡片 */
.comment {
  padding: 10px 0;
  border-bottom: 1px solid #222;
}
.comment:last-child {
  border-bottom: none;
}
.comment:first-child {
  padding-top: 0;
}
.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}
.comment-user {
  font-size: 12px;
  font-weight: 600;
  color: #ddd;
}
.comment-time {
  font-size: 11px;
  color: #555;
}
.comment-body {
  font-size: 13px;
  color: #aaa;
  line-height: 1.5;
}
.no-comments {
  font-size: 12px;
  color: #666;
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
  .cover {
    max-width: 100%;
  }
}
</style>
