import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useOnboarding from '../hooks/useOnboarding';
import Form from '../components/Form/Form';
import Button from '../components/Button/Button';
import Input from '../components/Input/Input';

function Step0() {
  return <p>Begin your journey through onboarding.</p>;
}

function Step1({ value, onChange }) {
  return (
    <>
      <Input
        id="display-name"
        label="Display Name"
        value={value}
        onChange={onChange}
        placeholder="Enter your display name"
        helpText="This will be visible to others"
        required
      />
    </>
  );
}

function Step2() {
  return <p>✅ Character linked? Click to confirm.</p>;
}

function Step3() {
  return <p>🎓 Tutorial complete?</p>;
}


export default function OnboardingPage() {
  console.log('OnboardingPage render');
  const navigate = useNavigate();
  //const navigate = () => {};
  const { step, progress, error, loading } = useOnboarding();
  const [formData, setFormData] = useState({});
  const [submitting, setSubmitting] = useState(false);


  // Auto-redirect if onboarding is already done
  useEffect(() => {
    if (step === 4) {
      navigate('/game');
    }
  }, [step, navigate]);

  if (loading || step === undefined) return <p>Loading onboarding status…</p>;

  const handleNext = async (e) => {
    e.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    const result = await progress(formData);
    setSubmitting(false);
    if (result?.step === 4) navigate('/game');
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <Step1
            value={formData.display_name || ''}
            onChange={(val) => setFormData({ ...formData, display_name: val })}
          />
        );
      case 2:
        return <Step2 />;
      case 3:
        return <Step3 />;
      default:
        return <Step0 />;
    }
  };


  //const renderStep = () => <Step0 />;

  const getButtonLabel = () => {
    switch (step) {
      case 1:
        return 'Continue';
      case 2:
        return 'Confirm Character';
      case 3:
        return 'Finish Tutorial';
      default:
        return 'Start Onboarding';
    }
  };

  return (
    <div>
      <h1>🧭 Onboarding Step {step ?? '...'}</h1>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      <Form onSubmit={handleNext}>
        {renderStep()}

        <Button type="submit" disabled={submitting}>
          {submitting ? 'Submitting...' : getButtonLabel()}
        </Button>
      </Form>
    </div>
  );
}
