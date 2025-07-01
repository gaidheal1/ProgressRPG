import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '../../../utils/api';
import { useAuth } from '../../context/AuthContext';
import Form from '../../components/Form/Form';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const fields = [
    {
      name: 'email',
      type: 'email',
      placeholder: 'Email',
      autoComplete: 'email',
      value: email,
      onChange: e => setEmail(e.target.value),
      required: true,
    },
    {
      name: 'password',
      type: 'password',
      placeholder: 'Password',
      autoComplete: 'new-password',
      value: password,
      onChange: e => setPassword(e.target.value),
      required: true,
    },
    {
      name: 'confirmPassword',
      type: 'password',
      placeholder: 'Confirm Password',
      autoComplete: 'new-password',
      value: confirmPassword,
      onChange: e => setConfirmPassword(e.target.value),
      required: true,
    },
  ];

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError("Passwords don't match");
      return;
    }

    try {
      const data = await apiFetch('/auth/registration/', {
        method: 'POST',
        body: JSON.stringify({
          email,
          password1: password,
          password2: confirmPassword,
        }),
      });

      localStorage.setItem('accessToken', data.access);
      localStorage.setItem('refreshToken', data.refresh);

      login(data.access, data.refresh);
      navigate('/onboarding');
    } catch (err) {
      console.error('[Register] Error:', err);
      setError(err.message || 'Registration failed');
    }
  };

  return (
    <Form
      title="📝 Register"
      fields={fields}
      error={error}
      onSubmit={handleSubmit}
      submitLabel="Create Account"
    />
  );
}
