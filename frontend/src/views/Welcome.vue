<template>
  <div class="welcome-page">
    <div class="brand-logo">NudgeeQ</div>
    
    <div class="welcome-layout">
      <div class="left-content">
        <h1 class="welcome-title">Welcome</h1>
        <p class="welcome-subtitle">
          Let's start enjoy your library time<br />with <span class="brand-highlight">NudgeeQ</span>
        </p>
      </div>
      
      <div class="right-content">
        <div class="avatar-bubbles">
          <img src="/avatars/colorful-smile.png" alt="avatar" class="bubble-avatar avatar-1" />
          <img src="/avatars/brown-smile.png" alt="avatar" class="bubble-avatar avatar-2" />
          <img src="/avatars/white-smile.png" alt="avatar" class="bubble-avatar avatar-3" />
        </div>
      </div>
    </div>
    
    <div class="join-section">
      <input 
        v-model="nickname"
        type="text"
        placeholder="Enter your name..."
        class="name-input"
        @keyup.enter="joinTable"
      />
      <button class="join-button" @click="joinTable">
        <span class="plus-icon">+</span>
      </button>
      <p class="join-text">Join Table</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { store } from '../store';
import { api } from '../api';

const router = useRouter();
const nickname = ref('');

const joinTable = async () => {
  try {
    if (!nickname.value.trim()) {
      alert('Please enter your name');
      return;
    }
    
    const inputNickname = nickname.value.trim();
    let user = null;
    
    // First try to find existing user by nickname
    try {
      user = await api.users.getByNickname(inputNickname);
      console.log('Found existing user by nickname:', user);
      
      // Update store with this user
      store.setUser(user);
      store.setSessionId(user.session_id);
      
      // Check if user already has a table
      try {
        const table = await api.tables.getByUser(user.id);
        console.log('User already in table:', table);
        store.setCurrentTable(table);
        // User has a table, go directly to table page
        router.push(`/table/${table.id}`);
        return;
      } catch (tableError) {
        // User exists but not in any table, go to seat select
        console.log('User exists but no table, go to seat select');
        router.push('/seat-select');
        return;
      }
    } catch (nicknameError) {
      // User not found by nickname, create new one
      console.log('User not found by nickname, creating new user');
      
      // Clear all old user data and generate new session for new user
      store.clearAll();
      store.generateSessionId();
      
      user = await api.users.create(store.sessionId, inputNickname);
      store.setUser(user);
      router.push('/seat-select');
    }
  } catch (error) {
    console.error('Failed to initialize:', error);
    alert('Failed to connect. Please check your network connection.');
  }
};
</script>

<style scoped>
.welcome-page {
  position: relative;
  min-height: 100vh;
  background: linear-gradient(135deg, #b794f6 0%, #a78bfa 50%, #c084fc 100%);
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

.welcome-layout {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 3rem;
  min-height: 70vh;
}

.left-content {
  flex: 1;
  color: white;
  padding-right: 2rem;
}

.welcome-title {
  font-size: 5rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  line-height: 1;
  color: white;
  letter-spacing: -0.02em;
}

.welcome-subtitle {
  font-size: 1.75rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 400;
  margin: 0;
}

.brand-highlight {
  font-weight: 600;
  color: white;
}

.right-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.avatar-bubbles {
  position: relative;
  width: 400px;
  height: 400px;
}

.bubble-avatar {
  position: absolute;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  object-fit: cover;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.avatar-1 {
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  z-index: 3;
}

.avatar-2 {
  top: 30%;
  right: 0;
  z-index: 2;
  width: 150px;
  height: 150px;
  padding: 15px;
}

.avatar-3 {
  bottom: 0;
  right: 20%;
  z-index: 1;
  width: 160px;
  height: 160px;
  padding: 18px;
}

.join-section {
  position: absolute;
  bottom: 8rem;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.name-input {
  width: 280px;
  padding: 0.9rem 1.5rem;
  border-radius: 25px;
  border: 2px solid rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  color: white;
  font-size: 1rem;
  font-weight: 500;
  text-align: center;
  outline: none;
  transition: all 0.3s ease;
}

.name-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.name-input:focus {
  border-color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.35);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.join-button {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
  border: 3px solid rgba(255, 255, 255, 0.5);
  color: white;
  font-size: 2.5rem;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.join-button:hover {
  background: rgba(255, 255, 255, 0.4);
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
}

.plus-icon {
  line-height: 1;
  font-weight: 300;
}

.join-text {
  font-size: 1.25rem;
  margin-top: 1.25rem;
  font-weight: 500;
  color: white;
  letter-spacing: 0.02em;
}

/* 装饰性元素 */
.welcome-page::before,
.welcome-page::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.welcome-page::before {
  width: 150px;
  height: 150px;
  top: 15%;
  left: 10%;
}

.welcome-page::after {
  width: 100px;
  height: 100px;
  bottom: 20%;
  right: 15%;
}
</style>

