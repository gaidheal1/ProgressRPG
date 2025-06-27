
// src/App.jsx or a test component
import { useEffect } from 'react';
import axios from 'axios';

console.log("Testing.. App.jsx");

function App() {
  useEffect(() => {
    axios.post('http://localhost:8000/api/v1/debug/', {
      message: 'App mounted!',
      timestamp: new Date().toISOString(),
    }).catch(() => {});
  }, []);

  return (
    <div>
      <h1>Hello from App!</h1>
    </div>
  );
}

export default App;
