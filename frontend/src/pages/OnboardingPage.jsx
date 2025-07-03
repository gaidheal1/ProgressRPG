import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useOnboarding from '../hooks/useOnboarding';
import Form from '../components/Form/Form';
import Button from '../components/Button/Button';

export default function OnboardingPage() {
  const navigate = useNavigate();
  const { step, progress, error } = useOnboarding();
  const [formData, setFormData] = useState({});

  const handleNext = async (e) => {
    e.preventDefault(); // needed if used inside <Form>
    const result = await progress(formData);
    if (result?.step === 4) {
      navigate('/game');
    }
  };

  return (
    <div >
      <h2>🧭 Onboarding Step {step || '...'}</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}

      <Form onSubmit={handleNext}>
        {step === 1 && (
          <>
            <label htmlFor="display_name">Display Name</label>
            <input
              id="display_name"
              name="display_name"
              placeholder="Display Name"
              value={formData.display_name || ''}
              onChange={(e) =>
                setFormData({ ...formData, display_name: e.target.value })
              }
              required
            />
          </>
        )}

        {step === 2 && <p>✅ Character linked? Click to confirm.</p>}
        {step === 3 && <p>🎓 Tutorial complete?</p>}
        {!step && <p>Begin your journey through onboarding.</p>}

        <Button type="submit">
          {step === 1 && 'Continue'}
          {step === 2 && 'Confirm Character'}
          {step === 3 && 'Finish Tutorial'}
          {!step && 'Start Onboarding'}
        </Button>
      </Form>
    </div>
  );
}
