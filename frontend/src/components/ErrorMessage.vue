<template>
  <div v-if="message" class="error-message">
    <span class="error-icon">⚠️</span>
    <span class="error-text">{{ message }}</span>
    <button v-if="onRetry" class="retry-btn" @click="onRetry">
      Retry
    </button>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';

defineProps({
  message: {
    type: String,
    required: true
  },
  onRetry: {
    type: Function,
    default: null
  }
});
</script>

<style scoped>
.error-message {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 1rem 1.5rem;
  background: #fee;
  border: 2px solid #e74c3c;
  border-radius: 10px;
  margin: 1rem 0;
}

.error-icon {
  font-size: 1.5rem;
}

.error-text {
  flex: 1;
  color: #c0392b;
  font-weight: 500;
}

.retry-btn {
  padding: 0.5rem 1rem;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #c0392b;
}
</style>

