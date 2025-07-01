import React from 'react';
import styles from './Form.module.scss';
import Button from '../Button/Button';
import ButtonFrame from '../Button/ButtonFrame';

export default function Form({
  title,
  onSubmit,
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
