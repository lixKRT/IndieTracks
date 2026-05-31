import { useRouter } from 'vue-router'

/**
 * 统一导航 composable — 消灭 5 个 view 中的 goToAlbum/goToCircle/goToTag 副本
 */
export function useNavigation() {
  const router = useRouter()

  function goToAlbum(album) {
    router.push(`/album/${album.album_id}`)
  }

  function goToCircle(albumOrCircle) {
    const id = albumOrCircle.circle_id
    if (id) router.push(`/label/${id}`)
  }

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
