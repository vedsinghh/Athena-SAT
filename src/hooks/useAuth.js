import { useEffect, useState } from 'react'
import { getSiteUrl, isSupabaseConfigured, supabase } from '../lib/supabase'

function isAlreadyRegisteredError(err) {
  const msg = String(err?.message || '').toLowerCase()
  return msg.includes('already registered') || msg.includes('already been registered') || msg.includes('user already exists')
}

function isDuplicateConfirmedSignup(data) {
  return Boolean(
    data?.user
    && !data?.session
    && Array.isArray(data.user.identities)
    && data.user.identities.length === 0
  )
}

export function userHasPasswordLogin(user) {
  if (!user) return false
  const providers = user.app_metadata?.providers
  if (Array.isArray(providers) && providers.length) {
    return providers.includes('email')
  }
  const identities = user.identities
  if (Array.isArray(identities) && identities.length) {
    return identities.some((id) => id?.provider === 'email')
  }
  return false
}

export function useAuth() {
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(isSupabaseConfigured)
  const [error, setError] = useState('')
  const [recovery, setRecovery] = useState(false)

  useEffect(() => {
    if (!supabase) {
      setLoading(false)
      return undefined
    }

    let mounted = true
    supabase.auth.getSession().then(({ data, error: err }) => {
      if (!mounted) return
      if (err) setError(err.message)
      setSession(data.session ?? null)
      if (typeof window !== 'undefined' && window.location.hash.includes('type=recovery')) {
        setRecovery(true)
      }
      setLoading(false)
    })

    const { data: sub } = supabase.auth.onAuthStateChange((event, next) => {
      if (event === 'PASSWORD_RECOVERY') setRecovery(true)
      setSession(next)
      setLoading(false)
    })

    return () => {
      mounted = false
      sub?.subscription?.unsubscribe()
    }
  }, [])

  const signIn = async (email, password) => {
    setError('')
    if (!supabase) throw new Error('Supabase is not configured')
    const { data, error: err } = await supabase.auth.signInWithPassword({ email, password })
    if (err) {
      setError(err.message)
      throw err
    }
    setSession(data.session)
    return data
  }

  const signUp = async (email, password) => {
    setError('')
    if (!supabase) throw new Error('Supabase is not configured')
    const siteUrl = getSiteUrl()
    const { data, error: err } = await supabase.auth.signUp({
      email,
      password,
      options: siteUrl ? { emailRedirectTo: `${siteUrl}/` } : undefined,
    })
    if (err) {
      if (isAlreadyRegisteredError(err)) {
        return { user: null, session: null, existingAccount: true }
      }
      setError(err.message)
      throw err
    }
    if (isDuplicateConfirmedSignup(data)) {
      return { ...data, existingAccount: true }
    }
    if (data.session) setSession(data.session)
    return data
  }

  const signInWithGoogle = async () => {
    setError('')
    if (!supabase) throw new Error('Supabase is not configured')
    const siteUrl = getSiteUrl()
    const { error: err } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: siteUrl ? { redirectTo: `${siteUrl}/` } : undefined,
    })
    if (err) {
      setError(err.message)
      throw err
    }
  }

  const signOut = async () => {
    setError('')
    if (!supabase) return
    const { error: err } = await supabase.auth.signOut()
    if (err) {
      setError(err.message)
      throw err
    }
    setSession(null)
    setRecovery(false)
  }

  const requestPasswordReset = async (email) => {
    setError('')
    if (!supabase) throw new Error('Supabase is not configured')
    const siteUrl = getSiteUrl()
    const { error: err } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: siteUrl ? `${siteUrl}/` : undefined,
    })
    if (err) {
      setError(err.message)
      throw err
    }
  }

  const completePasswordReset = async (newPassword) => {
    setError('')
    if (!supabase) throw new Error('Supabase is not configured')
    const { data, error: err } = await supabase.auth.updateUser({ password: newPassword })
    if (err) {
      setError(err.message)
      throw err
    }
    setRecovery(false)
    if (typeof window !== 'undefined') {
      const clean = `${window.location.pathname}${window.location.search}`
      window.history.replaceState({}, '', clean || '/')
    }
    if (data.session) setSession(data.session)
    return data
  }

  const updatePassword = async (currentPassword, newPassword) => {
    setError('')
    if (!supabase) throw new Error('Supabase is not configured')
    const email = session?.user?.email
    if (!email) throw new Error('No signed-in account')

    const { error: reauthError } = await supabase.auth.signInWithPassword({
      email,
      password: currentPassword,
    })
    if (reauthError) {
      const message = 'Current password is incorrect.'
      setError(message)
      throw new Error(message)
    }

    const { data, error: err } = await supabase.auth.updateUser({ password: newPassword })
    if (err) {
      setError(err.message)
      throw err
    }
    if (data.session) setSession(data.session)
    return data
  }

  return {
    session,
    user: session?.user ?? null,
    loading,
    error,
    configured: isSupabaseConfigured,
    signIn,
    signUp,
    signInWithGoogle,
    signOut,
    requestPasswordReset,
    completePasswordReset,
    updatePassword,
    recovery,
  }
}
