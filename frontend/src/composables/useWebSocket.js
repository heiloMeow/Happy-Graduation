import { ref, onUnmounted, getCurrentInstance } from 'vue';

export function useWebSocket(userId) {
  const ws = ref(null);
  const connected = ref(false);
  const messageHandlers = new Map();

  const connect = () => {
    if (!userId) return;

    // Extract host from API base URL or use default
    const apiBase = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';
    const host = apiBase.replace(/^https?:\/\//, '').replace(/\/api$/, '');
    const wsProtocol = apiBase.startsWith('https') ? 'wss' : 'ws';
    const wsUrl = `${wsProtocol}://${host}/ws/${userId}`;
    ws.value = new WebSocket(wsUrl);

    ws.value.onopen = () => {
      connected.value = true;
      console.log('WebSocket connected');
    };

    ws.value.onclose = () => {
      connected.value = false;
      console.log('WebSocket disconnected');
      setTimeout(() => {
        if (userId) connect();
      }, 3000);
    };

    ws.value.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const handler = messageHandlers.get(data.type);
        if (handler) {
          handler(data.data);
        }
      } catch (error) {
        console.error('WebSocket message parse error:', error);
      }
    };
  };

  const on = (type, handler) => {
    messageHandlers.set(type, handler);
  };

  const off = (type) => {
    messageHandlers.delete(type);
  };

  const disconnect = () => {
    if (ws.value) {
      ws.value.close();
      ws.value = null;
      connected.value = false;
    }
  };

  // Only register lifecycle hook if there's an active component instance
  const instance = getCurrentInstance();
  if (instance) {
    onUnmounted(() => {
      disconnect();
    });
  }

  return {
    connected,
    connect,
    disconnect,
    on,
    off,
  };
}

