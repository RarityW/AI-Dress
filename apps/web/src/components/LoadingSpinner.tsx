interface LoadingSpinnerProps {
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export default function LoadingSpinner({
  label = '加载中…',
  size = 'md',
  className = '',
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'h-5 w-5 border-2',
    md: 'h-8 w-8 border-b-2',
    lg: 'h-12 w-12 border-3',
  }[size];

  return (
    <div
      role="status"
      aria-live="polite"
      className={`flex flex-col justify-center items-center p-4 gap-2.5 ${className}`}
    >
      <div
        aria-hidden="true"
        className={`animate-spin rounded-full border-brand-600 border-t-transparent motion-reduce:animate-none ${sizeClasses}`}
      />
      <span className="sr-only">{label}</span>
    </div>
  );
}
