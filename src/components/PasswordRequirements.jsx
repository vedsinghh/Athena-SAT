import React from 'react'
import { Check } from 'lucide-react'
import { getPasswordChecks, PASSWORD_MIN_LENGTH } from '../lib/passwordRules'

const RULES = [
  {
    key: 'minLength',
    label: `At least ${PASSWORD_MIN_LENGTH} characters`,
  },
  {
    key: 'mixedChars',
    label: 'Mix of letters, numbers, and symbols',
  },
]

export default function PasswordRequirements({ password }) {
  const checks = getPasswordChecks(password)

  return (
    <ul className="password-requirements" aria-live="polite">
      {RULES.map(({ key, label }) => {
        const met = checks[key]
        return (
          <li key={key} className={`password-requirement ${met ? 'met' : ''}`}>
            <span className="password-requirement-icon" aria-hidden="true">
              {met ? <Check size={11} strokeWidth={3} /> : null}
            </span>
            <span>{label}</span>
          </li>
        )
      })}
    </ul>
  )
}
