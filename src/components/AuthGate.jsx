import React, { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { BookOpen, Calculator, Mail, Target, UserRound, X } from 'lucide-react'
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

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
    </svg>
  )
}

export default function AuthGate({ onSignIn, onSignUp, onSignInWithGoogle, error, configured }) {
  const [mode, setMode] = useState('signin')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [localError, setLocalError] = useState('')
  const [confirmEmailOpen, setConfirmEmailOpen] = useState(false)

  const closeConfirmEmail = () => {
    setConfirmEmailOpen(false)
    setMode('signin')
    setPassword('')
    setLocalError('')
  }

  const submit = async (e) => {
    e.preventDefault()
    setLocalError('')
    setConfirmEmailOpen(false)
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
          setConfirmEmailOpen(true)
        }
      }
    } catch (err) {
      setLocalError(err?.message || 'Authentication failed')
    } finally {
      setBusy(false)
    }
  }

  const handleGoogleSignIn = async () => {
    setLocalError('')
    setConfirmEmailOpen(false)
    if (!configured) {
      setLocalError('Supabase is not configured. Add VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY to .env.')
      return
    }
    setBusy(true)
    try {
      await onSignInWithGoogle()
    } catch (err) {
      setLocalError(err?.message || 'Google sign-in failed')
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
            setConfirmEmailOpen(false)
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

        <motion.div
          className="auth-pitch-copy"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.1, ease: 'easeOut' }}
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

        <motion.section
          className="auth-form-col"
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.14, ease: 'easeOut' }}
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

            <button
              type="button"
              disabled={busy}
              className="auth-google-btn mt-6"
              onClick={handleGoogleSignIn}
            >
              <GoogleIcon />
              Continue with Google
            </button>

            <div className="auth-divider" aria-hidden="true">
              <span>or continue with email</span>
            </div>

            <div className="grid gap-4">
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
                  <button type="button" className="font-bold text-athena-blue" onClick={() => { setMode('signup'); setLocalError(''); setConfirmEmailOpen(false) }}>
                    Create an account
                  </button>
                </>
              ) : (
                <>
                  Already practicing?{' '}
                  <button type="button" className="font-bold text-athena-blue" onClick={() => { setMode('signin'); setLocalError(''); setConfirmEmailOpen(false) }}>
                    Sign in
                  </button>
                </>
              )}
            </p>
          </form>
        </motion.section>
      </main>
      <AnimatePresence>
        {confirmEmailOpen && (
          <motion.div
            className="profile-edit-backdrop auth-confirm-backdrop"
            role="dialog"
            aria-modal="true"
            aria-labelledby="auth-confirm-title"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeConfirmEmail}
          >
            <motion.div
              className="profile-edit-modal auth-confirm-modal"
              initial={{ opacity: 0, y: 16, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 10, scale: 0.98 }}
              transition={{ duration: 0.22, ease: 'easeOut' }}
              onClick={(e) => e.stopPropagation()}
            >
              <button
                type="button"
                className="profile-edit-close auth-confirm-close"
                onClick={closeConfirmEmail}
                aria-label="Close"
              >
                <X size={18} />
              </button>

              <div className="auth-confirm-icon" aria-hidden="true">
                <Mail size={28} strokeWidth={1.8} />
              </div>

              <h2 id="auth-confirm-title" className="auth-confirm-title">
                Check your email
              </h2>
              <p className="auth-confirm-body">
                We sent a confirmation link to{' '}
                <strong>{email.trim()}</strong>. Open it to activate your account, then sign in here.
              </p>
              <p className="auth-confirm-note">
                Didn&apos;t see it? Check spam or wait a minute, then try again.
              </p>

              <button
                type="button"
                className="auth-confirm-btn"
                onClick={closeConfirmEmail}
              >
                Got it — take me to sign in
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      <footer className="auth-copyright">
        © {new Date().getFullYear()} Athena SAT. All rights reserved.
      </footer>
      <div className="greek-key" />
    </div>
  )
}
