import React from 'react';
import { useAuth } from '../hooks/useAuth'; // or however you access user data
import styles from './Footer.module.scss';
import { Link } from 'react-router-dom'; // assuming React Router

export default function Footer() {
  const { user } = useAuth(); // make sure this hook gives you `user.is_staff`

  return (
    <footer className={styles.footer}>
      {user?.is_staff && (
        <Link to="/admin" className={styles.adminLink}>
          Admin Panel
        </Link>
      )}
      <p>&copy; 2025 Progress RPG</p>
    </footer>
  );
}
