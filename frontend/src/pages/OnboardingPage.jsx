import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useOnboarding from '../hooks/useOnboarding';
import Form from '../components/Form/Form';
import Input from '../components/Input/Input';
import { useGame } from '../context/GameContext';

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

function Step2({ characterAvailable, character }) {
  if (!characterAvailable) {
    return (
      <p style={{ color: 'red' }}>
        No characters are currently available. Please check back later.
      </p>
    )
  } else {
    console.log("[ONBOARDING] Char:", character);
    return <p>✅ You have been linked with a character called {character.first_name}. His backstory: {character.backstory}</p>;
  }
}

function Step3() {
  return <p>🎓 Tutorial complete?</p>;
}


export default function OnboardingPage() {
  const navigate = useNavigate();
  const { step, progress, error, loading, characterAvailable } = useOnboarding();
  const [formData, setFormData] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const { character, setCharacter } = useGame();

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
    console.log("[ONBOARDING] Result:", result);

    if (result?.step === 2) {
      setCharacter(result.character);
    };
    if (result?.step === 4) navigate('/game');
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <Step1
            value={formData.display_name || ''}
            onChange={(val) => setFormData({ ...formData, display_name: val })}
            characterAvailable={characterAvailable}
          />
        );
      case 2:
        return (
          <Step2
            characterAvailable={characterAvailable}
            character={character}
          />
        );
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

      <Form
        onSubmit={handleNext}
        submitLabel={getButtonLabel()}
        isSubmitting={submitting}
        disabled={!characterAvailable && step === 2}
      >
        {renderStep()}
      </Form>
    </div>
  );
}
