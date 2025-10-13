const API_BASE = 'http://localhost:8000/api';

export async function fetchApi(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}

export const api = {
  users: {
    create: (sessionId, nickname = null) => fetchApi('/users/', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, nickname }),
    }),
    get: (userId) => fetchApi(`/users/${userId}`),
    update: (userId, data) => fetchApi(`/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
    getBySession: (sessionId) => fetchApi(`/users/session/${sessionId}`),
    getByNickname: (nickname) => fetchApi(`/users/nickname/${encodeURIComponent(nickname)}`),
  },
  
  seats: {
    getStatus: () => fetchApi('/seats/status'),
    occupy: (seatNum, userId) => fetchApi(`/seats/${seatNum}/occupy`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    }),
    release: (seatNum) => fetchApi(`/seats/${seatNum}/release`, {
      method: 'POST',
    }),
  },
  
  signals: {
    create: (userId, text, position) => fetchApi('/signals/', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, text, position }),
    }),
    getByUser: (userId) => fetchApi(`/signals/user/${userId}`),
    delete: (signalId) => fetchApi(`/signals/${signalId}`, {
      method: 'DELETE',
    }),
    deleteAll: (userId) => fetchApi(`/signals/user/${userId}/all`, {
      method: 'DELETE',
    }),
  },
  
  tables: {
    get: (tableId) => fetchApi(`/tables/${tableId}`),
    join: (userId, tableNumber = null) => fetchApi(`/tables/join?user_id=${userId}${tableNumber ? `&table_number=${tableNumber}` : ''}`, {
      method: 'POST',
    }),
    getByUser: (userId) => fetchApi(`/tables/user/${userId}`),
    getNearby: (keyword = '', excludeTableId = null) => {
      const params = new URLSearchParams();
      if (keyword) params.append('keyword', keyword);
      if (excludeTableId) params.append('exclude_table_id', excludeTableId);
      return fetchApi(`/tables/nearby?${params}`);
    },
    leave: (userId) => fetchApi(`/tables/leave?user_id=${userId}`, {
      method: 'POST',
    }),
  },
  
  messages: {
    send: (fromTableId, toTableId, content, toUserId = null) => fetchApi('/messages/send', {
      method: 'POST',
      body: JSON.stringify({ 
        from_table_id: fromTableId, 
        to_table_id: toTableId, 
        content,
        to_user_id: toUserId 
      }),
    }),
    reply: (messageId, reply, replierUserId = null) => fetchApi(`/messages/${messageId}/reply`, {
      method: 'PUT',
      body: JSON.stringify({ reply, replier_user_id: replierUserId }),
    }),
    getByTable: (tableId) => fetchApi(`/messages/table/${tableId}`),
  },
  
  admin: {
    getUsers: () => fetchApi('/admin/users'),
    getTables: () => fetchApi('/admin/tables'),
    getSeats: () => fetchApi('/admin/seats'),
    kickUser: (userId) => fetchApi(`/admin/kick/${userId}`, {
      method: 'POST',
    }),
    reset: () => fetchApi('/admin/reset', {
      method: 'POST',
    }),
    createUser: (userData) => fetchApi('/admin/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    }),
    updateUser: (userId, userData) => fetchApi(`/admin/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    }),
    assignSeat: (seatNumber, userId) => fetchApi(`/admin/seats/${seatNumber}/assign/${userId}`, {
      method: 'POST',
    }),
    getUserSignals: (userId) => fetchApi(`/admin/users/${userId}/signals`),
    addSignal: (userId, signalData) => fetchApi(`/admin/users/${userId}/signals`, {
      method: 'POST',
      body: JSON.stringify(signalData),
    }),
    deleteSignal: (signalId) => fetchApi(`/admin/signals/${signalId}`, {
      method: 'DELETE',
    }),
  },
};

