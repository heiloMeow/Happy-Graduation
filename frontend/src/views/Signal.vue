<template>
  <div class="signal-page">
    <div class="brand-logo">NudgeeQ</div>
    
    <h1 class="page-title">Step 3</h1>
    <h2 class="page-subtitle">Drag & Show Your Signal</h2>
    
    <button class="exit-btn" @click="saveDone">✕</button>
    
    <div class="signal-canvas">
      <!-- Draggable signal bubbles -->
      <div 
        v-for="signal in activeSignals" 
        :key="signal.id"
        class="signal-bubble"
        :class="signal.style"
        :style="{ 
          left: signal.x + 'px', 
          top: signal.y + 'px',
          transform: `rotate(${signal.rotation || 0}deg)`
        }"
        @mousedown="startDrag(signal, $event)"
        @dblclick="removeSignal(signal)"
      >
        {{ signal.text }}
        <span class="bubble-connector"></span>
      </div>
      
      <!-- Center avatar -->
      <div class="center-avatar">
        <img 
          :src="`/avatars/${avatarColor}-${avatarStatus}.png`" 
          alt="My Avatar"
          @error="handleImageError"
        />
      </div>
    </div>
    
    <!-- Signal options at bottom -->
    <div class="signal-options">
      <div class="signal-column">
        <button 
          v-for="signal in column1" 
          :key="signal"
          class="signal-btn"
          @click="addSignal(signal)"
        >
          {{ signal }}
        </button>
      </div>
      
      <div class="signal-column">
        <button 
          v-for="signal in column2" 
          :key="signal"
          class="signal-btn"
          @click="addSignal(signal)"
        >
          {{ signal }}
        </button>
      </div>
      
      <div class="signal-column">
        <button 
          v-for="signal in column3" 
          :key="signal"
          class="signal-btn"
          @click="addSignal(signal)"
        >
          {{ signal }}
        </button>
      </div>
      
      <div class="signal-column">
        <button 
          v-for="signal in column4" 
          :key="signal"
          class="signal-btn"
          @click="addSignal(signal)"
        >
          {{ signal }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { store } from '../store';
import { api } from '../api';

const router = useRouter();

// Signal options in 4 columns (from design mockup)
const column1 = [
  'I have pen',
  'I have Type-c cable',
  'I have Lighting cable'
];

const column2 = [
  'I have Macbook charger',
  'You can borrow my calculator'
];

const column3 = [
  'Feel free to seat here',
  'I am waiting for my friend',
  'Prefer to seat alone'
];

const column4 = [
  'Looking for study buddy',
  'Low energy, please be gentle',
  'Here if you need anytime'
];

const avatarColor = ref('colorful');
const avatarStatus = ref('smile');
const activeSignals = ref([]);
let signalIdCounter = 0;
let draggingSignal = null;
let dragOffset = { x: 0, y: 0 };

onMounted(async () => {
  // Load user avatar info
  if (!store.user || !store.user.id) {
    console.error('No user found in Signal page, redirecting to welcome');
    router.push('/');
    return;
  }
  
  if (!store.user.avatar_color || !store.user.avatar_status) {
    console.log('User missing avatar info, reloading from backend...');
    try {
      const userData = await api.users.get(store.user.id);
      console.log('Reloaded user data:', userData);
      store.setUser(userData);
      
      if (!userData.avatar_color || !userData.avatar_status) {
        console.log('User still missing avatar info after reload, redirecting to status select');
        router.push('/status-select');
        return;
      }
    } catch (error) {
      console.error('Failed to reload user data:', error);
      router.push('/status-select');
      return;
    }
  }
  
  avatarColor.value = store.user.avatar_color || 'colorful';
  avatarStatus.value = store.user.avatar_status || 'smile';
  
  // Load existing signals
  try {
    const signals = await api.signals.getByUser(store.user.id);
    // Position existing signals around the avatar
    activeSignals.value = signals.map((signal, index) => ({
      id: signal.id,
      text: signal.text,
      x: getInitialX(index, signals.length),
      y: getInitialY(index, signals.length),
      rotation: Math.random() * 10 - 5,
      style: getSignalStyle(index)
    }));
    signalIdCounter = Math.max(...signals.map(s => s.id)) + 1;
  } catch (error) {
    console.error('Failed to load signals:', error);
  }
});

const getInitialX = (index, total) => {
  const canvasWidth = 800;
  const centerX = canvasWidth / 2;
  const radius = 200;
  const angle = (index / total) * 2 * Math.PI;
  return centerX + Math.cos(angle) * radius - 100;
};

const getInitialY = (index, total) => {
  const canvasHeight = 400;
  const centerY = canvasHeight / 2;
  const radius = 150;
  const angle = (index / total) * 2 * Math.PI;
  return centerY + Math.sin(angle) * radius - 30;
};

const getSignalStyle = (index) => {
  const styles = ['bubble-left', 'bubble-right'];
  return styles[index % styles.length];
};

const addSignal = async (text) => {
  try {
    // Decide position alternating left/right
    const position = activeSignals.value.length % 2 === 0 ? 'left' : 'right';
    const signal = await api.signals.create(store.user.id, text, position);
    
    // Add to canvas at a random position
    const canvasWidth = 800;
    const canvasHeight = 400;
    const newSignal = {
      id: signal.id,
      text: signal.text,
      x: Math.random() * (canvasWidth - 200) + 50,
      y: Math.random() * (canvasHeight - 100) + 50,
      rotation: Math.random() * 10 - 5,
      style: position === 'left' ? 'bubble-left' : 'bubble-right'
    };
    
    activeSignals.value.push(newSignal);
  } catch (error) {
    console.error('Failed to add signal:', error);
    alert('Failed to add signal');
  }
};

const removeSignal = async (signal) => {
  if (confirm('Remove this signal?')) {
    try {
      await api.signals.delete(signal.id);
      activeSignals.value = activeSignals.value.filter(s => s.id !== signal.id);
    } catch (error) {
      console.error('Failed to remove signal:', error);
      alert('Failed to remove signal');
    }
  }
};

const startDrag = (signal, event) => {
  draggingSignal = signal;
  dragOffset.x = event.clientX - signal.x;
  dragOffset.y = event.clientY - signal.y;
  
  document.addEventListener('mousemove', onDrag);
  document.addEventListener('mouseup', stopDrag);
};

const onDrag = (event) => {
  if (draggingSignal) {
    draggingSignal.x = event.clientX - dragOffset.x;
    draggingSignal.y = event.clientY - dragOffset.y;
  }
};

const stopDrag = () => {
  draggingSignal = null;
  document.removeEventListener('mousemove', onDrag);
  document.removeEventListener('mouseup', stopDrag);
};

const saveDone = () => {
  router.push(`/table/${store.currentTable?.number || 1}`);
};

const handleImageError = (e) => {
  e.target.src = `/avatars/colorful-smile.png`;
};
</script>

<style scoped>
.signal-page {
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
}


.page-title {
  text-align: center;
  font-size: 2rem;
  font-weight: 600;
  color: white;
  margin: 2rem 0 0.5rem;
}

.page-subtitle {
  text-align: center;
  font-size: 1.5rem;
  font-weight: 400;
  color: white;
  margin: 0 0 2rem;
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

.signal-canvas {
  position: relative;
  width: 800px;
  height: 400px;
  margin: 2rem auto;
}

.center-avatar {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  padding: 15px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  border: 3px solid rgba(255, 255, 255, 0.3);
  z-index: 10;
}

.center-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.signal-bubble {
  position: absolute;
  padding: 0.8rem 1.5rem;
  background: rgba(209, 213, 219, 0.9);
  border-radius: 20px;
  font-size: 0.95rem;
  color: #1f2937;
  cursor: move;
  user-select: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: transform 0.1s;
  z-index: 5;
  max-width: 250px;
}

.signal-bubble:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.signal-bubble.bubble-left::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 20%;
  width: 0;
  height: 0;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-top: 10px solid rgba(209, 213, 219, 0.9);
}

.signal-bubble.bubble-right::after {
  content: '';
  position: absolute;
  bottom: -10px;
  right: 20%;
  width: 0;
  height: 0;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-top: 10px solid rgba(209, 213, 219, 0.9);
}

.bubble-connector {
  position: absolute;
  width: 15px;
  height: 15px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  bottom: -30px;
  left: 50%;
  transform: translateX(-50%);
}

.signal-options {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin: 2rem auto;
  max-width: 1000px;
  padding: 0 2rem;
}

.signal-column {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
}

.signal-btn {
  padding: 0.6rem 1rem;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  font-size: 0.85rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  white-space: nowrap;
}

.signal-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}

.signal-btn::before {
  content: '•';
  color: rgba(236, 72, 153, 0.8);
  margin-right: 0.5rem;
  font-weight: bold;
}
</style>
