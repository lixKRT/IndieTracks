<template>
  <MainContent
    :albums="allAlbums"
    :loading="loading"
    :showAll="showAllAlbums"
    :maxVisible="maxVisibleAlbums"
    @album-click="goToAlbum"
    @artist-click="goToArtist"
    @tag-click="filterByTag"
    @purchase="purchaseAlbum"
    @preview="previewAlbum"
    @view-all="showAllAlbums = true"
  />
</template>

<script>
import MainContent from '../components/MainContent.vue';

export default {
  name: 'HomeView',
  components: { MainContent },
  data() {
    return {
      loading: true,
      showAllAlbums: false,
      maxVisibleAlbums: 6,
      allAlbums: []
    };
  },
  methods: {
    purchaseAlbum(album) {
      if (album.free) {
        alert(`已下载 ${album.title}`);
      } else {
        alert(`正在购买 ${album.title} - ¥${album.price}`);
      }
    },
    previewAlbum(album) {
      alert(`正在试听 ${album.title}`);
    },
    goToAlbum(album) {
      alert(`跳转到专辑: ${album.title}`);
    },
    goToArtist(artistName) {
      alert(`跳转到艺术家: ${artistName}`);
    },
    filterByTag(tag) {
      alert(`按标签筛选: ${tag}`);
    }
  },
  mounted() {
    setTimeout(() => {
      this.allAlbums = [
        {
          id: 1,
          title: "Emotional Air",
          artist: "優しさの配列",
          price: 50,
          cover: "https://placehold.co/300x300/2a2a2a/ffffff?text=Album+Cover",
          tags: ["#pops", "#vocal", "#原创", "#同人音乐"],
          hires: true,
          free: false
        },
        {
          id: 2,
          title: "（补档）78+13=91",
          artist: "78Records",
          price: 0,
          cover: "https://placehold.co/300x300/2a2a2a/ffffff?text=Album+Cover",
          tags: ["#dariacore", "#gabber", "#hyper"],
          hires: true,
          free: true
        },
        {
          id: 3,
          title: "山越し独り",
          artist: "Kirisame Records",
          price: 36,
          cover: "https://placehold.co/300x300/2a2a2a/ffffff?text=Album+Cover",
          tags: ["#dreampop", "#Joulez", "#摇滚"],
          hires: true,
          free: false
        },
        {
          id: 4,
          title: "非对称集：2026冬",
          artist: "铁头动力 T^T Dynamics",
          price: 0,
          cover: "https://placehold.co/300x300/2a2a2a/ffffff?text=Album+Cover",
          tags: ["#VOCALOID", "#变拍子", "#非对称集"],
          hires: true,
          free: true
        },
        {
          id: 5,
          title: "78+91=13²",
          artist: "78Records",
          price: 45,
          cover: "https://placehold.co/300x300/2a2a2a/ffffff?text=Album+Cover",
          tags: ["#bailefunk", "#hybridtrap", "#dubstep"],
          hires: true,
          free: false
        },
        {
          id: 6,
          title: "以宇宙的嗓音",
          artist: "外星小鸟",
          price: 0,
          cover: "https://placehold.co/300x300/2a2a2a/ffffff?text=Album+Cover",
          tags: ["#原创", "#纯音乐"],
          hires: true,
          free: true
        },
        {
          id: 7,
          title: "negative_film",
          artist: "hisa_knowledge",
          price: 35,
          cover: "https://placehold.co/300x300/2a2a2a/ffffff?text=Album+Cover",
          tags: ["#东方project", "#同人音乐", "#管弦"],
          hires: true,
          free: false
        },
        {
          id: 8,
          title: "Rebirth",
          artist: "hisa_knowledge",
          price: 35,
          cover: "https://placehold.co/300x300/2a2a2a/ffffff?text=Album+Cover",
          tags: ["#东方project", "#同人音乐", "#管弦"],
          hires: true,
          free: false
        },
        {
          id: 9,
          title: "LoneLine",
          artist: "hisa_knowledge",
          price: 35,
          cover: "https://placehold.co/300x300/2a2a2a/ffffff?text=Album+Cover",
          tags: ["#东方project", "#同人音乐", "#流行弦乐"],
          hires: true,
          free: false
        },
        {
          id: 10,
          title: "Moving",
          artist: "CARDIOID",
          price: 0,
          cover: "https://placehold.co/300x300/2a2a2a/ffffff?text=Album+Cover",
          tags: ["#CARDIOID", "#House", "#Trance"],
          hires: true,
          free: true
        },
        {
          id: 11,
          title: "Other Worldly Power",
          artist: "Endless Sound Records",
          price: 20,
          cover: "https://placehold.co/300x300/2a2a2a/ffffff?text=Album+Cover",
          tags: ["#东方"],
          hires: true,
          free: false
        },
        {
          id: 12,
          title: "IONOSPHERE",
          artist: "project:2000x",
          price: 19,
          cover: "https://placehold.co/300x300/2a2a2a/ffffff?text=Album+Cover",
          tags: ["#HYPERTRANCE", "#NEOTRANCE", "#RAWSTYLE"],
          hires: true,
          free: false
        },
        {
          id: 13,
          title: "绫号宇宙",
          artist: "绫号宇宙",
          price: 0,
          cover: "https://placehold.co/300x300/2a2a2a/ffffff?text=Album+Cover",
          tags: ["#乐正绫", "#绫号宇宙"],
          hires: true,
          free: true
        },
        {
          id: 14,
          title: "C0RE C0LLECTION VOL.3 -Detachment-",
          artist: "EXperiment EXtreme C0re Noise AlcoholicS",
          price: 0,
          cover: "https://placehold.co/300x300/2a2a2a/ffffff?text=Album+Cover",
          tags: ["#Hardcore", "#Hardstyle", "#Speedcore"],
          hires: true,
          free: true
        },
        {
          id: 15,
          title: "Together We Rewind EP",
          artist: "Silent Xords",
          price: 30,
          cover: "https://placehold.co/300x300/2a2a2a/ffffff?text=Album+Cover",
          tags: ["#硬核", "#UK Hardcore", "#怀旧"],
          hires: true,
          free: false
        },
        {
          id: 16,
          title: "伪春 Revisit EP",
          artist: "EchoBottle",
          price: 0,
          cover: "https://placehold.co/300x300/2a2a2a/ffffff?text=Album+Cover",
          tags: ["#Vocaloid", "#ambient", "#rock"],
          hires: true,
          free: true
        },
        {
          id: 17,
          title: "EMOTIONA",
          artist: "THE FACTOTY OF SHEEP",
          price: 68,
          cover: "https://placehold.co/300x300/2a2a2a/ffffff?text=Album+Cover",
          tags: ["#纯音乐"],
          hires: true,
          free: false
        },
        {
          id: 18,
          title: "冬日咏叙调",
          artist: "Static World",
          price: 40,
          cover: "https://placehold.co/300x300/2a2a2a/ffffff?text=Album+Cover",
          tags: ["#纯音乐", "#Static World", "#治愈系"],
          hires: true,
          free: false
        }
      ];
      this.loading = false;
    }, 800);
  }
};
</script>
