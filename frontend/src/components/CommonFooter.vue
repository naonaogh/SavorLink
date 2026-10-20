<script setup lang="ts">
const year = new Date().getFullYear()
</script>

<template>
  <footer class="common-footer">
    <div class="footer-inner">
      <div class="footer-top">
        <div class="brand-block">
          <div class="brand">
            <span class="brand-mark">S</span>
            <span class="brand-name">SavorLink</span>
          </div>
          <p class="brand-text">
            Платформа для удобной работы ресторанов, поставщиков и документов в одном месте.
          </p>
        </div>

        <nav class="footer-col" aria-label="Навигация">
          <h3>Навигация</h3>
          <router-link to="/catalog">Каталог</router-link>
          <router-link to="/favorites">Избранное</router-link>
          <router-link to="/profile">Профиль</router-link>
        </nav>

        <nav class="footer-col" aria-label="Сервисы">
          <h3>Сервисы</h3>
          <router-link to="/chat">Чат</router-link>
          <router-link to="/analytics">Аналитика</router-link>
          <router-link to="/documents">Документы</router-link>
        </nav>
      </div>

      <div class="footer-bottom">
        <span>© {{ year }} SavorLink</span>
        <span class="footer-tag">Поставщики — Рестораны</span>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.common-footer {
  width: 100%;
  max-width: 1200px;
  margin: auto auto 0;
  padding: 1.25rem 1rem 1.5rem;
}

.footer-inner {
  color: #fff;
  border-top: 3px solid var(--sl-lime);
  background:
    repeating-linear-gradient(135deg, rgba(198, 236, 154, 0.05) 0 1px, transparent 1px 14px),
    var(--sl-ink);
}

.footer-top {
  display: grid;
  grid-template-columns: 1.6fr 1fr 1fr;
  gap: 2rem;
  padding: clamp(1.5rem, 4vw, 2.75rem);
}

/* БРЕНД */
.brand-block {
  max-width: 420px;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.brand-mark {
  width: 2.25rem;
  height: 2.25rem;
  display: grid;
  place-items: center;
  background: var(--sl-lime);
  color: var(--sl-ink);
  font-family: var(--sl-display);
  font-weight: 700;
}

.brand-name {
  font-family: var(--sl-display);
  font-size: 1.05rem;
  font-weight: 600;
}

.brand-text {
  margin: 0;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
}

/* КОЛОНКИ */
.footer-col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.55rem;
}

.footer-col h3 {
  margin: 0 0 0.5rem;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-lime);
}

.footer-col a {
  position: relative;
  color: rgba(255, 255, 255, 0.82);
  transition: color 0.2s ease, padding-left 0.2s ease;
}

.footer-col a::before {
  content: '→';
  position: absolute;
  left: 0;
  opacity: 0;
  color: var(--sl-lime);
  transition: opacity 0.2s ease;
}

.footer-col a:hover {
  color: #fff;
  padding-left: 1.35rem;
}

.footer-col a:hover::before {
  opacity: 1;
}

.footer-col a:focus-visible {
  outline: 2px solid var(--sl-lime);
  outline-offset: 3px;
}

/* НИЖНЯЯ СТРОКА */
.footer-bottom {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem clamp(1.5rem, 4vw, 2.75rem);
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.55);
}

.footer-tag {
  letter-spacing: 0.2em;
  text-transform: uppercase;
  font-size: 0.7rem;
  font-weight: 700;
}

@media (max-width: 860px) {
  .footer-top {
    grid-template-columns: 1fr 1fr;
  }

  .brand-block {
    grid-column: 1 / -1;
  }
}

@media (max-width: 768px) {
  .common-footer {
    padding: 1rem 0.75rem 1rem;
  }
}

@media (max-width: 480px) {
  .footer-bottom {
    flex-direction: column;
    gap: 0.35rem;
  }
}
</style>
