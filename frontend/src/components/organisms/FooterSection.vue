<!-- 页脚 -->
<template>
  <footer class="footer">
    <div class="container-wide">
      <div class="footer-content">
        <div class="footer-section">
          <h3>DIZZYL@B</h3>
          <p>独立电子音乐发行平台，专注于高品质电子音乐作品的推广与销售。</p>
        </div>

        <div class="footer-section">
          <h4>快速链接</h4>
          <ul class="footer-links">
            <li><router-link to="/">首页</router-link></li>
            <li><router-link to="/tag">标签</router-link></li>
            <li><router-link to="/labels">社团</router-link></li>
          </ul>
        </div>

        <div class="footer-section">
          <h4>分类</h4>
          <ul class="footer-links">
            <li><router-link to="/tag?price=free">免费专辑</router-link></li>
            <li><router-link to="/tag?price=paid">付费专辑</router-link></li>
          </ul>
        </div>

        <div class="footer-section">
          <h4>联系方式</h4>
          <ul class="footer-contact">
            <li><i class="fas fa-envelope"></i> contact@indietracks.net</li>
            <li><i class="fab fa-github"></i> IndieTracks</li>
          </ul>
        </div>
      </div>

      <div class="copyright">
        &copy; 2026 IndieTracks. All rights reserved.
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
.footer {
  background: var(--color-bg-primary);
  border-top: 1px solid var(--color-border);
  padding: var(--spacing-2xl) 0 var(--spacing-lg);
  margin-top: var(--spacing-2xl);
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-xl);
  margin-bottom: var(--spacing-xl);
}

.footer-section h3 {
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-md);
  font-size: 1.3rem;
}

.footer-section h4 {
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-md);
  font-size: 1rem;
}

.footer-section p {
  color: var(--color-text-muted);
  font-size: 0.9rem;
  line-height: 1.6;
}

.footer-links li {
  margin-bottom: 0.7rem;
}

.footer-links a {
  color: var(--color-text-muted);
  text-decoration: none;
  transition: color var(--transition-normal);
  font-size: 0.9rem;
}

.footer-links a:hover {
  color: var(--color-accent);
}

.footer-contact {
  color: var(--color-text-muted);
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
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
  color: var(--color-text-dim);
  font-size: 0.9rem;
}
</style>
