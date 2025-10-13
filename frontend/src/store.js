import { reactive } from 'vue';

// Load user from localStorage
const loadUser = () => {
  const userData = localStorage.getItem('nudgeeq_user');
  if (userData) {
    try {
      return JSON.parse(userData);
    } catch (e) {
      console.error('Failed to parse user data:', e);
      return null;
    }
  }
  return null;
};

export const store = reactive({
  user: loadUser(),
  sessionId: localStorage.getItem('nudgeeq_session') || null,
  currentTable: null,
  
  setUser(user) {
    this.user = user;
    if (user) {
      localStorage.setItem('nudgeeq_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('nudgeeq_user');
    }
  },
  
  setSessionId(sessionId) {
    this.sessionId = sessionId;
    if (sessionId) {
      localStorage.setItem('nudgeeq_session', sessionId);
    } else {
      localStorage.removeItem('nudgeeq_session');
    }
  },
  
  setCurrentTable(table) {
    this.currentTable = table;
  },
  
  generateSessionId() {
    const id = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    this.setSessionId(id);
    return id;
  },
  
  clearAll() {
    this.user = null;
    this.sessionId = null;
    this.currentTable = null;
    localStorage.removeItem('nudgeeq_user');
    localStorage.removeItem('nudgeeq_session');
  },
});

