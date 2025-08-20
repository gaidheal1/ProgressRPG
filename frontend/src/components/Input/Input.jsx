import styles from './Input.module.scss';

export default function Input({
  id,
  label,
  type = 'text',
  value,
  onChange,
  placeholder = '',
  helpText = '',
  error = '',
  required = false,
  autoComplete,
  checked,
  minLength,
  maxLength,
}) {
  const isCheckbox = type === 'checkbox';

  return (
    <div className={styles.inputGroup}>
      {label && (
        <label htmlFor={id} className={styles.label}>
          {label} {required && <span className={styles.required}>*</span>}
        </label>
      )}

      <input
        id={id}
        type={type}
        className={`${styles.inputField} ${error ? styles.inputError : ''}`}
        value={isCheckbox ? undefined : value}
        checked={isCheckbox ? checked : undefined}
        onChange={(e) => {
          if (onChange) {
            isCheckbox ? onChange(e) : onChange(e.target.value);
          }
        }}
        placeholder={placeholder}
        aria-invalid={!!error}
        autoComplete={autoComplete}
        required={required}
        minLength={minLength}
        maxLength={maxLength}
      />

      {helpText && !error && (
        <p className={styles.helpText}>{helpText}</p>
      )}
      {error && <p className={styles.errorText}>{error}</p>}
    </div>
  );
}

/* EXAMPLE USAGE

import Input from './Input';

<Input
  id="display-name"
  label="Display Name"
  value={formData.display_name}
  onChange={(val) => setFormData({ ...formData, display_name: val })}
  placeholder="Enter your display name"
  helpText="This will be visible to others"
  error={formData.display_name === '' ? 'Name is required' : ''}
/>
 */
