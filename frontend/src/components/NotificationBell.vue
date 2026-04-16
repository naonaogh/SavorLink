
<script setup lang="ts">
defineProps<{
  count: number;
}>();
</script>

<template>
  <div class="bell-container" :class="{ 'has-unread': count > 0 }">
    <div class="bell-icon">🔔</div>
    <div v-if="count > 0" class="badge">
      {{ count > 9 ? '9+' : count }}
    </div>
  </div>
</template>

<style scoped>
.bell-container {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: white;
  border-radius: 50%;
  border: 1px solid #e5e7eb;
  font-size: 1.25rem;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  cursor: pointer;
}

.bell-container:hover {
  transform: scale(1.1) rotate(15deg);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.has-unread .bell-icon {
  animation: ring 2s infinite ease-in-out;
}

.badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #ef4444;
  color: white;
  font-size: 0.65rem;
  font-weight: 800;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
}

@keyframes ring {
  0% { transform: rotate(0); }
  5% { transform: rotate(20deg); }
  10% { transform: rotate(-18deg); }
  15% { transform: rotate(14deg); }
  20% { transform: rotate(-10deg); }
  25% { transform: rotate(6deg); }
  30% { transform: rotate(-4deg); }
  35% { transform: rotate(2deg); }
  40% { transform: rotate(0); }
  100% { transform: rotate(0); }
}
</style>
