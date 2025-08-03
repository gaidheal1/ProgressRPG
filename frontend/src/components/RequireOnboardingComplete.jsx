import { Navigate } from 'react-router-dom';
import useOnboarding from '../hooks/useOnboarding';

export default function RequireOnboardingComplete({ children }) {
  const { step, loading } = useOnboarding();

  if (loading || step === undefined) return <p>Loading onboarding status…</p>;

  return step < 4 ? <Navigate to="/onboarding" replace /> : children;
}
