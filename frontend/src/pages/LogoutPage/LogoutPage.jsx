import { useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function LogoutPage() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      logout(); // Clear tokens, state, etc.
      navigate('/');
    }, 800); // Slight delay for smoother UX

    return () => clearTimeout(timer); // Cleanup in case unmounted early
  }, [logout, navigate]);

  return (
    <div className="centered-page">
      <h2>👋 Logging you out...</h2>
      <p>Please wait a moment.</p>
    </div>
  );
}
