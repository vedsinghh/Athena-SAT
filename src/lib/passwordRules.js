export const PASSWORD_MIN_LENGTH = 9

export function getPasswordChecks(password = '') {
  const hasLetter = /[a-zA-Z]/.test(password)
  const hasNumber = /\d/.test(password)
  const hasSymbol = /[^a-zA-Z0-9]/.test(password)
  return {
    minLength: password.length >= PASSWORD_MIN_LENGTH,
    mixedChars: hasLetter && hasNumber && hasSymbol,
  }
}

export function isPasswordValid(password) {
  const checks = getPasswordChecks(password)
  return checks.minLength && checks.mixedChars
}

export function passwordValidationMessage(password) {
  const checks = getPasswordChecks(password)
  if (!checks.minLength) return `Password must be at least ${PASSWORD_MIN_LENGTH} characters.`
  if (!checks.mixedChars) return 'Password must include letters, numbers, and symbols.'
  return null
}
