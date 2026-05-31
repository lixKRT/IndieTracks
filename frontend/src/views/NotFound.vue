<template>
  <div class="not-found">
    <h1>404</h1>
    <p>页面不存在</p>
    <router-link to="/" class="back-home">返回首页</router-link>
  </div>
</template>

<script>
export default { name: 'NotFound' };
</script>

<style scoped>
.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  color: var(--color-text-muted);
}
.not-found h1 {
  font-size: 6rem;
  color: var(--color-accent);
  font-weight: 800;
  margin-bottom: 1rem;
}
.not-found p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
}
.back-home {
  color: var(--color-accent);
  text-decoration: none;
  font-size: 1rem;
  padding: 0.6rem 2rem;
  border: 1px solid var(--color-accent);
  transition: all 0.2s;
}
.back-home:hover {
  background: var(--color-accent);
  color: var(--color-bg-primary);
}
</style>
