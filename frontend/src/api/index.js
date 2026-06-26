// 统一 re-export，外部只需 `import { ... } from '@/api'` 即可
export {
  fetchAlbums, fetchAlbum, fetchRecommendations,
  fetchCircles, fetchCircle,
  getTags,
  fetchUser, getUserFavorites, getUserFollowingCircles, getUserFollowingUsers,
  fetchComments, addComment, updateComment, deleteComment,
  getFavorites, addFavorite, removeFavorite, checkFavorite,
  purchaseAlbum, checkPurchased, getUserPurchases,
  getCart, addToCart, removeFromCart, getCartCount, checkInCart, checkoutCart,
  followCircle, unfollowCircle, checkCircleFollow,
  followUser, unfollowUser, checkUserFollow,
  register, login, logout, fetchMe, uploadAvatar
} from './request.js';
