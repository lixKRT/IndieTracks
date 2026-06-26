/**
 * 爬虫抓取文本清洗工具
 * 从 AlbumDetail.vue 提取，消除 view 层的噪音清洗逻辑
 */

const BOILERPLATE = [
  '提供高品质MP3和无损FLAC格式下载',
  '完整歌曲在线串流',
  '包含实体物品',
  '这个商品需要一个邮寄地址',
  '购买完成后请添加主理人微信',
  '喜欢《',
  '您可以使用BOOST',
  '您可以支付',
  '购买',
  '最少需要',
  '元',
  '在您购买这个商品之后',
  '折扣码',
  '兑换的商品无法使用折扣码',
  '短评',
  '和……相似的作品',
  'OrganicNight',
  '@dizzylab',
  '收件人',
  '手机号',
  '收货地址',
  '附言',
  'BOOST',
  '在声音中寻找本真',
  '粤网文',
  '节目制作经营许可证',
  'Links',
]

/**
 * 清洗爬虫抓取的页面噪音
 * @param {string} text - 原始文本
 * @returns {string} - 清洗后的文本
 */
export function cleanText(text) {
  if (!text) return ''
  // 移除孤立的低代理项（lone surrogates），爬虫抓取时可能产生这类非法 UTF-16
  let cleaned = text.replace(/[\udc00-\udfff]/g, '')
  // 按行过滤
  const lines = cleaned.split('\n').filter(line => {
    const l = line.trim()
    if (!l) return false
    // 跳过纯数字行、百分比、日期行
    if (/^\d+%$/.test(l)) return false
    if (/^发布于?\d{4}年/.test(l)) return false
    if (/^发布于/.test(l)) return false
    // 跳过包含噪音关键词的行
    for (const bp of BOILERPLATE) {
      if (l.includes(bp)) return false
    }
    return true
  })
  return lines.join('\n').trim()
}
