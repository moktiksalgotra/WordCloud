import { io } from 'socket.io-client';

const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || 'wss://wordcloud-n2ew.onrender.com';

const socket = io(SOCKET_URL, {
  autoConnect: true,
  transports: ['websocket'],
  withCredentials: true,
});

export default socket; 