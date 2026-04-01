<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import BasketIcon from '@/assets/icons/basket.svg'
import TruckIcon from '@/assets/icons/grusovik.svg'
import DocsIcon from '@/assets/icons/docs.svg'
import QuestionIcon from '@/assets/icons/questionn.svg'

const router = useRouter()

const steps = [
  { title: 'Заказываете нужные товары в каталоге', icon: 'cart' },
  { title: 'Поставщик подтверждает и привозит', icon: 'truck' },
  { title: 'Система генерирует все документы', icon: 'doc' },
]
const features = [
  {
    bold: 'Работа по официальным документам',
    regular: ' (счёт-фактура, договор, акт)',
  },
  {
    bold: 'Поддержка полного цикла',
    regular: ' — от заказа до оплаты и отчёта',
  },
  {
    bold: 'Проверенные партнёры и защита обеих сторон сделки.',
    regular: '',
  },
]

const goRegisterBuyer = () => {
  router.push({ name: 'Register', query: { role: 'buyer' } })
}

const goRegisterSupplier = () => {
  router.push({ name: 'Register', query: { role: 'supplier' } })
}

const goLogin = () => {
  router.push({ name: 'Login' })
}
</script>
<template>
  <div class="home">
    <!-- Шапка — скрин 1 -->
    <header class="header">
      <nav class="nav">
        <a href="/" class="header-logo">Logo</a>
        <div class="nav-links">
          <router-link to="/" class="nav-link">Главная</router-link>
          <router-link to="/catalog" class="nav-link">Каталог</router-link>
          <router-link to="/profile" class="nav-link">Профиль</router-link>
          <router-link to="/features" class="nav-link">Возможности</router-link>
          <router-link to="/reviews" class="nav-link">Отзывы</router-link>
          <span class="nav-sep" aria-hidden="true">|</span>
          <router-link to="/register" class="nav-link">Регистрация</router-link>
          <button type="button" class="btn-login" @click="goLogin">Вход</button>
        </div>
      </nav>
    </header>
    <!-- Первый экран: hero слева + панель «О нас» справа -->
    <section class="screen screen-1">
      <div class="hero-col">
        <span class="deco deco-triangle" aria-hidden="true" />
        <span class="deco deco-rings" aria-hidden="true" />
        <h1 class="hero-headline">
          ПОСТАВЩИКИ И<br>РЕСТОРАНЫ НАХОДЯТ<br>ДРУГ ДРУГА ЗА<br>СЧИТАННЫЕ МИНУТЫ
        </h1>
        <p class="hero-sub">Без посредников и переплат</p>
        <div class="hero-cta">
          <button type="button" class="btn-buyer" @click="goRegisterBuyer">Покупатель</button>
          <button type="button" class="btn-supplier" @click="goRegisterSupplier">
            Поставщик
          </button>
        </div>
      </div>
      <!-- Панель справа — всегда видна, без крестика, фон чёрный полупрозрачный -->
      <div class="about-panel">
        <h2 class="about-panel-title">savorlink</h2>
        <p class="about-panel-text">
          SavorLink – экосистема, где рестораны каждый день получают самые свежие продукты по прямым ценам, а поставщики получают новых клиентов. Никаких посредников, звонков и ожидания — только проверенные поставщики и ваш привычный ритм кухни.
        </p>
      </div>
    </section>
    <!-- Второй экран: Как это работает -->
    <section class="screen screen-2">
      <span class="deco deco-triangle-tl" aria-hidden="true" />
      <span class="deco deco-triangle-tr" aria-hidden="true" />
      <span class="deco deco-circles-bl" aria-hidden="true" />
      <h2 class="screen-title">Как это работает</h2>
      <div class="steps-row">
        <div v-for="(step, i) in steps" :key="step.icon" class="step-cell">
          <div class="step-icon-wrap">
            <span v-if="i > 0" class="connector-line connector-line--left" aria-hidden="true">
              <span class="connector-line__dot" />
            </span>
            <div class="step-icon" :class="`step-icon--${step.icon}`">
              <template v-if="step.icon === 'cart'">
                <img :src="BasketIcon" alt="" class="step-svg" aria-hidden="true" />
              </template>
              <template v-else-if="step.icon === 'truck'">
                <img :src="TruckIcon" alt="" class="step-svg" aria-hidden="true" />
              </template>
              <template v-else>
                <img :src="DocsIcon" alt="" class="step-svg" aria-hidden="true" />
              </template>
            </div>
            <span v-if="i < steps.length - 1" class="connector-line connector-line--right" aria-hidden="true">
              <span class="connector-line__dot" />
            </span>
          </div>
          <p class="step-text">{{ step.title }}</p>
        </div>
      </div>
    </section>
    <!-- Третий экран: Почему стоит выбрать нас -->
    <section class="screen screen-3">
      <span class="deco deco-triangles-tl" aria-hidden="true" />
      <span class="deco deco-x-br" aria-hidden="true">×</span>
      <h2 class="screen-title">Почему стоит выбрать нас</h2>
      <div class="why-content">
        <div class="why-left">
          <p class="why-intro">
            Пользователям будут доступны сравнение цен и условий от нескольких поставщиков в
            реальном времени, верификацию качества через отзывы и сертификаты
          </p>
          <div class="why-icon-q">
            <img :src="QuestionIcon" alt="" class="q-icon" aria-hidden="true" />
          </div>
        </div>
        <ul class="why-list">
          <li v-for="(f, i) in features" :key="i" class="why-item">
            <span class="why-item-mark" aria-hidden="true">✦</span>
            <span class="why-item-text">
              <strong>{{ f.bold }}</strong>{{ f.regular }}
            </span>
          </li>
        </ul>
      </div>
    </section>
    <!-- Подвал — без изменений -->
    <footer class="footer">
      <div class="footer-inner">
        <div class="footer-col footer-col--logo">
          <div class="logo">
            <span class="logo-icon">OO</span>
            <span class="logo-text">SavorLink</span>
          </div>
          <p class="footer-contact">+1 (7635) 547-12-97</p>
          <p class="footer-contact">info@qr.agency</p>
          <div class="footer-social">
            <a href="#" class="footer-social-link" aria-label="LinkedIn">in</a>
            <a href="#" class="footer-social-link" aria-label="Facebook">fb</a>
            <a href="#" class="footer-social-link" aria-label="Twitter">tw</a>
          </div>
        </div>
        <div class="footer-col">
          <h4 class="footer-heading">Quick Links</h4>
          <a href="#" class="footer-link">Product</a>
          <a href="#" class="footer-link">Information</a>
        </div>
        <div class="footer-col">
          <h4 class="footer-heading">Company</h4>
          <a href="#" class="footer-link">SavorLink</a>
          <a href="#" class="footer-link">QR Media</a>
        </div>
      </div>
      <div class="footer-bottom">
        <span>A product of</span>
        <span>© 2020 QR Media. All rights reserved</span>
      </div>
    </footer>
  </div>
</template>
<style scoped>
/* Один шрифт для всех текстов */
.home {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    sans-serif;
  color: #2c2c2c;
  min-height: 100vh;
  background: #3f4a2f;
}
.home {
  --screen1-panel: #f5efdf;
  --text-dark: #2e2a23;
  --text-muted: #6d6254;
  --nav-link: #e8dcc7;
  --green-bright: #a97c50;
  --olive: #3f4a2f;
  --sand: #ebe2ce;
  --card: #f2e4c8;
}
/* ========== Шапка (скрин 1) ========== */
.header {
  background: linear-gradient(120deg, #2c3521 0%, #333e25 55%, #3a452b 100%);
  padding: 0.875rem 1.5rem;
  position: sticky;
  top: 0;
  z-index: 20;
  border-bottom: 1px solid rgba(232, 220, 199, 0.28);
}
.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  max-width: 1200px;
  margin: 0 auto;
  flex-wrap: wrap;
}
.header-logo {
  font-size: 1rem;
  font-weight: 700;
  color: #f3e8d6;
  text-decoration: none;
}
.nav-links {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}
.nav-link {
  color: var(--nav-link);
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 400;
}
.nav-link:hover {
  color: #fff;
}
.nav-sep {
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.9rem;
}
.btn-login {
  padding: 0.5rem 1.25rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: #2d261f;
  background: #d8bf98;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-family: inherit;
}
.btn-login:hover {
  background: #e4ceab;
}
/* ========== Первый экран: две колонки ========== */
.screen-1 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 85vh;
  background: linear-gradient(180deg, #3f4a2f 0%, #465335 100%);
  position: relative;
}
.hero-col {
  padding: 3rem 2rem 3rem 4.5rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
}
.deco {
  position: absolute;
  pointer-events: none;
}
.deco-triangle {
  left: 1.5rem;
  top: 2rem;
  width: 0;
  height: 0;
  border-left: 40px solid transparent;
  border-right: 40px solid transparent;
  border-bottom: 70px solid rgba(255, 255, 255, 0.25);
}
.deco-rings {
  right: 2rem;
  bottom: 3rem;
  width: 60px;
  height: 60px;
  border: 2px solid rgba(255, 255, 255, 0.25);
  border-radius: 50%;
}
.deco-rings::after {
  content: '';
  position: absolute;
  left: 8px;
  top: 8px;
  right: 8px;
  bottom: 8px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
}
.hero-headline {
  font-size: 2.35rem; /* основной размер — как на скрине, не огромный */
  font-weight: 900;
  color: #f7efdf;
  line-height: 1.05; /* плотные строки, почти вплотную */
  letter-spacing: -0.015em; /* лёгкое сжатие для выразительности */
  margin: 0 0 1.2rem;
  position: relative;
  z-index: 1;
  text-transform: uppercase;
}
.hero-sub {
  font-size: 1.4rem;
  font-weight: 500;
  color: #e8dcc7;
  margin: 0 0 2.5rem;
  position: relative;
  z-index: 1;
}
.hero-cta {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  position: relative;
  z-index: 1;
}
.btn-buyer {
  padding: 0.8rem 1.8rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: #000;
  background: #fff;
  border: none;
  border-radius: 0.6rem;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.btn-supplier {
  padding: 0;
  font-size: 1.1rem;
  font-weight: 500;
  color: #f3e8d6;
  background: none;
  border: none;
  cursor: pointer;
  text-decoration: underline;
}
.btn-supplier:hover {
  opacity: 0.8;
}
.hero-headline {
  font-size: 2.9rem;
  line-height: 1.02;
}
/* Панель «О нас» справа — крупнее, фон чёрный полупрозрачный */
.about-panel {
  background: rgba(245, 239, 223, 0.12);
  border: 1px solid rgba(233, 214, 181, 0.34);
  margin: 2rem;
  padding: 3.5rem 3rem;
  border-radius: 1.5rem;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
  align-self: center;
  max-width: 520px;
  position: relative;
  z-index: 2;
  backdrop-filter: blur(6px);
  color: #fff;
}
.about-panel-title {
  font-size: 4.2rem;
  font-weight: 900;
  margin: 0 0 1.8rem;
  text-transform: lowercase;
  background: linear-gradient(90deg, #d6ba90 0%, #a97c50 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 0.9;
  letter-spacing: -0.04em;
}
.about-panel-text {
  font-size: 1.35rem;
  line-height: 1.7;
  color: #e0e0e0;
  font-weight: 400;
}
.about-panel {
  margin: 3rem 3rem 3rem 0;
  padding: 3.5rem 3rem;
}
/* Остальные стили без изменений (вернул как было) */
.screen-2 {
  background: linear-gradient(180deg, #ebe2ce 0%, #e1d3b7 50%, #dbcba9 100%);
  min-height: 25vh;
  padding: 5rem 2rem 6rem;
  position: relative;
  overflow: hidden;
}
.deco-triangle-tl {
  left: 1.5rem;
  top: 2rem;
  width: 0;
  height: 0;
  border-left: 30px solid transparent;
  border-right: 30px solid transparent;
  border-bottom: 52px solid rgba(255, 255, 255, 0.3);
}
.deco-triangle-tr {
  right: 2rem;
  top: 2rem;
  width: 0;
  height: 0;
  border-left: 24px solid transparent;
  border-right: 24px solid transparent;
  border-bottom: 42px solid rgba(255, 255, 255, 0.25);
}
.deco-circles-bl {
  left: 2rem;
  bottom: 3rem;
  width: 50px;
  height: 50px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
}
.deco-circles-bl::after {
  content: '';
  position: absolute;
  left: 10px;
  top: 10px;
  right: 10px;
  bottom: 10px;
  border: 2px solid rgba(255, 255, 255, 0.25);
  border-radius: 50%;
}
.screen-title {
  font-size: 1.75rem;
  font-weight: 700;
  font-family: 'Trebuchet MS', 'Segoe UI', sans-serif;
  color: var(--text-dark);
  text-align: center;
  margin: 0 0 2rem;
  position: relative;
  z-index: 1;
}
.screen-2 .screen-title,
.screen-3 .screen-title {
  font-size: 2.05rem;
  margin: 0 0 4rem;
  text-align: center;
}
.screen-2 .steps-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2.5rem;
  max-width: 1100px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}
.step-cell {
  text-align: center;
}
.screen-2 .step-icon-wrap {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
}
.screen-2 .step-icon {
  width: 132px;
  height: 94px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
}
.step-svg {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.connector-line {
  display: none;
  position: absolute;
  top: 50%;
  width: 74px;
  height: 2px;
  background: linear-gradient(90deg, rgba(63, 74, 47, 0.25), #3f4a2f, rgba(63, 74, 47, 0.25));
}
.connector-line__dot {
  position: absolute;
  right: 18px;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #a97c50;
  box-shadow: 0 0 0 6px rgba(169, 124, 80, 0.2);
}
@media (min-width: 640px) {
  .connector-line {
    display: block;
  }
  .connector-line--left {
    left: -52px;
  }
  .connector-line--right {
    right: -52px;
  }
  .connector-line--left .connector-line__dot {
    left: 18px;
    right: auto;
  }
}
.screen-2 .step-text {
  font-size: 1.17rem;
  font-weight: 600;
  font-family: 'Trebuchet MS', 'Segoe UI', sans-serif;
  color: var(--text-dark);
  margin: 0;
  line-height: 1.45;
}
.screen-2 .screen-title,
.screen-3 .screen-title {
  font-size: 2.25rem;
}
.screen-2 .step-text {
  font-size: 1.15rem;
}
.screen-2 .step-icon {
  width: 120px;
  height: 84px;
}
/* ========== Третий экран: Почему стоит выбрать нас (шире) ========== */
.screen-3 {
  background: linear-gradient(180deg, #f0e5cd 0%, #e7d8b7 45%, #e0ccaa 100%);
  padding: 4rem 1.5rem 5rem;
  position: relative;
  overflow: hidden;
}
/* Два перекрывающихся треугольника — верхний левый угол экрана 3 */
.deco-triangles-tl {
  left: 1.5rem;
  top: 2rem;
  width: 0;
  height: 0;
  border-left: 28px solid transparent;
  border-right: 28px solid transparent;
  border-bottom: 48px solid rgba(255, 255, 255, 0.35);
}
.deco-triangles-tl::after {
  content: '';
  position: absolute;
  left: 8px;
  top: 8px;
  width: 0;
  height: 0;
  border-left: 22px solid transparent;
  border-right: 22px solid transparent;
  border-bottom: 38px solid rgba(255, 255, 255, 0.25);
}
.deco-x-br {
  position: absolute;
  right: 1.5rem;
  bottom: 2rem;
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.5);
}
.why-intro {
  font-size: 1.05rem;
  font-weight: 400;
  color: var(--text-muted);
  line-height: 1.6;
  margin: 0 0 2rem;
  max-width: 560px;
  position: relative;
  z-index: 1;
}
.why-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2.5rem;
  max-width: 1280px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}
.why-left {
  position: relative;
}
.why-icon-q {
  margin-top: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.q-icon {
  width: 170px;
  height: 170px;
  object-fit: contain;
  filter: drop-shadow(0 8px 16px rgba(0, 0, 0, 0.3));
}
@media (min-width: 768px) {
  .q-icon {
    width: 160px;
    height: 160px;
  }
}
.why-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.why-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.25rem;
}
.why-item-mark {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  margin-top: -0.05rem;
  border-radius: 0.45rem;
  color: #f8f1e3;
  background: linear-gradient(145deg, #a97c50, #8f693f);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.82rem;
}
.why-item-text {
  font-size: 1rem;
  font-weight: 400;
  color: var(--text-dark);
  line-height: 1.5;
}
.why-item-text strong {
  font-weight: 700;
}
/* ========== Подвал — градиент в той же гамме ========== */
.footer {
  background: linear-gradient(180deg, #364128 0%, #3f4a2f 100%);
  padding: 2rem 1.5rem 1.5rem;
  margin-top: 0;
}
.footer-inner {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}
.footer-col--logo .logo {
  margin-bottom: 1rem;
}
.logo {
  display: inline-flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.15rem;
}
.logo-icon {
  font-size: 1.5rem;
  color: var(--green-bright);
  letter-spacing: -0.2em;
}
.logo-text {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--green-bright);
  letter-spacing: 0.15em;
}
.footer-contact {
  color: #fff;
  font-size: 0.9rem;
  margin: 0 0 0.25rem;
}
.footer-social {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}
.footer-social-link {
  color: #fff;
  text-decoration: none;
  font-size: 0.85rem;
}
.footer-social-link:hover {
  text-decoration: underline;
}
.footer-heading {
  color: #fff;
  font-size: 0.9rem;
  font-weight: 600;
}
.footer-link {
  display: block;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}
.footer-link:hover {
  text-decoration: underline;
}
.footer-bottom {
  max-width: 1200px;
  margin: 2rem auto 0;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.85rem;
}
</style>
