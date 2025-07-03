import { io } from 'socket.io-client';

const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || 'http://localhost:8000';

const socket = io(SOCKET_URL, {
  autoConnect: true,
  transports: ['websocket'],
  withCredentials: true,
});

export default socket; 