import { io } from 'socket.io-client';

const SOCKET_URL = process.env.NODE_ENV === 'production'
  ? 'wss://wordcloud-hro4.onrender.com'
  : 'ws://localhost:8000';

const socket = io(SOCKET_URL, {
  autoConnect: true,
  transports: ['websocket'],
  withCredentials: true,
});

export default socket; 