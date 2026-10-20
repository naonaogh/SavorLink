<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
const goHome = () => router.push('/')
</script>

<template>
  <div class="placeholder-page">
    <section class="content-card">
      <div class="content-main">
        <p class="kicker">Раздел / Возможности</p>
        <h1>Возможности</h1>
        <p class="content-text">Этот раздел находится в разработке. Здесь будет описание всех функций системы SavorLink.</p>
        <button @click="goHome" class="back-btn">На главную <span class="arrow" aria-hidden="true">→</span></button>
      </div>

      <div class="content-aside" aria-hidden="true">
        <span class="corner corner--tl"></span>
        <span class="corner corner--br"></span>
        <div class="blueprint">
          <span class="is-on"></span><span></span><span></span>
          <span></span><span class="is-on"></span><span></span>
          <span></span><span></span><span></span>
        </div>
        <p class="status"><span class="status-dot"></span>В разработке</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.placeholder-page {
  padding: 1.25rem 0 2rem;
  color: var(--sl-ink);
}

.content-card {
  display: grid;
  grid-template-columns: minmax(0, 7fr) minmax(0, 5fr);
  min-height: min(60vh, 520px);
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
}

.content-main {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  padding: clamp(1.75rem, 5vw, 3.5rem);
}

.kicker {
  margin: 0 0 0.9rem;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-leaf);
}

h1 {
  margin: 0;
  font-size: clamp(1.6rem, 3.2vw, 2.5rem);
  line-height: 1.15;
  color: var(--sl-ink);
}

.content-text {
  max-width: 52ch;
  margin: 1.25rem 0 2rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--sl-line);
  line-height: 1.6;
  color: #4f5f48;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.85rem 1.4rem;
  border-radius: 0;
  background: var(--sl-ink);
  color: #fff;
  border: 1px solid var(--sl-ink);
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.back-btn:hover {
  background: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

.back-btn .arrow {
  transition: transform 0.2s ease;
}

.back-btn:hover .arrow {
  transform: translateX(4px);
}

.back-btn:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: 3px;
}

/* ДЕКОР */
.content-aside {
  position: relative;
  display: grid;
  place-items: center;
  padding: 3rem 2rem;
  background:
    repeating-linear-gradient(135deg, rgba(198, 236, 154, 0.05) 0 1px, transparent 1px 14px),
    var(--sl-forest);
}

.corner {
  position: absolute;
  width: 26px;
  height: 26px;
  border: 0 solid var(--sl-lime);
  opacity: 0.85;
}

.corner--tl { top: 1.25rem; left: 1.25rem; border-top-width: 2px; border-left-width: 2px; }
.corner--br { bottom: 1.25rem; right: 1.25rem; border-bottom-width: 2px; border-right-width: 2px; }

.blueprint {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  width: min(220px, 70%);
  aspect-ratio: 1;
  background: rgba(198, 236, 154, 0.3);
  border: 1px solid rgba(198, 236, 154, 0.3);
}

.blueprint span {
  background: var(--sl-forest);
}

.blueprint span.is-on {
  background: var(--sl-lime);
}

.status {
  position: absolute;
  left: 50%;
  bottom: 2.5rem;
  transform: translateX(-50%);
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.35rem 0.7rem;
  background: var(--sl-ink);
  color: var(--sl-lime);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  white-space: nowrap;
}

.status-dot {
  width: 7px;
  height: 7px;
  background: var(--sl-lime);
}

@media (max-width: 860px) {
  .content-card {
    grid-template-columns: 1fr;
    min-height: 0;
  }

  .content-aside {
    order: -1;
    padding: 2.25rem 1.5rem 4.5rem;
  }

  .blueprint {
    width: 120px;
  }

  .status {
    bottom: 1.5rem;
  }
}

@media (max-width: 768px) {
  .placeholder-page {
    padding-top: 0.75rem;
  }
}
</style>
