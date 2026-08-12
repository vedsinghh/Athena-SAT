import { useEffect, useState } from 'react'
import { isSupabaseConfigured, supabase } from '../lib/supabase'

export function useAuth() {
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(isSupabaseConfigured)
  const [error, setError] = useState('')

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
      setLoading(false)
    })

    const { data: sub } = supabase.auth.onAuthStateChange((_event, next) => {
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
    const { data, error: err } = await supabase.auth.signUp({ email, password })
    if (err) {
      setError(err.message)
      throw err
    }
    if (data.session) setSession(data.session)
    return data
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
    signOut,
    updatePassword,
  }
}
