import { supabase } from './supabase'

export const STORAGE_KEY = 'athena_sat_profiles_react_v1'
export const ACTIVE_KEY = 'athena_sat_active_profile_react_v1'

function importFlagKey(userId) {
  return `athena_sat_local_import_done_v1_${userId}`
}

export function readLocalProfilesRaw() {
  try {
    const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export function writeLocalProfiles(profiles) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(profiles))
}

export function readActiveProfileId() {
  try {
    return localStorage.getItem(ACTIVE_KEY)
  } catch {
    return null
  }
}

export function writeActiveProfileId(id) {
  if (id) localStorage.setItem(ACTIVE_KEY, id)
  else localStorage.removeItem(ACTIVE_KEY)
}

export function hasPendingLocalImport(userId) {
  if (!userId) return false
  try {
    if (localStorage.getItem(importFlagKey(userId))) return false
  } catch {
    return false
  }
  return readLocalProfilesRaw().length > 0
}

export function markLocalImportDone(userId) {
  if (!userId) return
  try {
    localStorage.setItem(importFlagKey(userId), '1')
  } catch {
    /* ignore */
  }
}

export function skipLocalImport(userId) {
  markLocalImportDone(userId)
}

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i

export function ensureProfileId(id) {
  if (id && UUID_RE.test(String(id))) return String(id)
  return crypto.randomUUID?.() || '00000000-0000-4000-8000-000000000000'
}

function rowToProfile(row) {
  const data = row?.data && typeof row.data === 'object' ? row.data : {}
  return {
    ...data,
    id: row.id,
    name: row.name || data.name || 'Profile',
  }
}

function profileToRow(profile, userId) {
  const id = ensureProfileId(profile.id)
  const name = profile.name || 'Profile'
  const { id: _ignore, name: _n, ...rest } = profile
  return {
    id,
    user_id: userId,
    name,
    data: { ...rest, name },
    updated_at: new Date().toISOString(),
  }
}

/** Ensure every profile has a Postgres-safe UUID primary key. */
export function withValidProfileIds(profiles) {
  return (profiles || []).map((p) => {
    const id = ensureProfileId(p.id)
    return id === p.id ? p : { ...p, id }
  })
}

export async function fetchCloudProfiles(userId) {
  if (!supabase || !userId) return []
  const { data, error } = await supabase
    .from('profiles')
    .select('id, name, data, updated_at, created_at')
    .eq('user_id', userId)
    .order('created_at', { ascending: true })
  if (error) throw error
  return (data || []).map(rowToProfile)
}

export async function upsertCloudProfiles(userId, profiles) {
  if (!supabase || !userId) return
  const rows = profiles.map((p) => profileToRow(p, userId))
  if (!rows.length) return
  const { error } = await supabase.from('profiles').upsert(rows, { onConflict: 'id' })
  if (error) throw error
}

export async function deleteCloudProfiles(userId, ids) {
  if (!supabase || !userId || !ids?.length) return
  const { error } = await supabase
    .from('profiles')
    .delete()
    .eq('user_id', userId)
    .in('id', ids)
  if (error) throw error
}

/** Last-write-wins full sync: upsert current set, delete rows no longer present. */
export async function syncCloudProfiles(userId, profiles) {
  if (!supabase || !userId) return
  const { data: existing, error: listError } = await supabase
    .from('profiles')
    .select('id')
    .eq('user_id', userId)
  if (listError) throw listError

  const nextIds = new Set(profiles.map((p) => p.id))
  const toDelete = (existing || []).map((r) => r.id).filter((id) => !nextIds.has(id))
  if (toDelete.length) await deleteCloudProfiles(userId, toDelete)
  if (profiles.length) await upsertCloudProfiles(userId, profiles)
}
