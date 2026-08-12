import React, { useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Mail, ShieldCheck, X } from 'lucide-react'
import PasswordRequirements from '../PasswordRequirements'
import { isPasswordValid, passwordValidationMessage } from '../../lib/passwordRules'

function GoogleMark() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
    </svg>
  )
}

export default function AuthModal({
  open,
  mode = 'signin',
  onModeChange,
  onClose,
  onSignIn,
  onSignUp,
  onSignInWithGoogle,
  error,
  configured,
}) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [localError, setLocalError] = useState('')
  const [sentTo, setSentTo] = useState('')
  const emailRef = useRef(null)

  useEffect(() => {
    if (!open) return undefined
    const onKey = (e) => {
      if (e.key === 'Escape') onClose?.()
    }
    document.addEventListener('keydown', onKey)
    const prevOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = prevOverflow
    }
  }, [open, onClose])

  useEffect(() => {
    if (!open) return
    setLocalError('')
    setSentTo('')
    setBusy(false)
    const t = window.setTimeout(() => emailRef.current?.focus(), 120)
    return () => window.clearTimeout(t)
  }, [open, mode])

  const isSignup = mode === 'signup'

  const submit = async (e) => {
    e.preventDefault()
    setLocalError('')
    if (!configured) {
      setLocalError('Supabase is not configured. Add VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY to .env.')
      return
    }
    if (!email.trim() || !password) {
      setLocalError('Enter your email and password.')
      return
    }
    if (isSignup) {
      const message = passwordValidationMessage(password)
      if (message) {
        setLocalError(message)
        return
      }
    }
    setBusy(true)
    try {
      if (isSignup) {
        const data = await onSignUp(email.trim(), password)
        if (!data?.session) setSentTo(email.trim())
      } else {
        await onSignIn(email.trim(), password)
      }
    } catch (err) {
      setLocalError(err?.message || 'Authentication failed')
    } finally {
      setBusy(false)
    }
  }

  const google = async () => {
    setLocalError('')
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
    <AnimatePresence>
      {open ? (
        <motion.div
          className="lp-auth-backdrop"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          role="presentation"
        >
          <motion.div
            className="lp-auth-sheet"
            role="dialog"
            aria-modal="true"
            aria-label={isSignup ? 'Create your account' : 'Sign in'}
            initial={{ opacity: 0, y: 22, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 14, scale: 0.98 }}
            transition={{ duration: 0.26, ease: [0.22, 1, 0.36, 1] }}
            onClick={(e) => e.stopPropagation()}
          >
            <button type="button" className="lp-auth-close" onClick={onClose} aria-label="Close">
              <X size={18} />
            </button>

            {sentTo ? (
              <div className="lp-auth-sent">
                <div className="lp-auth-sent-icon"><Mail size={26} strokeWidth={1.9} /></div>
                <h2>Check your email</h2>
                <p>
                  We sent a confirmation link to <strong>{sentTo}</strong>. Open it to activate your
                  account, then come back and sign in.
                </p>
                <p className="lp-auth-sent-note">Not there? Check spam, then try again in a minute.</p>
                <button
                  type="button"
                  className="lp-btn lp-btn-primary lp-btn-block"
                  onClick={() => {
                    setSentTo('')
                    setPassword('')
                    onModeChange?.('signin')
                  }}
                >
                  Back to sign in
                </button>
              </div>
            ) : (
              <>
                <div className="lp-auth-head">
                  <div className="lp-auth-owl" aria-hidden="true">🦉</div>
                  <h2>{isSignup ? 'Start practicing free' : 'Welcome back'}</h2>
                  <p>
                    {isSignup
                      ? 'Build a study streak with real digital SAT–style questions.'
                      : 'Pick up your practice exactly where you left off.'}
                  </p>
                </div>

                <div className="lp-auth-tabs" role="tablist">
                  <button
                    type="button"
                    role="tab"
                    aria-selected={!isSignup}
                    className={!isSignup ? 'on' : ''}
                    onClick={() => onModeChange?.('signin')}
                  >
                    Log in
                  </button>
                  <button
                    type="button"
                    role="tab"
                    aria-selected={isSignup}
                    className={isSignup ? 'on' : ''}
                    onClick={() => onModeChange?.('signup')}
                  >
                    Sign up
                  </button>
                </div>

                <button type="button" className="lp-auth-google" onClick={google} disabled={busy}>
                  <GoogleMark />
                  Continue with Google
                </button>

                <div className="lp-auth-divider"><span>or use email</span></div>

                <form onSubmit={submit} className="lp-auth-form">
                  <label className="lp-auth-field">
                    <span>Email</span>
                    <input
                      ref={emailRef}
                      type="email"
                      autoComplete="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="you@example.com"
                    />
                  </label>

                  <label className="lp-auth-field">
                    <span>Password</span>
                    <input
                      type="password"
                      autoComplete={isSignup ? 'new-password' : 'current-password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder={isSignup ? 'Create a strong password' : 'Your password'}
                    />
                  </label>

                  {isSignup ? <PasswordRequirements password={password} /> : null}

                  {showError ? <p className="lp-auth-error">{showError}</p> : null}

                  <button
                    type="submit"
                    className="lp-btn lp-btn-primary lp-btn-block"
                    disabled={busy || (isSignup && !isPasswordValid(password))}
                  >
                    {busy ? 'Please wait…' : isSignup ? 'Create free account' : 'Log in'}
                  </button>
                </form>

                <p className="lp-auth-foot">
                  <ShieldCheck size={14} />
                  Free forever. No card required.
                </p>
              </>
            )}
          </motion.div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  )
}
