import React from 'react';
import classNames from 'classnames';
import styles from './Button.module.scss';

export default function Button({
  children,
  variant = 'primary', // or 'secondary', 'ghost', etc.
  //fullWidth = false,
  icon = null,
  as = 'button', // can be 'a' or 'button'
  href,
  onClick,
  className,
  frameClass,
  ...props
}) {
  const Component = as === 'a' ? 'a' : 'button';

  return (
    <div className={classNames(styles.frame, frameClass)}>
      <Component
        className={classNames(
          styles.button,
          styles[variant],
          // { [styles.fullWidth]: fullWidth },
          className
        )}
        href={as === 'a' ? href : undefined}
        onClick={onClick}
        {...props}
      >
        {icon && <span className={styles.icon}>{icon}</span>}
        {children}
      </Component>
    </div>
  );
}

{/* USAGE EXAMPLES
     <Button>Default Button</Button>

<Button variant="secondary" fullWidth>
  Full Width Secondary
</Button>

<Button as="a" href="/register" icon={<UserIcon />}>
  Sign Up
</Button>
 */}
