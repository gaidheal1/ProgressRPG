import React from 'react';
import { useAuth } from '../../context/AuthContext';
import styles from './Footer.module.scss';
import { Link } from 'react-router-dom'; // assuming React Router

export default function Footer() {
  const { user, isAuthenticated } = useAuth();
  const now = new Date;

  return (
    <footer className={styles.footer}>
      {user?.is_staff && isAuthenticated && (
        <a href="http://localhost:8000/admin" target="_blank" rel="noopener noreferrer">
          Admin Panel
        </a>
      )}
      <p>&copy; {now.getFullYear()} Progress RPG</p>
    </footer>
  );
}
