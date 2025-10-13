<template>
  <div class="notify-page">
    <div class="brand-logo">NudgeeQ</div>
    
    <button class="exit-btn" @click="goBack">
      ✕
    </button>
    
    <h1 class="page-title">{{ targetUser?.nickname || 'User ' + targetUser?.user_id }}</h1>
    <p class="page-location">Table {{ targetUser?.table_number }}, Seat {{ targetUser?.seat_number }}</p>
    
    <div class="main-content">
      <div class="left-panel">
        <div class="target-info">
          <div class="signal-bubble top">
            {{ getTargetSignal(0) || 'Here if you need anytime' }}
          </div>
          
          <div class="avatar-display">
            <img 
              :src="getTargetAvatar()" 
              alt="target avatar"
              class="target-avatar"
            />
          </div>
          
          <div class="signal-bubble bottom">
            {{ getTargetSignal(1) || 'I have Lighting cable' }}
          </div>
        </div>
      </div>
      
      <div class="right-panel">
        <h2 class="panel-title">Click and send short message</h2>
        
        <button 
          class="quick-message-btn"
          @click="sendMessage(templates[0])"
        >
          {{ templates[0] }}
        </button>
        
        <button 
          class="quick-message-btn"
          @click="sendMessage(templates[1])"
        >
          {{ templates[1] }}
        </button>
        
        <div class="custom-message-box">
          <textarea 
            v-model="customMessage"
            placeholder="Edit by yourself and send..."
            class="message-textarea"
          ></textarea>
          <button class="send-inline-btn" @click="sendMessage(customMessage)">
            Send
          </button>
        </div>
      </div>
    </div>
    
    <NotifyPrompt 
      v-if="showPrompt"
      :message="receivedMessage"
      @close="closePrompt"
      @reply="handleReply"
    />
    
    <NotifyReply 
      v-if="showReply"
      :reply-data="replyData"
      @close="closeReply"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { store } from '../store';
import { api } from '../api';
import { useWebSocket } from '../composables/useWebSocket';
import NotifyPrompt from '../components/NotifyPrompt.vue';
import NotifyReply from '../components/NotifyReply.vue';

const router = useRouter();
const route = useRoute();

const targetTable = ref(null);
const targetUser = ref(null);
const customMessage = ref('');

const templates = [
  'Hi, Can I borrow your cable?',
  'Hi, Could you please keep Quiet?'
];

const showPrompt = ref(false);
const receivedMessage = ref(null);

const showReply = ref(false);
const replyData = ref(null);

const ws = useWebSocket(store.user?.id);

const getTargetAvatar = () => {
  if (targetUser.value) {
    return `/avatars/${targetUser.value.avatar_color || 'colorful'}-${targetUser.value.avatar_status || 'smile'}.png`;
  }
  return '/avatars/colorful-smile.png';
};

const getTargetSignal = (index) => {
  if (targetUser.value && targetUser.value.signals && targetUser.value.signals[index]) {
    return targetUser.value.signals[index].text;
  }
  return '';
};

onMounted(async () => {
  try {
    if (!store.user || !store.user.id) {
      console.error('No user found, redirecting to welcome');
      router.push('/');
      return;
    }
    
    if (!store.currentTable || !store.currentTable.id) {
      console.error('No current table found, redirecting to welcome');
      router.push('/');
      return;
    }
    
    const tableId = parseInt(route.params.tableId);
    const userId = parseInt(route.params.userId);
    
    // Get table details
    targetTable.value = await api.tables.get(tableId);
    
    if (!targetTable.value) {
      alert('Target table not found');
      router.push('/nearby');
      return;
    }
    
    // Find the target user in the table
    targetUser.value = targetTable.value.members.find(m => m.user_id === userId);
    
    if (!targetUser.value) {
      alert('Target user not found');
      router.push('/nearby');
      return;
    }
    
    if (ws) {
      ws.connect();
      ws.on('message_received', (data) => {
        receivedMessage.value = data;
        showPrompt.value = true;
      });
      ws.on('message_reply', (data) => {
        replyData.value = data;
        showReply.value = true;
      });
    }
  } catch (error) {
    console.error('Failed to load data:', error);
  }
});

const sendMessage = async (content) => {
  if (!content || !content.trim()) {
    alert('Please enter a message');
    return;
  }
  
  if (!store.currentTable || !store.currentTable.id) {
    alert('No current table found');
    router.push('/');
    return;
  }
  
  if (!targetUser.value) {
    alert('Target user not found');
    return;
  }
  
  try {
    await api.messages.send(
      store.currentTable.id,
      targetTable.value.id,
      content,
      targetUser.value.user_id  // Send to specific user
    );
    
    customMessage.value = '';
    alert('Message sent!');
  } catch (error) {
    console.error('Failed to send message:', error);
    alert('Failed to send message. Please try again.');
  }
};

const goBack = () => {
  router.back();
};

const closePrompt = () => {
  showPrompt.value = false;
  receivedMessage.value = null;
};

const handleReply = async (messageId, reply) => {
  try {
    await api.messages.reply(messageId, reply, store.user.id);
    closePrompt();
  } catch (error) {
    console.error('Failed to reply:', error);
  }
};

const closeReply = () => {
  showReply.value = false;
  replyData.value = null;
};
</script>

<style scoped>
.notify-page {
  position: relative;
  min-height: 100vh;
  background: linear-gradient(180deg, #b794f6 0%, #9f7aea 30%, #805ad5 60%, #2d1b47 100%);
  overflow: hidden;
  padding: 2rem;
}

.brand-logo {
  position: absolute;
  top: 2.5rem;
  left: 3rem;
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
  letter-spacing: -0.01em;
  z-index: 10;
}

.exit-btn {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  z-index: 100;
}

.exit-btn:hover {
  background: rgba(255, 255, 255, 0.35);
  transform: scale(1.1);
}

.page-title {
  position: absolute;
  top: 8rem;
  left: 50%;
  transform: translateX(-50%);
  font-size: 2.5rem;
  font-weight: 600;
  color: white;
  margin: 0;
  letter-spacing: 0.02em;
  z-index: 10;
}

.page-location {
  position: absolute;
  top: 11rem;
  left: 50%;
  transform: translateX(-50%);
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  z-index: 10;
}

.main-content {
  display: flex;
  gap: 3rem;
  margin-top: 180px;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 250px);
}

.left-panel {
  flex: 1;
  max-width: 400px;
  display: flex;
  justify-content: center;
}

.target-info {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.avatar-display {
  width: 200px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.target-avatar {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid rgba(0, 0, 0, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.signal-bubble {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  padding: 1rem 1.5rem;
  border-radius: 18px;
  font-weight: 500;
  color: #333;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  font-size: 1rem;
  max-width: 280px;
  text-align: center;
}

.signal-bubble.top {
  position: relative;
}

.signal-bubble.bottom {
  position: relative;
}

.right-panel {
  flex: 1;
  max-width: 500px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 25px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.panel-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 1.5rem 0;
}

.quick-message-btn {
  width: 100%;
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.95);
  border: none;
  border-radius: 15px;
  font-size: 1rem;
  font-weight: 500;
  color: #333;
  cursor: pointer;
  text-align: left;
  margin-bottom: 1rem;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.quick-message-btn:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.custom-message-box {
  position: relative;
  margin-top: 1.5rem;
  background: rgba(255, 255, 255, 0.95);
  border: 3px solid #2563eb;
  border-radius: 20px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message-textarea {
  width: 100%;
  border: none;
  background: transparent;
  font-family: inherit;
  font-size: 1rem;
  color: #666;
  resize: none;
  min-height: 100px;
  outline: none;
  padding: 0.5rem;
}

.message-textarea::placeholder {
  color: #999;
}

.send-inline-btn {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  background: transparent;
  border: none;
  color: #666;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  padding: 0.5rem 1rem;
  transition: all 0.2s;
}

.send-inline-btn:hover {
  color: #2563eb;
  transform: scale(1.05);
}
</style>
