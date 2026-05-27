// 模拟数据 - 标签列表
const tags = [
  { tag_id: 1, name: '东方Project' },
  { tag_id: 2, 'name': '电子' },
  { tag_id: 3, 'name': '摇滚' },
  { tag_id: 4, 'name': '硬核' },
  { tag_id: 5, 'name': '纯音乐' },
  { tag_id: 6, 'name': '管弦乐' },
  { tag_id: 7, 'name': 'Vocaloid' },
  { tag_id: 8, 'name': 'Hardcore' },
  { tag_id: 9, 'name': 'UK Hardcore' },
  { tag_id: 10, 'name': 'Trance' },
  { tag_id: 11, 'name': 'House' },
  { tag_id: 12, 'name': 'Techno' },
  { tag_id: 13, 'name': '氛围' },
  { tag_id: 14, 'name': '实验' },
  { tag_id: 15, 'name': '摇滚融合' }
];

// 模拟数据 - 社团列表
const circles = [
  {
    circle_id: 1,
    name: 'hisa_knowledge',
    logo_url: 'https://placehold.co/200x200/2a2a2a/ffffff?text=HK',
    description: '专注于东方Project管弦乐改编的社团，风格大气磅礴。'
  },
  {
    circle_id: 2,
    name: 'EXperiment EXtreme',
    logo_url: 'https://placehold.co/200x200/2a2a2a/ffffff?text=EXEX',
    description: '硬核电子音乐制作社团，擅长Hardcore、Speedcore等极端风格。'
  },
  {
    circle_id: 3,
    name: 'EchoBottle',
    logo_url: 'https://placehold.co/200x200/2a2a2a/ffffff?text=EB',
    description: 'Vocaloid同人音乐社团，风格以氛围电子和实验摇滚为主。'
  },
  {
    circle_id: 4,
    name: 'Static World',
    logo_url: 'https://placehold.co/200x200/2a2a2a/ffffff?text=SW',
    description: '纯音乐创作社团，主打治愈系、冬季主题的轻音乐。'
  },
  {
    circle_id: 5,
    name: 'THE FACTOTY OF SHEEP',
    logo_url: 'https://placehold.co/200x200/2a2a2a/ffffff?text=TFOS',
    description: '多元化电子音乐社团，涵盖Trance、House、Techno等多种风格。'
  }
];

// 模拟数据 - 用户列表
const users = [
  { user_id: 1, username: 'admin', avatar_url: 'https://placehold.co/100x100/000000/ffffff?text=AD', user_role: 'admin' },
  { user_id: 2, username: 'user1', avatar_url: 'https://placehold.co/100x100/333333/ffffff?text=U1', user_role: 'user' },
  { user_id: 3, username: 'user2', avatar_url: 'https://placehold.co/100x100/444444/ffffff?text=U2', user_role: 'user' },
  { user_id: 4, username: 'user3', avatar_url: 'https://placehold.co/100x100/555555/ffffff?text=U3', user_role: 'user' },
  { user_id: 5, username: 'composer1', avatar_url: 'https://placehold.co/100x100/666666/ffffff?text=C1', user_role: 'pro' },
  { user_id: 6, username: 'composer2', avatar_url: 'https://placehold.co/100x100/777777/ffffff?text=C2', user_role: 'pro' },
  { user_id: 7, username: 'composer3', avatar_url: 'https://placehold.co/100x100/888888/ffffff?text=C3', user_role: 'pro' },
  { user_id: 8, username: 'composer4', avatar_url: 'https://placehold.co/100x100/999999/ffffff?text=C4', user_role: 'pro' },
  { user_id: 9, username: 'composer5', avatar_url: 'https://placehold.co/100x100/aaaaaa/ffffff?text=C5', user_role: 'pro' },
  { user_id: 10, username: 'composer6', avatar_url: 'https://placehold.co/100x100/bbbbbb/ffffff?text=C6', user_role: 'pro' },
  { user_id: 11, username: 'composer7', avatar_url: 'https://placehold.co/100x100/cccccc/ffffff?text=C7', user_role: 'pro' },
  { user_id: 12, username: 'composer8', avatar_url: 'https://placehold.co/100x100/dddddd/ffffff?text=C8', user_role: 'pro' },
  { user_id: 13, username: 'listener1', avatar_url: 'https://placehold.co/100x100/eeeeee/ffffff?text=L1', user_role: 'user' },
  { user_id: 14, username: 'listener2', avatar_url: 'https://placehold.co/100x100/ffff00/ffffff?text=L2', user_role: 'user' }
];

// 模拟数据 - 专辑列表
const albums = [
  {
    album_id: 1,
    title: '幻想交响诗',
    circle_id: 1,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=Symphony',
    price: 50.0,
    publish_date: '2026-01-15',
    info_title: '幻想交响诗',
    info_content: 'hisa_knowledge 首张东方Project管弦乐改编专辑，收录8首经典曲目改编。',
    tag_ids: [1, 6],
    tracks: [
      { file_id: 1, file_name: '幻想序曲', duration: '3:30', sort_order: 1, file_type: 'preview' },
      { file_id: 2, file_name: '红魔乡交响诗', duration: '5:15', sort_order: 2, file_type: 'preview' },
      { file_id: 3, file_name: '妖々夢のテーマ', duration: '4:40', sort_order: 3, file_type: 'preview' },
      { file_id: 4, file_name: '永夜抄', duration: '6:00', sort_order: 4, file_type: 'preview' },
      { file_id: 5, file_name: '風神録', duration: '5:20', sort_order: 5, file_type: 'preview' },
      { file_id: 6, file_name: '地霊殿', duration: '4:30', sort_order: 6, file_type: 'preview' },
      { file_id: 7, file_name: '星莲船', duration: '5:45', sort_order: 7, file_type: 'preview' },
      { file_id: 8, file_name: '神霊廟', duration: '4:10', sort_order: 8, file_type: 'preview' }
    ],
    comments: [
      { comment_id: 1, user_id: 2, content: '管弦乐改编太惊艳了！', created_at: '2026-01-20' },
      { comment_id: 2, user_id: 3, content: '红魔乡交响诗那段高潮起鸡皮疙瘩', created_at: '2026-01-22' }
    ]
  },
  {
    album_id: 2,
    title: 'HYPERNOISE',
    circle_id: 2,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=HYPERNOISE',
    price: 45.0,
    publish_date: '2026-01-20',
    info_title: 'HYPERNOISE',
    info_content: 'EXperiment EXtreme 硬核电子专辑，高速BPM与极端噪音的完美融合。',
    tag_ids: [2, 4, 8],
    tracks: [
      { file_id: 9, file_name: 'NOISE ATTACK', duration: '4:00', sort_order: 1, file_type: 'preview' },
      { file_id: 10, file_name: 'HYPER SPEED', duration: '3:45', sort_order: 2, file_type: 'preview' },
      { file_id: 11, file_name: 'CORE DESTRUCTION', duration: '5:10', sort_order: 3, file_type: 'preview' },
      { file_id: 12, file_name: 'EXTREME BASS', duration: '4:30', sort_order: 4, file_type: 'preview' },
      { file_id: 13, file_name: 'DARKNESS', duration: '6:00', sort_order: 5, file_type: 'preview' },
      { file_id: 14, file_name: 'SPEEDCORE NIGHTMARE', duration: '3:15', sort_order: 6, file_type: 'preview' },
      { file_id: 15, file_name: 'FINAL EXPLOSION', duration: '5:20', sort_order: 7, file_type: 'preview' }
    ],
    comments: [
      { comment_id: 3, user_id: 4, content: '耳膜炸裂警告！', created_at: '2026-01-25' },
      { comment_id: 4, user_id: 5, content: '最喜欢SPEEDCORE NIGHTMARE这段，BPM拉满', created_at: '2026-01-28' }
    ]
  },
  {
    album_id: 3,
    title: '回响瓶',
    circle_id: 3,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=EchoBottle',
    price: 0.0,
    publish_date: '2026-02-01',
    info_title: '回响瓶',
    info_content: 'EchoBottle 首张免费专辑，Vocaloid与氛围电子的结合，如梦似幻。',
    tag_ids: [7, 13, 14],
    tracks: [
      { file_id: 16, file_name: '回响瓶', duration: '5:00', sort_order: 1, file_type: 'preview' },
      { file_id: 17, file_name: '虚ろな空', duration: '4:20', sort_order: 2, file_type: 'preview' },
      { file_id: 18, file_name: '水底の声', duration: '6:15', sort_order: 3, file_type: 'preview' },
      { file_id: 19, file_name: '風のメッセージ', duration: '5:30', sort_order: 4, file_type: 'preview' },
      { file_id: 20, file_name: '星の雫', duration: '4:45', sort_order: 5, file_type: 'preview' },
      { file_id: 21, file_name: '永遠の輪廻', duration: '7:00', sort_order: 6, file_type: 'preview' }
    ],
    comments: [
      { comment_id: 5, user_id: 6, content: '免费专辑质量这么高！', created_at: '2026-02-05' },
      { comment_id: 6, user_id: 7, content: '水底の声这段太治愈了', created_at: '2026-02-08' }
    ]
  },
  {
    album_id: 4,
    title: 'Silent World',
    circle_id: 4,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=Silent',
    price: 30.0,
    publish_date: '2026-02-10',
    info_title: 'Silent World',
    info_content: 'Static World 首张专辑，纯音乐风格，营造静谧的听觉体验。',
    tag_ids: [5, 13],
    tracks: [
      { file_id: 22, file_name: 'Silent World', duration: '4:15', sort_order: 1, file_type: 'preview' },
      { file_id: 23, file_name: 'Morning Breeze', duration: '3:50', sort_order: 2, file_type: 'preview' },
      { file_id: 24, file_name: 'Quiet Stream', duration: '5:20', sort_order: 3, file_type: 'preview' },
      { file_id: 25, file_name: 'Evening Glow', duration: '4:40', sort_order: 4, file_type: 'preview' },
      { file_id: 26, file_name: 'Night Sky', duration: '6:10', sort_order: 5, file_type: 'preview' },
      { file_id: 27, file_name: 'Midnight', duration: '3:30', sort_order: 6, file_type: 'preview' },
      { file_id: 28, file_name: 'Dawn', duration: '4:00', sort_order: 7, file_type: 'preview' }
    ],
    comments: [
      { comment_id: 7, user_id: 8, content: '学习时听太合适了', created_at: '2026-02-15' },
      { comment_id: 8, user_id: 9, content: 'Morning Breeze这段循环了一整天', created_at: '2026-02-18' }
    ]
  },
  {
    album_id: 5,
    title: 'ELECTRONIC DREAMS',
    circle_id: 5,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=ED',
    price: 55.0,
    publish_date: '2026-02-18',
    info_title: 'ELECTRONIC DREAMS',
    tag_ids: [2, 10, 11],
    tracks: [
      { file_id: 29, file_name: 'Dreamscape', duration: '5:30', sort_order: 1, file_type: 'preview' },
      { file_id: 30, file_name: 'Cybernetic', duration: '4:45', sort_order: 2, file_type: 'preview' },
      { file_id: 31, file_name: 'Neon Dreams', duration: '6:00', sort_order: 3, file_type: 'preview' },
      { file_id: 32, file_name: 'Digital Paradise', duration: '5:15', sort_order: 4, file_type: 'preview' },
      { file_id: 33, file_name: 'Synthwave Nights', duration: '4:30', sort_order: 5, file_type: 'preview' },
      { file_id: 34, file_name: 'Future Retro', duration: '5:45', sort_order: 6, file_type: 'preview' },
      { file_id: 35, file_name: 'Electric Dreams', duration: '6:20', sort_order: 7, file_type: 'preview' },
      { file_id: 36, file_name: 'Final Frontier', duration: '4:00', sort_order: 8, file_type: 'preview' }
    ],
    comments: [
      { comment_id: 9, user_id: 10, content: 'Synthwave Nights太有80年代感觉了', created_at: '2026-02-22' },
      { comment_id: 10, user_id: 11, content: '循环停不下来', created_at: '2026-02-25' }
    ]
  },
  {
    album_id: 6,
    title: '幻想电子诗',
    circle_id: 1,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=Electronic',
    price: 40.0,
    publish_date: '2026-03-01',
    info_title: '幻想电子诗',
    info_content: 'hisa_knowledge 东方电子管弦融合专辑，传统与现代的碰撞。',
    tag_ids: [1, 2, 6],
    tracks: [
      { file_id: 37, file_name: '幻想電子詩', duration: '4:30', sort_order: 1, file_type: 'preview' },
      { file_id: 38, file_name: '博麗神社', duration: '5:10', sort_order: 2, file_type: 'preview' },
      { file_id: 39, file_name: '霊夢のテーマ', duration: '4:20', sort_order: 3, file_type: 'preview' },
      { file_id: 40, file_name: '魔理沙の冒険', duration: '5:40', sort_order: 4, file_type: 'preview' },
      { file_id: 41, file_name: '紅魔館', duration: '4:50', sort_order: 5, file_type: 'preview' },
      { file_id: 42, file_name: '妖夢', duration: '6:00', sort_order: 6, file_type: 'preview' },
      { file_id: 43, file_name: '幽々子', duration: '5:20', sort_order: 7, file_type: 'preview' },
      { file_id: 44, file_name: 'ファイナルファンタジー', duration: '3:30', sort_order: 8, file_type: 'preview' }
    ],
    comments: [
      { comment_id: 11, user_id: 12, content: '管弦+电子的组合太妙了', created_at: '2026-03-05' }
    ]
  },
  {
    album_id: 7,
    title: 'NOISE FLOOR',
    circle_id: 2,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=NOISE',
    price: 0.0,
    publish_date: '2026-03-05',
    info_title: 'NOISE FLOOR',
    info_content: 'EXperiment EXtreme 免费硬核EP，噪音美学的极致体现。',
    tag_ids: [2, 4, 8],
    tracks: [
      { file_id: 45, file_name: 'NOISE FLOOR', duration: '3:45', sort_order: 1, file_type: 'preview' },
      { file_id: 46, file_name: 'BASS DROP', duration: '4:10', sort_order: 2, file_type: 'preview' },
      { file_id: 47, file_name: 'HARDCORE NATION', duration: '5:00', sort_order: 3, file_type: 'preview' },
      { file_id: 48, file_name: 'EXTREME NOISE', duration: '4:20', sort_order: 4, file_type: 'preview' },
      { file_id: 49, file_name: 'FINAL BATTLE', duration: '3:50', sort_order: 5, file_type: 'preview' }
    ],
    comments: [
      { comment_id: 12, user_id: 13, content: '免费的都这么顶！', created_at: '2026-03-10' }
    ]
  },
  {
    album_id: 8,
    title: '夢の浮橋',
    circle_id: 3,
    cover_url: 'https://placehold.co/600x600/2a2a2a/ffffff?text=Yume',
    price: 35.0,
    publish_date: '2026-03-12',
    info_title: '夢の浮橋',
    info_content: 'EchoBottle Vocaloid 叙事专辑，以梦境为主题的音乐故事。',
    tag_ids: [7, 14, 5],
    tracks: [
      { file_id: 50, file_name: '夢の浮橋', duration: '5:15', sort_order: 1, file_type: 'preview' },
      { file_id: 51, file_name: '醒めない夢', duration: '4:30', sort_order: 2, file_type: 'preview' },
      { file_id: 52, file_name: '夢と現実', duration: '6:00', sort_order: 3, file_type: 'preview' },
      { file_id: 53, file_name: '記憶の欠片', duration: '4:45', sort_order: 4, file_type: 'preview' },
      { file_id: 54, file_name: '忘却の彼方', duration: '5:20', sort_order: 5, file_type: 'preview' },
      { file_id: 55, file_name: '再び夢へ', duration: '3:50', sort_order: 6, file_type: 'preview' },
      { file_id: 56, file_name: '目覚め', duration: '4:10', sort_order: 7, file_type: 'preview' }
    ],
    comments: []
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
      { file_id: 74, file_name: '凍える夜', duration: '4:45', sort_order: 4, file_type: 'preview' },
      { file_id: 75, file_name: '静寂', duration: '6:30', sort_order: 5, file_type: 'preview' },
      { file_id: 76, file_name: '春の兆し', duration: '3:15', sort_order: 6, file_type: 'preview' },
      { file_id: 77, file_name: '雪解け', duration: '5:40', sort_order: 7, file_type: 'preview' },
      { file_id: 78, file_name: 'また来年', duration: '2:00', sort_order: 8, file_type: 'preview' }
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
      { file_id: 83, file_name: 'Electric Dreams', duration: '6:00', sort_order: 5, file_type: 'preview' },
      { file_id: 84, file_name: 'Synthetic Love', duration: '5:30', sort_order: 6, file_type: 'preview' },
      { file_id: 85, file_name: 'Pixel Rain', duration: '4:00', sort_order: 7, file_type: 'preview' },
      { file_id: 86, file_name: 'Reboot', duration: '3:45', sort_order: 8, file_type: 'preview' },
      { file_id: 87, file_name: 'Analog Sunset', duration: '5:15', sort_order: 9, file_type: 'preview' },
      { file_id: 88, file_name: 'EMOTIONA -Outro-', duration: '2:00', sort_order: 10, file_type: 'preview' }
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
      { file_id: 92, file_name: '空へ', duration: '6:10', sort_order: 4, file_type: 'preview' },
      { file_id: 93, file_name: '光', duration: '4:50', sort_order: 5, file_type: 'preview' },
      { file_id: 94, file_name: '再生', duration: '5:00', sort_order: 6, file_type: 'preview' },
      { file_id: 95, file_name: '希望', duration: '3:40', sort_order: 7, file_type: 'preview' },
      { file_id: 96, file_name: '旅立ち', duration: '2:30', sort_order: 8, file_type: 'preview' }
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
      { file_id: 100, file_name: '出会い', duration: '4:45', sort_order: 4, file_type: 'preview' },
      { file_id: 101, file_name: '別れ', duration: '5:20', sort_order: 5, file_type: 'preview' },
      { file_id: 102, file_name: '想い', duration: '3:50', sort_order: 6, file_type: 'preview' },
      { file_id: 103, file_name: '辿り着く場所', duration: '6:00', sort_order: 7, file_type: 'preview' },
      { file_id: 104, file_name: 'また歩き出す', duration: '3:00', sort_order: 8, file_type: 'preview' }
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
      { file_id: 108, file_name: 'Rise', duration: '5:45', sort_order: 4, file_type: 'preview' },
      { file_id: 109, file_name: 'Float', duration: '4:20', sort_order: 5, file_type: 'preview' }
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
      { file_id: 113, file_name: 'Last Spell', duration: '6:00', sort_order: 4, file_type: 'preview' },
      { file_id: 114, file_name: 'Game Over', duration: '3:00', sort_order: 5, file_type: 'preview' }
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
      { file_id: 118, file_name: 'MESOSPHERE', duration: '5:00', sort_order: 4, file_type: 'preview' },
      { file_id: 119, file_name: 'THERMOSPHERE', duration: '7:30', sort_order: 5, file_type: 'preview' },
      { file_id: 120, file_name: 'EXOSPHERE', duration: '4:00', sort_order: 6, file_type: 'preview' },
      { file_id: 121, file_name: 'REENTRY', duration: '3:45', sort_order: 7, file_type: 'preview' },
      { file_id: 122, file_name: 'LANDING', duration: '2:30', sort_order: 8, file_type: 'preview' }
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
      { file_id: 126, file_name: '宇宙ステーション', duration: '4:40', sort_order: 4, file_type: 'preview' },
      { file_id: 127, file_name: '惑星探査', duration: '6:20', sort_order: 5, file_type: 'preview' },
      { file_id: 128, file_name: '帰還信号', duration: '3:15', sort_order: 6, file_type: 'preview' }
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
      { file_id: 132, file_name: 'GABBA GABBA HEY', duration: '4:15', sort_order: 4, file_type: 'preview' },
      { file_id: 133, file_name: 'NOISE CANNON', duration: '6:00', sort_order: 5, file_type: 'preview' },
      { file_id: 134, file_name: 'BREAKCORE RUINS', duration: '5:30', sort_order: 6, file_type: 'preview' },
      { file_id: 135, file_name: 'ATTACHMENT', duration: '3:00', sort_order: 7, file_type: 'preview' }
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
      { file_id: 139, file_name: 'Fast Forward', duration: '4:15', sort_order: 4, file_type: 'preview' },
      { file_id: 140, file_name: 'Pause', duration: '3:00', sort_order: 5, file_type: 'preview' }
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
      { file_id: 144, file_name: '朧', duration: '3:45', sort_order: 4, file_type: 'preview' },
      { file_id: 145, file_name: '泡沫', duration: '4:30', sort_order: 5, file_type: 'preview' }
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
 * 社团列表（增强版：补充最新专辑日期、代表性标签）
 */
export async function fetchCircles(params = {}) {
  await delay();

  const enhancedCircles = circles.map(c => {
    const circleAlbums = getCircleAlbums(c.circle_id);

    // 最新专辑日期
    let latestAlbumDate = null;
    if (circleAlbums.length > 0) {
      const sorted = [...circleAlbums].sort((a, b) => new Date(b.publish_date) - new Date(a.publish_date));
      latestAlbumDate = sorted[0].publish_date;
    }

    // 统计标签频率，取前3
    const tagFreq = new Map();
    circleAlbums.forEach(album => {
      album.tag_ids.forEach(tid => {
        const tagName = getTag(tid)?.name;
        if (tagName) {
          tagFreq.set(tagName, (tagFreq.get(tagName) || 0) + 1);
        }
      });
    });
    const representativeTags = Array.from(tagFreq.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([name]) => name);

    // 新增：获取最新的4张预览专辑（取前2个标签）
    const previewAlbums = circleAlbums
      .sort((a, b) => new Date(b.publish_date) - new Date(a.publish_date))
      .slice(0, 4)
      .map(a => ({
        album_id: a.album_id,
        title: a.title,
        cover_url: a.cover_url,
        tags: a.tag_ids.map(tid => getTag(tid)?.name).filter(Boolean).slice(0, 2) // 取前2个标签用于展示
      }));

    return {
      circle_id: c.circle_id,
      name: c.name,
      logo_url: c.logo_url,
      description: c.description,
      album_count: circleAlbums.length,
      member_count: getCircleMembers(c.circle_id).length,
      latest_album_date: latestAlbumDate,
      representative_tags: representativeTags,
      preview_albums: previewAlbums // 新增预览专辑字段
    };
  });

  return { data: enhancedCircles };
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