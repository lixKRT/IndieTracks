import { fetchAlbum } from '../api'
import { usePlayerStore } from '../stores/player.js'

/**
 * 预览播放 composable — 统一 "fetch album → play tracks" 流程
 * 消灭 Home/LabelDetail/TagBrowse/AlbumDetail 中的重复播放逻辑
 */
export function usePreviewPlay() {
  const player = usePlayerStore()

  /**
   * 加载专辑曲目并添加到播放列表
   */
  async function addPreview(albumId) {
    const detail = await fetchAlbum(albumId)
    player.addAlbumTracks(detail.tracks, 0)
  }

  /**
   * 加载专辑曲目并替换播放列表
   */
  async function playPreview(albumId) {
    const detail = await fetchAlbum(albumId)
    player.playAlbumTracks(detail.tracks, 0)
  }

  return { addPreview, playPreview }
}
