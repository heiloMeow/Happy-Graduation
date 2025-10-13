<template>
  <div class="seat-select-page">
    <div class="brand-logo">NudgeeQ</div>
    
    <div class="stars-decoration"></div>
    
    <div class="content-wrapper">
      <h1 class="main-title">Step 1</h1>
      <h2 class="sub-title">Select Your Seat</h2>
      
      <div class="tables-container">
        <div class="table-section">
          <h3 class="table-label">Table 1</h3>
          <div class="seats-card">
            <div class="seats-grid">
              <button
                v-for="seat in table1Seats"
                :key="seat.number"
                :class="['seat-button', { occupied: seat.occupied && seat.current_user_id !== store.user?.id }]"
                :disabled="seat.occupied && seat.current_user_id !== store.user?.id"
                @click="selectSeat(seat.number)"
              >
                {{ seat.number }}
              </button>
            </div>
            <div class="divider-horizontal"></div>
            <div class="divider-vertical"></div>
          </div>
        </div>
        
        <div class="table-section">
          <h3 class="table-label">Table 2</h3>
          <div class="seats-card">
            <div class="seats-grid">
              <button
                v-for="seat in table2Seats"
                :key="seat.number"
                :class="['seat-button', { occupied: seat.occupied && seat.current_user_id !== store.user?.id }]"
                :disabled="seat.occupied && seat.current_user_id !== store.user?.id"
                @click="selectSeat(seat.number)"
              >
                {{ seat.number }}
              </button>
            </div>
            <div class="divider-horizontal"></div>
            <div class="divider-vertical"></div>
          </div>
        </div>
      </div>
      
      <p v-if="error" class="error-message">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { store } from '../store';
import { api } from '../api';

const router = useRouter();
const seats = ref([]);
const error = ref('');

const table1Seats = computed(() => seats.value.filter(s => s.number >= 1 && s.number <= 4));
const table2Seats = computed(() => seats.value.filter(s => s.number >= 5 && s.number <= 8));

onMounted(async () => {
  try {
    // Ensure we have a valid user
    if (!store.user || !store.user.id) {
      console.error('No user in store, redirecting to welcome');
      router.push('/');
      return;
    }
    
    // Check if user already has a table
    try {
      const table = await api.tables.getByUser(store.user.id);
      console.log('User already in table, redirecting:', table);
      store.setCurrentTable(table);
      router.push(`/table/${table.id}`);
      return;
    } catch (tableError) {
      // User not in any table, continue to seat selection
      console.log('User not in table, show seat selection');
    }
    
    seats.value = await api.seats.getStatus();
  } catch (err) {
    error.value = 'Failed to load seats. Please retry.';
    console.error(err);
  }
});

const selectSeat = async (seatNum) => {
  try {
    error.value = '';
    const result = await api.seats.occupy(seatNum, store.user.id);
    console.log('Seat occupied:', result);
    
    // After occupying seat, get table info
    try {
      const table = await api.tables.getByUser(store.user.id);
      store.setCurrentTable(table);
    } catch (tableError) {
      console.log('Failed to get table after seat selection:', tableError);
    }
    
    router.push('/status-select');
  } catch (err) {
    error.value = err.message || 'Failed to occupy seat';
  }
};
</script>

<style scoped>
.seat-select-page {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(180deg, #b794f6 0%, #8b5cf6 30%, #6b46c1 60%, #1a1a2e 100%);
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

.stars-decoration {
  position: absolute;
  bottom: 15%;
  left: 8%;
  width: 80px;
  height: 80px;
  opacity: 0.3;
}

.stars-decoration::before,
.stars-decoration::after {
  content: '';
  position: absolute;
  width: 40px;
  height: 40px;
  border: 2px solid white;
  transform: rotate(45deg);
}

.stars-decoration::before {
  top: 0;
  left: 0;
}

.stars-decoration::after {
  bottom: -20px;
  right: -20px;
  width: 30px;
  height: 30px;
  opacity: 0.6;
}

.content-wrapper {
  text-align: center;
  max-width: 1400px;
  width: 90%;
}

.tables-container {
  display: flex;
  gap: 3rem;
  justify-content: center;
  align-items: flex-start;
  flex-wrap: wrap;
}

.table-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.table-label {
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
  margin: 0;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
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
  margin-bottom: 3rem;
  opacity: 0.95;
}

.seats-card {
  position: relative;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(20px);
  border-radius: 30px;
  padding: 3rem 2.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.2);
  width: 100%;
  max-width: 450px;
}

.seats-grid {
  position: relative;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 3rem;
  justify-items: center;
  align-items: center;
  z-index: 1;
}

.divider-horizontal {
  position: absolute;
  top: 50%;
  left: 10%;
  right: 10%;
  height: 1px;
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-50%);
  z-index: 0;
}

.divider-vertical {
  position: absolute;
  left: 50%;
  top: 10%;
  bottom: 10%;
  width: 1px;
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(-50%);
  z-index: 0;
}

.seat-button {
  width: 130px;
  height: 130px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.9);
  font-size: 3rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 1;
}

.seat-button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.35);
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
  border-color: rgba(255, 255, 255, 0.5);
}

.seat-button:active:not(:disabled) {
  transform: scale(0.98);
}

.seat-button.occupied {
  background: rgba(100, 100, 100, 0.3);
  border-color: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.4);
  cursor: not-allowed;
}

.seat-button:disabled {
  opacity: 0.5;
}

.error-message {
  color: #fca5a5;
  margin-top: 1.5rem;
  font-weight: 500;
  font-size: 1rem;
  background: rgba(239, 68, 68, 0.2);
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  border: 1px solid rgba(239, 68, 68, 0.3);
}
</style>

