import { useCallback, useEffect, useRef, useState } from 'react'
import {
  fetchCloudProfiles,
  hasPendingLocalImport,
  markLocalImportDone,
  readActiveProfileId,
  readLocalProfilesRaw,
  skipLocalImport,
  syncCloudProfiles,
  withValidProfileIds,
  writeActiveProfileId,
  writeLocalProfiles,
} from '../lib/profileStorage'

const SAVE_DEBOUNCE_MS = 500

export function useProfiles({ userId, normalizeProfiles, onSyncError } = {}) {
  const [profiles, setProfiles] = useState([])
  const [activeId, setActiveIdState] = useState(null)
  const [loading, setLoading] = useState(Boolean(userId))
  const [syncing, setSyncing] = useState(false)
  const [importOffer, setImportOffer] = useState(null)
  const profilesRef = useRef(profiles)
  const saveTimer = useRef(null)
  const loadedForUser = useRef(null)

  useEffect(() => {
    profilesRef.current = profiles
  }, [profiles])

  const setActiveId = useCallback((id) => {
    setActiveIdState(id)
    writeActiveProfileId(id)
  }, [])

  const resolveActive = useCallback((list) => {
    if (!list?.length) return null
    const stored = readActiveProfileId()
    if (stored && list.some((p) => p.id === stored)) return stored
    return list[0].id
  }, [])

  const flushCloud = useCallback(async (list) => {
    if (!userId) return
    setSyncing(true)
    try {
      await syncCloudProfiles(userId, list)
    } catch (err) {
      onSyncError?.(err?.message || 'Could not sync profiles')
    } finally {
      setSyncing(false)
    }
  }, [userId, onSyncError])

  const scheduleCloudSave = useCallback((list) => {
    if (!userId) return
    window.clearTimeout(saveTimer.current)
    saveTimer.current = window.setTimeout(() => {
      flushCloud(list)
    }, SAVE_DEBOUNCE_MS)
  }, [userId, flushCloud])

  useEffect(() => () => window.clearTimeout(saveTimer.current), [])

  useEffect(() => {
    if (!userId) {
      loadedForUser.current = null
      setProfiles([])
      setActiveIdState(null)
      setImportOffer(null)
      setLoading(false)
      return undefined
    }

    if (loadedForUser.current === userId) return undefined

    let cancelled = false
    setLoading(true)

    ;(async () => {
      try {
        const cloud = await fetchCloudProfiles(userId)
        if (cancelled) return
        let normalized = withValidProfileIds(
          normalizeProfiles ? normalizeProfiles(cloud) : cloud,
        )
        // One account → one profile: keep active/first, drop extras from cloud.
        if (normalized.length > 1) {
          const keepId = resolveActive(normalized)
          normalized = normalized.filter((p) => p.id === keepId).slice(0, 1)
          await syncCloudProfiles(userId, normalized)
        }
        loadedForUser.current = userId
        setProfiles(normalized)
        writeLocalProfiles(normalized)
        const nextActive = resolveActive(normalized)
        setActiveIdState(nextActive)
        writeActiveProfileId(nextActive)

        if (!normalized.length && hasPendingLocalImport(userId)) {
          const local = readLocalProfilesRaw()
          const localNorm = withValidProfileIds(
            normalizeProfiles ? normalizeProfiles(local) : local,
          )
          if (localNorm.length) setImportOffer(localNorm)
        } else {
          setImportOffer(null)
          if (normalized.length) markLocalImportDone(userId)
        }
      } catch (err) {
        if (!cancelled) {
          onSyncError?.(err?.message || 'Could not load profiles')
          // Fall back to local cache so the session isn't a hard brick.
          const local = readLocalProfilesRaw()
          const localNorm = withValidProfileIds(
            normalizeProfiles ? normalizeProfiles(local) : local,
          )
          loadedForUser.current = userId
          setProfiles(localNorm)
          setActiveIdState(resolveActive(localNorm))
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()

    return () => {
      cancelled = true
    }
  }, [userId, normalizeProfiles, onSyncError, resolveActive])

  const persistProfiles = useCallback((nextOrUpdater) => {
    setProfiles((prev) => {
      const raw = typeof nextOrUpdater === 'function' ? nextOrUpdater(prev) : nextOrUpdater
      const next = withValidProfileIds(raw)
      writeLocalProfiles(next)
      scheduleCloudSave(next)
      return next
    })
  }, [scheduleCloudSave])

  const acceptLocalImport = useCallback(async () => {
    if (!userId || !importOffer?.length) return
    const preferredId = readActiveProfileId()
    const chosen = importOffer.find((p) => p.id === preferredId) || importOffer[0]
    const next = withValidProfileIds([chosen])
    setProfiles(next)
    writeLocalProfiles(next)
    setActiveIdState(next[0].id)
    writeActiveProfileId(next[0].id)
    setImportOffer(null)
    markLocalImportDone(userId)
    await flushCloud(next)
  }, [userId, importOffer, flushCloud])

  const declineLocalImport = useCallback(() => {
    if (!userId) return
    skipLocalImport(userId)
    setImportOffer(null)
  }, [userId])

  return {
    profiles,
    setProfiles,
    activeId,
    setActiveId,
    loading,
    syncing,
    persistProfiles,
    importOffer,
    acceptLocalImport,
    declineLocalImport,
  }
}
