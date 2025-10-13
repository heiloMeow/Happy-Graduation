<template>
  <div class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <h2 class="modal-title">From Table {{ replyData?.from_table_number }}</h2>
      
      <p class="reply-message">
        <span v-if="replyData?.reply === 'SURE'" class="reply-sure">
          Come On! You can grab now
        </span>
        <span v-else-if="replyData?.reply === 'SORRY'" class="reply-sorry">
          Sorry, not available right now
        </span>
        <span v-else class="reply-ignore">
          No response
        </span>
      </p>
      
      <button class="done-btn" @click="close">
        Done
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  replyData: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close']);

const close = () => {
  emit('close');
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: #f5f3ff;
  padding: 4rem 3rem 3rem;
  border-radius: 35px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 90%;
  text-align: center;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-title {
  font-size: 2.5rem;
  font-weight: 600;
  color: #9f7aea;
  margin-bottom: 3rem;
  letter-spacing: 0.01em;
}

.reply-message {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 3rem;
  color: #1a1a1a;
}

.reply-sure {
  color: #1a1a1a;
}

.reply-sorry {
  color: #1a1a1a;
}

.reply-ignore {
  color: #64748b;
}

.done-btn {
  padding: 1rem 3rem;
  background: rgba(255, 255, 255, 0.7);
  color: #1a1a1a;
  border: none;
  border-radius: 20px;
  font-size: 1.2rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-width: 150px;
}

.done-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  background: rgba(255, 255, 255, 0.9);
}

.done-btn:active {
  transform: translateY(0);
}
</style>

