import React from 'react';
import styles from './Form.module.scss';
import Button from '../Button/Button';
import ButtonFrame from '../Button/ButtonFrame';
import Input from '../Input/Input';

export default function Form({
  title,
  onSubmit,
  fields = [],
  children,
  submitLabel = 'Submit',
  isSubmitting = false,
  disabled = false,
  className,
  frameClass,
}) {
  return (
    <div className={`${styles.formFrame} ${frameClass || ''}`}>
      {title && <h2 className={styles.formTitle}>{title}</h2>}

      <form onSubmit={onSubmit} className={`${styles.form} ${className || ''}`}>

        {fields.map(field => (
            <Input
              key={field.name}
              id={field.id || field.name}
              label={field.label || field.name}
              type={field.type}
              value={field.value}
              onChange={field.onChange}
              placeholder={field.placeholder}
              helpText={field.helpText}
              required={field.required}
              autoComplete={field.autoComplete}
              error={field.error}
            />
        ))}

        {children}

        <div className={styles.actions}>
          <ButtonFrame>
            <Button
              type="submit"
              className={styles.submitButton}
              disabled={isSubmitting || disabled}
            >
              {isSubmitting ? 'Submitting…' : submitLabel}
            </Button>
          </ButtonFrame>
        </div>
      </form>
    </div>
  );
}
