/**
 * mock.js — 集中 Mock 数据
 *
 * 约定：
 * - 全链路 snake_case（字段名 = 数据库列名 = 后端 JSON key）
 * - 模拟多表关联结构
 * - 所有接口函数返回 Promise，模拟 200-400ms 网络延迟
 */

// ============================================================
// 原始数据
// ============================================================

const tags = [
  { tag_id: 1, name: '东方project' },
  { tag_id: 2, name: '电子音乐' },
  { tag_id: 3, name: 'Colour Bass' },
  { tag_id: 4, name: 'Hyper Trance' },
  { tag_id: 5, name: '纯音乐' },
  { tag_id: 6, name: '同人音乐' },
  { tag_id: 7, name: 'Vocaloid' },
  { tag_id: 8, name: '硬核' },
  { tag_id: 9, name: 'UK Hardcore' },
  { tag_id: 10, name: 'Drum and Bass' },
  { tag_id: 11, name: 'Dubstep' },
  { tag_id: 12, name: 'House' },
  { tag_id: 13, name: 'Trance' },
  { tag_id: 14, name: 'Rock' },
  { tag_id: 15, name: 'Ambient' }
];

const circles = [
  {
    circle_id: 1,
    name: 'Chroma_Sounds虹彩',
    logo_url: 'https://placehold.co/200x200/2a2a2a/ffffff?text=CS',
    description: '东方同人电子音乐社团。Diversity | Retro-Futurism | Next-Generation'
  },
  {
    circle_id: 2,
    name: '78Records',
    logo_url: 'https://placehold.co/200x200/2a2a2a/ffffff?text=78',
    description: '专注于实验电子与硬核音乐的创作团体。'
  },
  {
    circle_id: 3,
    name: '優しさの配列',
    logo_url: 'https://placehold.co/200x200/2a2a2a/ffffff?text=YA',
    description: '氛围音乐与流行电子制作。'
  },
  {
    circle_id: 4,
    name: 'Static World',
    logo_url: 'https://placehold.co/200x200/2a2a2a/ffffff?text=SW',
    description: '治愈系纯音乐与交响电子创作社团。'
  },
  {
    circle_id: 5,
    name: 'THE FACTOTY OF SHEEP',
    logo_url: 'https://placehold.co/200x200/2a2a2a/ffffff?text=FS',
    description: '独立电子音乐厂牌，覆盖多种电子风格。'
  }
];

const users = [
  { user_id: 1, username: 'Rainbow Illusion', avatar_url: 'https://placehold.co/64x64/444/fff?text=RI', user_role: 'pro' },
  { user_id: 2, username: 'X-ENON', avatar_url: 'https://placehold.co/64x64/444/fff?text=XE', user_role: 'pro' },
  { user_id: 3, username: 'Excillex', avatar_url: 'https://placehold.co/64x64/444/fff?text=EX', user_role: 'pro' },
  { user_id: 4, username: 'Voxelkana', avatar_url: 'https://placehold.co/64x64/444/fff?text=VX', user_role: 'pro' },
  { user_id: 5, username: 'Shiorei_', avatar_url: 'https://placehold.co/64x64/444/fff?text=SH', user_role: 'pro' },
  { user_id: 6, username: 'Salty Salt', avatar_url: 'https://placehold.co/64x64/444/fff?text=SS', user_role: 'pro' },
  { user_id: 7, username: 'Boring-X-', avatar_url: 'https://placehold.co/64x64/444/fff?text=BX', user_role: 'pro' },
  { user_id: 8, username: 'dj Toast', avatar_url: 'https://placehold.co/64x64/444/fff?text=DT', user_role: 'pro' },
  { user_id: 9, username: 'Kirisame Records', avatar_url: 'https://placehold.co/64x64/444/fff?text=KR', user_role: 'pro' },
  { user_id: 10, username: '铁头动力', avatar_url: 'https://placehold.co/64x64/444/fff?text=TT', user_role: 'pro' },
  { user_id: 11, username: '听众A', avatar_url: 'https://placehold.co/64x64/444/fff?text=A', user_role: 'normal' },
  { user_id: 12, username: '听众B', avatar_url: 'https://placehold.co/64x64/444/fff?text=B', user_role: 'normal' },
  { user_id: 13, username: '乐迷小C', avatar_url: 'https://placehold.co/64x64/444/fff?text=C', user_role: 'normal' },
  { user_id: 14, username: '音乐猎人', avatar_url: 'https://placehold.co/64x64/444/fff?text=MH', user_role: 'normal' }
];

const albums = [
  {
    album_id: 1,
    title: 'Touhou Colours：Aquamarine',
    circle_id: 1,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=Aquamarine',
    price: 65.0,
    publish_date: '2026-05-01',
    info_title: 'Touhou Colours: Aquamarine',
    info_content: 'ChromaSounds虹彩第四张专辑A侧。科学技术的进步，真是飞速啊。突然间，有个叫互联网的东西闯入了幻想乡。而我，蕾米莉亚——红魔馆的家主，自然也不能错过这波科技浪潮。',
    tag_ids: [1, 2, 3, 4],
    tracks: [
      { file_id: 1, file_name: 'Transcendence of Fluid Neon - Voxelkana', duration: '4:46', sort_order: 1, file_type: 'preview' },
      { file_id: 2, file_name: '千年の響き - Shiorei_', duration: '4:40', sort_order: 2, file_type: 'preview' },
      { file_id: 3, file_name: 'G FREE - Salty Salt', duration: '4:20', sort_order: 3, file_type: 'preview' },
      { file_id: 4, file_name: 'here and there, after a hangover - Boring-X-', duration: '3:53', sort_order: 4, file_type: 'preview' },
      { file_id: 5, file_name: 'Phantastic Flowers - Kamino Yoruneko', duration: '6:05', sort_order: 5, file_type: 'preview' },
      { file_id: 6, file_name: 'LUNARiA - dj Toast', duration: '4:07', sort_order: 6, file_type: 'preview' },
      { file_id: 7, file_name: 'Encounter the Summer Solstice - Fragrant_MT', duration: '4:01', sort_order: 7, file_type: 'preview' },
      { file_id: 8, file_name: 'Phase_Orbit - Anicille', duration: '3:45', sort_order: 8, file_type: 'preview' },
      { file_id: 9, file_name: '「-」 - Afrixon', duration: '9:22', sort_order: 9, file_type: 'full' },
      { file_id: 10, file_name: '賢者之石 - Herun', duration: '4:30', sort_order: 10, file_type: 'full' },
      { file_id: 11, file_name: 'Blue Lotus ft. toki - Deltaranged', duration: '6:15', sort_order: 11, file_type: 'full' },
      { file_id: 12, file_name: 'Evanescent, a shattered realm - W1ldflow3r', duration: '4:42', sort_order: 12, file_type: 'full' },
      { file_id: 13, file_name: '1764 - Pleinerz', duration: '4:25', sort_order: 13, file_type: 'full' },
      { file_id: 14, file_name: 'Rearrival - Mirage_Sonata', duration: '4:51', sort_order: 14, file_type: 'full' },
      { file_id: 15, file_name: 'soranishizumu - Farah', duration: '4:19', sort_order: 15, file_type: 'full' },
      { file_id: 16, file_name: 'wait for me. - Rainbow Illusion', duration: '4:37', sort_order: 16, file_type: 'full' }
    ],
    comments: [
      { comment_id: 1, user_id: 11, content: 'Voxelkana 的 Tr.01 太惊艳了，Neo Trance 和东方旋律的结合非常自然！', created_at: '2026-05-03' },
      { comment_id: 2, user_id: 12, content: 'Colour Bass 爱好者必入。Shiorei 和 Salty Salt 的曲目尤其出色。', created_at: '2026-05-05' },
      { comment_id: 3, user_id: 13, content: '封面设计也很好看，和 Aquamarine 的主题非常贴合。', created_at: '2026-05-08' },
      { comment_id: 4, user_id: 14, content: '已购，物超所值。16 首曲目这个价格很良心了。', created_at: '2026-05-10' }
    ]
  },
  {
    album_id: 2,
    title: '（补档）78+13=91',
    circle_id: 2,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=78%2B13',
    price: 0,
    publish_date: '2026-04-28',
    info_title: '78+13=91',
    info_content: '78Records 早期作品补档合集，收录 dariacore、gabber、hyper 等多种风格。',
    tag_ids: [2, 8],
    tracks: [
      { file_id: 17, file_name: 'DARIACORE ANTHEM', duration: '3:22', sort_order: 1, file_type: 'preview' },
      { file_id: 18, file_name: 'GABBER DESTROYER', duration: '4:10', sort_order: 2, file_type: 'preview' },
      { file_id: 19, file_name: 'HYPER DRIVE', duration: '3:45', sort_order: 3, file_type: 'preview' },
      { file_id: 20, file_name: 'BREAKCORE SUNDAY', duration: '5:01', sort_order: 4, file_type: 'preview' },
      { file_id: 21, file_name: 'SPEEDCORE NIGHT', duration: '6:33', sort_order: 5, file_type: 'full' },
      { file_id: 22, file_name: 'HARDCORE RAVE', duration: '4:18', sort_order: 6, file_type: 'full' },
      { file_id: 23, file_name: 'TERROR DRUMZ', duration: '3:55', sort_order: 7, file_type: 'full' },
      { file_id: 24, file_name: 'NOISE WALL', duration: '8:00', sort_order: 8, file_type: 'full' }
    ],
    comments: [
      { comment_id: 5, user_id: 14, content: '免费专辑质量还这么高，太良心了。', created_at: '2026-05-01' }
    ]
  },
  {
    album_id: 3,
    title: 'Emotional Air',
    circle_id: 3,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=Emotional+Air',
    price: 50.0,
    publish_date: '2026-04-25',
    info_title: 'Emotional Air',
    info_content: '優しさの配列 最新作。pops 旋律与电子音色的融合，温暖而又充满力量。',
    tag_ids: [6, 5],
    tracks: [
      { file_id: 25, file_name: 'Emotional Air', duration: '4:30', sort_order: 1, file_type: 'preview' },
      { file_id: 26, file_name: 'Gentle Breeze', duration: '3:55', sort_order: 2, file_type: 'preview' },
      { file_id: 27, file_name: 'Floating City', duration: '5:12', sort_order: 3, file_type: 'preview' },
      { file_id: 28, file_name: 'Rainy Window', duration: '4:08', sort_order: 4, file_type: 'full' },
      { file_id: 29, file_name: 'Starlight Road', duration: '6:00', sort_order: 5, file_type: 'full' },
      { file_id: 30, file_name: 'Morning Dew', duration: '3:45', sort_order: 6, file_type: 'full' },
      { file_id: 31, file_name: 'Sunset Memories', duration: '5:22', sort_order: 7, file_type: 'full' },
      { file_id: 32, file_name: 'Good Night', duration: '2:30', sort_order: 8, file_type: 'full' }
    ],
    comments: [
      { comment_id: 6, user_id: 11, content: '很适合在夜晚安静地听。', created_at: '2026-04-28' },
      { comment_id: 7, user_id: 13, content: 'Emotional Air 这首单曲循环了好几天。', created_at: '2026-05-02' }
    ]
  },
  {
    album_id: 4,
    title: '山越し独り',
    circle_id: 3,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=Yamagoshi',
    price: 36.0,
    publish_date: '2026-04-20',
    info_title: '山越し独り',
    info_content: 'dreampop 与摇滚的跨界尝试。Joulez 风格贯穿全专。',
    tag_ids: [6, 14],
    tracks: [
      { file_id: 33, file_name: '山越し独り', duration: '5:10', sort_order: 1, file_type: 'preview' },
      { file_id: 34, file_name: '遠くの灯り', duration: '4:35', sort_order: 2, file_type: 'preview' },
      { file_id: 35, file_name: '川沿いの道', duration: '3:50', sort_order: 3, file_type: 'preview' },
      { file_id: 36, file_name: '帰り道', duration: '4:22', sort_order: 4, file_type: 'full' },
      { file_id: 37, file_name: '星空', duration: '6:15', sort_order: 5, file_type: 'full' },
      { file_id: 38, file_name: 'ひとり', duration: '2:48', sort_order: 6, file_type: 'full' }
    ],
    comments: [
      { comment_id: 8, user_id: 12, content: '封面很有意境，音乐也是。', created_at: '2026-04-25' }
    ]
  },
  {
    album_id: 5,
    title: '非对称集：2026冬',
    circle_id: 2,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=Asymmetric',
    price: 0,
    publish_date: '2026-04-18',
    info_title: '非对称集：2026冬',
    info_content: '铁头动力 T^T Dynamics 冬季作品集。VOCALOID × 变拍子实验。',
    tag_ids: [7, 5],
    tracks: [
      { file_id: 39, file_name: '非対称の世界', duration: '4:05', sort_order: 1, file_type: 'preview' },
      { file_id: 40, file_name: '冬の残響', duration: '5:30', sort_order: 2, file_type: 'preview' },
      { file_id: 41, file_name: '鏡の中', duration: '3:55', sort_order: 3, file_type: 'preview' },
      { file_id: 42, file_name: '歪んだ時計', duration: '4:42', sort_order: 4, file_type: 'full' },
      { file_id: 43, file_name: '氷の城', duration: '6:10', sort_order: 5, file_type: 'full' },
      { file_id: 44, file_name: '春を待つ', duration: '3:20', sort_order: 6, file_type: 'full' },
      { file_id: 45, file_name: '非対称集 エピローグ', duration: '2:15', sort_order: 7, file_type: 'full' },
      { file_id: 46, file_name: 'Bonus Track - Snowfield', duration: '4:00', sort_order: 8, file_type: 'full' }
    ],
    comments: [
      { comment_id: 9, user_id: 11, content: '变拍子用得很巧妙，VOCALOID 调教也很自然。', created_at: '2026-04-22' }
    ]
  },
  {
    album_id: 6,
    title: '78+91=13²',
    circle_id: 2,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=13%C2%B2',
    price: 45.0,
    publish_date: '2026-04-15',
    info_title: '78+91=13²',
    info_content: 'baile funk × hybrid trap × dubstep。78Records 最具实验性的一张。',
    tag_ids: [2, 11],
    tracks: [
      { file_id: 47, file_name: 'BAILE FUNK 3000', duration: '3:30', sort_order: 1, file_type: 'preview' },
      { file_id: 48, file_name: 'HYBRID TRAP ATTACK', duration: '4:15', sort_order: 2, file_type: 'preview' },
      { file_id: 49, file_name: 'DUBSTEP KINGDOM', duration: '5:00', sort_order: 3, file_type: 'preview' },
      { file_id: 50, file_name: 'RIDDIM NIGHT', duration: '3:45', sort_order: 4, file_type: 'full' },
      { file_id: 51, file_name: 'WOBBLE CITY', duration: '4:20', sort_order: 5, file_type: 'full' },
      { file_id: 52, file_name: 'BASS CANNON', duration: '3:55', sort_order: 6, file_type: 'full' },
      { file_id: 53, file_name: 'DROP THE BEAT', duration: '4:10', sort_order: 7, file_type: 'full' },
      { file_id: 54, file_name: 'OUTRO - Silence', duration: '1:30', sort_order: 8, file_type: 'full' }
    ],
    comments: []
  },
  {
    album_id: 7,
    title: '以宇宙的嗓音',
    circle_id: 4,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=Cosmos',
    price: 0,
    publish_date: '2026-04-12',
    info_title: '以宇宙的嗓音',
    info_content: '外星小鸟 首张纯音乐专辑。用声音描绘宇宙的浩瀚。',
    tag_ids: [5],
    tracks: [
      { file_id: 55, file_name: '宇宙の声', duration: '4:30', sort_order: 1, file_type: 'preview' },
      { file_id: 56, file_name: '星雲', duration: '5:15', sort_order: 2, file_type: 'preview' },
      { file_id: 57, file_name: 'ブラックホール', duration: '6:00', sort_order: 3, file_type: 'preview' },
      { file_id: 58, file_name: '惑星の軌道', duration: '4:45', sort_order: 4, file_type: 'full' },
      { file_id: 59, file_name: '彗星', duration: '3:30', sort_order: 5, file_type: 'full' },
      { file_id: 60, file_name: '銀河', duration: '7:00', sort_order: 6, file_type: 'full' },
      { file_id: 61, file_name: '地球', duration: '4:00', sort_order: 7, file_type: 'full' },
      { file_id: 62, file_name: '帰還', duration: '2:45', sort_order: 8, file_type: 'full' }
    ],
    comments: [
      { comment_id: 10, user_id: 13, content: '闭上眼睛听仿佛真的在太空漫游。', created_at: '2026-04-16' }
    ]
  },
  {
    album_id: 8,
    title: 'negative_film',
    circle_id: 1,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=Negative',
    price: 35.0,
    publish_date: '2026-04-10',
    info_title: 'negative_film',
    info_content: 'hisa_knowledge 管弦东方编曲集。宏大而细腻的交响电子。',
    tag_ids: [1, 6, 5],
    tracks: [
      { file_id: 63, file_name: 'negative_film', duration: '5:20', sort_order: 1, file_type: 'preview' },
      { file_id: 64, file_name: '紅い瞳', duration: '4:50', sort_order: 2, file_type: 'preview' },
      { file_id: 65, file_name: '竹林', duration: '6:10', sort_order: 3, file_type: 'preview' },
      { file_id: 66, file_name: '月時計', duration: '5:00', sort_order: 4, file_type: 'full' },
      { file_id: 67, file_name: '桜花', duration: '4:35', sort_order: 5, file_type: 'full' },
      { file_id: 68, file_name: '永遠', duration: '6:50', sort_order: 6, file_type: 'full' },
      { file_id: 69, file_name: '境界', duration: '5:15', sort_order: 7, file_type: 'full' },
      { file_id: 70, file_name: '現像', duration: '3:00', sort_order: 8, file_type: 'full' }
    ],
    comments: [
      { comment_id: 11, user_id: 14, content: '管弦和东方的结合太棒了。', created_at: '2026-04-14' },
      { comment_id: 12, user_id: 11, content: '重新编曲的红楼曲目很有新鲜感。', created_at: '2026-04-18' }
    ]
  },
  {
    album_id: 9,
    title: '冬日咏叙调',
    circle_id: 4,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=Winter',
    price: 40.0,
    publish_date: '2026-04-08',
    info_title: '冬日咏叙调',
    info_content: 'Static World 冬季主题纯音乐专辑。治愈系旋律温暖寒冬。',
    tag_ids: [5],
    tracks: [
      { file_id: 71, file_name: '冬日咏叙调', duration: '5:00', sort_order: 1, file_type: 'preview' },
      { file_id: 72, file_name: '雪の降る街', duration: '4:20', sort_order: 2, file_type: 'preview' },
      { file_id: 73, file_name: '暖炉のそばで', duration: '3:50', sort_order: 3, file_type: 'preview' },
      { file_id: 74, file_name: '凍える夜', duration: '4:45', sort_order: 4, file_type: 'full' },
      { file_id: 75, file_name: '静寂', duration: '6:30', sort_order: 5, file_type: 'full' },
      { file_id: 76, file_name: '春の兆し', duration: '3:15', sort_order: 6, file_type: 'full' },
      { file_id: 77, file_name: '雪解け', duration: '5:40', sort_order: 7, file_type: 'full' },
      { file_id: 78, file_name: 'また来年', duration: '2:00', sort_order: 8, file_type: 'full' }
    ],
    comments: []
  },
  {
    album_id: 10,
    title: 'EMOTIONA',
    circle_id: 5,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=EMOTIONA',
    price: 68.0,
    publish_date: '2026-04-05',
    info_title: 'EMOTIONA',
    info_content: 'THE FACTOTY OF SHEEP 最新电子专辑。融合多种电子风格的情感之旅。',
    tag_ids: [2, 5],
    tracks: [
      { file_id: 79, file_name: 'EMOTIONA -Intro-', duration: '2:30', sort_order: 1, file_type: 'preview' },
      { file_id: 80, file_name: 'Neon Pulse', duration: '4:45', sort_order: 2, file_type: 'preview' },
      { file_id: 81, file_name: 'Digital Tears', duration: '5:10', sort_order: 3, file_type: 'preview' },
      { file_id: 82, file_name: 'Binary Heart', duration: '4:20', sort_order: 4, file_type: 'preview' },
      { file_id: 83, file_name: 'Electric Dreams', duration: '6:00', sort_order: 5, file_type: 'full' },
      { file_id: 84, file_name: 'Synthetic Love', duration: '5:30', sort_order: 6, file_type: 'full' },
      { file_id: 85, file_name: 'Pixel Rain', duration: '4:00', sort_order: 7, file_type: 'full' },
      { file_id: 86, file_name: 'Reboot', duration: '3:45', sort_order: 8, file_type: 'full' },
      { file_id: 87, file_name: 'Analog Sunset', duration: '5:15', sort_order: 9, file_type: 'full' },
      { file_id: 88, file_name: 'EMOTIONA -Outro-', duration: '2:00', sort_order: 10, file_type: 'full' }
    ],
    comments: [
      { comment_id: 13, user_id: 12, content: '每首曲目都很有层次感，制作精良。', created_at: '2026-04-10' }
    ]
  },
  {
    album_id: 11,
    title: 'Rebirth',
    circle_id: 1,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=Rebirth',
    price: 35.0,
    publish_date: '2026-04-02',
    info_title: 'Rebirth',
    info_content: 'hisa_knowledge 管弦东方系列第二弹。重生与希望的主题贯穿全专。',
    tag_ids: [1, 6, 5],
    tracks: [
      { file_id: 89, file_name: 'Rebirth', duration: '5:45', sort_order: 1, file_type: 'preview' },
      { file_id: 90, file_name: '新生', duration: '4:30', sort_order: 2, file_type: 'preview' },
      { file_id: 91, file_name: '翼', duration: '5:20', sort_order: 3, file_type: 'preview' },
      { file_id: 92, file_name: '空へ', duration: '6:10', sort_order: 4, file_type: 'full' },
      { file_id: 93, file_name: '光', duration: '4:50', sort_order: 5, file_type: 'full' },
      { file_id: 94, file_name: '再生', duration: '5:00', sort_order: 6, file_type: 'full' },
      { file_id: 95, file_name: '希望', duration: '3:40', sort_order: 7, file_type: 'full' },
      { file_id: 96, file_name: '旅立ち', duration: '2:30', sort_order: 8, file_type: 'full' }
    ],
    comments: []
  },
  {
    album_id: 12,
    title: 'LoneLine',
    circle_id: 1,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=LoneLine',
    price: 35.0,
    publish_date: '2026-03-28',
    info_title: 'LoneLine',
    info_content: 'hisa_knowledge 流行弦乐东方编曲。独行者的一人旅程。',
    tag_ids: [1, 6, 5],
    tracks: [
      { file_id: 97, file_name: 'LoneLine', duration: '4:15', sort_order: 1, file_type: 'preview' },
      { file_id: 98, file_name: '旅路', duration: '5:30', sort_order: 2, file_type: 'preview' },
      { file_id: 99, file_name: '迷い', duration: '4:00', sort_order: 3, file_type: 'preview' },
      { file_id: 100, file_name: '出会い', duration: '4:45', sort_order: 4, file_type: 'full' },
      { file_id: 101, file_name: '別れ', duration: '5:20', sort_order: 5, file_type: 'full' },
      { file_id: 102, file_name: '想い', duration: '3:50', sort_order: 6, file_type: 'full' },
      { file_id: 103, file_name: '辿り着く場所', duration: '6:00', sort_order: 7, file_type: 'full' },
      { file_id: 104, file_name: 'また歩き出す', duration: '3:00', sort_order: 8, file_type: 'full' }
    ],
    comments: [
      { comment_id: 14, user_id: 13, content: '一人旅のお供にぴったり。', created_at: '2026-04-01' }
    ]
  },
  {
    album_id: 13,
    title: 'Moving',
    circle_id: 5,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=Moving',
    price: 0,
    publish_date: '2026-03-25',
    info_title: 'Moving',
    info_content: 'CARDIOID 免费 EP。House × Trance 的律动之旅。',
    tag_ids: [2, 12, 13],
    tracks: [
      { file_id: 105, file_name: 'Moving', duration: '5:00', sort_order: 1, file_type: 'preview' },
      { file_id: 106, file_name: 'Deep Breath', duration: '4:30', sort_order: 2, file_type: 'preview' },
      { file_id: 107, file_name: 'Waves', duration: '6:15', sort_order: 3, file_type: 'preview' },
      { file_id: 108, file_name: 'Rise', duration: '5:45', sort_order: 4, file_type: 'full' },
      { file_id: 109, file_name: 'Float', duration: '4:20', sort_order: 5, file_type: 'full' }
    ],
    comments: []
  },
  {
    album_id: 14,
    title: 'Other Worldly Power',
    circle_id: 5,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=OWP',
    price: 20.0,
    publish_date: '2026-03-22',
    info_title: 'Other Worldly Power',
    info_content: 'Endless Sound Records 东方电子 EP。异世界的能量。',
    tag_ids: [1, 2],
    tracks: [
      { file_id: 110, file_name: 'Other Worldly Power', duration: '4:50', sort_order: 1, file_type: 'preview' },
      { file_id: 111, file_name: 'Spirit Barrier', duration: '5:30', sort_order: 2, file_type: 'preview' },
      { file_id: 112, file_name: 'Danmaku Rain', duration: '4:15', sort_order: 3, file_type: 'preview' },
      { file_id: 113, file_name: 'Last Spell', duration: '6:00', sort_order: 4, file_type: 'full' },
      { file_id: 114, file_name: 'Game Over', duration: '3:00', sort_order: 5, file_type: 'full' }
    ],
    comments: []
  },
  {
    album_id: 15,
    title: 'IONOSPHERE',
    circle_id: 2,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=IONO',
    price: 19.0,
    publish_date: '2026-03-20',
    info_title: 'IONOSPHERE',
    info_content: 'project:2000x 高速电子结界。HYPERTRANCE × NEOTRANCE × RAWSTYLE。',
    tag_ids: [2, 4, 13],
    tracks: [
      { file_id: 115, file_name: 'IONOSPHERE', duration: '5:20', sort_order: 1, file_type: 'preview' },
      { file_id: 116, file_name: 'STRATOSPHERE', duration: '4:45', sort_order: 2, file_type: 'preview' },
      { file_id: 117, file_name: 'TROPOSPHERE', duration: '6:10', sort_order: 3, file_type: 'preview' },
      { file_id: 118, file_name: 'MESOSPHERE', duration: '5:00', sort_order: 4, file_type: 'full' },
      { file_id: 119, file_name: 'THERMOSPHERE', duration: '7:30', sort_order: 5, file_type: 'full' },
      { file_id: 120, file_name: 'EXOSPHERE', duration: '4:00', sort_order: 6, file_type: 'full' },
      { file_id: 121, file_name: 'REENTRY', duration: '3:45', sort_order: 7, file_type: 'full' },
      { file_id: 122, file_name: 'LANDING', duration: '2:30', sort_order: 8, file_type: 'full' }
    ],
    comments: [
      { comment_id: 15, user_id: 14, content: '从第一首到最后一首完全不踩刹车，太爽了。', created_at: '2026-03-25' }
    ]
  },
  {
    album_id: 16,
    title: '绫号宇宙',
    circle_id: 3,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=Linghao',
    price: 0,
    publish_date: '2026-03-18',
    info_title: '绫号宇宙',
    info_content: '乐正绫主题同人音乐专辑。以绫号宇宙的概念展开的声音冒险。',
    tag_ids: [7, 6],
    tracks: [
      { file_id: 123, file_name: '绫号宇宙', duration: '4:30', sort_order: 1, file_type: 'preview' },
      { file_id: 124, file_name: '星間飛行', duration: '3:55', sort_order: 2, file_type: 'preview' },
      { file_id: 125, file_name: '通信衛星', duration: '5:10', sort_order: 3, file_type: 'preview' },
      { file_id: 126, file_name: '宇宙ステーション', duration: '4:40', sort_order: 4, file_type: 'full' },
      { file_id: 127, file_name: '惑星探査', duration: '6:20', sort_order: 5, file_type: 'full' },
      { file_id: 128, file_name: '帰還信号', duration: '3:15', sort_order: 6, file_type: 'full' }
    ],
    comments: []
  },
  {
    album_id: 17,
    title: 'C0RE C0LLECTION VOL.3 -Detachment-',
    circle_id: 2,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=C0RE',
    price: 0,
    publish_date: '2026-03-15',
    info_title: 'C0RE C0LLECTION VOL.3',
    info_content: 'EXperiment EXtreme C0re Noise AlcoholicS 核心合集第三弹。Hardcore × Hardstyle × Speedcore。',
    tag_ids: [8, 2],
    tracks: [
      { file_id: 129, file_name: 'DETACHMENT', duration: '4:00', sort_order: 1, file_type: 'preview' },
      { file_id: 130, file_name: 'CORE MELTDOWN', duration: '3:30', sort_order: 2, file_type: 'preview' },
      { file_id: 131, file_name: 'TERROR SQUAD', duration: '5:00', sort_order: 3, file_type: 'preview' },
      { file_id: 132, file_name: 'GABBA GABBA HEY', duration: '4:15', sort_order: 4, file_type: 'full' },
      { file_id: 133, file_name: 'NOISE CANNON', duration: '6:00', sort_order: 5, file_type: 'full' },
      { file_id: 134, file_name: 'BREAKCORE RUINS', duration: '5:30', sort_order: 6, file_type: 'full' },
      { file_id: 135, file_name: 'ATTACHMENT', duration: '3:00', sort_order: 7, file_type: 'full' }
    ],
    comments: [
      { comment_id: 16, user_id: 12, content: '音量警告！戴上耳机效果更佳。', created_at: '2026-03-20' }
    ]
  },
  {
    album_id: 18,
    title: 'Together We Rewind EP',
    circle_id: 4,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=Rewind',
    price: 30.0,
    publish_date: '2026-03-12',
    info_title: 'Together We Rewind EP',
    info_content: 'Silent Xords UK Hardcore EP。怀旧与未来的交差点。',
    tag_ids: [8, 9, 2],
    tracks: [
      { file_id: 136, file_name: 'Together We Rewind', duration: '5:00', sort_order: 1, file_type: 'preview' },
      { file_id: 137, file_name: 'Flashback', duration: '4:30', sort_order: 2, file_type: 'preview' },
      { file_id: 138, file_name: 'Rewind Time', duration: '5:45', sort_order: 3, file_type: 'preview' },
      { file_id: 139, file_name: 'Fast Forward', duration: '4:15', sort_order: 4, file_type: 'full' },
      { file_id: 140, file_name: 'Pause', duration: '3:00', sort_order: 5, file_type: 'full' }
    ],
    comments: []
  },
  {
    album_id: 19,
    title: '伪春 Revisit EP',
    circle_id: 3,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=Revisit',
    price: 0,
    publish_date: '2026-03-10',
    info_title: '伪春 Revisit EP',
    info_content: 'EchoBottle 氛围电子 EP。Vocaloid × ambient × rock 的实验碰撞。',
    tag_ids: [7, 14, 15],
    tracks: [
      { file_id: 141, file_name: '伪春', duration: '5:20', sort_order: 1, file_type: 'preview' },
      { file_id: 142, file_name: 'Revisit', duration: '4:10', sort_order: 2, file_type: 'preview' },
      { file_id: 143, file_name: '残響', duration: '6:00', sort_order: 3, file_type: 'preview' },
      { file_id: 144, file_name: '朧', duration: '3:45', sort_order: 4, file_type: 'full' },
      { file_id: 145, file_name: '泡沫', duration: '4:30', sort_order: 5, file_type: 'full' }
    ],
    comments: [
      { comment_id: 17, user_id: 13, content: 'Vocaloid 和 ambient 的结合意外地协调。', created_at: '2026-03-15' }
    ]
  }
];

// ============================================================
// 辅助查询函数
// ============================================================

function getCircle(circle_id) {
  return circles.find(c => c.circle_id === circle_id) || null;
}

function getTag(tag_id) {
  return tags.find(t => t.tag_id === tag_id) || null;
}

function getUser(user_id) {
  return users.find(u => u.user_id === user_id) || null;
}

function getCircleMembers(circle_id) {
  // 简化：返回 id 在 circle_id * 2 附近的 pro 用户
  return users.filter(u => u.user_role === 'pro').slice(circle_id * 2 - 2, circle_id * 2 + 2);
}

function getCircleAlbums(circle_id) {
  return albums.filter(a => a.circle_id === circle_id);
}

// ============================================================
// 模拟 API 接口
// ============================================================

function delay(ms = 200 + Math.random() * 200) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 首页/列表 — 专辑列表（flat 结构）
 * 支持：?page=&page_size=&tag=&search=&price=&sort=
 */
export async function fetchAlbums(params = {}) {
  await delay();

  const tag = params.tag;
  const search = (params.search || '').toLowerCase();
  const price = params.price;    // 'free' | 'paid'
  const sort = params.sort || 'publish_date_desc';
  const page = parseInt(params.page) || 1;
  const page_size = parseInt(params.page_size) || 12;

  let filtered = [...albums];

  // 标签筛选
  if (tag) {
    const tag_obj = tags.find(t => t.name === tag);
    if (tag_obj) {
      filtered = filtered.filter(a => a.tag_ids.includes(tag_obj.tag_id));
    }
  }

  // 搜索筛选
  if (search) {
    filtered = filtered.filter(a => {
      const circle = getCircle(a.circle_id);
      const circle_name = circle ? circle.name.toLowerCase() : '';
      return a.title.toLowerCase().includes(search) || circle_name.includes(search);
    });
  }

  // 价格筛选
  if (price === 'free') {
    filtered = filtered.filter(a => a.price === 0);
  } else if (price === 'paid') {
    filtered = filtered.filter(a => a.price > 0);
  }

  // 排序
  if (sort === 'publish_date_desc') {
    filtered.sort((a, b) => new Date(b.publish_date) - new Date(a.publish_date));
  } else if (sort === 'publish_date_asc') {
    filtered.sort((a, b) => new Date(a.publish_date) - new Date(b.publish_date));
  } else if (sort === 'price_asc') {
    filtered.sort((a, b) => a.price - b.price);
  } else if (sort === 'price_desc') {
    filtered.sort((a, b) => b.price - a.price);
  }

  const total = filtered.length;
  const start = (page - 1) * page_size;
  const paged = filtered.slice(start, start + page_size);

  const data = paged.map(a => {
    const circle = getCircle(a.circle_id);
    return {
      album_id: a.album_id,
      title: a.title,
      circle_name: circle ? circle.name : '',
      cover_url: a.cover_url,
      price: a.price,
      publish_date: a.publish_date,
      tags: a.tag_ids.map(tid => getTag(tid)?.name).filter(Boolean),
      track_count: a.tracks.length
    };
  });

  return { data, total, page, page_size };
}

/**
 * 专辑详情
 */
export async function fetchAlbum(album_id) {
  await delay(300);

  const album = albums.find(a => a.album_id === parseInt(album_id));
  if (!album) throw new Error('Album not found');

  const circle = getCircle(album.circle_id);

  return {
    album_id: album.album_id,
    title: album.title,
    circle: circle ? {
      circle_id: circle.circle_id,
      name: circle.name,
      logo_url: circle.logo_url
    } : null,
    cover_url: album.cover_url,
    price: album.price,
    publish_date: album.publish_date,
    info_title: album.info_title,
    info_content: album.info_content,
    tags: album.tag_ids.map(tid => {
      const t = getTag(tid);
      return t ? { tag_id: t.tag_id, name: t.name } : null;
    }).filter(Boolean),
    tracks: album.tracks,
    comments: album.comments.map(c => {
      const user = getUser(c.user_id);
      return {
        comment_id: c.comment_id,
        username: user ? user.username : '未知用户',
        avatar_url: user ? user.avatar_url : '',
        content: c.content,
        created_at: c.created_at
      };
    })
  };
}

/**
 * 社团列表
 */
export async function fetchCircles(params = {}) {
  await delay();

  const data = circles.map(c => {
    const circle_albums = getCircleAlbums(c.circle_id);
    return {
      circle_id: c.circle_id,
      name: c.name,
      logo_url: c.logo_url,
      description: c.description,
      album_count: circle_albums.length,
      member_count: getCircleMembers(c.circle_id).length
    };
  });

  return { data };
}

/**
 * 社团详情
 */
export async function fetchCircle(circle_id) {
  await delay(300);

  const circle = circles.find(c => c.circle_id === parseInt(circle_id));
  if (!circle) throw new Error('Circle not found');

  const circle_albums = getCircleAlbums(circle.circle_id).map(a => {
    const c = getCircle(a.circle_id);
    return {
      album_id: a.album_id,
      title: a.title,
      circle_name: c ? c.name : '',
      cover_url: a.cover_url,
      price: a.price,
      publish_date: a.publish_date,
      tags: a.tag_ids.map(tid => getTag(tid)?.name).filter(Boolean),
      track_count: a.tracks.length
    };
  });

  const members = getCircleMembers(circle.circle_id).map(u => ({
    user_id: u.user_id,
    username: u.username,
    avatar_url: u.avatar_url,
    user_role: u.user_role
  }));

  return {
    circle_id: circle.circle_id,
    name: circle.name,
    logo_url: circle.logo_url,
    description: circle.description,
    albums: circle_albums,
    members
  };
}

/**
 * 标签列表
 */
export function getTags() {
  return tags;
}

/**
 * 用户详情
 */
export async function fetchUser(user_id) {
  await delay();

  const user = users.find(u => u.user_id === parseInt(user_id));
  if (!user) throw new Error('User not found');

  return {
    user_id: user.user_id,
    username: user.username,
    avatar_url: user.avatar_url,
    user_role: user.user_role
    // 收藏列表、所属社团等后续扩展
  };
}
