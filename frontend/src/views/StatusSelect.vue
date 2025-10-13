<template>
  <div class="status-select-page">
    <div class="brand-logo">NudgeeQ</div>
    
    <button class="exit-btn" @click="$router.back()">
      ✕
    </button>
    
    <div class="content-wrapper">
      <h1 class="main-title">Step 2</h1>
      <h2 class="sub-title">Pick Your Status</h2>
      
      <button class="edit-avatar-link" @click="goToAvatar">
        Edit My Avatar
      </button>
      
      <div class="avatar-selector">
        <button class="nav-btn" @click="prevColor">
          <span class="nav-arrow">‹‹</span>
        </button>
        <div class="avatar-display">
          <img 
            :src="`/avatars/${selectedColor}-${selectedStatus}.png`" 
            :alt="`${selectedColor} ${selectedStatus}`"
            class="avatar-large"
          />
        </div>
        <button class="nav-btn" @click="nextColor">
          <span class="nav-arrow">››</span>
        </button>
      </div>
      
      <div class="status-options">
        <button
          v-for="status in statusLabels"
          :key="status.value"
          :class="['status-btn', { active: selectedStatus === status.value }]"
          @click="selectedStatus = status.value"
        >
          {{ status.label }}
        </button>
      </div>
      
      <button class="confirm-btn" @click="confirmStatus">
        That's It
      </button>
    </div>
    
    <div class="decoration-dots">
      <span class="dot dot-1"></span>
      <span class="dot dot-2"></span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { store } from '../store';
import { api } from '../api';

const router = useRouter();

const colors = ['colorful', 'brown', 'white', 'white2', 'yellow'];
const statusLabels = [
  { value: 'normal', label: 'Working' },
  { value: 'smile', label: 'Happy' },
  { value: 'okay', label: 'All Good' }
];

const selectedColor = ref('colorful');
const selectedStatus = ref('smile');

const currentColorIndex = ref(0);

const prevColor = () => {
  currentColorIndex.value = (currentColorIndex.value - 1 + colors.length) % colors.length;
  selectedColor.value = colors[currentColorIndex.value];
};

const nextColor = () => {
  currentColorIndex.value = (currentColorIndex.value + 1) % colors.length;
  selectedColor.value = colors[currentColorIndex.value];
};

const goToAvatar = () => {
  router.push('/avatar');
};

const confirmStatus = async () => {
  try {
    // Update user and get the complete updated data from backend
    const updatedUser = await api.users.update(store.user.id, {
      avatar_color: selectedColor.value,
      avatar_status: selectedStatus.value,
    });
    
    console.log('Updated user from API:', updatedUser);
    
    // Use the complete data returned from API to ensure consistency
    store.setUser(updatedUser);
    
    console.log('User in store after update:', store.user);
    
    router.push('/signal');
  } catch (error) {
    console.error('Failed to save status:', error);
    alert('Failed to save. Please try again.');
  }
};
</script>

<style scoped>
.status-select-page {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(180deg, #b794f6 0%, #9f7aea 30%, #805ad5 60%, #2d1b47 100%);
  overflow: hidden;
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
  max-width: 700px;
  width: 90%;
}

.main-title {
  font-size: 2.5rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.5rem;
  letter-spacing: 0.02em;
}

.sub-title {
  font-size: 1.75rem;
  font-weight: 500;
  color: white;
  margin-bottom: 1.5rem;
  opacity: 0.95;
}

.edit-avatar-link {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
  text-decoration: underline;
  cursor: pointer;
  margin-bottom: 2rem;
  padding: 0;
  transition: color 0.2s;
}

.edit-avatar-link:hover {
  color: white;
}

.avatar-selector {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 3rem;
  margin: 3rem 0;
}

.nav-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 3rem;
  cursor: pointer;
  transition: all 0.2s;
  padding: 0;
  line-height: 1;
}

.nav-btn:hover {
  color: white;
  transform: scale(1.1);
}

.nav-arrow {
  display: block;
  font-weight: 300;
}

.avatar-display {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.avatar-large {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.status-options {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  flex-wrap: wrap;
  margin: 3rem 0;
}

.status-btn {
  padding: 0.75rem 2rem;
  border-radius: 25px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  cursor: pointer;
  font-weight: 500;
  font-size: 1rem;
  transition: all 0.2s;
}

.status-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.status-btn.active {
  background: rgba(255, 255, 255, 0.4);
  border-color: rgba(255, 255, 255, 0.6);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.confirm-btn {
  margin-top: 2rem;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.5);
  color: white;
  padding: 1rem 3rem;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s;
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
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
}

.dot-1 {
  top: 10%;
  right: 10%;
}

.dot-2 {
  bottom: 15%;
  left: 12%;
  width: 80px;
  height: 80px;
}
</style>

