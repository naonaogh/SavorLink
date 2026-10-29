<script setup lang="ts">
import CommonFooter from '@/components/CommonFooter.vue'
import CommonNavbar from '@/components/CommonNavbar.vue'
import ConfirmHost from '@/components/ui/ConfirmHost.vue'
import ToastHost from '@/components/ui/ToastHost.vue'
</script>

<template>
  <div class="app-shell">
    <a href="#main-content" class="skip-link">Перейти к содержимому</a>
    <CommonNavbar />

    <main id="main-content" class="app-main ui-container" tabindex="-1">
      <router-view />
    </main>

    <CommonFooter />
    <ToastHost />
    <ConfirmHost />
  </div>
</template>

<style>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-main {
  flex: 1;
  padding-top: clamp(1.25rem, 3vw, 2rem);
  padding-bottom: clamp(2.5rem, 5vw, 4rem);
  outline: none;
}

.skip-link {
  position: absolute;
  top: -100px;
  left: 1rem;
  z-index: 2000;
  padding: 0.6rem 1rem;
  border-radius: var(--r-sm);
  background: var(--c-brand-800);
  color: #fff;
  font-weight: 700;
}

.skip-link:focus {
  top: 0.75rem;
}
</style>
