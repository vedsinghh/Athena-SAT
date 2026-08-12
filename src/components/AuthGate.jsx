import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { BookOpen, Calculator, Target, UserRound } from 'lucide-react'
import PasswordRequirements from './PasswordRequirements'
import { isPasswordValid, passwordValidationMessage } from '../lib/passwordRules'

function Brand() {
  return (
    <div className="flex items-center gap-3">
      <div className="grid h-10 w-10 place-items-center text-athena-gold">
        <div className="text-4xl leading-none">🦉</div>
      </div>
      <div className="leading-none">
        <div className="brand-serif text-[27px] font-bold tracking-[.18em] text-[#315bb7]">ATHENA</div>
        <div className="mt-1 flex items-center justify-center gap-2 text-[13px] font-bold tracking-[.32em] text-athena-gold">
          <span className="h-[2px] w-8 bg-athena-gold" /> SAT <span className="h-[2px] w-8 bg-athena-gold" />
        </div>
      </div>
    </div>
  )
}

function Field({ label, children }) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-bold text-[#1b2d53]">{label}</span>
      <div className="profile-field">{children}</div>
    </label>
  )
}

export default function AuthGate({ onSignIn, onSignUp, error, configured }) {
  const [mode, setMode] = useState('signin')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [localError, setLocalError] = useState('')
  const [info, setInfo] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setLocalError('')
    setInfo('')
    if (!configured) {
      setLocalError('Supabase is not configured. Add VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY to .env.')
      return
    }
    if (!email.trim() || !password) {
      setLocalError('Enter email and password.')
      return
    }
    if (mode === 'signup') {
      const message = passwordValidationMessage(password)
      if (message) {
        setLocalError(message)
        return
      }
    }
    setBusy(true)
    try {
      if (mode === 'signin') {
        await onSignIn(email.trim(), password)
      } else {
        const data = await onSignUp(email.trim(), password)
        if (!data?.session) {
          setInfo('Check your email to confirm your account, then sign in.')
        }
      }
    } catch (err) {
      setLocalError(err?.message || 'Authentication failed')
    } finally {
      setBusy(false)
    }
  }

  const showError = localError || error

  return (
    <div className="welcome-shell auth-landing">
      <header className="welcome-header">
        <Brand />
        <button
          type="button"
          className="welcome-badge rounded-full border border-[#d5deef] px-4 py-2 text-xs font-bold tracking-[.12em] text-[#62718f] transition hover:border-athena-blue hover:text-athena-blue"
          onClick={() => {
            setMode('signup')
            setLocalError('')
            setInfo('')
          }}
        >
          FREE TO START
        </button>
      </header>

      <main className="auth-landing-main">
        <motion.div
          className="auth-pitch-visual"
          initial={{ opacity: 0, x: -12 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.45, ease: 'easeOut' }}
        >
          <div className="laurel laurel-left">❧</div>
          <div className="laurel laurel-right">❧</div>
          <motion.img
            src="/athena.png"
            alt="Athena"
            className="welcome-athena auth-pitch-athena"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.08, ease: 'easeOut' }}
          />
        </motion.div>

        <motion.section
          className="auth-form-col"
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.12, ease: 'easeOut' }}
        >
          <form onSubmit={submit} className="profile-card auth-card">
            <div className="mx-auto mb-3 grid h-12 w-12 place-items-center rounded-full bg-[#eef3ff] text-athena-blue">
              <UserRound size={24} strokeWidth={1.8} />
            </div>
            <h2 className="text-center text-[32px] font-bold tracking-[-.04em] text-athena-navy">
              {mode === 'signin' ? 'Welcome back' : 'Start practicing'}
            </h2>
            <p className="mt-1.5 text-center text-[14px] text-[#6c7892]">
              {mode === 'signin'
                ? 'Sign in to pick up your SAT practice where you left off.'
                : 'Create a free account and start building toward your goal score.'}
            </p>

            <div className="mt-6 grid gap-4">
              <Field label="Email">
                <input
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                />
              </Field>
              <Field label="Password">
                <input
                  type="password"
                  autoComplete={mode === 'signin' ? 'current-password' : 'new-password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={mode === 'signin' ? 'Your password' : 'Create a strong password'}
                />
              </Field>
              {mode === 'signup' && <PasswordRequirements password={password} />}
            </div>

            {showError && <p className="mt-2 text-sm font-medium text-red-500">{showError}</p>}
            {info && <p className="mt-2 text-sm font-medium text-athena-blue">{info}</p>}

            <button
              type="submit"
              disabled={busy || (mode === 'signup' && !isPasswordValid(password))}
              className="mt-5 h-13 w-full rounded-full bg-athena-blue py-3.5 text-[17px] font-bold text-white shadow-lg shadow-blue-100 transition hover:-translate-y-0.5 disabled:opacity-60"
            >
              {busy ? 'Please wait…' : mode === 'signin' ? 'Sign In' : 'Create free account'}
            </button>

            <p className="mt-4 text-center text-sm text-[#748096]">
              {mode === 'signin' ? (
                <>
                  New here?{' '}
                  <button type="button" className="font-bold text-athena-blue" onClick={() => { setMode('signup'); setLocalError(''); setInfo('') }}>
                    Create an account
                  </button>
                </>
              ) : (
                <>
                  Already practicing?{' '}
                  <button type="button" className="font-bold text-athena-blue" onClick={() => { setMode('signin'); setLocalError(''); setInfo('') }}>
                    Sign in
                  </button>
                </>
              )}
            </p>
          </form>
        </motion.section>

        <motion.div
          className="auth-pitch-copy"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.14, ease: 'easeOut' }}
        >
          <h1 className="auth-pitch-headline">
            Digital SAT prep that tracks every point.
          </h1>
          <p className="auth-pitch-sub">
            Practice with real digital SAT–style Math and Reading &amp; Writing questions, run timed sets, and climb toward your goal score—synced across devices.
          </p>
          <ul className="auth-pitch-points">
            <li>
              <Calculator size={18} strokeWidth={1.9} />
              <span>Real digital SAT–style questions</span>
            </li>
            <li>
              <BookOpen size={18} strokeWidth={1.9} />
              <span>Question bank with skills &amp; domains</span>
            </li>
            <li>
              <Target size={18} strokeWidth={1.9} />
              <span>Score goals, streaks &amp; analytics</span>
            </li>
          </ul>
        </motion.div>
      </main>
      <footer className="auth-copyright">
        © {new Date().getFullYear()} Athena SAT. All rights reserved.
      </footer>
      <div className="greek-key" />
    </div>
  )
}
