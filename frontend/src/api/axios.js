// src/api/axios.js
import axios from 'axios';

import { API_BASE_URL } from '../config';

const instance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // if using cookies/auth
});

export default instance;
