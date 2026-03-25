<script setup lang="ts">
defineProps<{
  variant?: 'primary' | 'outline'
  type?: 'button' | 'submit'
  href?: string
  to?: string
}>()
</script>

<template>
  <component
    :is="href ? 'a' : to ? 'router-link' : 'button'"
    :href="href"
    :to="to"
    :type="!href && !to ? (type ?? 'button') : undefined"
    class="btn"
    :class="[variant === 'primary' ? 'btn--primary' : 'btn--outline']"
  >
    <slot />
  </component>
</template>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 0.5rem;
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.2s, border-color 0.2s, color 0.2s;
  white-space: nowrap;
}

.btn--outline {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.5);
  color: #fff;
}

.btn--outline:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.8);
}

.btn--primary {
  background: #fff;
  border: none;
  color: #2d5a3a;
}

.btn--primary:hover {
  background: #f0f0f0;
}
</style>
