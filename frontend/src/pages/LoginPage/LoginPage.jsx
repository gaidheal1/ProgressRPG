import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useLogin from '../../hooks/useLogin';
import { useAuth } from '../../context/AuthContext';
import Form from '../../components/Form/Form';
import styles from './LoginPage.module.scss';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const loginWithJwt = useLogin();
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    const result = await loginWithJwt(email, password);
    setSubmitting(false);

    if (result.success) {
      login(result.tokens.access, result.tokens.refresh);

      if (result.onboarding_step && result.onboarding_step < 4) {
        navigate('/onboarding');
      } else {
        navigate('/game');
      }
    } else {
      setError(result.error || 'Login failed');
    }
  };

  return (
    <Form
      title="🔐 Log In"
      onSubmit={handleSubmit}
      isSubmitting={submitting}
      submitLabel="Log In"
      className={styles.form}
    >
      {error && <p className={styles.error}>{error}</p>}
      <input
        type="email"
        name="email"
        placeholder="Email"
        autoComplete='email'
        value={email}
        onChange={e => setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        name="password"
        placeholder="Password"
        autoComplete='current-password'
        value={password}
        onChange={e => setPassword(e.target.value)}
        required
      />
      <p className={styles.footer}>
        New here? <a href="/register">Create an account</a>
      </p>
    </Form>
  );
}
