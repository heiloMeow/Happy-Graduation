<template>
  <div class="nearby-page">
    <div class="brand-logo">NudgeeQ</div>
    
    <button class="exit-btn" @click="goBack">
      ✕
    </button>
    
    <h1 class="page-title">Near by Table</h1>
    
    <div class="search-box">
      <svg class="search-icon-left" width="18" height="18" viewBox="0 0 24 24" fill="none">
        <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
        <path d="M21 21L16.65 16.65" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <input 
        v-model="keyword"
        type="text"
        placeholder="Filter by keyword (optional)..."
        class="search-input"
        @input="search"
      />
      <button 
        v-if="keyword" 
        class="clear-btn" 
        @click="clearSearch"
      >
        ✕
      </button>
    </div>
    
    <div class="tables-canvas">
      <div 
        v-for="(table, index) in nearbyTables" 
        :key="table.id"
        :class="['table-card', `position-${index % 4}`]"
      >
        <div class="table-header">
          <h3 class="table-number">Table {{ table.number }}</h3>
          <span class="members-count">{{ table.members.length }} member{{ table.members.length !== 1 ? 's' : '' }}</span>
        </div>
        
        <div class="members-preview">
          <div 
            v-for="member in table.members.slice(0, 3)" 
            :key="member.user_id"
            class="member-preview"
          >
            <img 
              :src="getAvatarPath(member)"
              :alt="`${member.nickname || 'User'}`"
              class="preview-avatar"
              @error="handleImageError"
            />
            <div class="preview-info">
              <div class="preview-name">{{ member.nickname || 'User ' + member.user_id }}</div>
              <div class="preview-location">Seat {{ member.seat_number }}</div>
            </div>
          </div>
          <div v-if="table.members.length > 3" class="more-members">
            +{{ table.members.length - 3 }} more
          </div>
        </div>
        
        <div class="keywords-display">
          <div v-for="keyword in getTableKeywords(table)" :key="keyword" class="keyword-tag">
            {{ keyword }}
          </div>
          <div v-if="getTableKeywords(table).length === 0" class="keyword-tag empty">No signals</div>
        </div>
        
        <button 
          class="contact-btn" 
          @click="selectTable(table.id)"
          :class="{ 'my-table': table.id === store.currentTable?.id }"
        >
          {{ table.id === store.currentTable?.id ? 'Contact Tablemate' : 'Contact' }}
        </button>
      </div>
      
      <div v-if="nearbyTables.length === 0" class="empty-state">
        <p>{{ keyword ? 'No matching tables' : 'No other tables available' }}</p>
        <p v-if="keyword" class="empty-hint">Try different keywords or clear the filter</p>
        <p v-else class="empty-hint">Other tables will appear here when people join</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { store } from '../store';
import { api } from '../api';

const router = useRouter();
const keyword = ref('');
const nearbyTables = ref([]);

const search = async () => {
  try {
    // Note: We pass current table id for API compatibility, but backend shows ALL tables
    // (including user's own table) to reduce social anxiety - users see themselves in the list
    const excludeId = store.currentTable?.id || null;
    nearbyTables.value = await api.tables.getNearby(keyword.value, excludeId);
  } catch (error) {
    console.error('Failed to search tables:', error);
  }
};

const clearSearch = () => {
  keyword.value = '';
  search();
};

onMounted(async () => {
  // Ensure user is loaded
  if (!store.user || !store.user.id) {
    console.error('No user in store');
    // Don't redirect, just show empty state
    return;
  }
  
  // If no current table, try to load it
  if (!store.currentTable) {
    try {
      const table = await api.tables.getByUser(store.user.id);
      store.setCurrentTable(table);
    } catch (error) {
      console.log('User has no table yet');
    }
  }
  
  search();
});

const getAvatarPath = (member) => {
  const color = member.avatar_color || 'colorful';
  const status = member.avatar_status || 'smile';
  return `/avatars/${color}-${status}.png`;
};

const handleImageError = (e) => {
  // Fallback to default avatar if image fails to load
  e.target.src = '/avatars/colorful-smile.png';
};

const getTableKeywords = (table) => {
  // Extract keywords from all members' signals
  const keywords = [];
  if (table.members && table.members.length > 0) {
    for (const member of table.members) {
      if (member.signals && member.signals.length > 0) {
        // Get first 2 signals from each member
        member.signals.slice(0, 2).forEach(signal => {
          if (!keywords.includes(signal.text)) {
            keywords.push(signal.text);
          }
        });
      }
    }
  }
  return keywords.slice(0, 3); // Max 3 keywords to display
};

const selectTable = (tableId) => {
  // Go to person selection page first
  router.push(`/select-person/${tableId}`);
};

const goBack = () => {
  router.back();
};
</script>

<style scoped>
.nearby-page {
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

.search-box {
  position: absolute;
  top: 2.5rem;
  right: 3rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 25px;
  padding: 0.7rem 1.2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 10;
  min-width: 280px;
}

.search-icon-left {
  color: #666;
  flex-shrink: 0;
}

.search-input {
  border: none;
  background: transparent;
  padding: 0;
  font-size: 0.95rem;
  color: #333;
  outline: none;
  flex: 1;
  min-width: 0;
}

.search-input::placeholder {
  color: #999;
}

.clear-btn {
  background: rgba(0, 0, 0, 0.1);
  border: none;
  color: #666;
  cursor: pointer;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: rgba(0, 0, 0, 0.2);
  color: #333;
}

.tables-canvas {
  position: relative;
  width: 100%;
  height: calc(100vh - 200px);
  margin-top: 180px;
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

.table-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  padding: 1.5rem;
  min-width: 240px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  transition: all 0.3s;
}

.table-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.table-number {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: white;
}

.members-count {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.8);
}

.table-card.position-0 {
  transform: translate(-20px, -30px);
}

.table-card.position-1 {
  transform: translate(20px, 40px);
}

.table-card.position-2 {
  transform: translate(-30px, 20px);
}

.table-card.position-3 {
  transform: translate(15px, -20px);
}

.table-card:hover {
  transform: translate(0, -10px) !important;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.25);
  background: rgba(255, 255, 255, 0.25);
}

.members-preview {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  width: 100%;
  padding: 0.5rem 0;
}

.member-preview {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.preview-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
}

.preview-info {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  flex: 1;
}

.preview-name {
  color: white;
  font-size: 0.95rem;
  font-weight: 600;
}

.preview-location {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
}

.more-members {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  text-align: center;
  padding: 0.3rem;
}

.keywords-display {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  max-width: 220px;
}

.keyword-tag {
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  padding: 0.4rem 0.8rem;
  border-radius: 15px;
  font-size: 0.85rem;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.keyword-tag.empty {
  background: rgba(255, 255, 255, 0.6);
  color: #666;
  font-style: italic;
}

.contact-btn {
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: 20px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.contact-btn:hover {
  background: white;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.contact-btn.my-table {
  background: rgba(139, 92, 246, 0.4);
  border-color: rgba(139, 92, 246, 0.6);
}

.contact-btn.my-table:hover {
  background: rgba(139, 92, 246, 0.5);
}

.empty-state {
  text-align: center;
  color: white;
  padding: 3rem;
}

.empty-state p {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.empty-hint {
  font-size: 1rem;
  opacity: 0.8;
}
</style>

