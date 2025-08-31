import { clsx } from 'clsx'

export function cn(...inputs) {
  return clsx(inputs)
}

// Alternative implementation without additional dependencies
export function classNames(...classes) {
  return classes.filter(Boolean).join(' ')
}
