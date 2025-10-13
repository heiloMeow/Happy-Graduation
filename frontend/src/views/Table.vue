<template>
  <div class="table-page">
    <div class="brand-logo">NudgeeQ</div>
    
    <h1 class="table-title">Table {{ table?.number || '...' }}</h1>
    
    <div class="content-wrapper">
      <div class="members-grid">
        <div 
          v-for="member in table?.members || []" 
          :key="member.user_id"
          class="member-container"
        >
          <div class="member-display">
            <div class="member-signals-left">
              <div 
                v-for="signal in member.signals.filter(s => s.position === 'left')" 
                :key="signal.id"
                class="signal-bubble left"
              >
                {{ signal.text }}
              </div>
            </div>
            
            <div class="member-center">
              <img 
                :src="`/avatars/${member.avatar_color || 'colorful'}-${member.avatar_status || 'smile'}.png`" 
                alt="avatar"
                class="member-avatar"
              />
              <p class="member-nickname">{{ member.nickname || 'User ' + member.user_id }}</p>
              <p class="member-location">Table {{ member.table_number }}, Seat {{ member.seat_number }}</p>
            </div>
            
            <div class="member-signals-right">
              <div 
                v-for="signal in member.signals.filter(s => s.position === 'right')" 
                :key="signal.id"
                class="signal-bubble right"
              >
                {{ signal.text }}
              </div>
            </div>
          </div>
          
          <button 
            v-if="member.user_id === store.user?.id"
            class="edit-signal-btn" 
            @click="editSignal"
          >
            Edit Signal
          </button>
          <div v-else class="edit-signal-placeholder">Edit Signal</div>
        </div>
      </div>
      
      <button class="seek-help-btn" @click="seekHelp">
        Seek Help
      </button>
    </div>
    
    <button class="exit-btn" @click="leaveTable">
      ✕
    </button>
    
    <div class="decoration-dots">
      <span class="dot dot-1"></span>
      <span class="dot dot-2"></span>
      <span class="dot dot-3"></span>
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
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { store } from '../store';
import { api } from '../api';
import { useWebSocket } from '../composables/useWebSocket';
import NotifyPrompt from '../components/NotifyPrompt.vue';
import NotifyReply from '../components/NotifyReply.vue';

const router = useRouter();
const route = useRoute();
const table = ref(null);

let ws = null;

const showPrompt = ref(false);
const receivedMessage = ref(null);
const showReply = ref(false);
const replyData = ref(null);

onMounted(async () => {
  try {
    if (!store.user || !store.user.id) {
      console.error('No user found, redirecting to welcome');
      router.push('/');
      return;
    }
    
    // Refresh user data from backend to ensure avatar info is up-to-date
    try {
      const userData = await api.users.get(store.user.id);
      store.setUser(userData);
    } catch (userError) {
      console.error('Failed to refresh user data:', userError);
    }
    
    const tableId = parseInt(route.params.id);
    table.value = await api.tables.getByUser(store.user.id);
    store.setCurrentTable(table.value);
    
    // Initialize WebSocket after we have user info
    ws = useWebSocket(store.user.id);
    if (ws) {
      ws.on('table_update', (data) => {
        console.log('Received table_update:', data);
        table.value = data;
        store.setCurrentTable(data);
      });
      ws.on('message_received', (data) => {
        console.log('Received message:', data);
        receivedMessage.value = data;
        showPrompt.value = true;
      });
      ws.on('message_reply', (data) => {
        console.log('Received reply:', data);
        replyData.value = data;
        showReply.value = true;
      });
      ws.connect();
    }
  } catch (error) {
    console.error('Failed to load table:', error);
  }
});

onUnmounted(() => {
  if (ws) {
    ws.disconnect();
  }
});

const editSignal = () => {
  router.push('/signal');
};

const seekHelp = () => {
  router.push('/nearby');
};

const leaveTable = async () => {
  try {
    await api.tables.leave(store.user.id);
    store.clearAll(); // Clear all user data
    router.push('/');
  } catch (error) {
    console.error('Failed to leave table:', error);
  }
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
.table-page {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
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
}

.table-title {
  position: absolute;
  top: 8rem;
  left: 50%;
  transform: translateX(-50%);
  font-size: 2.5rem;
  font-weight: 600;
  color: white;
  margin: 0;
  letter-spacing: 0.02em;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 6rem;
  max-width: 1200px;
  width: 100%;
}

.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 4rem 6rem;
  width: 100%;
  margin-bottom: 3rem;
  justify-items: center;
}

.member-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.member-display {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2.5rem;
}

.member-signals-left,
.member-signals-right {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  min-width: 150px;
  max-width: 180px;
}

.signal-bubble {
  position: relative;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  padding: 0.75rem 1.2rem;
  border-radius: 18px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  font-weight: 500;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  font-size: 0.85rem;
  word-wrap: break-word;
}

.signal-bubble::before {
  content: '';
  position: absolute;
  width: 0;
  height: 0;
  border-style: solid;
}

.signal-bubble.left::before {
  right: -8px;
  top: 50%;
  transform: translateY(-50%);
  border-width: 8px 0 8px 8px;
  border-color: transparent transparent transparent rgba(255, 255, 255, 0.25);
}

.signal-bubble.right::before {
  left: -8px;
  top: 50%;
  transform: translateY(-50%);
  border-width: 8px 8px 8px 0;
  border-color: transparent rgba(255, 255, 255, 0.25) transparent transparent;
}

.member-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.member-avatar {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  object-fit: cover;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  padding: 15px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.member-nickname {
  font-weight: 600;
  color: white;
  margin: 0 0 0.3rem 0;
  font-size: 1.1rem;
}

.member-location {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.edit-signal-btn {
  padding: 0.6rem 1.5rem;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.4);
  color: white;
  font-size: 0.95rem;
  font-weight: 500;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.edit-signal-btn:hover {
  background: rgba(255, 255, 255, 0.35);
  transform: translateY(-2px);
}

.edit-signal-placeholder {
  padding: 0.6rem 1.5rem;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.95rem;
  font-weight: 500;
  white-space: nowrap;
}

.seek-help-btn {
  margin-top: 2rem;
  padding: 1rem 3.5rem;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.5);
  color: white;
  font-size: 1.15rem;
  font-weight: 600;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.seek-help-btn:hover {
  background: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
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

.decoration-dots {
  position: absolute;
}

.dot {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
}

.dot-1 {
  width: 100px;
  height: 100px;
  top: 20%;
  right: 8%;
}

.dot-2 {
  width: 60px;
  height: 60px;
  top: 35%;
  left: 12%;
}

.dot-3 {
  width: 80px;
  height: 80px;
  bottom: 35%;
  right: 15%;
}
</style>

