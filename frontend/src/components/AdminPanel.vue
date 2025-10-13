<template>
  <div v-if="testEnabled">
    <button class="admin-toggle-btn" @click="togglePanel">
      Admin
    </button>
    
    <div 
      v-if="showPanel" 
      class="admin-panel"
      :style="panelStyle"
      @mousedown="startDrag"
    >
      <div class="panel-header" @mousedown.stop="startDrag">
        <h2>Admin Panel</h2>
        <div class="header-actions">
          <button class="minimize-btn" @click="toggleMinimize">{{ isMinimized ? '□' : '_' }}</button>
          <button class="close-btn" @click="closePanel">&times;</button>
        </div>
      </div>
        
        <div v-if="!isMinimized" class="panel-content">
          <div class="section">
            <div class="section-header">
              <h3>All Users ({{ users.length }})</h3>
              <div class="header-btns">
                <button class="add-btn" @click="showAddUserForm = true">+ Add User</button>
                <button class="refresh-btn" @click="loadData">Refresh</button>
              </div>
            </div>
            
            <div v-if="showAddUserForm" class="add-user-form">
              <input v-model="newUser.nickname" placeholder="Nickname" />
              <select v-model="newUser.avatar_color">
                <option value="">Select Color</option>
                <option value="colorful">Colorful</option>
                <option value="brown">Brown</option>
                <option value="white">White</option>
                <option value="white2">White2</option>
                <option value="yellow">Yellow</option>
              </select>
              <select v-model="newUser.avatar_status">
                <option value="">Select Status</option>
                <option value="smile">Smile</option>
                <option value="normal">Normal</option>
                <option value="okay">Okay</option>
                <option value="annoying">Annoying</option>
              </select>
              <button class="save-btn" @click="addUser">Save</button>
              <button class="cancel-btn" @click="showAddUserForm = false">Cancel</button>
            </div>
            
            <div class="users-list">
              <div v-for="user in users" :key="user.id">
                <div class="user-item">
                  <div v-if="editingUserId === user.id" class="user-edit-form">
                    <input v-model="editForm.nickname" placeholder="Nickname" />
                    <select v-model="editForm.avatar_color">
                      <option value="colorful">Colorful</option>
                      <option value="brown">Brown</option>
                      <option value="white">White</option>
                      <option value="white2">White2</option>
                      <option value="yellow">Yellow</option>
                    </select>
                    <select v-model="editForm.avatar_status">
                      <option value="smile">Smile</option>
                      <option value="normal">Normal</option>
                      <option value="okay">Okay</option>
                      <option value="annoying">Annoying</option>
                    </select>
                    <select v-model="editForm.seat_number">
                      <option :value="null">No Seat</option>
                      <option 
                        v-for="n in 8" 
                        :key="n" 
                        :value="n"
                        :disabled="isSeatOccupied(n, user.id)"
                      >
                        Seat {{ n }}{{ isSeatOccupied(n, user.id) ? ' (Occupied)' : '' }}
                      </option>
                    </select>
                    <button class="save-btn" @click="saveUserEdit(user.id)">Save</button>
                    <button class="cancel-btn" @click="cancelEdit">Cancel</button>
                  </div>
                  <template v-else>
                    <div class="user-info">
                      <div class="user-main">
                        <strong>{{ user.nickname || 'No name' }}</strong>
                        <span class="user-id">#{{ user.id }}</span>
                      </div>
                      <div class="user-details">
                        <span v-if="user.table_number" class="badge table">Table {{ user.table_number }}</span>
                        <span v-if="user.seat_number" class="badge seat">Seat {{ user.seat_number }}</span>
                        <span v-if="user.avatar_color" class="badge avatar">{{ user.avatar_color }}-{{ user.avatar_status }}</span>
                        <span class="badge signals">{{ user.signals_count }} signals</span>
                      </div>
                    </div>
                    <div class="user-actions">
                      <button class="edit-btn" @click="startEdit(user)">Edit</button>
                      <button class="signal-btn" @click="manageSignals(user.id)">Signals</button>
                      <button class="kick-btn" @click="kickUser(user.id)">Kick</button>
                    </div>
                  </template>
                </div>
                
                <!-- Signal Management Panel -->
                <div v-if="managingSignalsUserId === user.id" class="signals-panel">
                  <div class="signals-header">
                    <h4>Manage Signals</h4>
                    <button class="close-signals-btn" @click="closeSignalsPanel">✕</button>
                  </div>
                  
                  <div class="signals-list">
                    <div v-for="signal in userSignals" :key="signal.id" class="signal-item">
                      <span class="signal-position-badge" :class="signal.position">{{ signal.position }}</span>
                      <span class="signal-text">{{ signal.text }}</span>
                      <button class="delete-signal-btn" @click="deleteSignal(signal.id)">✕</button>
                    </div>
                    <div v-if="!userSignals.length" class="no-signals">No signals yet</div>
                  </div>
                  
                  <div class="add-signal-form">
                    <input v-model="newSignal.text" placeholder="Signal text..." />
                    <select v-model="newSignal.position">
                      <option value="left">Left</option>
                      <option value="right">Right</option>
                    </select>
                    <button class="add-signal-btn" @click="addSignal(managingSignalsUserId)">Add</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="section">
            <h3>All Tables</h3>
            <div class="tables-list">
              <div v-for="table in tables" :key="table.id" class="table-item">
                <div class="table-info">
                  <strong>Table {{ table.number }}</strong>
                  <span class="members-count">{{ table.members_count }} / 4 members</span>
                </div>
                <div v-if="table.members.length" class="table-members">
                  <span v-for="member in table.members" :key="member.user_id" class="member-tag">
                    {{ member.nickname || 'User ' + member.user_id }} (Seat {{ member.seat_number }})
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="section">
            <h3>All Seats</h3>
            <div class="seats-grid">
              <div v-for="seat in seats" :key="seat.number" :class="['seat-card', { occupied: seat.occupied }]">
                <div class="seat-number">{{ seat.number }}</div>
                <div class="seat-status">
                  <span v-if="seat.occupied">{{ seat.user_nickname || 'User ' + seat.user_id }}</span>
                  <span v-else class="empty">Empty</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="section danger-zone">
            <h3>Danger Zone</h3>
            <button class="reset-btn" @click="resetDatabase">Reset All Data</button>
          </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { api } from '../api';

const testEnabled = ref(true);
const showPanel = ref(false);
const isMinimized = ref(false);
const users = ref([]);
const tables = ref([]);
const seats = ref([]);

// Panel dragging
const panelPosition = ref({ x: window.innerWidth - 450, y: 80 });
const isDragging = ref(false);
const dragStart = ref({ x: 0, y: 0 });

// Add/Edit user
const showAddUserForm = ref(false);
const editingUserId = ref(null);
const newUser = ref({ nickname: '', avatar_color: '', avatar_status: '' });
const editForm = ref({ nickname: '', avatar_color: '', avatar_status: '', seat_number: null });

// Signal management
const managingSignalsUserId = ref(null);
const userSignals = ref([]);
const newSignal = ref({ text: '', position: 'left' });

const panelStyle = computed(() => ({
  top: `${panelPosition.value.y}px`,
  left: `${panelPosition.value.x}px`,
}));

const togglePanel = () => {
  showPanel.value = !showPanel.value;
  if (showPanel.value) {
    loadData();
  }
};

const closePanel = () => {
  showPanel.value = false;
  isMinimized.value = false;
};

const toggleMinimize = () => {
  isMinimized.value = !isMinimized.value;
};

const startDrag = (e) => {
  if (e.target.tagName === 'BUTTON' || e.target.tagName === 'INPUT') return;
  
  isDragging.value = true;
  dragStart.value = {
    x: e.clientX - panelPosition.value.x,
    y: e.clientY - panelPosition.value.y
  };
  
  const onMouseMove = (e) => {
    if (!isDragging.value) return;
    panelPosition.value = {
      x: Math.max(0, Math.min(window.innerWidth - 400, e.clientX - dragStart.value.x)),
      y: Math.max(0, Math.min(window.innerHeight - 100, e.clientY - dragStart.value.y))
    };
  };
  
  const onMouseUp = () => {
    isDragging.value = false;
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
  };
  
  document.addEventListener('mousemove', onMouseMove);
  document.addEventListener('mouseup', onMouseUp);
};

const loadData = async () => {
  try {
    [users.value, tables.value, seats.value] = await Promise.all([
      api.admin.getUsers(),
      api.admin.getTables(),
      api.admin.getSeats()
    ]);
  } catch (error) {
    console.error('Failed to load admin data:', error);
    if (error.message.includes('404')) {
      testEnabled.value = false;
      alert('Admin API not available. Set test.enabled=true in config.yaml');
    }
  }
};

const addUser = async () => {
  if (!newUser.value.nickname.trim()) {
    alert('Please enter a nickname');
    return;
  }
  
  try {
    await api.admin.createUser(newUser.value);
    await loadData();
    newUser.value = { nickname: '', avatar_color: '', avatar_status: '' };
    showAddUserForm.value = false;
    alert('User added successfully');
  } catch (error) {
    console.error('Failed to add user:', error);
    alert('Failed to add user: ' + error.message);
  }
};

const startEdit = (user) => {
  console.log('Starting edit for user:', user);
  editingUserId.value = user.id;
  editForm.value = {
    nickname: user.nickname || '',
    avatar_color: user.avatar_color || 'colorful',
    avatar_status: user.avatar_status || 'smile',
    seat_number: user.seat_number || null
  };
  console.log('Edit form initialized:', editForm.value);
};

const cancelEdit = () => {
  editingUserId.value = null;
  editForm.value = { nickname: '', avatar_color: '', avatar_status: '', seat_number: null };
};

const saveUserEdit = async (userId) => {
  try {
    console.log('Saving user edit for userId:', userId);
    console.log('Edit form data:', editForm.value);
    
    // Update user info first
    await api.admin.updateUser(userId, {
      nickname: editForm.value.nickname,
      avatar_color: editForm.value.avatar_color,
      avatar_status: editForm.value.avatar_status
    });
    console.log('User info updated successfully');
    
    // Handle seat assignment separately
    const user = users.value.find(u => u.id === userId);
    const oldSeat = user.seat_number;
    const newSeat = editForm.value.seat_number;
    
    console.log(`Old seat: ${oldSeat}, New seat: ${newSeat}`);
    
    // If seat changed
    if (oldSeat !== newSeat) {
      if (newSeat !== null && newSeat !== '') {
        // Assign new seat
        console.log(`Assigning seat ${newSeat} to user ${userId}`);
        try {
          await api.admin.assignSeat(newSeat, userId);
          console.log('Seat assigned successfully');
        } catch (seatError) {
          console.error('Seat assignment failed:', seatError);
          if (seatError.message.includes('occupied') || seatError.message.includes('409')) {
            alert(`Seat ${newSeat} is already occupied by another user. Please choose a different seat.`);
          } else {
            throw seatError;
          }
          await loadData();
          return;
        }
      }
      // Note: We don't handle releasing seat here since assignSeat already handles it
    }
    
    await loadData();
    cancelEdit();
    alert('User updated successfully!');
  } catch (error) {
    console.error('Failed to update user:', error);
    alert('Failed to update user: ' + (error.message || 'Unknown error'));
    await loadData();
  }
};

const manageSignals = async (userId) => {
  if (managingSignalsUserId.value === userId) {
    closeSignalsPanel();
    return;
  }
  
  managingSignalsUserId.value = userId;
  try {
    userSignals.value = await api.admin.getUserSignals(userId);
  } catch (error) {
    console.error('Failed to load signals:', error);
    alert('Failed to load signals: ' + error.message);
  }
};

const isSeatOccupied = (seatNumber, currentUserId) => {
  const seat = seats.value.find(s => s.number === seatNumber);
  if (!seat || !seat.occupied) {
    return false;
  }
  // Seat is not considered occupied if it's occupied by the current user being edited
  return seat.user_id !== currentUserId;
};

const closeSignalsPanel = () => {
  managingSignalsUserId.value = null;
  userSignals.value = [];
  newSignal.value = { text: '', position: 'left' };
};

const addSignal = async (userId) => {
  if (!newSignal.value.text.trim()) {
    alert('Please enter signal text');
    return;
  }
  
  try {
    await api.admin.addSignal(userId, newSignal.value);
    userSignals.value = await api.admin.getUserSignals(userId);
    newSignal.value = { text: '', position: 'left' };
    await loadData(); // Refresh user list to update signal count
  } catch (error) {
    console.error('Failed to add signal:', error);
    alert('Failed to add signal: ' + error.message);
  }
};

const deleteSignal = async (signalId) => {
  if (!confirm('Delete this signal?')) {
    return;
  }
  
  try {
    await api.admin.deleteSignal(signalId);
    userSignals.value = await api.admin.getUserSignals(managingSignalsUserId.value);
    await loadData(); // Refresh user list to update signal count
  } catch (error) {
    console.error('Failed to delete signal:', error);
    alert('Failed to delete signal: ' + error.message);
  }
};

const kickUser = async (userId) => {
  if (!confirm(`Are you sure you want to kick user ${userId}?`)) {
    return;
  }
  
  try {
    await api.admin.kickUser(userId);
    await loadData();
    closeSignalsPanel();
    alert('User kicked successfully');
  } catch (error) {
    console.error('Failed to kick user:', error);
    alert('Failed to kick user: ' + error.message);
  }
};

const resetDatabase = async () => {
  if (!confirm('⚠️ This will DELETE ALL DATA. Are you sure?')) {
    return;
  }
  
  if (!confirm('⚠️⚠️ This action is IRREVERSIBLE. Continue?')) {
    return;
  }
  
  try {
    await api.admin.reset();
    await loadData();
    alert('Database reset successfully');
  } catch (error) {
    console.error('Failed to reset database:', error);
    alert('Failed to reset database: ' + error.message);
  }
};

onMounted(() => {
  // Check if admin API is available
  api.admin.getUsers().catch(() => {
    testEnabled.value = false;
  });
});
</script>

<style scoped>
.admin-toggle-btn {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  padding: 0.6rem 1.2rem;
  background: rgba(59, 130, 246, 0.9);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transition: all 0.2s;
}

.admin-toggle-btn:hover {
  background: rgba(59, 130, 246, 1);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
}

.admin-panel {
  position: fixed;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  width: 400px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.8);
  z-index: 10000;
  resize: both;
  overflow: hidden;
  cursor: move;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  background: rgba(59, 130, 246, 0.1);
  cursor: move;
  user-select: none;
}

.panel-header h2 {
  margin: 0;
  font-size: 1rem;
  color: #1f2937;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 0.25rem;
}

.minimize-btn,
.close-btn {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #6b7280;
  cursor: pointer;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.minimize-btn:hover,
.close-btn:hover {
  background: rgba(0, 0, 0, 0.1);
  color: #1f2937;
}

.panel-content {
  overflow-y: auto;
  padding: 1rem;
  cursor: default;
}

.section {
  margin-bottom: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.section h3 {
  margin: 0;
  font-size: 0.95rem;
  color: #374151;
  font-weight: 600;
}

.header-btns {
  display: flex;
  gap: 0.5rem;
}

.add-btn,
.refresh-btn {
  padding: 0.3rem 0.6rem;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.75rem;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.add-btn {
  background: #dbeafe;
  border-color: #3b82f6;
  color: #1e40af;
}

.add-btn:hover {
  background: #bfdbfe;
}

.refresh-btn:hover {
  background: #e5e7eb;
}

.add-user-form,
.user-edit-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  margin-bottom: 0.75rem;
}

.add-user-form input,
.add-user-form select,
.user-edit-form input,
.user-edit-form select {
  padding: 0.4rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.85rem;
}

.save-btn,
.cancel-btn {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.save-btn {
  background: #3b82f6;
  color: white;
}

.save-btn:hover {
  background: #2563eb;
}

.cancel-btn {
  background: #e5e7eb;
  color: #374151;
}

.cancel-btn:hover {
  background: #d1d5db;
}

.users-list, .tables-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
}

.user-item, .table-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: rgba(249, 250, 251, 0.8);
  border: 1px solid rgba(229, 231, 235, 0.8);
  border-radius: 6px;
  transition: all 0.2s;
  font-size: 0.85rem;
}

.user-item:hover, .table-item:hover {
  background: rgba(243, 244, 246, 0.9);
}

.user-info, .table-info {
  flex: 1;
}

.user-main {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 0.4rem;
  font-size: 0.9rem;
}

.user-id {
  font-size: 0.75rem;
  color: #6b7280;
  font-family: monospace;
}

.user-details {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.user-actions {
  display: flex;
  gap: 0.4rem;
}

.edit-btn {
  padding: 0.35rem 0.7rem;
  background: #dbeafe;
  border: 1px solid #3b82f6;
  border-radius: 4px;
  color: #1e40af;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.edit-btn:hover {
  background: #bfdbfe;
}

.signal-btn {
  padding: 0.35rem 0.7rem;
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 4px;
  color: #92400e;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.signal-btn:hover {
  background: #fde68a;
}

.signals-panel {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: #fffbeb;
  border: 1px solid #fbbf24;
  border-radius: 6px;
}

.signals-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.signals-header h4 {
  margin: 0;
  font-size: 0.9rem;
  color: #92400e;
}

.close-signals-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #92400e;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-signals-btn:hover {
  background: rgba(0, 0, 0, 0.1);
}

.signals-list {
  margin-bottom: 0.75rem;
  max-height: 150px;
  overflow-y: auto;
}

.signal-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: white;
  border: 1px solid #fbbf24;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.signal-position-badge {
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.signal-position-badge.left {
  background: #dbeafe;
  color: #1e40af;
}

.signal-position-badge.right {
  background: #d1fae5;
  color: #065f46;
}

.signal-text {
  flex: 1;
  font-size: 0.85rem;
  color: #374151;
}

.delete-signal-btn {
  background: #fef2f2;
  border: 1px solid #fca5a5;
  color: #dc2626;
  font-size: 0.9rem;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.2s;
}

.delete-signal-btn:hover {
  background: #fee2e2;
}

.no-signals {
  text-align: center;
  padding: 1rem;
  color: #92400e;
  font-size: 0.85rem;
  font-style: italic;
}

.add-signal-form {
  display: flex;
  gap: 0.5rem;
}

.add-signal-form input {
  flex: 1;
  padding: 0.4rem;
  border: 1px solid #fbbf24;
  border-radius: 4px;
  font-size: 0.85rem;
}

.add-signal-form select {
  padding: 0.4rem;
  border: 1px solid #fbbf24;
  border-radius: 4px;
  font-size: 0.85rem;
}

.add-signal-btn {
  padding: 0.4rem 0.8rem;
  background: #f59e0b;
  border: none;
  border-radius: 4px;
  color: white;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.add-signal-btn:hover {
  background: #d97706;
}

.badge {
  padding: 0.15rem 0.5rem;
  border-radius: 3px;
  font-size: 0.7rem;
  font-weight: 500;
}

.badge.table {
  background: #dbeafe;
  color: #1e40af;
}

.badge.seat {
  background: #d1fae5;
  color: #065f46;
}

.badge.avatar {
  background: #e9d5ff;
  color: #6b21a8;
}

.badge.signals {
  background: #fef3c7;
  color: #92400e;
}

.members-count {
  font-size: 0.9rem;
  color: #6b7280;
  margin-left: 0.5rem;
}

.table-members {
  margin-top: 0.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.member-tag {
  padding: 0.3rem 0.7rem;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.8rem;
  color: #374151;
}

.kick-btn {
  padding: 0.35rem 0.7rem;
  background: #fef2f2;
  border: 1px solid #fca5a5;
  border-radius: 4px;
  color: #dc2626;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.kick-btn:hover {
  background: #fee2e2;
  border-color: #f87171;
}

.seats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
}

.seat-card {
  padding: 0.5rem;
  background: rgba(249, 250, 251, 0.8);
  border: 1px solid rgba(229, 231, 235, 0.8);
  border-radius: 4px;
  text-align: center;
  transition: all 0.2s;
  font-size: 0.75rem;
}

.seat-card.occupied {
  background: rgba(219, 234, 254, 0.8);
  border-color: #3b82f6;
}

.seat-number {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.seat-status {
  font-size: 0.7rem;
  color: #6b7280;
}

.seat-status .empty {
  color: #9ca3af;
  font-style: italic;
}

.danger-zone {
  border-top: 1px solid #fca5a5;
  padding-top: 1rem;
}

.danger-zone h3 {
  color: #dc2626;
  font-size: 0.9rem;
}

.reset-btn {
  padding: 0.5rem 1rem;
  background: #dc2626;
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
}

.reset-btn:hover {
  background: #b91c1c;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

.members-count {
  font-size: 0.8rem;
  color: #6b7280;
  margin-left: 0.4rem;
}

.table-members {
  margin-top: 0.4rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.member-tag {
  padding: 0.25rem 0.5rem;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.7rem;
  color: #374151;
}
</style>

