import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Form from '../../components/Form/Form';
import useRegister from '../../hooks/useRegister';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const navigate = useNavigate();
  const register = useRegister();
  const [inviteCode, setInviteCode] = useState('');
  const [agreeToTerms, setAgreeToTerms] = useState(false);


  const handleSubmit = async e => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError("Passwords don't match");
      return;
    }

    const { success, errors, errorMessage } = await register(
      email,
      password,
      confirmPassword,
      inviteCode,
      agreeToTerms
    );

    if (success) {
      navigate('/onboarding');
    } else {
      setError(errorMessage);
      setFieldErrors(errors || {});
      console.log(errorMessage);
    }
  };

  return (
    <Form
      title="📝 Register"
      fields={[
        {
          name: 'email',
          label: 'Email:',
          type: 'email',
          placeholder: 'Email',
          autoComplete: 'email',
          value: email,
          onChange: setEmail,
          required: true,
          error: fieldErrors.email?.[0],
        },
        {
          name: 'password',
          label: 'Password:',
          type: 'password',
          placeholder: 'Password',
          autoComplete: 'new-password',
          value: password,
          onChange: setPassword,
          required: true,
          error: fieldErrors.password1?.[0],
        },
        {
          name: 'confirmPassword',
          label: 'Confirm password:',
          type: 'password',
          placeholder: 'Confirm Password',
          autoComplete: 'new-password',
          value: confirmPassword,
          onChange: setConfirmPassword,
          required: true,
          error: fieldErrors.password2?.[0],
        },
        {
          name: 'invite_code',
          label: 'Invite Code:',
          type: 'text',
          placeholder: 'e.g. TESTER',
          value: inviteCode,
          onChange: setInviteCode,
          required: true,
          error: fieldErrors.invite_code?.[0],
        },
        {
          name: 'agree_to_terms',
          label: (
            <>
              I agree to the{' '}
              <a href="https://progressrpg.com/terms-of-service/" target='_blank' rel='noopener noreferrer'>
                Terms of Service
              </a>{' '}
              and{' '}
              <a href="https://progressrpg.com/privacy-policy-2/" target='_blank' rel='noopener noreferrer'>
                Privacy Policy
              </a>
              .
            </>
          ),
          type: 'checkbox',
          checked: agreeToTerms,
          onChange: e => setAgreeToTerms(e.target.checked),
          required: true,
          error: fieldErrors.agree_to_terms?.[0],
        },
      ]}
      error={error}
      onSubmit={handleSubmit}
      submitLabel="Create Account"
    />
  );
}
