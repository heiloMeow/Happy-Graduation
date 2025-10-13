<template>
  <div class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <h2 class="modal-title">From Table {{ message?.from_table_number }}</h2>
      
      <p class="message-text">{{ message?.content }}</p>
      
      <div class="action-buttons">
        <button class="reply-btn sorry" @click="reply('SORRY')">
          SORRY
        </button>
        <button class="reply-btn ignore" @click="reply('IGNORE')">
          IGNORE
        </button>
        <button class="reply-btn sure" @click="reply('SURE')">
          SURE
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  message: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close', 'reply']);

const close = () => {
  emit('close');
};

const reply = (replyType) => {
  emit('reply', props.message.id, replyType);
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

.message-text {
  font-size: 2rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 3rem;
  line-height: 1.5;
  padding: 0 1rem;
}

.action-buttons {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  flex-wrap: wrap;
}

.reply-btn {
  padding: 1rem 2.5rem;
  border: none;
  border-radius: 20px;
  font-size: 1.2rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  color: #1a1a1a;
  background: rgba(255, 255, 255, 0.7);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-width: 120px;
}

.reply-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  background: rgba(255, 255, 255, 0.9);
}

.reply-btn:active {
  transform: translateY(0);
}

.sorry,
.ignore,
.sure {
  background: rgba(255, 255, 255, 0.7);
}
</style>

