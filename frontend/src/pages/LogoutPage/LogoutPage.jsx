import { useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function LogoutPage() {
  console.log('[LogoutPage] mounted');
  const { logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    console.log('[LogoutPage] Triggering logout...');
    logout();

    const timer = setTimeout(() => {
      console.log('[LogoutPage] Navigating to /');
      navigate('/');
    }, 800); // Slight delay for smoother UX

    return () => clearTimeout(timer); // Cleanup in case unmounted early
  }, []);

  return (
    <div>
      <h2>👋 Logging you out...</h2>
      <p>Please wait a moment.</p>
    </div>
  );
}
