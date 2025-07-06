import { io } from 'socket.io-client';

// Dynamically set the socket URL based on environment
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const SOCKET_URL = isLocalhost
  ? 'http://localhost:5000'  // Changed from 8000 to 5000 to match Flask app
  : (process.env.REACT_APP_SOCKET_URL || 'wss://wordcloud-n2ew.onrender.com');

// Create a mock socket for now since WebSocket server is not implemented
const createMockSocket = () => {
  const mockSocket = {
    connected: false,
    on: () => {},
    off: () => {},  // Added missing off method
    emit: () => {},
    connect: () => {
      console.log('Mock WebSocket: Connection attempted (not implemented)');
    },
    disconnect: () => {
      console.log('Mock WebSocket: Disconnected');
    }
  };
  return mockSocket;
};

// Use mock socket for now to prevent connection errors
const socket = createMockSocket();

export default socket; 