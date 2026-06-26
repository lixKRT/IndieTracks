import { useRouter } from 'vue-router'

/**
 * 统一导航 composable — 消灭 5 个 view 中的 goToAlbum/goToCircle/goToTag 副本
 */
export function useNavigation() {
  const router = useRouter()

  function goToAlbum(album) {
    router.push(`/album/${album.album_id}`)
  }

  // 兼容专辑对象和社团对象（都有 circle_id）
  function goToCircle(albumOrCircle) {
    const id = albumOrCircle.circle_id
    if (id) router.push(`/label/${id}`)
  }

  // 兼容字符串和标签对象两种入参
  function goToTag(tag) {
    const name = typeof tag === 'string' ? tag : tag.name
    router.push({ path: '/tag', query: { tag: name } })
  }

  function goToUser(user) {
    router.push(`/user/${user.user_id}`)
  }

  function goToCircleById(circleId) {
    router.push(`/label/${circleId}`)
  }

  return { goToAlbum, goToCircle, goToTag, goToUser, goToCircleById }
}
