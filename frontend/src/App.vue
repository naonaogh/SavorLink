<script setup lang="ts">
import CommonFooter from '@/components/CommonFooter.vue'
import CommonNavbar from '@/components/CommonNavbar.vue'
</script>

<template>
  <div class="app-shell">
    <CommonNavbar />

    <main class="app-main">
      <router-view />
    </main>

    <CommonFooter />
  </div>
</template>

<style>
:root {
  --sl-green-1: #bfe59e;
  --sl-green-2: #a5db74;
  --sl-green-3: #6f9f43;
  --sl-green-4: #3f5f2a;
  --sl-green-soft: #e8f5da;
  --sl-surface: rgba(255, 255, 255, 0.75);
  --sl-surface-strong: rgba(255, 255, 255, 0.9);
  --sl-border: rgba(63, 95, 42, 0.14);
  --sl-text: #1f2f1a;
  --sl-muted: #5c6f57;
  --sl-shadow: 0 20px 50px rgba(40, 80, 20, 0.12);

  /* строгий стиль: главная, шапка, подвал */
  --sl-ink: #14210f;
  --sl-forest: #1f3a17;
  --sl-leaf: #5e8f35;
  --sl-lime: #c6ec9a;
  --sl-paper: #f7f9f2;
  --sl-line: rgba(20, 33, 15, 0.14);
  --sl-display: 'Unbounded', 'Manrope', 'Segoe UI', sans-serif;
}

html,
body,
#app {
  min-height: 100%;
}

html {
  background: linear-gradient(135deg, var(--sl-green-1), var(--sl-green-2));
}

body {
  margin: 0;
  font-family: 'Manrope', 'Segoe UI', system-ui, sans-serif;
  color: var(--sl-text);
  line-height: 1.5;
  background:
    radial-gradient(circle at 15% 20%, rgba(255, 255, 255, 0.35), transparent 35%),
    radial-gradient(circle at 85% 10%, rgba(255, 255, 255, 0.2), transparent 30%),
    radial-gradient(circle at 20% 90%, rgba(111, 159, 67, 0.2), transparent 40%),
    linear-gradient(135deg, var(--sl-green-1), var(--sl-green-2));
  background-attachment: fixed;
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
}

* {
  box-sizing: border-box;
}

button,
input,
select,
textarea {
  font: inherit;
}

a {
  color: inherit;
  text-decoration: none;
}

img {
  max-width: 100%;
  display: block;
}

.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-main {
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 1rem 0;
}

h1,
h2 {
  font-family: var(--sl-display);
  font-weight: 600;
  letter-spacing: -0.01em;
  line-height: 1.2;
}

::selection {
  background: var(--sl-lime);
  color: var(--sl-ink);
}

.glass-card,
.surface-panel {
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-radius: 0;
}

.soft-button {
  border: 1px solid var(--sl-ink);
  border-radius: 0;
  padding: 0.7rem 1.3rem;
  background: var(--sl-ink);
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.soft-button:hover {
  background: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

.page-title,
.screen-title,
.section-title,
.hero-headline {
  color: var(--sl-ink);
}

.text-muted {
  color: var(--sl-muted);
}

input,
select,
textarea,
.search-input,
.field-input {
  background: #fff;
  border: 1px solid var(--sl-line);
  border-radius: 0;
  padding: 0.7rem 0.9rem;
  color: var(--sl-text);
}

input:focus-visible,
select:focus-visible,
textarea:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: -1px;
}

input[type='checkbox'],
input[type='radio'] {
  padding: 0;
  accent-color: var(--sl-ink);
}

.card {
  background: #fff;
  border: 1px solid var(--sl-line);
  border-radius: 0;
  padding: 1rem;
}

@media (max-width: 768px) {
  .app-main {
    padding-inline: 0.75rem;
  }
}
</style>
