<template>
  <div class="avatar-page">
    <div class="brand-logo">NudgeeQ</div>
    
    <button class="exit-btn" @click="$router.back()">
      ✕
    </button>
    
    <div class="content-wrapper">
      <h1 class="main-title">My Avatar</h1>
      
      <div class="avatar-carousel">
        <button class="nav-btn left" @click="prevColor">
          <span class="nav-arrow">‹‹</span>
        </button>
        
        <div class="avatars-strip">
          <div 
            v-for="(color, index) in getVisibleColors()" 
            :key="color"
            :class="['avatar-item', { 
              center: index === 2,
              side: index === 1 || index === 3,
              far: index === 0 || index === 4
            }]"
            @click="selectColor(color)"
          >
            <img 
              :src="`/avatars/${color}-${selectedStatus}.png`" 
              :alt="color"
              class="avatar-img"
            />
          </div>
        </div>
        
        <button class="nav-btn right" @click="nextColor">
          <span class="nav-arrow">››</span>
        </button>
      </div>
      
      <div class="status-selector">
        <div 
          v-for="status in statusOptions" 
          :key="status.value"
          class="status-option"
        >
          <div 
            :class="['status-avatar-wrapper', { selected: selectedStatus === status.value }]"
            @click="selectedStatus = status.value"
          >
            <img 
              :src="`/avatars/${selectedColor}-${status.value}.png`" 
              :alt="status.label"
              class="status-avatar"
            />
          </div>
          <p class="status-label">{{ status.label }}</p>
        </div>
      </div>
      
      <button class="confirm-btn" @click="confirmAvatar">
        That's Me
      </button>
    </div>
    
    <div class="decoration-dots">
      <span class="dot dot-1"></span>
      <span class="dot dot-2"></span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { store } from '../store';
import { api } from '../api';

const router = useRouter();

const colors = ['colorful', 'brown', 'white', 'white2', 'yellow'];
const statusOptions = [
  { value: 'smile', label: 'Happy' },
  { value: 'okay', label: 'All Good' },
  { value: 'normal', label: 'Working' },
  { value: 'annoying', label: 'Annoying' }
];

const selectedColor = ref('white');
const selectedStatus = ref('normal');
const currentColorIndex = ref(2);

onMounted(() => {
  if (store.user?.avatar_color) {
    selectedColor.value = store.user.avatar_color;
    currentColorIndex.value = colors.indexOf(store.user.avatar_color);
  }
  if (store.user?.avatar_status) {
    selectedStatus.value = store.user.avatar_status;
  }
});

const getVisibleColors = () => {
  const result = [];
  for (let i = -2; i <= 2; i++) {
    const index = (currentColorIndex.value + i + colors.length) % colors.length;
    result.push(colors[index]);
  }
  return result;
};

const selectColor = (color) => {
  selectedColor.value = color;
  currentColorIndex.value = colors.indexOf(color);
};

const prevColor = () => {
  currentColorIndex.value = (currentColorIndex.value - 1 + colors.length) % colors.length;
  selectedColor.value = colors[currentColorIndex.value];
};

const nextColor = () => {
  currentColorIndex.value = (currentColorIndex.value + 1) % colors.length;
  selectedColor.value = colors[currentColorIndex.value];
};

const confirmAvatar = async () => {
  try {
    // Update user and get the complete updated data from backend
    const updatedUser = await api.users.update(store.user.id, {
      avatar_color: selectedColor.value,
      avatar_status: selectedStatus.value,
    });
    
    console.log('Updated user from API (Avatar page):', updatedUser);
    
    // Use the complete data returned from API to ensure consistency
    store.setUser(updatedUser);
    
    router.back();
  } catch (error) {
    console.error('Failed to save avatar:', error);
    alert('Failed to save. Please try again.');
  }
};
</script>

<style scoped>
.avatar-page {
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

.content-wrapper {
  text-align: center;
  max-width: 900px;
  width: 100%;
}

.main-title {
  font-size: 2.5rem;
  font-weight: 600;
  color: white;
  margin-bottom: 3rem;
  letter-spacing: 0.02em;
}

.avatar-carousel {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  margin: 3rem 0;
  position: relative;
}

.nav-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 2rem;
  cursor: pointer;
  transition: all 0.2s;
  padding: 1rem;
  z-index: 10;
}

.nav-btn:hover {
  transform: scale(1.1);
}

.nav-arrow {
  font-size: 2rem;
  font-weight: 300;
}

.avatars-strip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  height: 220px;
}

.avatar-item {
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-item.center {
  width: 180px;
  height: 180px;
  opacity: 1;
  transform: scale(1);
  z-index: 3;
}

.avatar-item.side {
  width: 140px;
  height: 140px;
  opacity: 0.85;
  transform: scale(0.85);
  z-index: 2;
}

.avatar-item.far {
  width: 100px;
  height: 100px;
  opacity: 0.6;
  transform: scale(0.7);
  z-index: 1;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  padding: 15px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.avatar-item.center .avatar-img {
  padding: 20px;
  border-width: 4px;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.3);
}

.status-selector {
  display: flex;
  gap: 2rem;
  justify-content: center;
  margin: 3rem 0;
  flex-wrap: wrap;
}

.status-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.status-avatar-wrapper {
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  border: 3px solid transparent;
  transition: all 0.2s;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
}

.status-avatar-wrapper.selected {
  border-color: rgba(37, 99, 235, 0.8);
  background: rgba(255, 255, 255, 0.25);
  box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
}

.status-avatar-wrapper:hover {
  transform: scale(1.05);
  background: rgba(255, 255, 255, 0.2);
}

.status-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  display: block;
}

.status-label {
  margin: 0;
  font-size: 1rem;
  font-weight: 500;
  color: white;
}

.confirm-btn {
  margin-top: 2rem;
  padding: 1rem 3rem;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.5);
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.confirm-btn:hover {
  background: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
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
  top: 15%;
  left: 8%;
}

.dot-2 {
  width: 60px;
  height: 60px;
  bottom: 20%;
  right: 10%;
}
</style>

