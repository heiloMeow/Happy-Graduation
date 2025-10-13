<template>
  <div class="select-person-page">
    <div class="brand-logo">NudgeeQ</div>
    
    <button class="exit-btn" @click="$router.back()">
      ✕
    </button>
    
    <div class="content">
      <h1 class="page-title">Select Person</h1>
      <h2 class="table-subtitle">Table {{ table?.number }}</h2>
      
      <div v-if="loading" class="loading">Loading...</div>
      
      <div v-else-if="members.length === 0" class="empty-state">
        <p>No members at this table</p>
      </div>
      
      <div v-else class="members-grid">
        <div 
          v-for="member in members" 
          :key="member.user_id"
          class="member-card"
          @click="selectPerson(member)"
        >
          <div class="avatar-wrapper">
            <img 
              :src="`/avatars/${member.avatar_color || 'colorful'}-${member.avatar_status || 'smile'}.png`" 
              :alt="member.nickname"
              @error="e => e.target.src = '/avatars/colorful-smile.png'"
            />
          </div>
          
          <div class="member-info">
            <h3 class="member-name">{{ member.nickname || 'User ' + member.user_id }}</h3>
            <p class="member-location">Table {{ member.table_number }}, Seat {{ member.seat_number }}</p>
            
            <div v-if="member.signals && member.signals.length > 0" class="signals">
              <span 
                v-for="signal in member.signals.slice(0, 2)" 
                :key="signal.id"
                class="signal-tag"
              >
                {{ signal.text }}
              </span>
              <span v-if="member.signals.length > 2" class="more-signals">
                +{{ member.signals.length - 2 }}
              </span>
            </div>
            <div v-else class="no-signals">No signals</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { api } from '../api';
import { store } from '../store';

const router = useRouter();
const route = useRoute();

const table = ref(null);
const members = ref([]);
const loading = ref(true);

onMounted(async () => {
  const tableId = parseInt(route.params.tableId);
  
  try {
    // Get table details
    table.value = await api.tables.get(tableId);
    
    // Filter out current user (cannot message yourself)
    // Shows all other members from any table (including own table)
    members.value = table.value.members.filter(m => m.user_id !== store.user?.id);
    
    loading.value = false;
  } catch (error) {
    console.error('Failed to load table members:', error);
    alert('Failed to load members');
    router.back();
  }
});

const selectPerson = (member) => {
  router.push({
    name: 'Notify',
    params: {
      tableId: table.value.id,
      userId: member.user_id
    }
  });
};
</script>

<style scoped>
.select-person-page {
  position: relative;
  min-height: 100vh;
  background: linear-gradient(180deg, #b794f6 0%, #9f7aea 30%, #805ad5 60%, #2d1b47 100%);
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

.content {
  max-width: 900px;
  margin: 0 auto;
  padding-top: 6rem;
}

.page-title {
  text-align: center;
  font-size: 2rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.5rem;
}

.table-subtitle {
  text-align: center;
  font-size: 1.3rem;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2rem;
}

.loading {
  text-align: center;
  color: white;
  font-size: 1.2rem;
  margin-top: 2rem;
}

.empty-state {
  text-align: center;
  color: white;
  font-size: 1.1rem;
  margin-top: 2rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
}

.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.member-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.member-card:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.avatar-wrapper {
  width: 120px;
  height: 120px;
  margin: 0 auto 1rem;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  padding: 10px;
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.avatar-wrapper img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.member-info {
  text-align: center;
}

.member-name {
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0 0 0.3rem;
}

.member-location {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  margin: 0 0 0.8rem;
}

.signals {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}

.signal-tag {
  background: rgba(139, 92, 246, 0.4);
  color: white;
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  font-size: 0.8rem;
  border: 1px solid rgba(139, 92, 246, 0.6);
}

.more-signals {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
  align-self: center;
}

.no-signals {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  font-style: italic;
}
</style>

