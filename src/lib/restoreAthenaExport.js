/**
 * One-shot profile restore for a signed-in user.
 * Fetches an ATHENA_SAT_PROFILE export and replaces the account's single profile.
 */
export async function restoreAthenaExport({ supabase, userId, url }) {
  if (!supabase || !userId || !url) {
    throw new Error('Missing restore context')
  }

  const res = await fetch(url)
  if (!res.ok) throw new Error(`Could not load backup (${res.status})`)
  const payload = await res.json()
  if (payload.format !== 'ATHENA_SAT_PROFILE' || !payload.profile?.name) {
    throw new Error('Invalid Athena profile backup')
  }

  const profile = { ...payload.profile }
  // Prefer existing cloud row id so we overwrite the one-profile account cleanly.
  const { data: existing, error: listError } = await supabase
    .from('profiles')
    .select('id')
    .eq('user_id', userId)
  if (listError) throw listError

  const keepId = existing?.[0]?.id || profile.id
  profile.id = keepId

  const { id, name, ...rest } = profile
  const row = {
    id,
    user_id: userId,
    name: name || 'Profile',
    data: { ...rest, name: name || 'Profile' },
    updated_at: new Date().toISOString(),
  }

  const extraIds = (existing || []).map((r) => r.id).filter((x) => x !== id)
  if (extraIds.length) {
    const { error: delError } = await supabase
      .from('profiles')
      .delete()
      .eq('user_id', userId)
      .in('id', extraIds)
    if (delError) throw delError
  }

  const { error: upsertError } = await supabase.from('profiles').upsert(row, { onConflict: 'id' })
  if (upsertError) throw upsertError

  return profile
}
