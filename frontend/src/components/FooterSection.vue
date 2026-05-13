<!-- 页脚文件 -->
<template>
  <footer>
    <div class="container-full">
      <div class="footer-content">
        <div class="footer-section">
          <h3>DIZZYL@B</h3>
          <p>独立电子音乐发行平台，专注于高品质电子音乐作品的推广与销售。</p>
        </div>

        <div class="footer-section">
          <h4>快速链接</h4>
          <ul class="footer-links">
            <li><router-link to="/about">关于我们</router-link></li>
            <li><router-link to="/artists">艺术家入驻</router-link></li>
            <li><router-link to="/support">客户服务</router-link></li>
            <li><router-link to="/privacy">隐私政策</router-link></li>
          </ul>
        </div>

        <div class="footer-section">
          <h4>分类</h4>
          <ul class="footer-links">
            <li><router-link to="/browse/digital">数字专辑</router-link></li>
            <li><router-link to="/browse/ep">单曲EP</router-link></li>
            <li><router-link to="/browse/download">下载商品</router-link></li>
          </ul>
        </div>

        <div class="footer-section">
          <h4>联系方式</h4>
          <ul class="footer-contact">
            <li><i class="fas fa-envelope"></i> contact@dizzylab.net</li>
            <li><i class="fab fa-steam"></i> STEAM: DIZZYL@B</li>
            <li><i class="fab fa-weibo"></i> 微博: @DIZZYL@B</li>
          </ul>
        </div>
      </div>

      <div class="copyright">
        &copy; 2023 DIZZYL@B. All rights reserved. 专注于电子音乐发行。
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'FooterSection'
};
</script>

<style scoped>
footer {
  background: #0a0a0a;
  border-top: 1px solid #222;
  padding: 3rem 0 1.5rem;
  margin-top: 3rem;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.footer-section h3 {
  color: white;
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

.footer-section h4 {
  color: #ddd;
  margin-bottom: 1rem;
  font-size: 1rem;
}

.footer-section p {
  color: #aaa;
  font-size: 0.9rem;
  line-height: 1.6;
}

.footer-links {
  list-style: none;
}

.footer-links li {
  margin-bottom: 0.7rem;
}

.footer-links a {
  color: #aaa;
  text-decoration: none;
  transition: color 0.3s;
  font-size: 0.9rem;
}

.footer-links a:hover {
  color: #ff6b6b;
}

.footer-contact {
  list-style: none;
  color: #aaa;
  font-size: 0.9rem;
}

.footer-contact li {
  margin-bottom: 0.7rem;
  display: flex;
  align-items: center;
  gap: 0.7rem;
}

.copyright {
  text-align: center;
  padding-top: 1.5rem;
  border-top: 1px solid #222;
  color: #666;
  font-size: 0.9rem;
  max-width: 1400px;
  margin: 0 auto;
}
</style>
