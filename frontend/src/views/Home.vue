<script setup lang="ts">
import { useRouter } from 'vue-router'
import BasketIcon from '@/assets/icons/basket.svg'
import TruckIcon from '@/assets/icons/grusovik.svg'
import DocsIcon from '@/assets/icons/docs.svg'
import HeroImage from '@/assets/images/home-hero.jpg'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const steps = [
  { title: 'Выбираете поставщика и товары в каталоге', icon: BasketIcon },
  { title: 'Оформляете заказ и отслеживаете статусы', icon: TruckIcon },
  { title: 'Получаете документы и аналитику в одном месте', icon: DocsIcon },
]

const advantages = [
  'Работа без посредников и скрытых наценок',
  'Карточки поставщиков и товаров в едином стиле',
  'Чат, документы и уведомления доступны из одного интерфейса',
]

const pad = (n: number) => String(n).padStart(2, '0')

const goRegisterBuyer = () => router.push({ path: '/auth', query: { mode: 'register', role: 'buyer' } })
const goRegisterSupplier = () => router.push({ path: '/auth', query: { mode: 'register', role: 'supplier' } })
const goCatalog = () => router.push('/catalog')
</script>

<template>
  <main class="home-page">
    <!-- ===== HERO ===== -->
    <section class="hero-block">
      <div class="hero">
        <img :src="HeroImage" alt="" class="hero-bg" aria-hidden="true" />
        <div class="hero-overlay"></div>

        <span class="corner corner--tl" aria-hidden="true"></span>
        <span class="corner corner--tr" aria-hidden="true"></span>
        <span class="corner corner--bl" aria-hidden="true"></span>
        <span class="corner corner--br" aria-hidden="true"></span>

        <div class="hero-copy">
          <p class="eyebrow"><span class="eyebrow-mark"></span>SavorLink</p>
          <h1>Поставщики и&nbsp;рестораны находят друг друга <em>быстрее</em></h1>
        </div>

        <p class="hero-side" aria-hidden="true">Поставщики — Рестораны</p>
      </div>

      <div class="action-bar">
        <p class="action-bar__label">Начать работу</p>

        <div class="hero-actions">
          <button type="button" class="primary-btn" @click="goRegisterBuyer">Я покупатель</button>
          <button type="button" class="secondary-btn" @click="goRegisterSupplier">Я поставщик</button>
        </div>

        <button type="button" class="catalog-link" @click="goCatalog">
          Смотреть каталог <span class="arrow" aria-hidden="true">→</span>
        </button>
      </div>
    </section>

    <!-- ===== КАК ЭТО РАБОТАЕТ ===== -->
    <section class="section">
      <header class="section-head">
        <div>
          <p class="section-index">01 / Процесс</p>
          <h2>Как это работает</h2>
        </div>
        <p class="section-lead">
          Покупка и работа с поставщиками проходят в несколько простых шагов без лишних переходов и путаницы.
        </p>
      </header>

      <ol class="steps-grid">
        <li v-for="(step, index) in steps" :key="step.title" class="step-card">
          <div class="step-top">
            <span class="step-num">{{ pad(index + 1) }}</span>
            <span class="step-icon-wrap">
              <img :src="step.icon" alt="" aria-hidden="true" class="step-icon" />
            </span>
          </div>
          <h3>{{ step.title }}</h3>
        </li>
      </ol>
    </section>

    <!-- ===== ПОЧЕМУ ЭТО УДОБНО ===== -->
    <section class="section why">
      <div class="why-aside">
        <p class="section-index section-index--light">02 / Преимущества</p>
        <h2>Почему это удобно</h2>
      </div>

      <ul class="why-list">
        <li v-for="(item, index) in advantages" :key="item" class="why-item">
          <span class="why-num">/{{ pad(index + 1) }}</span>
          <p>{{ item }}</p>
        </li>
      </ul>
    </section>
  </main>
</template>

<style scoped>
.home-page {
  --ink: var(--sl-ink);
  --forest: var(--sl-forest);
  --leaf: var(--sl-leaf);
  --lime: var(--sl-lime);
  --paper: var(--sl-paper);
  --line: var(--sl-line);
  --display: var(--sl-display);

  display: grid;
  gap: 1.25rem;
  padding-bottom: 2rem;
  color: var(--ink);
}

h1,
h2,
h3 {
  margin: 0;
}

/* ===== HERO ===== */
.hero-block {
  display: grid;
}

.hero {
  position: relative;
  min-height: min(76vh, 720px);
  overflow: hidden;
  display: flex;
  align-items: center;
  padding: clamp(1.75rem, 6vw, 5rem);
  padding-bottom: clamp(6rem, 10vw, 8rem);
  background: var(--ink);
}

.hero-bg,
.hero-overlay {
  position: absolute;
  inset: 0;
}

.hero-bg {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scale(1.04);
  animation: hero-zoom 1.6s ease-out both;
}

.hero-overlay {
  background:
    linear-gradient(90deg, rgba(12, 22, 9, 0.9) 0%, rgba(12, 22, 9, 0.62) 48%, rgba(12, 22, 9, 0.2) 100%),
    linear-gradient(0deg, rgba(12, 22, 9, 0.55), transparent 45%);
}

/* уголки-«кадрирование» */
.corner {
  position: absolute;
  z-index: 1;
  width: 26px;
  height: 26px;
  border: 0 solid var(--lime);
  opacity: 0.85;
}

.corner--tl { top: 1.25rem; left: 1.25rem; border-top-width: 2px; border-left-width: 2px; }
.corner--tr { top: 1.25rem; right: 1.25rem; border-top-width: 2px; border-right-width: 2px; }
.corner--bl { bottom: 1.25rem; left: 1.25rem; border-bottom-width: 2px; border-left-width: 2px; }
.corner--br { bottom: 1.25rem; right: 1.25rem; border-bottom-width: 2px; border-right-width: 2px; }

.hero-copy {
  position: relative;
  z-index: 1;
  max-width: 780px;
  color: #fff;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  margin: 0 0 1.5rem;
  padding: 0.4rem 0.8rem;
  border: 1px solid rgba(198, 236, 154, 0.45);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--lime);
  animation: rise 0.7s ease-out both;
}

.eyebrow-mark {
  width: 8px;
  height: 8px;
  background: var(--lime);
}

.hero-copy h1 {
  font-family: var(--display);
  font-weight: 600;
  font-size: clamp(2rem, 4.8vw, 3.75rem);
  line-height: 1.12;
  letter-spacing: -0.01em;
  animation: rise 0.8s 0.1s ease-out both;
}

.hero-copy em {
  font-style: normal;
  color: var(--lime);
  background: linear-gradient(var(--lime), var(--lime)) left 92% / 100% 3px no-repeat;
}

.hero-side {
  position: absolute;
  z-index: 1;
  right: 2.25rem;
  top: 50%;
  margin: 0;
  transform: translateY(-50%) rotate(180deg);
  writing-mode: vertical-rl;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.32em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.6);
}

/* ===== ПЛАШКА ДЕЙСТВИЙ ===== */
.action-bar {
  position: relative;
  z-index: 2;
  margin: -3.5rem clamp(1rem, 5vw, 4rem) 0;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 1.5rem;
  padding: 1rem 1rem 1rem 1.5rem;
  background: #fff;
  border: 1px solid var(--line);
  border-left: 4px solid var(--leaf);
  box-shadow: 0 24px 48px rgba(20, 33, 15, 0.18);
  animation: rise 0.8s 0.25s ease-out both;
}

.action-bar__label {
  margin: 0;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--leaf);
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

/* ===== КНОПКИ ===== */
.primary-btn,
.secondary-btn {
  border-radius: 0;
  padding: 0.95rem 1.5rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.primary-btn {
  background: var(--ink);
  color: #fff;
  border: 1px solid var(--ink);
}

.primary-btn:hover {
  background: var(--leaf);
  border-color: var(--leaf);
}

.secondary-btn {
  background: transparent;
  color: var(--ink);
  border: 1px solid var(--ink);
}

.secondary-btn:hover {
  background: var(--lime);
  border-color: var(--lime);
}

.catalog-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.95rem 0.5rem;
  background: none;
  border: none;
  border-bottom: 1px solid transparent;
  font-weight: 700;
  color: var(--ink);
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.catalog-link .arrow {
  transition: transform 0.2s ease;
}

.catalog-link:hover {
  border-bottom-color: var(--ink);
}

.catalog-link:hover .arrow {
  transform: translateX(4px);
}

.primary-btn:focus-visible,
.secondary-btn:focus-visible,
.catalog-link:focus-visible {
  outline: 2px solid var(--leaf);
  outline-offset: 3px;
}

/* ===== СЕКЦИИ ===== */
.section {
  background: var(--paper);
  border: 1px solid var(--line);
  padding: clamp(1.5rem, 4vw, 3.5rem);
}

.section-head {
  display: grid;
  grid-template-columns: 1fr minmax(0, 420px);
  align-items: end;
  gap: 1.5rem 3rem;
  padding-bottom: 2rem;
  margin-bottom: 2.5rem;
  border-bottom: 1px solid var(--line);
}

.section-index {
  margin: 0 0 0.9rem;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--leaf);
}

.section-index--light {
  color: var(--lime);
}

.section h2 {
  font-family: var(--display);
  font-weight: 600;
  font-size: clamp(1.6rem, 3.2vw, 2.5rem);
  line-height: 1.15;
}

.section-lead {
  margin: 0;
  color: #4f5f48;
}

/* ===== ШАГИ ===== */
.steps-grid {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  background: var(--line);
  border: 1px solid var(--line);
}

.step-card {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 2.5rem;
  min-height: 250px;
  padding: 2rem 1.75rem;
  background: #fff;
  transition: background 0.25s ease;
}

.step-card::before {
  content: '';
  position: absolute;
  top: -1px;
  left: 0;
  width: 0;
  height: 3px;
  background: var(--lime);
  transition: width 0.35s ease;
}

.step-card:hover {
  background: var(--ink);
}

.step-card:hover::before {
  width: 100%;
}

.step-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.step-num {
  font-family: var(--display);
  font-size: 3rem;
  font-weight: 700;
  line-height: 1;
  color: transparent;
  -webkit-text-stroke: 1px var(--leaf);
  transition: -webkit-text-stroke-color 0.25s ease;
}

.step-card:hover .step-num {
  -webkit-text-stroke-color: var(--lime);
}

.step-icon-wrap {
  width: 56px;
  height: 56px;
  display: grid;
  place-items: center;
  background: var(--paper);
  border: 1px solid var(--line);
}

.step-icon {
  width: 30px;
  height: 30px;
  object-fit: contain;
}

.step-card h3 {
  max-width: 24ch;
  font-size: 1.15rem;
  font-weight: 700;
  line-height: 1.35;
  color: var(--ink);
  transition: color 0.25s ease;
}

.step-card:hover h3 {
  color: #fff;
}

/* ===== ПОЧЕМУ ЭТО УДОБНО ===== */
.why {
  display: grid;
  grid-template-columns: minmax(0, 5fr) minmax(0, 7fr);
  padding: 0;
}

.why-aside {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0;
  padding: clamp(1.5rem, 4vw, 3.5rem);
  color: #fff;
  background:
    repeating-linear-gradient(135deg, rgba(198, 236, 154, 0.05) 0 1px, transparent 1px 14px),
    var(--forest);
}

.why-aside h2 {
  color: #fff;
}

.why-list {
  list-style: none;
  margin: 0;
  padding: clamp(1rem, 3vw, 2.5rem) clamp(1.5rem, 4vw, 3.5rem);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.why-item {
  display: grid;
  grid-template-columns: 3.5rem 1fr;
  align-items: baseline;
  gap: 1rem;
  padding: 1.5rem 0;
  border-bottom: 1px solid var(--line);
  transition: padding-left 0.25s ease;
}

.why-item:last-child {
  border-bottom: none;
}

.why-item:hover {
  padding-left: 0.5rem;
}

.why-num {
  font-family: var(--display);
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--leaf);
}

.why-item p {
  margin: 0;
  font-size: 1.08rem;
  font-weight: 600;
  line-height: 1.45;
}

/* ===== АНИМАЦИИ ===== */
@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

@keyframes hero-zoom {
  from {
    transform: scale(1.12);
  }
  to {
    transform: scale(1.04);
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero-bg,
  .eyebrow,
  .hero-copy h1,
  .action-bar {
    animation: none;
  }
}

/* ===== АДАПТИВ ===== */
@media (max-width: 900px) {
  .hero {
    min-height: 62vh;
  }

  .hero-side {
    display: none;
  }

  .action-bar {
    grid-template-columns: 1fr;
    gap: 1rem;
    margin-top: -2.5rem;
  }

  .catalog-link {
    justify-self: start;
    padding-inline: 0;
  }

  .section-head {
    grid-template-columns: 1fr;
  }

  .steps-grid {
    grid-template-columns: 1fr;
  }

  .step-card {
    min-height: 0;
    gap: 1.5rem;
  }

  .why {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 520px) {
  .action-bar {
    margin-inline: 0.75rem;
  }

  .hero-actions > button {
    flex: 1 1 100%;
  }
}
</style>
