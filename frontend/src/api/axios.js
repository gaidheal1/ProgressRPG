// src/api/axios.js
import axios from 'axios';

const instance = axios.create({
  baseURL: 'http://localhost:8000', // adjust to your Django backend
  withCredentials: true, // if using cookies/auth
});

export default instance;
