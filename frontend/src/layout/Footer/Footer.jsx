import React from 'react';
import { useAuth } from '../../context/AuthContext';
import styles from './Footer.module.scss';
import { Link } from 'react-router-dom'; // assuming React Router
import { API_BASE_URL } from '../../config';

export default function Footer() {
  const { user, isAuthenticated } = useAuth();
  const now = new Date();

  return (
    <footer className={styles.footer}>
      {user?.is_superuser && isAuthenticated && (
        <a href={`${API_BASE_URL}/admin`} target="_blank" rel="noopener noreferrer">
          Admin Panel
        </a>
      )}
      <p>&copy; {now.getFullYear()} Progress RPG</p>
    </footer>
  );
}
