<template>
  <div class="album-form-page">
    <h1 class="page-title">{{ isEdit ? '编辑专辑' : '新增专辑' }}</h1>

    <LoadingSpinner v-if="loading" />

    <template v-else>
      <!-- 基本信息表单 -->
      <form @submit.prevent="handleSubmit" class="album-form">
        <div class="form-section">
          <h3 class="section-title">基本信息</h3>
          <div class="form-row">
            <div class="form-group">
              <label>标题 *</label>
              <input type="text" v-model="form.title" required placeholder="专辑标题" />
            </div>
            <div class="form-group">
              <label>所属社团 *</label>
              <select v-model="form.circle_id" required :disabled="!isStaff">
                <option value="">请选择社团</option>
                <option v-for="circle in circles" :key="circle.circle_id" :value="circle.circle_id">{{ circle.name }}</option>
              </select>
            </div>
          </div>

          <!-- 封面上传 -->
          <div class="form-group">
            <label>封面</label>
            <div class="cover-upload">
              <img v-if="form.cover_url" :src="form.cover_url" class="cover-preview" />
              <div v-else class="cover-placeholder"><i class="fas fa-image"></i></div>
              <div class="cover-actions">
                <input type="text" v-model="form.cover_url" placeholder="封面 URL" class="cover-url-input" />
                <input type="file" ref="coverFile" accept="image/*" style="display:none" @change="uploadCover" />
                <button type="button" class="btn-upload-cover" @click="$refs.coverFile.click()">
                  <i class="fas fa-upload"></i> 上传封面
                </button>
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>价格</label>
              <input type="number" v-model="form.price" min="0" step="0.01" placeholder="0" />
            </div>
            <div class="form-group">
              <label>发布日期</label>
              <input type="date" v-model="form.publish_date" />
            </div>
          </div>

          <div class="form-group">
            <label>内容标题</label>
            <input type="text" v-model="form.info_title" placeholder="专辑内容标题" />
          </div>
          <div class="form-group">
            <label>内容描述</label>
            <textarea v-model="form.info_content" rows="4" placeholder="专辑内容描述"></textarea>
          </div>
        </div>

        <!-- 标签管理（编辑模式） -->
        <div v-if="isEdit" class="form-section">
          <h3 class="section-title">标签管理</h3>
          <div class="tags-list">
            <span v-for="tag in albumTags" :key="tag.tag_id" class="tag-item">
              #{{ tag.name }}
              <button type="button" class="tag-remove" @click="removeTag(tag)" title="移除">&times;</button>
            </span>
            <span v-if="albumTags.length === 0" class="no-tags">暂无标签</span>
          </div>
          <div class="add-tag">
            <input type="text" v-model="newTagName" placeholder="输入标签名" @keyup.enter="addTag" />
            <button type="button" class="btn-add-tag" @click="addTag" :disabled="!newTagName.trim()">添加</button>
          </div>
        </div>

        <!-- 曲目管理（编辑模式） -->
        <div v-if="isEdit" class="form-section">
          <h3 class="section-title">曲目列表</h3>
          <div class="tracks-list">
            <div v-for="(track, index) in albumTracks" :key="track.file_id" class="track-item"
              :class="{ active: isCurrentTrack(track) }">
              <span class="track-index">
                <span v-if="isCurrentTrack(track) && isPlaying" class="playing-indicator">
                  <span></span><span></span><span></span>
                </span>
                <span v-else>{{ String(index + 1).padStart(2, '0') }}</span>
              </span>
              <span class="track-name" :class="{ 'is-playing': isCurrentTrack(track) && isPlaying }">{{ track.file_name }}</span>
              <span class="track-duration">{{ track.track_length }}</span>
              <span class="track-type">{{ track.file_type }}</span>
              <div class="track-actions">
                <button type="button" class="btn-action" @click="playTrack(track, index)" title="播放">
                  <i :class="isCurrentTrack(track) && isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
                </button>
                <a :href="getTrackUrl(track)" download class="btn-action" title="下载"><i class="fas fa-download"></i></a>
                <button type="button" class="btn-action btn-delete" @click="deleteTrack(track)" title="删除"><i class="fas fa-trash"></i></button>
              </div>
            </div>
            <div v-if="albumTracks.length === 0" class="no-tracks">暂无曲目</div>
          </div>
          <button type="button" class="btn-upload-track" @click="showUploadModal = true">
            <i class="fas fa-upload"></i> 上传曲目
          </button>
        </div>

        <div class="form-actions">
          <router-link to="/admin/albums" class="btn-cancel">返回列表</router-link>
          <button type="submit" class="btn-submit" :disabled="submitting">
            {{ submitting ? '保存中...' : '保存' }}
          </button>
        </div>
      </form>
    </template>

    <!-- 曲目上传弹窗 -->
    <Teleport to="body">
      <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
        <div class="modal-content">
          <div class="modal-header">
            <h3>上传曲目</h3>
            <button class="modal-close" @click="showUploadModal = false">&times;</button>
          </div>
          <div class="modal-body">
            <div class="upload-area" @dragover.prevent @drop.prevent="handleDrop">
              <input type="file" ref="trackFileInput" accept=".mp3,.flac,.wav" style="display:none" @change="handleFileSelect" />
              <div v-if="!selectedFile" class="upload-placeholder" @click="$refs.trackFileInput.click()">
                <i class="fas fa-cloud-upload-alt"></i>
                <p>点击选择或拖拽音频文件到此处</p>
                <span class="upload-hint">支持 MP3、FLAC、WAV 格式</span>
              </div>
              <div v-else class="upload-file-info">
                <i class="fas fa-music"></i>
                <span>{{ selectedFile.name }}</span>
                <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
                <button type="button" class="btn-remove-file" @click="selectedFile = null">&times;</button>
              </div>
            </div>
            <div v-if="uploadProgress > 0" class="upload-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
              </div>
              <span>{{ uploadProgress }}%</span>
            </div>
            <div class="form-actions">
              <button type="button" class="btn-cancel" @click="showUploadModal = false">取消</button>
              <button type="button" class="btn-submit" @click="uploadTrack" :disabled="!selectedFile || uploading">
                {{ uploading ? '上传中...' : '确认上传' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
import { createAlbum, updateAlbum } from '../../api/admin.js';
import { fetchCircles } from '../../api/index.js';
import { useUserStore } from '../../stores/user.js';
import { usePlayerStore } from '../../stores/player.js';
import LoadingSpinner from '../../components/atoms/LoadingSpinner.vue';

export default {
  name: 'AdminAlbumForm',
  components: { LoadingSpinner },
  setup() {
    const userStore = useUserStore();
    const playerStore = usePlayerStore();
    return { userStore, playerStore };
  },
  data() {
    return {
      form: { title: '', cover_url: '', price: 0, circle_id: '', info_title: '', info_content: '', publish_date: '' },
      circles: [],
      albumTags: [],
      albumTracks: [],
      newTagName: '',
      loading: true,
      submitting: false,
      showUploadModal: false,
      selectedFile: null,
      uploadProgress: 0,
      uploading: false
    };
  },
  computed: {
    isEdit() { return !!this.$route.params.id; },
    isStaff() { return this.userStore.user?.user_role === 'staff'; },
    isPlaying() { return this.playerStore.is_playing; }
  },
  async mounted() { await this.loadData(); },
  methods: {
    async loadData() {
      this.loading = true;
      try {
        const circleResult = await fetchCircles({ page_size: 1000 });
        this.circles = circleResult.data || [];

        if (this.isEdit) {
          const albumId = this.$route.params.id;
          const resp = await fetch(`/api/albums/${albumId}`);
          const album = await resp.json();
          if (album) {
            this.form = {
              title: album.title || '',
              cover_url: album.cover_url || '',
              price: album.price || 0,
              circle_id: album.circle?.circle_id || '',
              info_title: album.info_title || '',
              info_content: album.info_content || '',
              publish_date: album.publish_date || ''
            };
            this.albumTags = album.tags || [];
            this.albumTracks = album.tracks || [];
          }
        }
      } catch (e) { console.error('加载数据失败:', e); }
      finally { this.loading = false; }
    },
    async handleSubmit() {
      this.submitting = true;
      try {
        if (this.isEdit) {
          await updateAlbum(this.$route.params.id, this.form);
          alert('专辑更新成功');
        } else {
          await createAlbum(this.form);
          alert('专辑创建成功');
          this.$router.push('/admin/albums');
        }
      } catch (e) {
        console.error('保存失败:', e);
        alert('保存失败: ' + (e.response?.data?.error || e.message));
      } finally { this.submitting = false; }
    },
    // 封面上传
    async uploadCover() {
      const file = this.$refs.coverFile.files[0];
      if (!file) return;
      const formData = new FormData();
      formData.append('file', file);
      try {
        const resp = await fetch('/api/admin/upload/cover', { method: 'POST', body: formData });
        const data = await resp.json();
        if (data.url) {
          this.form.cover_url = data.url;
        }
      } catch (e) { console.error('上传封面失败:', e); alert('上传失败'); }
    },
    // 标签管理
    async addTag() {
      const name = this.newTagName.trim();
      if (!name) return;
      try {
        const resp = await fetch(`/api/admin/albums/${this.$route.params.id}/tags`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name })
        });
        if (resp.ok) {
          this.albumTags.push({ tag_id: Date.now(), name });
          this.newTagName = '';
        }
      } catch (e) { console.error('添加标签失败:', e); }
    },
    async removeTag(tag) {
      try {
        const resp = await fetch(`/api/admin/albums/${this.$route.params.id}/tags/${tag.tag_id}`, { method: 'DELETE' });
        if (resp.ok) {
          this.albumTags = this.albumTags.filter(t => t.tag_id !== tag.tag_id);
        }
      } catch (e) { console.error('移除标签失败:', e); }
    },
    // 曲目管理 - 使用播放器
    isCurrentTrack(track) {
      const current = this.playerStore.current_track;
      return current && current.file_id === track.file_id;
    },
    playTrack(track, index) {
      const previewTracks = this.albumTracks.filter(t => t.file_type === 'preview');
      if (previewTracks.length === 0) return;

      const clickedPreviewIndex = previewTracks.findIndex(t => t.file_id === track.file_id);
      if (clickedPreviewIndex >= 0) {
        this.playerStore.playAlbumTracks(this.albumTracks, clickedPreviewIndex);
      } else {
        // 如果点击的不是 preview，找下一个 preview
        const nextIdx = previewTracks.findIndex(t => {
          const origIdx = this.albumTracks.findIndex(tt => tt.file_id === t.file_id);
          return origIdx > index;
        });
        if (nextIdx >= 0) {
          this.playerStore.playAlbumTracks(this.albumTracks, nextIdx);
        }
      }
    },
    getTrackUrl(track) {
      return `/minio/indietracks/${track.object_key}`;
    },
    async deleteTrack(track) {
      if (!confirm(`确定删除曲目「${track.file_name}」？`)) return;
      try {
        const resp = await fetch(`/api/admin/albums/${this.$route.params.id}/tracks/${track.file_id}`, { method: 'DELETE' });
        if (resp.ok) {
          this.albumTracks = this.albumTracks.filter(t => t.file_id !== track.file_id);
        }
      } catch (e) { console.error('删除失败:', e); alert('删除失败'); }
    },
    // 曲目上传弹窗
    handleFileSelect(e) {
      this.selectedFile = e.target.files[0];
    },
    handleDrop(e) {
      const file = e.dataTransfer.files[0];
      if (file && (file.name.endsWith('.mp3') || file.name.endsWith('.flac') || file.name.endsWith('.wav'))) {
        this.selectedFile = file;
      }
    },
    async uploadTrack() {
      if (!this.selectedFile) return;
      this.uploading = true;
      this.uploadProgress = 0;
      const formData = new FormData();
      formData.append('file', this.selectedFile);
      try {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/admin/upload/audio');
        xhr.upload.onprogress = (e) => {
          if (e.lengthComputable) this.uploadProgress = Math.round((e.loaded / e.total) * 100);
        };
        xhr.onload = () => {
          if (xhr.status === 200) {
            const data = JSON.parse(xhr.responseText);
            // 添加到曲目列表
            const track = {
              file_id: Date.now(),
              file_name: this.selectedFile.name.replace(/\.[^.]+$/, ''),
              object_key: data.object_key,
              preview_url: data.url,
              file_type: 'preview',
              track_length: '--:--'
            };
            this.albumTracks.push(track);
            this.showUploadModal = false;
            this.selectedFile = null;
            this.uploadProgress = 0;
          } else {
            alert('上传失败');
          }
          this.uploading = false;
        };
        xhr.onerror = () => { alert('上传失败'); this.uploading = false; };
        xhr.send(formData);
      } catch (e) { console.error('上传失败:', e); this.uploading = false; }
    },
    formatFileSize(bytes) {
      if (bytes < 1024) return bytes + ' B';
      if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
      return (bytes / 1048576).toFixed(1) + ' MB';
    }
  }
};
</script>

<style scoped>
.album-form-page { max-width: 900px; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--color-text-primary); margin-bottom: var(--spacing-xl); }
.album-form { display: flex; flex-direction: column; gap: var(--spacing-xl); }
.form-section { background: var(--color-bg-secondary); border: 1px solid var(--color-border); padding: var(--spacing-lg); }
.section-title { font-size: 1rem; font-weight: 600; color: var(--color-text-primary); margin-bottom: var(--spacing-lg); padding-bottom: var(--spacing-sm); border-bottom: 1px solid var(--color-border); }
.form-group { display: flex; flex-direction: column; gap: var(--spacing-xs); margin-bottom: var(--spacing-md); }
.form-group label { font-size: 0.85rem; color: var(--color-text-muted); font-weight: 600; }
.form-group input, .form-group select, .form-group textarea { padding: var(--spacing-sm) var(--spacing-md); background: var(--color-bg-tertiary); border: 1px solid var(--color-border); color: var(--color-text-primary); font-size: 0.9rem; }
.form-group input:focus, .form-group select:focus, .form-group textarea:focus { outline: none; border-color: var(--color-accent); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); }
/* 封面上传 */
.cover-upload { display: flex; gap: var(--spacing-md); align-items: flex-start; }
.cover-preview { width: 120px; height: 120px; object-fit: cover; border: 1px solid var(--color-border); }
.cover-placeholder { width: 120px; height: 120px; display: flex; align-items: center; justify-content: center; background: var(--color-bg-tertiary); border: 1px dashed var(--color-border); color: var(--color-text-dim); font-size: 2rem; }
.cover-actions { flex: 1; display: flex; flex-direction: column; gap: var(--spacing-sm); }
.cover-url-input { padding: var(--spacing-sm); background: var(--color-bg-tertiary); border: 1px solid var(--color-border); color: var(--color-text-primary); font-size: 0.85rem; }
.btn-upload-cover { padding: var(--spacing-sm); background: transparent; border: 1px solid var(--color-border); color: var(--color-text-muted); cursor: pointer; font-size: 0.85rem; }
.btn-upload-cover:hover { border-color: var(--color-accent); color: var(--color-accent); }
/* 标签 */
.tags-list { display: flex; flex-wrap: wrap; gap: var(--spacing-sm); margin-bottom: var(--spacing-md); }
.tag-item { display: flex; align-items: center; gap: 4px; padding: 4px 10px; background: rgba(255,107,107,0.1); color: var(--color-accent); font-size: 0.8rem; }
.tag-remove { background: none; border: none; color: var(--color-text-dim); cursor: pointer; font-size: 1rem; padding: 0 2px; }
.tag-remove:hover { color: #e53935; }
.no-tags { font-size: 0.85rem; color: var(--color-text-dim); }
.add-tag { display: flex; gap: var(--spacing-sm); }
.add-tag input { flex: 1; padding: var(--spacing-sm); background: var(--color-bg-tertiary); border: 1px solid var(--color-border); color: var(--color-text-primary); font-size: 0.85rem; }
.btn-add-tag { padding: var(--spacing-sm) var(--spacing-md); background: var(--color-accent); border: none; color: var(--color-text-primary); font-size: 0.85rem; cursor: pointer; }
.btn-add-tag:disabled { opacity: 0.5; }
/* 曲目 */
.tracks-list { margin-bottom: var(--spacing-md); }
.track-item { display: flex; align-items: center; gap: var(--spacing-md); padding: var(--spacing-sm); border-bottom: 1px solid var(--color-border); border-left: 3px solid transparent; transition: all var(--transition-fast); }
.track-item.active { background: rgba(255,107,107,0.06); border-left-color: var(--color-accent); }
.track-item:hover { background: rgba(255,255,255,0.02); }
.track-index { width: 28px; font-size: 0.8rem; color: var(--color-text-dim); text-align: center; display: flex; align-items: center; justify-content: center; }
.playing-indicator { display: flex; align-items: flex-end; gap: 2px; height: 14px; }
.playing-indicator span { display: block; width: 3px; background: var(--color-accent); animation: playing-bar 0.8s ease-in-out infinite; }
.playing-indicator span:nth-child(1) { height: 60%; animation-delay: 0s; }
.playing-indicator span:nth-child(2) { height: 100%; animation-delay: 0.2s; }
.playing-indicator span:nth-child(3) { height: 40%; animation-delay: 0.4s; }
@keyframes playing-bar { 0%,100% { transform: scaleY(1); } 50% { transform: scaleY(0.4); } }
.track-name { flex: 1; font-size: 0.85rem; color: var(--color-text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.track-name.is-playing { color: var(--color-accent); }
.track-duration { font-size: 0.8rem; color: var(--color-text-dim); }
.track-type { font-size: 0.75rem; color: var(--color-text-muted); padding: 2px 6px; background: rgba(255,255,255,0.05); }
.track-actions { display: flex; gap: var(--spacing-xs); }
.btn-action { width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; background: transparent; border: 1px solid var(--color-border); color: var(--color-text-muted); cursor: pointer; font-size: 0.75rem; text-decoration: none; }
.btn-action:hover { border-color: var(--color-accent); color: var(--color-accent); }
.btn-delete:hover { border-color: #e53935; color: #e53935; }
.no-tracks { font-size: 0.85rem; color: var(--color-text-dim); padding: var(--spacing-md) 0; }
.btn-upload-track { padding: var(--spacing-sm) var(--spacing-lg); background: transparent; border: 1px dashed var(--color-border); color: var(--color-text-muted); cursor: pointer; font-size: 0.85rem; width: 100%; }
.btn-upload-track:hover { border-color: var(--color-accent); color: var(--color-accent); }
/* 底部按钮 */
.form-actions { display: flex; gap: var(--spacing-md); justify-content: flex-end; margin-top: var(--spacing-lg); }
.btn-cancel { padding: var(--spacing-sm) var(--spacing-lg); background: transparent; border: 1px solid var(--color-border); color: var(--color-text-muted); text-decoration: none; cursor: pointer; }
.btn-cancel:hover { border-color: var(--color-text-dim); color: var(--color-text-primary); }
.btn-submit { padding: var(--spacing-sm) var(--spacing-lg); background: var(--color-accent); border: none; color: var(--color-text-primary); font-weight: 600; cursor: pointer; }
.btn-submit:hover:not(:disabled) { background: var(--color-accent-hover); }
.btn-submit:disabled { opacity: 0.5; }
/* 上传弹窗 */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: var(--color-bg-secondary); border: 1px solid var(--color-border); width: 450px; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: var(--spacing-md) var(--spacing-lg); border-bottom: 1px solid var(--color-border); }
.modal-header h3 { font-size: 1rem; color: var(--color-text-primary); }
.modal-close { background: none; border: none; color: var(--color-text-dim); font-size: 1.2rem; cursor: pointer; }
.modal-body { padding: var(--spacing-lg); }
.upload-area { border: 2px dashed var(--color-border); padding: var(--spacing-xl); text-align: center; margin-bottom: var(--spacing-lg); transition: border-color var(--transition-fast); }
.upload-area:hover { border-color: var(--color-accent); }
.upload-placeholder { cursor: pointer; color: var(--color-text-dim); }
.upload-placeholder i { font-size: 2rem; margin-bottom: var(--spacing-sm); }
.upload-placeholder p { margin-bottom: var(--spacing-xs); }
.upload-hint { font-size: 0.75rem; color: var(--color-text-dim); }
.upload-file-info { display: flex; align-items: center; gap: var(--spacing-sm); color: var(--color-text-primary); }
.upload-file-info i { color: var(--color-accent); }
.file-size { font-size: 0.8rem; color: var(--color-text-dim); margin-left: auto; }
.btn-remove-file { background: none; border: none; color: var(--color-text-dim); cursor: pointer; font-size: 1.2rem; }
.upload-progress { margin-bottom: var(--spacing-lg); }
.progress-bar { height: 4px; background: var(--color-border); margin-bottom: var(--spacing-xs); }
.progress-fill { height: 100%; background: var(--color-accent); transition: width 0.2s; }
</style>
