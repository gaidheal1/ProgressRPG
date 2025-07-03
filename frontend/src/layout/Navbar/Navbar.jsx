import React from 'react';
import styles from './Navbar.module.scss';
import Button from '../../components/Button/Button';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function Navbar() {
  const { isAuthenticated } = useAuth();
  return (
    <header className={styles.header}>
      <nav className={styles.navbar}>
        <div className={styles.leftLinks}>
          <Link to={isAuthenticated ? '/game' : '/'}>{isAuthenticated ? 'Game' : 'Home'}</Link>
        </div>

        <div className={styles.rightLinks}>
          {isAuthenticated ? (
            <>
              <div className={styles.link}>
                <div className={styles.textWrapper}>
                  <Link to="/logout">Log out</Link>
                </div>
              </div>
              <Button className={styles.buttonFilled}>
                <Link to="/profile">Account</Link>
              </Button>
            </>
          ) : (
            <>
              <Link to="/login">Login</Link>
              <Button className={styles.buttonFilled}>
                <Link to="/register">Sign up</Link>
              </Button>
            </>
          )}
          <div className={styles.account}>
            {/* Reserved for future icons or dropdowns */}
          </div>
        </div>

        <div className={styles.icons}>
          <Link to="/menu">Menu Icon</Link>
          <Link to="/game">Home Icon</Link>
          <Link to="/profile">Account Icon</Link>
        </div>
      </nav>
    </header>
  );
}
