import React, { useEffect, useMemo, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { AnimatePresence, animate, motion } from 'framer-motion'
import {
  AlertTriangle, BarChart3, BookOpen, Calculator, CalendarDays,
  ChevronDown, ChevronRight, ClipboardList, Clock, ExternalLink, Filter,
  Flame, FunctionSquare, Highlighter, Home, Import, Lightbulb, List, Pause, PenLine, Radical, Save,
  Settings, Shuffle, Sparkles, SpellCheck2, Target, Triangle, Trophy, Trash2, UserRound, X, CheckCircle2, Check,
  FileText, Vault, Building2, ChevronUp, ListFilter
} from 'lucide-react'
import mathQuestions from './data/mathQuestions.json'
import readingQuestions from './data/readingQuestions.json'
import mathSkillCounts from './data/mathSkillCounts.json'
import readingSkillCounts from './data/readingSkillCounts.json'

const QUESTION_POOLS = ['Collegeboard Summer 2026']
const DEFAULT_QUESTION_POOL = QUESTION_POOLS[0]
const STAT_NA = 'N/A'

const READING_DOMAIN_NAMES = [
  'Information and Ideas',
  'Craft and Structure',
  'Expression of Ideas',
  'Standard English Conventions',
]

const MATH_DOMAIN_NAMES = [
  'Algebra',
  'Advanced Math',
  'Problem-Solving and Data Analysis',
  'Geometry and Trigonometry',
]

function isValidStatNumber(value) {
  return typeof value === 'number' && Number.isFinite(value)
}

function formatStatPct(value) {
  return isValidStatNumber(value) ? `${Math.round(value)}%` : STAT_NA
}

function formatStatCount(value) {
  return isValidStatNumber(value) ? value : STAT_NA
}

function formatStatText(value) {
  if (value == null) return STAT_NA
  const text = String(value).trim()
  return text ? text : STAT_NA
}

function accuracyFromEntries(entries) {
  if (!entries?.length) return null
  const correct = entries.filter((item) => item.correct).length
  return Math.round((correct / entries.length) * 100)
}

function deriveOverallAccuracy(progress) {
  return accuracyFromEntries(Object.values(progress || {}))
}

function deriveSubjectStats(progress, subject, domainNames, questions = []) {
  const entries = Object.values(progress || {}).filter((item) => item.subject === subject)
  const answered = entries.length
  const accuracy = accuracyFromEntries(entries)

  const domains = domainNames.map((name) => {
    const total = questions.filter((q) => q.domain === name).length
    const domainEntries = entries.filter((item) => item.domain === name)
    const done = domainEntries.length
    return {
      name,
      done,
      total,
      pct: accuracyFromEntries(domainEntries),
    }
  })

  const ranked = domains
    .filter((d) => d.done > 0 && isValidStatNumber(d.pct))
    .sort((a, b) => b.pct - a.pct)

  const strengths = ranked.filter((d) => d.pct >= 70).slice(0, 2).map((d) => d.name)
  const needsWork = [...ranked]
    .filter((d) => d.pct < 60)
    .sort((a, b) => a.pct - b.pct)
    .slice(0, 2)
    .map((d) => d.name)
  const weakestDomain = ranked.length >= 2
    ? [...ranked].sort((a, b) => a.pct - b.pct)[0].name
    : null

  return {
    accuracy,
    answered,
    weekAccuracyDelta: null,
    weekAnswered: null,
    avgTime: null,
    avgTimeDelta: null,
    weakestDomain,
    strengths,
    needsWork,
    domains,
  }
}

function formatAvgTime(seconds) {
  if (!isValidStatNumber(seconds) || seconds < 0) return STAT_NA
  const total = Math.round(seconds)
  const m = Math.floor(total / 60)
  const s = total % 60
  if (m <= 0) return `${s}s`
  return `${m}:${String(s).padStart(2, '0')}`
}

/** Aggregate accuracy / answered / avg time from progress history for a subject. */
function deriveSubjectActivityStats(history, subject, { dayKey = null } = {}) {
  let correct = 0
  let answered = 0
  let timeSum = 0
  let timeCount = 0

  ;(history || []).forEach((entry) => {
    if (entry?.subject !== subject) return
    if (dayKey && localDayKey(entry.createdAt) !== dayKey) return

    if (entry.type === 'bank') {
      answered += 1
      if (entry.correct) correct += 1
      if (isValidStatNumber(entry.elapsed) && entry.elapsed > 0) {
        timeSum += entry.elapsed
        timeCount += 1
      }
      return
    }

    if (entry.type !== 'set') return
    const items = Array.isArray(entry.items)
      ? entry.items.filter((item) => item && item.correct != null)
      : []

    if (items.length) {
      let itemTimeCount = 0
      items.forEach((item) => {
        answered += 1
        if (item.correct) correct += 1
        if (isValidStatNumber(item.elapsed) && item.elapsed > 0) {
          timeSum += item.elapsed
          itemTimeCount += 1
        }
      })
      if (!itemTimeCount && isValidStatNumber(entry.elapsed) && entry.elapsed > 0) {
        timeSum += entry.elapsed
        timeCount += items.length
      } else {
        timeCount += itemTimeCount
      }
      return
    }

    const count = Number(entry.answered) || Number(entry.total) || 0
    if (!count) return
    answered += count
    correct += Number(entry.correct) || 0
    if (isValidStatNumber(entry.elapsed) && entry.elapsed > 0) {
      timeSum += entry.elapsed
      timeCount += count
    }
  })

  return {
    answered,
    accuracy: answered ? Math.round((correct / answered) * 100) : null,
    avgTimeSec: timeCount ? Math.round(timeSum / timeCount) : null,
  }
}

function localDayKey(value = new Date()) {
  const d = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(d.getTime())) return null
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function computeStreakFromHistory(history) {
  const days = [...new Set(
    (history || []).map((item) => localDayKey(item.createdAt)).filter(Boolean),
  )].sort()

  if (!days.length) return { streak: 0, bestStreak: 0 }

  let best = 1
  let run = 1
  for (let i = 1; i < days.length; i += 1) {
    const prev = new Date(`${days[i - 1]}T12:00:00`)
    const cur = new Date(`${days[i]}T12:00:00`)
    const diff = Math.round((cur - prev) / 86400000)
    if (diff === 1) {
      run += 1
      best = Math.max(best, run)
    } else {
      run = 1
    }
  }

  const today = localDayKey(new Date())
  const yesterdayDate = new Date()
  yesterdayDate.setDate(yesterdayDate.getDate() - 1)
  const yesterday = localDayKey(yesterdayDate)
  const daySet = new Set(days)

  let streak = 0
  let cursor = null
  if (daySet.has(today)) cursor = new Date()
  else if (daySet.has(yesterday)) cursor = yesterdayDate

  while (cursor && daySet.has(localDayKey(cursor))) {
    streak += 1
    cursor = new Date(cursor)
    cursor.setDate(cursor.getDate() - 1)
  }

  return { streak, bestStreak: Math.max(best, streak) }
}

function historyToActivityItem(entry) {
  if (entry.type === 'bank') {
    return {
      title: entry.title,
      sub: entry.sub,
      meta: entry.correct ? 'Correct' : 'Incorrect',
      tone: entry.subject === 'math' ? 'green' : 'purple',
    }
  }
  return {
    title: entry.title,
    sub: entry.sub,
    meta: entry.meta || (isValidStatNumber(entry.accuracy) ? `Score: ${entry.accuracy}%` : `Score: ${STAT_NA}`),
    tone: entry.subject === 'math' ? 'green' : 'purple',
  }
}

function applyStreakFromHistory(profile) {
  const { streak, bestStreak } = computeStreakFromHistory(profile.progressHistory)
  return {
    ...profile,
    streak,
    bestStreak,
  }
}

function appendProgressHistory(profile, entry) {
  const progressHistory = [entry, ...(profile.progressHistory || [])].slice(0, 250)
  const activity = [historyToActivityItem(entry), ...(profile.activity || [])].slice(0, 40)
  return applyStreakFromHistory({
    ...profile,
    progressHistory,
    activity,
  })
}

function applyBankHistoryLine(profile, question, answer, subject, { elapsed = null } = {}) {
  const correct = isAnswerCorrect(question, answer)
  if (correct == null) return profile
  const isMath = subject === 'math'
  const timeSpent = isValidStatNumber(elapsed) && elapsed > 0 ? Math.round(elapsed) : null
  return appendProgressHistory(profile, {
    id: crypto.randomUUID?.() || `${Date.now()}-${Math.random()}`,
    type: 'bank',
    subject,
    title: isMath ? 'Question Bank · Math' : 'Question Bank · Reading',
    sub: [question.domain, question.skill || question.topic].filter(Boolean).join(' · ') || 'Practice question',
    correct: Boolean(correct),
    questionId: String(question.id),
    answer: answer ?? null,
    difficulty: question.difficulty || null,
    elapsed: timeSpent,
    createdAt: new Date().toISOString(),
  })
}

function lookupQuestion(questionId, subject) {
  if (questionId == null || questionId === '') return null
  const list = subject === 'math' ? mathQuestions : readingQuestions
  return list.find((q) => String(q.id) === String(questionId)) || null
}

function applyPracticeSetReport(profile, {
  subject,
  questions = [],
  answers = [],
  elapsed = 0,
  questionTimes = [],
  config = {},
}) {
  const answeredPairs = questions
    .map((q, i) => ({
      q,
      answer: answers[i],
      correct: isAnswerCorrect(q, answers[i]),
      elapsed: isValidStatNumber(questionTimes[i]) ? Math.max(0, Math.round(questionTimes[i])) : null,
    }))
    .filter((row) => row.correct != null)
  const correct = answeredPairs.filter((row) => row.correct).length
  const answeredCount = answeredPairs.length
  const accuracy = answeredCount ? Math.round((correct / answeredCount) * 100) : null
  const isMath = subject === 'math'
  const domains = config.domains?.length
    ? config.domains
    : [...new Set(answeredPairs.map((row) => row.q.domain).filter(Boolean))]
  const domainLabel = domains.length === 1
    ? domains[0]
    : (domains.length > 1 ? `${domains.length} Domains` : (config.domain || 'Mixed'))
  const difficulty = Array.isArray(config.difficulties)
    ? (config.difficulties.length === 1
      ? config.difficulties[0]
      : (config.difficulties.length ? `${config.difficulties.length} levels` : null))
    : (config.difficulty || null)

  let next = profile
  answeredPairs.forEach(({ q, answer }) => {
    next = applyQuestionCompletion(next, q, answer, subject)
  })

  // Don't create empty practice-set tiles (e.g. Strict Mode remount / End with nothing answered).
  if (!answeredCount) return next

  const timed = answeredPairs.filter((row) => isValidStatNumber(row.elapsed) && row.elapsed > 0)
  const timedSum = timed.reduce((sum, row) => sum + row.elapsed, 0)
  const fallbackPerQuestion = elapsed > 0
    ? Math.max(1, Math.round(elapsed / answeredCount))
    : null
  const avgTime = timed.length
    ? Math.round(timedSum / timed.length)
    : fallbackPerQuestion

  return appendProgressHistory(next, {
    id: crypto.randomUUID?.() || `${Date.now()}-${Math.random()}`,
    type: 'set',
    subject,
    title: isMath ? 'Math Practice Set' : 'Reading & Writing Practice Set',
    sub: [domainLabel, difficulty, `${answeredCount} Questions`].filter(Boolean).join(' · '),
    meta: accuracy != null ? `Score: ${accuracy}%` : `Score: ${STAT_NA}`,
    correct,
    answered: answeredCount,
    total: answeredCount,
    accuracy,
    elapsed: elapsed || timedSum || 0,
    avgTime,
    domains,
    items: answeredPairs.map(({ q, answer, correct: isCorrect, elapsed: itemElapsed }) => ({
      questionId: String(q.id),
      answer: answer ?? null,
      correct: isCorrect,
      domain: q.domain || null,
      skill: q.skill || q.topic || null,
      elapsed: (isValidStatNumber(itemElapsed) && itemElapsed > 0) ? itemElapsed : fallbackPerQuestion,
    })),
    createdAt: new Date().toISOString(),
  })
}

function formatHistoryWhen(iso) {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return STAT_NA
  return d.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

const STORAGE_KEY = 'athena_sat_profiles_react_v1'
const ACTIVE_KEY = 'athena_sat_active_profile_react_v1'
const FILE_VERSION = 1

const GRADE_OPTIONS = [
  '',
  '8th Grade',
  '9th Grade',
  '10th Grade',
  '11th Grade',
  '12th Grade',
  'College / Other',
]

function normalizeSatScore(value) {
  if (value === '' || value == null) return null
  const n = Number(value)
  if (!Number.isFinite(n)) return null
  return n
}

function isValidSatScore(value, { allowEmpty = false } = {}) {
  if (value === '' || value == null) return allowEmpty
  const n = Number(value)
  return Number.isFinite(n) && n >= 400 && n <= 1600 && n % 10 === 0
}

function profileBestScore(profile) {
  const best = normalizeSatScore(profile?.bestScore)
  if (best != null) return best
  return normalizeSatScore(profile?.currentScore) ?? null
}

const demoProfile = {
  id: 'demo-srishti',
  name: 'Srishti Singh',
  grade: '12th Grade',
  school: '',
  testDate: '',
  goalScore: 1550,
  bestScore: 1420,
  currentScore: 1420,
  streak: 0,
  bestStreak: 0,
  overallAccuracy: null,
  reading: {
    accuracy: null,
    answered: 0,
    weekAccuracyDelta: null,
    weekAnswered: null,
    avgTime: null,
    avgTimeDelta: null,
    weakestDomain: null,
    strengths: [],
    needsWork: [],
    domains: READING_DOMAIN_NAMES.map((name) => ({ name, pct: null, done: 0, total: 0 })),
  },
  math: {
    accuracy: null,
    answered: 0,
    weekAccuracyDelta: null,
    weekAnswered: null,
    avgTime: null,
    avgTimeDelta: null,
    weakestDomain: null,
    strengths: [],
    needsWork: [],
    domains: MATH_DOMAIN_NAMES.map((name) => ({ name, pct: null, done: 0, total: 0 })),
    progressPoints: [],
  },
  activity: [],
  progressHistory: [],
  upcoming: [
    { title: 'Practice Test 3', sub: 'Full Length · May 10, 2026', type: 'test' },
    { title: 'Math – Advanced', sub: 'Mixed Practice · 20 Qs', type: 'math' },
    { title: 'Reading – Craft & Structure', sub: 'Focus Practice · 15 Qs', type: 'reading' },
  ],
  createdAt: new Date().toISOString()
}

function isEmptyPracticeSetEntry(entry) {
  if (!entry || entry.type !== 'set') return false
  const answered = Number(entry.answered) || 0
  const total = Number(entry.total) || 0
  if (answered === 0 || total === 0) return true
  const items = Array.isArray(entry.items) ? entry.items : []
  if (entry.accuracy == null && !entry.elapsed && !items.length) return true
  return false
}

function scrubEmptyPracticeSets(profile) {
  const history = Array.isArray(profile.progressHistory) ? profile.progressHistory : []
  const cleaned = history.filter((entry) => !isEmptyPracticeSetEntry(entry))
  if (cleaned.length === history.length) {
    return {
      ...profile,
      progressHistory: history,
    }
  }
  return applyStreakFromHistory({
    ...profile,
    progressHistory: cleaned,
    activity: cleaned.map(historyToActivityItem).slice(0, 40),
  })
}

function safeReadProfiles() {
  let profiles = []
  try {
    const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    if (Array.isArray(parsed)) profiles = parsed
  } catch {
    /* ignore */
  }
  const normalized = profiles.map((p) => scrubEmptyPracticeSets(applyStreakFromHistory({
    ...p,
    progressHistory: Array.isArray(p.progressHistory) ? p.progressHistory : [],
  })))
  // Persist scrubbed empty set entries so they stay gone.
  try {
    const before = JSON.stringify(profiles.map((p) => p.progressHistory || []))
    const after = JSON.stringify(normalized.map((p) => p.progressHistory || []))
    if (before !== after) localStorage.setItem(STORAGE_KEY, JSON.stringify(normalized))
  } catch {
    /* ignore */
  }
  return normalized
}

function resolveActiveProfileId(profiles) {
  const stored = localStorage.getItem(ACTIVE_KEY)
  if (stored && profiles.some((p) => p.id === stored)) return stored
  return null
}

function saveProfiles(profiles) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(profiles))
}

function makeStarterProfile({ name, grade, goalScore, bestScore, school, testDate }) {
  const goal = goalScore ? Number(goalScore) : 1550
  const best = bestScore ? Number(bestScore) : null
  return {
    ...demoProfile,
    id: crypto.randomUUID?.() || `${Date.now()}-${Math.random()}`,
    name: name.trim(),
    grade: grade || '',
    school: (school || '').trim(),
    testDate: testDate || '',
    goalScore: goal,
    bestScore: best,
    currentScore: best ?? 1200,
    streak: 0,
    bestStreak: 0,
    overallAccuracy: null,
    reading: { accuracy: null, answered: 0, strengths: [], needsWork: [] },
    math: { accuracy: null, answered: 0, strengths: [], needsWork: [] },
    activity: [],
    progressHistory: [],
    upcoming: demoProfile.upcoming,
    createdAt: new Date().toISOString()
  }
}

export default function App() {
  const [profiles, setProfiles] = useState(() => safeReadProfiles())
  const [activeId, setActiveId] = useState(() => resolveActiveProfileId(safeReadProfiles()))
  const [screen, setScreen] = useState(() => (
    resolveActiveProfileId(safeReadProfiles()) ? 'dashboard' : 'welcome'
  ))
  const [profilesOpen, setProfilesOpen] = useState(false)
  const [toast, setToast] = useState('')

  const activeProfile = useMemo(
    () => (activeId ? profiles.find((p) => p.id === activeId) || null : null),
    [profiles, activeId]
  )

  const persistProfiles = (next) => {
    setProfiles(next)
    saveProfiles(next)
  }

  const openProfile = (profile) => {
    setActiveId(profile.id)
    localStorage.setItem(ACTIVE_KEY, profile.id)
    setScreen('dashboard')
    setProfilesOpen(false)
    showToast(`Opened ${profile.name}`)
  }

  const createProfile = (profile) => {
    const next = [...profiles, profile]
    persistProfiles(next)
    openProfile(profile)
    showToast(`Welcome, ${profile.name}!`)
  }

  const updateProfile = (profileId, patch) => {
    const next = profiles.map((p) => {
      if (p.id !== profileId) return p
      const updated = { ...p, ...patch }
      if (Object.prototype.hasOwnProperty.call(patch, 'bestScore')) {
        updated.currentScore = patch.bestScore ?? updated.currentScore
      }
      return updated
    })
    persistProfiles(next)
    showToast('Profile updated')
  }

  const deleteProfile = (profileId) => {
    const target = profiles.find((p) => p.id === profileId)
    if (!target) return
    const next = profiles.filter((p) => p.id !== profileId)
    setProfilesOpen(false)
    if (!next.length) {
      persistProfiles([])
      setActiveId(null)
      localStorage.removeItem(ACTIVE_KEY)
      setScreen('welcome')
      showToast('Profile deleted')
      return
    }
    persistProfiles(next)
    if (activeId === profileId) {
      const fallback = next[0]
      setActiveId(fallback.id)
      localStorage.setItem(ACTIVE_KEY, fallback.id)
      setScreen('dashboard')
    }
    showToast(`${target.name} deleted`)
  }

  const goToDashboard = () => {
    setScreen('dashboard')
    setProfilesOpen(false)
  }

  const showToast = (text) => {
    setToast(text)
    window.clearTimeout(window.__athenaToast)
    window.__athenaToast = window.setTimeout(() => setToast(''), 2200)
  }

  return (
    <div className="min-h-screen bg-white text-[#14284f]">
      <AnimatePresence mode="wait">
        {screen === 'welcome' || !activeProfile ? (
          <motion.div
            key="welcome"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, scale: .99 }}
          >
            <WelcomePage
              profiles={profiles}
              onCreate={createProfile}
              onOpenProfiles={() => setProfilesOpen(true)}
            />
          </motion.div>
        ) : (
          <motion.div
            key="dashboard"
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <Dashboard
              profile={activeProfile}
              onGoDashboard={goToDashboard}
              onOpenProfiles={() => setProfilesOpen(true)}
              onNewProfile={() => {
                setScreen('welcome')
                setActiveId(null)
                localStorage.removeItem(ACTIVE_KEY)
              }}
              onUpdateProfile={updateProfile}
              onDeleteProfile={deleteProfile}
              onCompleteQuestion={(question, answer, subject, meta) => {
                persistProfiles(profiles.map((p) => {
                  if (p.id !== activeId) return p
                  let next = p
                  // Generated practice sets defer progress until the session ends.
                  if (meta?.updateProgress !== false) {
                    next = applyQuestionCompletion(next, question, answer, subject)
                  }
                  if (meta?.logHistory) {
                    next = applyBankHistoryLine(next, question, answer, subject, {
                      elapsed: meta?.elapsed,
                    })
                  }
                  return next
                }))
              }}
              onCompleteSession={(payload) => {
                persistProfiles(profiles.map((p) => (
                  p.id === activeId ? applyPracticeSetReport(p, payload) : p
                )))
              }}
            />
          </motion.div>
        )}
      </AnimatePresence>

      <ProfileDrawer
        open={profilesOpen}
        profiles={profiles}
        onClose={() => setProfilesOpen(false)}
        onOpen={openProfile}
        onImport={(p) => {
          const next = [...profiles, p]
          persistProfiles(next)
          openProfile(p)
        }}
        onToast={showToast}
      />

      <AnimatePresence>
        {toast && (
          <motion.div
            className="fixed bottom-5 left-1/2 z-[100] -translate-x-1/2 rounded-full bg-[#12346f] px-5 py-3 text-sm font-semibold text-white shadow-xl"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
          >
            {toast}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

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

function WelcomePage({ profiles, onCreate, onOpenProfiles }) {
  const [name, setName] = useState('')
  const [goalScore, setGoalScore] = useState('')
  const [error, setError] = useState('')

  const submit = (e) => {
    e.preventDefault()
    if (!name.trim()) return setError('Enter a profile name.')
    if (goalScore && !isValidSatScore(goalScore)) {
      return setError('Goal score must be 400–1600 in increments of 10.')
    }
    setError('')
    onCreate(makeStarterProfile({ name, goalScore }))
  }

  return (
    <div className="welcome-shell">
      <header className="welcome-header">
        <Brand />
        <button onClick={onOpenProfiles} className="rounded-full border border-athena-blue px-5 py-2.5 text-sm font-bold text-athena-blue transition hover:bg-blue-50">
          {profiles.length ? `Profiles (${profiles.length})` : 'Profiles'}
        </button>
      </header>

      <main className="welcome-main">
        <section className="relative flex h-full items-center justify-center overflow-hidden">
          <div className="laurel laurel-left">❧</div>
          <div className="laurel laurel-right">❧</div>
          <img src="/athena.png" alt="Athena mascot" className="welcome-athena" />
          <div className="speech-bubble">
            <span>Let’s start<br />your SAT<br />journey!</span>
          </div>
        </section>

        <section className="flex h-full items-center justify-center">
          <form onSubmit={submit} className="profile-card">
            <div className="mx-auto mb-4 grid h-14 w-14 place-items-center rounded-full bg-[#eef3ff] text-athena-blue">
              <UserRound size={28} strokeWidth={1.8} />
            </div>
            <h1 className="text-center text-[38px] font-bold tracking-[-.04em] text-athena-navy">Create Your Profile</h1>
            <p className="mt-2 text-center text-[15px] text-[#6c7892]">Your progress is saved locally on this device.</p>

            <div className="mt-7 grid gap-4">
              <Field label="Profile Name">
                <input value={name} onChange={e => setName(e.target.value)} placeholder="Enter a name" />
              </Field>
              <Field label="Goal Score (Optional)">
                <input value={goalScore} onChange={e => setGoalScore(e.target.value)} inputMode="numeric" placeholder="Enter your target SAT score" />
              </Field>
            </div>

            {error && <p className="mt-2 text-sm font-medium text-red-500">{error}</p>}

            <button type="submit" className="mt-5 h-13 w-full rounded-full bg-athena-blue py-3.5 text-[17px] font-bold text-white shadow-lg shadow-blue-100 transition hover:-translate-y-0.5">
              Create Profile
            </button>

            <p className="mt-4 text-center text-xs text-[#748096]">
              Saved in this browser. Export a .athena backup anytime.
            </p>
          </form>
        </section>
      </main>
      <div className="greek-key" />
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

function PeeringAthena({ pageKey }) {
  const hostRef = useRef(null)
  const restoreRef = useRef(null)
  const [mount, setMount] = useState(null)
  const [phase, setPhase] = useState('in') // in | away | gone

  useEffect(() => {
    let cancelled = false
    setMount(null)
    setPhase('in')

    const cleanupHost = () => {
      const restore = restoreRef.current
      if (restore?.host) {
        restore.host.style.position = restore.position
        restore.host.style.overflow = restore.overflow
        restore.host.classList.remove('athena-peek-host')
      }
      restoreRef.current = null
      hostRef.current = null
    }

    cleanupHost()

    const dismiss = () => {
      cleanupHost()
      setMount(null)
    }

    const pick = () => {
      if (cancelled) return
      if (document.querySelector('.practice-page')) return

      const root = document.querySelector('.dashboard-main')
      if (!root) return

      const candidates = [...root.querySelectorAll('.card, .progress-set-tile, .qbank-subject, .math-stat')]
        .filter((el) => {
          // Keep page heroes (Progress / Reading / etc.) clear of peeks.
          if (
            el.classList.contains('progress-summary-card')
            || el.closest('.progress-hero')
            || el.closest('.math-top')
            || el.closest('.qbank-hero')
          ) return false
          const rect = el.getBoundingClientRect()
          return (
            rect.width >= 150
            && rect.height >= 72
            && rect.top >= 180
            && rect.top < window.innerHeight - 48
            && rect.left < window.innerWidth - 48
            && rect.right > 48
          )
        })

      if (!candidates.length) return

      const host = candidates[Math.floor(Math.random() * candidates.length)]
      const computed = getComputedStyle(host)
      restoreRef.current = {
        host,
        position: host.style.position,
        overflow: host.style.overflow,
      }
      if (computed.position === 'static') host.style.position = 'relative'
      host.style.overflow = 'visible'
      host.classList.add('athena-peek-host')
      hostRef.current = host

      setMount({
        leftPct: 20 + Math.floor(Math.random() * 50),
        tick: Date.now(),
      })
      setPhase('in')
    }

    const timer = window.setTimeout(() => {
      requestAnimationFrame(pick)
    }, 90)

    const root = document.querySelector('.dashboard-main')
    const observer = root
      ? new MutationObserver(() => {
          if (cancelled) return
          if (document.querySelector('.practice-page')) {
            dismiss()
            return
          }
          if (hostRef.current && !hostRef.current.isConnected) dismiss()
        })
      : null
    if (observer && root) observer.observe(root, { childList: true, subtree: true })

    return () => {
      cancelled = true
      window.clearTimeout(timer)
      observer?.disconnect()
      cleanupHost()
      setMount(null)
    }
  }, [pageKey])

  if (!mount || !hostRef.current || phase === 'gone') return null

  const fleeing = phase === 'away'
  const peekTransition = { type: 'spring', stiffness: 360, damping: 20, mass: 0.75 }

  return createPortal(
    <motion.button
      type="button"
      className="athena-peek-wrap"
      style={{ left: `${mount.leftPct}%` }}
      aria-label="Dismiss Athena"
      title="Click to scare her off"
      onClick={(e) => {
        e.stopPropagation()
        if (phase !== 'in') return
        setPhase('away')
      }}
    >
      <motion.div
        key={mount.tick}
        className="athena-peek-motion"
        initial={{ y: '108%' }}
        animate={{ y: fleeing ? '108%' : '0%' }}
        transition={fleeing ? { ...peekTransition, stiffness: 400, damping: 24 } : { ...peekTransition, delay: 0.06 }}
        onAnimationComplete={() => {
          if (!fleeing) return
          const restore = restoreRef.current
          if (restore?.host) {
            restore.host.style.position = restore.position
            restore.host.style.overflow = restore.overflow
            restore.host.classList.remove('athena-peek-host')
          }
          restoreRef.current = null
          hostRef.current = null
          setPhase('gone')
          setMount(null)
        }}
      >
        <motion.img
          src="/athena-peek.png"
          alt=""
          draggable={false}
          animate={fleeing ? { y: 0 } : { y: [0, -3.5, 0] }}
          transition={
            fleeing
              ? { duration: 0.05 }
              : { duration: 2.6, repeat: Infinity, ease: 'easeInOut', delay: 0.85 }
          }
        />
      </motion.div>
    </motion.button>,
    hostRef.current,
  )
}

function Dashboard({
  profile,
  onGoDashboard,
  onOpenProfiles,
  onNewProfile,
  onUpdateProfile,
  onDeleteProfile,
  onCompleteQuestion,
  onCompleteSession,
}) {
  const [page, setPage] = useState('dashboard')

  const goDashboard = () => {
    setPage('dashboard')
    onGoDashboard()
  }

  const navigate = (key) => {
    if (key === 'dashboard') goDashboard()
    else if (key === 'profiles') onOpenProfiles()
    else setPage(key)
  }

  return (
    <div className={`dashboard-shell ${page === 'dashboard' ? 'dashboard-home' : ''}`}>
      <div className="dashboard-laurel dashboard-laurel-left" aria-hidden="true">❧</div>
      <div className="dashboard-laurel dashboard-laurel-right" aria-hidden="true">❧</div>
      <Sidebar
        page={page}
        profile={profile}
        onNavigate={navigate}
        onOpenProfiles={onOpenProfiles}
        onNewProfile={onNewProfile}
        onUpdateProfile={onUpdateProfile}
        onDeleteProfile={onDeleteProfile}
      />
      <main className="dashboard-main">
        {page === 'dashboard' ? (
        <div className="dashboard-grid">
          <section className="min-w-0 relative">
            <div className="mb-5">
              <h1 className="text-[34px] font-bold tracking-[-.04em] text-athena-navy">Welcome back, {profile.name.split(' ')[0]}! 👋</h1>
              <p className="mt-1 text-[#687590]">Ready to reach your target score?</p>
            </div>

            <div className="grid grid-cols-[1.55fr_.7fr] gap-4">
              <ScoreProgress profile={profile} />
              <AccuracyCard profile={profile} />
            </div>

            <div className="mt-4 relative grid grid-cols-2 gap-4">
              <div className="subject-laurel" aria-hidden="true">❧</div>
              <SectionCard
                title="Reading"
                icon={<BookOpen size={20} />}
                accent="purple"
                data={deriveSubjectStats(profile.qbankProgress, 'reading', READING_DOMAIN_NAMES, readingQuestions)}
                onStart={() => setPage('Reading')}
              />
              <SectionCard
                title="Math"
                icon={<Calculator size={20} />}
                accent="green"
                data={deriveSubjectStats(profile.qbankProgress, 'math', MATH_DOMAIN_NAMES, mathQuestions)}
                onStart={() => setPage('Math')}
              />
            </div>

            <div className="mt-4 grid grid-cols-[1.15fr_.85fr] gap-4">
              <RecentActivity profile={profile} onViewAll={() => setPage('Progress')} />
              <QuickActions />
            </div>
          </section>

          <aside className="space-y-4">
            <StreakCard profile={profile} />
            <UpcomingCard profile={profile} />
            <CoachCard />
          </aside>
        </div>
        ) : page === 'Math' ? (
          <MathPage
            profile={profile}
            onCompleteQuestion={onCompleteQuestion}
            onCompleteSession={onCompleteSession}
          />
        ) : page === 'Reading' ? (
          <ReadingPage
            profile={profile}
            onCompleteQuestion={onCompleteQuestion}
            onCompleteSession={onCompleteSession}
          />
        ) : page === 'Question Bank' ? (
          <QuestionBankPage
            profile={profile}
            onOpenMath={() => setPage('Question Bank Math')}
            onOpenReading={() => setPage('Question Bank Reading')}
          />
        ) : page === 'Question Bank Math' ? (
          <QuestionBankMathPage
            profile={profile}
            onBack={() => setPage('Question Bank')}
            onCompleteQuestion={onCompleteQuestion}
          />
        ) : page === 'Question Bank Reading' ? (
          <QuestionBankReadingPage
            profile={profile}
            onBack={() => setPage('Question Bank')}
            onCompleteQuestion={onCompleteQuestion}
          />
        ) : page === 'Progress' ? (
          <ProgressPage profile={profile} />
        ) : (
          <PlaceholderPage title={page} onGoDashboard={goDashboard} />
        )}
        <PeeringAthena pageKey={page} />
      </main>
    </div>
  )
}

function ProfileEditModal({ open, profile, onClose, onSave }) {
  const [name, setName] = useState('')
  const [grade, setGrade] = useState('')
  const [school, setSchool] = useState('')
  const [testDate, setTestDate] = useState('')
  const [goalScore, setGoalScore] = useState('')
  const [bestScore, setBestScore] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (!open || !profile) return
    setName(profile.name || '')
    setGrade(profile.grade || '')
    setSchool(profile.school || '')
    setTestDate(profile.testDate || '')
    setGoalScore(profile.goalScore != null ? String(profile.goalScore) : '')
    const best = profileBestScore(profile)
    setBestScore(best != null ? String(best) : '')
    setError('')
  }, [open, profile])

  useEffect(() => {
    if (!open) return undefined
    const onKey = (e) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [open, onClose])

  if (!open) return null

  const submit = (e) => {
    e.preventDefault()
    if (!name.trim()) return setError('Enter a profile name.')
    if (!isValidSatScore(goalScore, { allowEmpty: false })) {
      return setError('Goal score must be 400–1600 in increments of 10.')
    }
    if (!isValidSatScore(bestScore, { allowEmpty: true })) {
      return setError('Best SAT score must be 400–1600 in increments of 10.')
    }
    setError('')
    onSave({
      name: name.trim(),
      grade,
      school: school.trim(),
      testDate,
      goalScore: Number(goalScore),
      bestScore: bestScore === '' ? null : Number(bestScore),
    })
  }

  return (
    <div className="profile-edit-backdrop" onClick={onClose} role="presentation">
      <form
        className="profile-edit-modal"
        onClick={(e) => e.stopPropagation()}
        onSubmit={submit}
      >
        <div className="profile-edit-head">
          <div>
            <div className="profile-edit-eyebrow">Personal info</div>
            <h3>Edit profile</h3>
          </div>
          <button type="button" className="profile-edit-close" onClick={onClose} aria-label="Close">
            <X size={18} />
          </button>
        </div>

        <div className="profile-edit-grid">
          <Field label="Name">
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" autoFocus />
          </Field>
          <Field label="Grade level">
            <select value={grade} onChange={(e) => setGrade(e.target.value)}>
              <option value="">Select grade</option>
              {GRADE_OPTIONS.filter(Boolean).map((g) => (
                <option key={g} value={g}>{g}</option>
              ))}
            </select>
          </Field>
          <Field label="School (optional)">
            <input value={school} onChange={(e) => setSchool(e.target.value)} placeholder="High school or program" />
          </Field>
          <Field label="Next test date (optional)">
            <input type="date" value={testDate} onChange={(e) => setTestDate(e.target.value)} />
          </Field>
          <Field label="Best SAT score">
            <input
              value={bestScore}
              onChange={(e) => setBestScore(e.target.value)}
              inputMode="numeric"
              placeholder="e.g. 1420"
            />
          </Field>
          <Field label="SAT goal">
            <input
              value={goalScore}
              onChange={(e) => setGoalScore(e.target.value)}
              inputMode="numeric"
              placeholder="e.g. 1550"
            />
          </Field>
        </div>

        {error && <p className="profile-edit-error">{error}</p>}

        <div className="profile-edit-actions">
          <button type="button" className="profile-edit-cancel" onClick={onClose}>Cancel</button>
          <button type="submit" className="profile-edit-save">Save changes</button>
        </div>
      </form>
    </div>
  )
}

function PlaceholderPage({ title, onGoDashboard }) {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <h1 className="text-[34px] font-bold tracking-[-.04em] text-athena-navy">{title}</h1>
      <p className="mt-2 text-[#687590]">This section is coming soon.</p>
      <button onClick={onGoDashboard} className="mt-6 rounded-full bg-athena-blue px-6 py-3 text-sm font-bold text-white transition hover:-translate-y-0.5">
        Back to Dashboard
      </button>
    </div>
  )
}

function QuestionBankPage({ profile, onOpenMath, onOpenReading }) {
  const progress = profile.qbankProgress || {}
  const readingTotal = readingQuestions.length
  const mathTotal = mathQuestions.length
  const readingSolved = Object.values(progress).filter((item) => item.subject === 'reading').length
  const mathSolved = Object.values(progress).filter((item) => item.subject === 'math').length
  const readingPct = readingTotal ? Math.round((readingSolved / readingTotal) * 100) : 0
  const mathPct = mathTotal ? Math.round((mathSolved / mathTotal) * 100) : 0
  const attempted = readingSolved + mathSolved
  const accuracy = deriveOverallAccuracy(progress)
  const streak = computeStreakFromHistory(profile.progressHistory).streak

  return (
    <div className="qbank-page">
      <header className="qbank-hero">
        <div className="qbank-hero-badge" aria-hidden="true">
          <Vault size={22} strokeWidth={2.1} />
        </div>
        <div>
          <h1>Question Bank</h1>
          <p>Practice {readingTotal + mathTotal} official-style SAT questions and track your progress.</p>
        </div>
      </header>

      <div className="qbank-subjects">
        <div className="card qbank-subject qbank-subject-reading">
          <div className="qbank-subject-copy">
            <h2>Reading & Writing</h2>
            <div className="qbank-subject-stats">
              <span>{readingSolved} of {readingTotal} solved</span>
              <strong>{readingPct}%</strong>
            </div>
            <div className="qbank-subject-bar">
              <motion.div
                className="qbank-subject-fill"
                initial={{ width: 0 }}
                animate={{ width: `${readingPct}%` }}
                transition={{ duration: 0.8 }}
              />
            </div>
            <button type="button" className="qbank-open-btn reading" onClick={onOpenReading}>
              Open <ChevronRight size={16} />
            </button>
          </div>
          <div className="qbank-subject-art" aria-hidden="true">
            <img src="/athena-qbank-rw.png" alt="" className="qbank-art-athena reading" />
          </div>
        </div>

        <div className="card qbank-subject qbank-subject-math">
          <div className="qbank-subject-copy">
            <h2>Math</h2>
            <div className="qbank-subject-stats">
              <span>{mathSolved} of {mathTotal} solved</span>
              <strong>{mathPct}%</strong>
            </div>
            <div className="qbank-subject-bar">
              <motion.div
                className="qbank-subject-fill"
                initial={{ width: 0 }}
                animate={{ width: `${mathPct}%` }}
                transition={{ duration: 0.8 }}
              />
            </div>
            <button type="button" className="qbank-open-btn math" onClick={onOpenMath}>
              Open <ChevronRight size={16} />
            </button>
          </div>
          <div className="qbank-subject-art" aria-hidden="true">
            <img src="/athena-qbank-math.png" alt="" className="qbank-art-athena math" />
          </div>
        </div>
      </div>

      <section className="qbank-analytics">
        <div className="qbank-analytics-head">
          <div className="qbank-analytics-title">
            <span className="qbank-analytics-icon" aria-hidden="true">
              <BarChart3 size={18} strokeWidth={2.2} />
            </span>
            <div>
              <h3>Question Analytics</h3>
              <p>Track your overall performance and study consistency.</p>
            </div>
          </div>
          <button type="button" className="qbank-view-all">View all analytics →</button>
        </div>

        <div className="qbank-metrics">
          <div className="qbank-metric qbank-metric-purple">
            <div className="qbank-metric-icon"><ClipboardList size={18} /></div>
            <div className="qbank-metric-label">Questions Attempted</div>
            <div className="qbank-metric-value">{attempted}</div>
          </div>
          <div className="qbank-metric qbank-metric-green">
            <div className="qbank-metric-icon"><Target size={18} /></div>
            <div className="qbank-metric-label">Current Accuracy</div>
            <div className="qbank-metric-value">{formatStatPct(accuracy)}</div>
          </div>
          <div className="qbank-metric qbank-metric-indigo">
            <div className="qbank-metric-icon"><Flame size={18} /></div>
            <div className="qbank-metric-label">Study Streak</div>
            <div className="qbank-metric-value">{formatStatCount(streak)}</div>
          </div>
        </div>
      </section>
    </div>
  )
}

function buildQBankTopics(sections, skillCounts) {
  return sections.map((section) => {
    const counts = skillCounts[section.name]?.skills || {}
    return {
      ...section,
      skills: section.skills.map((skill) => ({
        ...skill,
        total: counts[skill.name] ?? skill.total,
        done: Math.min(skill.done, counts[skill.name] ?? skill.total),
        accuracy: skill.done ? skill.accuracy : null,
      })),
    }
  })
}

const MATH_QBANK_TOPICS = buildQBankTopics([
  {
    id: 'algebra',
    name: 'Algebra',
    skills: [
      { name: 'Linear equations in one variable', done: 0, total: 0, accuracy: 0 },
      { name: 'Linear equations in two variables', done: 0, total: 0, accuracy: 0 },
      { name: 'Linear functions', done: 0, total: 0, accuracy: 0 },
      { name: 'Systems of two linear equations in two variables', done: 0, total: 0, accuracy: 0 },
      { name: 'Linear inequalities in one or two variables', done: 0, total: 0, accuracy: 0 },
    ],
  },
  {
    id: 'advanced',
    name: 'Advanced Math',
    skills: [
      { name: 'Equivalent expressions', done: 0, total: 0, accuracy: 0 },
      { name: 'Nonlinear equations in one variable and systems of equations in two variables', done: 0, total: 0, accuracy: 0 },
      { name: 'Nonlinear functions', done: 0, total: 0, accuracy: 0 },
    ],
  },
  {
    id: 'psda',
    name: 'Problem-Solving and Data Analysis',
    skills: [
      { name: 'Ratios, rates, proportional relationships, and units', done: 0, total: 0, accuracy: 0 },
      { name: 'Percentages', done: 0, total: 0, accuracy: 0 },
      { name: 'One-variable data: distributions and measures of center and spread', done: 0, total: 0, accuracy: 0 },
      { name: 'Two-variable data: models and scatterplots', done: 0, total: 0, accuracy: 0 },
      { name: 'Probability and conditional probability', done: 0, total: 0, accuracy: 0 },
      { name: 'Inference from sample statistics and margin of error', done: 0, total: 0, accuracy: 0 },
      { name: 'Evaluating statistical claims: observational studies and experiments', done: 0, total: 0, accuracy: 0 },
    ],
  },
  {
    id: 'geo',
    name: 'Geometry and Trigonometry',
    skills: [
      { name: 'Area and volume', done: 0, total: 0, accuracy: 0 },
      { name: 'Lines, angles, and triangles', done: 0, total: 0, accuracy: 0 },
      { name: 'Right triangles and trigonometry', done: 0, total: 0, accuracy: 0 },
      { name: 'Circles', done: 0, total: 0, accuracy: 0 },
    ],
  },
], mathSkillCounts)

const READING_QBANK_TOPICS = buildQBankTopics([
  {
    id: 'info',
    name: 'Information and Ideas',
    skills: [
      { name: 'Central Ideas and Details', done: 0, total: 0, accuracy: 0 },
      { name: 'Command of Evidence', done: 0, total: 0, accuracy: 0 },
      { name: 'Inferences', done: 0, total: 0, accuracy: 0 },
    ],
  },
  {
    id: 'craft',
    name: 'Craft and Structure',
    skills: [
      { name: 'Words in Context', done: 0, total: 0, accuracy: 0 },
      { name: 'Text Structure and Purpose', done: 0, total: 0, accuracy: 0 },
      { name: 'Cross-Text Connections', done: 0, total: 0, accuracy: 0 },
    ],
  },
  {
    id: 'expression',
    name: 'Expression of Ideas',
    skills: [
      { name: 'Rhetorical Synthesis', done: 0, total: 0, accuracy: 0 },
      { name: 'Transitions', done: 0, total: 0, accuracy: 0 },
    ],
  },
  {
    id: 'conventions',
    name: 'Standard English Conventions',
    skills: [
      { name: 'Boundaries', done: 0, total: 0, accuracy: 0 },
      { name: 'Form, Structure, and Sense', done: 0, total: 0, accuracy: 0 },
    ],
  },
], readingSkillCounts)

function QuestionBankSubjectPage({
  subject,
  subjectKey,
  topics,
  questions = [],
  progress = {},
  badge,
  decoSrc,
  tone = 'math',
  onBack,
  onStartPractice,
}) {
  const [openSections, setOpenSections] = useState(() => (
    Object.fromEntries(topics.map((t, i) => [t.id, i === 0]))
  ))
  const [selected, setSelected] = useState([])
  const [openMenu, setOpenMenu] = useState(null)
  const [filterDifficulties, setFilterDifficulties] = useState(['Easy', 'Medium', 'Hard'])
  const [completedFilter, setCompletedFilter] = useState('all')
  const [filterPools, setFilterPools] = useState([DEFAULT_QUESTION_POOL])
  const [shuffle, setShuffle] = useState(false)
  const filtersRef = useRef(null)

  const availablePools = useMemo(() => {
    const fromData = [...new Set(questions.map((q) => q.pool).filter(Boolean))]
    return [...new Set([...QUESTION_POOLS, ...fromData])]
  }, [questions])

  useEffect(() => {
    if (!openMenu) return undefined
    const onPointerDown = (event) => {
      if (filtersRef.current && !filtersRef.current.contains(event.target)) {
        setOpenMenu(null)
      }
    }
    const onKeyDown = (event) => {
      if (event.key === 'Escape') setOpenMenu(null)
    }
    document.addEventListener('pointerdown', onPointerDown)
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('pointerdown', onPointerDown)
      document.removeEventListener('keydown', onKeyDown)
    }
  }, [openMenu])

  const filteredTopics = useMemo(() => {
    const levels = filterDifficulties
    return topics
      .map((section) => {
        const skills = section.skills
          .map((skill) => {
            const matching = questions.filter((q) => (
              q.domain === section.name
              && q.skill === skill.name
              && (!filterPools.length || filterPools.includes(q.pool || DEFAULT_QUESTION_POOL))
              && (!levels.length || levels.includes(q.difficulty))
            ))
            const total = matching.length
            const skillProgress = countSkillProgress(
              progress,
              subjectKey,
              section.name,
              skill.name,
              matching.map((q) => q.id),
            )
            return {
              ...skill,
              total,
              done: skillProgress.done,
              accuracy: skillProgress.accuracy,
            }
          })
          .filter((skill) => {
            if (skill.total === 0) return false
            if (completedFilter === 'completed') return skill.done >= skill.total
            if (completedFilter === 'in_progress') return skill.done > 0 && skill.done < skill.total
            if (completedFilter === 'not_started') return skill.done === 0
            return true
          })
        return { ...section, skills }
      })
      .filter((section) => section.skills.length > 0)
  }, [topics, questions, filterDifficulties, completedFilter, progress, subjectKey, filterPools])

  const practicePool = useMemo(() => {
    const skillKeys = selected.length
      ? new Set(selected)
      : new Set(
        filteredTopics.flatMap((section) => (
          section.skills.map((skill) => `${section.id}:${skill.name}`)
        )),
      )
    return questions.filter((q) => {
      if (filterPools.length && !filterPools.includes(q.pool || DEFAULT_QUESTION_POOL)) return false
      if (filterDifficulties.length && !filterDifficulties.includes(q.difficulty)) return false
      return filteredTopics.some((section) => (
        section.skills.some((skill) => {
          const key = `${section.id}:${skill.name}`
          return skillKeys.has(key) && skill.name === q.skill && section.name === q.domain
        })
      ))
    })
  }, [selected, filteredTopics, questions, filterDifficulties, filterPools])

  const totalSkills = filteredTopics.reduce((n, t) => n + t.skills.length, 0)
  const selectedCount = selected.length
  const practiceSkillCount = selectedCount || totalSkills
  const practiceQuestionCount = practicePool.length

  const toggleSection = (id) => {
    setOpenSections((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  const toggleSkill = (key) => {
    setSelected((prev) => (
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]
    ))
  }

  const toggleDifficulty = (level) => {
    setFilterDifficulties((prev) => {
      if (prev.includes(level)) {
        if (prev.length === 1) return prev
        return prev.filter((d) => d !== level)
      }
      return [...prev, level]
    })
  }

  const togglePool = (pool) => {
    setFilterPools((prev) => {
      if (prev.includes(pool)) {
        if (prev.length === 1) return prev
        return prev.filter((p) => p !== pool)
      }
      return [...prev, pool]
    })
  }

  const toggleDomainSkills = (section) => {
    const keys = section.skills.map((skill) => `${section.id}:${skill.name}`)
    setSelected((prev) => {
      const allOn = keys.every((key) => prev.includes(key))
      if (allOn) return prev.filter((key) => !keys.includes(key))
      return [...new Set([...prev, ...keys])]
    })
  }

  const accuracyTone = (pct) => {
    if (!isValidStatNumber(pct)) return 'na'
    if (pct >= 80) return 'good'
    if (pct >= 70) return 'mid'
    return 'low'
  }

  const difficultyLabel = filterDifficulties.length === 3
    ? 'Difficulty'
    : `Difficulty (${filterDifficulties.length})`

  const poolLabel = filterPools.length === 1
    ? filterPools[0]
    : `Question Pool (${filterPools.length})`

  const completedLabel = {
    all: 'Completed',
    completed: 'Completed only',
    in_progress: 'In progress',
    not_started: 'Not started',
  }[completedFilter]

  const startPractice = () => {
    if (!practicePool.length) return

    const ordered = orderBankPracticeQuestions(practicePool, progress, subjectKey, { shuffle })
    const domains = [...new Set(ordered.questions.map((q) => q.domain))]
    const skills = [...new Set(ordered.questions.map((q) => q.skill))]
    onStartPractice?.({
      questions: ordered.questions,
      count: ordered.questions.length,
      shuffle: false,
      startIndex: ordered.startIndex,
      initialAnswers: ordered.initialAnswers,
      domains,
      difficulties: [...filterDifficulties],
      pools: [...filterPools],
      domain: domains.length === 1 ? domains[0] : `${domains.length} Domains`,
      topic: skills.length === 1 ? skills[0] : `${skills.length} skills`,
      feedbackMode: 'immediate',
      source: 'bank',
    })
  }

  return (
    <div className={`qbm-page qbm-${tone}`}>
      <button type="button" className="qbm-back" onClick={onBack}>
        ← Back to Question Bank
      </button>

      <header className="qbm-hero">
        <div className="qbm-hero-main">
          <div className="qbm-hero-badge" aria-hidden="true">
            {badge}
          </div>
          <div>
            <h1>{subject}</h1>
            <p>Explore skills, track progress, and practice what matters most.</p>
          </div>
        </div>
        {decoSrc ? (
          <img src={decoSrc} alt="" className="qbm-hero-deco" aria-hidden="true" />
        ) : null}
      </header>

      <div className="qbm-filters" ref={filtersRef}>
        <div className={`qbm-filter-dd ${openMenu === 'pool' ? 'open' : ''}`}>
          <button
            type="button"
            className={`qbm-filter-btn ${filterPools.length !== availablePools.length ? 'active' : ''}`}
            aria-expanded={openMenu === 'pool'}
            onClick={() => setOpenMenu((m) => (m === 'pool' ? null : 'pool'))}
          >
            <Vault size={15} />
            {poolLabel}
            <ChevronDown size={14} className={`qbm-filter-chevron ${openMenu === 'pool' ? 'open' : ''}`} />
          </button>
          {openMenu === 'pool' && (
            <div className="qbm-filter-menu qbm-filter-menu-wide" role="menu" aria-label="Question Pool">
              {availablePools.map((pool) => {
                const on = filterPools.includes(pool)
                return (
                  <button
                    key={pool}
                    type="button"
                    role="menuitemcheckbox"
                    aria-checked={on}
                    className={`qbm-filter-option ${on ? 'on' : ''}`}
                    onClick={() => togglePool(pool)}
                  >
                    <span className={`qbm-filter-check ${on ? 'on' : ''}`}>
                      {on ? <Check size={12} strokeWidth={3} /> : null}
                    </span>
                    {pool}
                  </button>
                )
              })}
            </div>
          )}
        </div>

        <div className={`qbm-filter-dd ${openMenu === 'difficulty' ? 'open' : ''}`}>
          <button
            type="button"
            className={`qbm-filter-btn ${filterDifficulties.length < 3 ? 'active' : ''}`}
            aria-expanded={openMenu === 'difficulty'}
            onClick={() => setOpenMenu((m) => (m === 'difficulty' ? null : 'difficulty'))}
          >
            <BarChart3 size={15} />
            {difficultyLabel}
            <ChevronDown size={14} className={`qbm-filter-chevron ${openMenu === 'difficulty' ? 'open' : ''}`} />
          </button>
          {openMenu === 'difficulty' && (
            <div className="qbm-filter-menu" role="menu" aria-label="Difficulty">
              {['Easy', 'Medium', 'Hard'].map((level) => {
                const on = filterDifficulties.includes(level)
                return (
                  <button
                    key={level}
                    type="button"
                    role="menuitemcheckbox"
                    aria-checked={on}
                    className={`qbm-filter-option ${on ? 'on' : ''}`}
                    onClick={() => toggleDifficulty(level)}
                  >
                    <span className={`qbm-filter-check ${on ? 'on' : ''}`}>
                      {on ? <Check size={12} strokeWidth={3} /> : null}
                    </span>
                    {level}
                  </button>
                )
              })}
            </div>
          )}
        </div>

        <div className={`qbm-filter-dd ${openMenu === 'completed' ? 'open' : ''}`}>
          <button
            type="button"
            className={`qbm-filter-btn ${completedFilter !== 'all' ? 'active' : ''}`}
            aria-expanded={openMenu === 'completed'}
            onClick={() => setOpenMenu((m) => (m === 'completed' ? null : 'completed'))}
          >
            <CheckCircle2 size={15} />
            {completedLabel}
            <ChevronDown size={14} className={`qbm-filter-chevron ${openMenu === 'completed' ? 'open' : ''}`} />
          </button>
          {openMenu === 'completed' && (
            <div className="qbm-filter-menu" role="menu" aria-label="Completed">
              {[
                { id: 'all', label: 'All skills' },
                { id: 'completed', label: 'Completed' },
                { id: 'in_progress', label: 'In progress' },
                { id: 'not_started', label: 'Not started' },
              ].map((opt) => (
                <button
                  key={opt.id}
                  type="button"
                  role="menuitemradio"
                  aria-checked={completedFilter === opt.id}
                  className={`qbm-filter-option ${completedFilter === opt.id ? 'on' : ''}`}
                  onClick={() => {
                    setCompletedFilter(opt.id)
                    setOpenMenu(null)
                  }}
                >
                  <span className={`qbm-filter-check ${completedFilter === opt.id ? 'on' : ''}`}>
                    {completedFilter === opt.id ? <Check size={12} strokeWidth={3} /> : null}
                  </span>
                  {opt.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="card qbm-practice-banner">
        <img src="/athena.png" alt="" className="qbm-banner-athena" />
        <div className="qbm-banner-copy">
          <h3>{selectedCount ? 'Practice selected skills' : 'Practice filtered topics'}</h3>
          <p>
            {practiceQuestionCount
              ? `Start practicing ${practiceSkillCount} skill${practiceSkillCount === 1 ? '' : 's'} · ${practiceQuestionCount} questions.`
              : 'No questions match the current selection.'}
          </p>
        </div>
        <button
          type="button"
          className={`qbm-shuffle-btn ${shuffle ? 'on' : ''}`}
          aria-pressed={shuffle}
          title="Shuffle unfinished questions"
          onClick={() => setShuffle((v) => !v)}
        >
          <Shuffle size={15} />
          Shuffle
        </button>
        <button
          type="button"
          className="qbm-start-btn"
          onClick={startPractice}
          disabled={!practiceQuestionCount}
        >
          Start practice <ChevronRight size={16} />
        </button>
      </div>

      <div className="card qbm-topics-card">
        <div className="qbm-table-head">
          <span>Topic</span>
          <span>Progress</span>
          <span>Accuracy</span>
        </div>

        {!filteredTopics.length && (
          <div className="qbm-empty">No skills match these filters. Try adjusting Difficulty or Completed.</div>
        )}

        {filteredTopics.map((section) => {
          const isOpen = openSections[section.id] ?? true
          const sectionKeys = section.skills.map((skill) => `${section.id}:${skill.name}`)
          const allSelected = sectionKeys.length > 0 && sectionKeys.every((key) => selected.includes(key))
          return (
            <div key={section.id} className="qbm-section">
              <div className="qbm-section-head">
                <button
                  type="button"
                  className="qbm-section-toggle"
                  onClick={() => toggleSection(section.id)}
                  aria-expanded={isOpen}
                >
                  <span className="qbm-section-title">
                    <Building2 size={16} />
                    {section.name}
                  </span>
                  <ChevronDown size={18} className={`qbm-chevron ${isOpen ? 'open' : ''}`} />
                </button>
                <button
                  type="button"
                  className={`qbm-select-domain ${allSelected ? 'on' : ''}`}
                  onClick={() => toggleDomainSkills(section)}
                >
                  {allSelected ? 'Deselect' : 'Select'}
                </button>
              </div>

              {isOpen && (
                <div className="qbm-skill-list">
                  {section.skills.map((skill) => {
                    const key = `${section.id}:${skill.name}`
                    const pct = skill.total ? Math.round((skill.done / skill.total) * 100) : 0
                    const checked = selected.includes(key)
                    return (
                      <label key={key} className={`qbm-skill-row ${checked ? 'on' : ''}`}>
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={() => toggleSkill(key)}
                        />
                        <span className="qbm-skill-name">{skill.name}</span>
                        <span className="qbm-skill-progress">
                          <span className="qbm-progress-track">
                            <span className="qbm-progress-fill" style={{ width: `${pct}%` }} />
                          </span>
                          <span className="qbm-progress-count">{skill.done}/{skill.total}</span>
                        </span>
                        <span className={`qbm-skill-acc ${accuracyTone(skill.accuracy)}`}>
                          <i />
                          {skill.done ? formatStatPct(skill.accuracy) : STAT_NA}
                        </span>
                      </label>
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

function QuestionBankMathPage({ onBack, profile, onCompleteQuestion }) {
  const [session, setSession] = useState(null)

  if (session) {
    return (
      <MathPracticeSession
        config={session}
        onEnd={() => setSession(null)}
        onCompleteQuestion={onCompleteQuestion}
      />
    )
  }

  return (
    <QuestionBankSubjectPage
      subject="Math"
      subjectKey="math"
      topics={MATH_QBANK_TOPICS}
      questions={mathQuestions}
      progress={profile?.qbankProgress || {}}
      tone="math"
      decoSrc="/athena-qbank-math.png"
      badge={(
        <>
          <span>+</span><span>−</span><span>×</span><span>÷</span>
        </>
      )}
      onBack={onBack}
      onStartPractice={setSession}
    />
  )
}

function QuestionBankReadingPage({ onBack, profile, onCompleteQuestion }) {
  const [session, setSession] = useState(null)

  if (session) {
    return (
      <ReadingPracticeSession
        config={session}
        onEnd={() => setSession(null)}
        onCompleteQuestion={onCompleteQuestion}
      />
    )
  }

  return (
    <QuestionBankSubjectPage
      subject="Reading & Writing"
      subjectKey="reading"
      topics={READING_QBANK_TOPICS}
      questions={readingQuestions}
      progress={profile?.qbankProgress || {}}
      tone="reading"
      decoSrc="/athena-qbank-rw.png"
      badge={<BookOpen size={22} strokeWidth={2.1} />}
      onBack={onBack}
      onStartPractice={setSession}
    />
  )
}

function ReadingPage({ profile, onCompleteQuestion, onCompleteSession }) {
  const reading = deriveSubjectStats(
    profile.qbankProgress,
    'reading',
    READING_DOMAIN_NAMES,
    readingQuestions,
  )
  const history = profile.progressHistory || []
  const overallActivity = deriveSubjectActivityStats(history, 'reading')
  const todayActivity = deriveSubjectActivityStats(history, 'reading', { dayKey: localDayKey() })
  const domains = reading.domains.map((d) => ({
    ...d,
    icon: d.name.includes('Information') ? Lightbulb
      : d.name.includes('Craft') ? Highlighter
      : d.name.includes('Expression') ? PenLine
      : SpellCheck2,
  }))
  const [shuffle, setShuffle] = useState(false)
  const [filterDomains, setFilterDomains] = useState(['Information and Ideas'])
  const [filterDifficulties, setFilterDifficulties] = useState(['Medium'])
  const [questionCount, setQuestionCount] = useState('20')
  const [session, setSession] = useState(null)
  const [athenaFactOpen, setAthenaFactOpen] = useState(false)
  const athenaFactRef = useRef(null)

  useEffect(() => {
    if (!athenaFactOpen) return undefined
    const onPointerDown = (e) => {
      if (athenaFactRef.current && !athenaFactRef.current.contains(e.target)) {
        setAthenaFactOpen(false)
      }
    }
    const onKey = (e) => {
      if (e.key === 'Escape') setAthenaFactOpen(false)
    }
    document.addEventListener('pointerdown', onPointerDown)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('pointerdown', onPointerDown)
      document.removeEventListener('keydown', onKey)
    }
  }, [athenaFactOpen])

  const toggleDomain = (name) => {
    setFilterDomains((prev) => {
      if (prev.includes(name)) {
        if (prev.length === 1) return prev
        return prev.filter((d) => d !== name)
      }
      return [...prev, name]
    })
  }

  const toggleDifficulty = (level) => {
    setFilterDifficulties((prev) => {
      if (prev.includes(level)) {
        if (prev.length === 1) return prev
        return prev.filter((d) => d !== level)
      }
      return [...prev, level]
    })
  }

  const stats = [
    {
      label: 'Accuracy',
      value: formatStatPct(reading.accuracy),
      sub: isValidStatNumber(todayActivity.accuracy)
        ? `${todayActivity.accuracy}% today`
        : 'N/A today',
      icon: <Target size={18} />,
      tone: 'purple',
    },
    {
      label: 'Questions Answered',
      value: reading.answered,
      sub: `${todayActivity.answered} today`,
      icon: <ClipboardList size={18} />,
      tone: 'blue',
    },
    {
      label: 'Avg. Time / Question',
      value: formatAvgTime(overallActivity.avgTimeSec),
      sub: isValidStatNumber(todayActivity.avgTimeSec)
        ? `${formatAvgTime(todayActivity.avgTimeSec)} today`
        : 'N/A today',
      icon: <Clock size={18} />,
      tone: 'green',
    },
    {
      label: 'Weakest Domain',
      value: reading.weakestDomain || 'Not enough data',
      sub: reading.weakestDomain ? 'Improve here!' : 'Need attempts in 2+ domains',
      icon: <AlertTriangle size={18} />,
      tone: 'orange',
      compact: true,
    },
  ]

  const startPractice = () => {
    const primary = filterDomains[0] || 'Information and Ideas'
    setSession({
      domains: filterDomains,
      domain: filterDomains.length > 1 ? `${filterDomains.length} Domains` : primary,
      topic: filterDomains.length > 1 ? filterDomains.join(' · ') : primary,
      difficulty: filterDifficulties,
      difficulties: filterDifficulties,
      count: Number(questionCount) || 20,
      shuffle,
      feedbackMode: 'deferred',
      source: 'set',
      excludeIds: [...completedQuestionIds(profile.qbankProgress, 'reading')],
    })
  }

  if (session) {
    return (
      <ReadingPracticeSession
        config={session}
        onEnd={() => setSession(null)}
        onCompleteQuestion={onCompleteQuestion}
        onCompleteSession={onCompleteSession}
      />
    )
  }

  return (
    <div className="math-page reading-page">
      <div className="math-shell">
        <div className="math-primary">
          <div className="reading-athena-layer" ref={athenaFactRef}>
            <div className="math-mascot reading-mascot">
              <img src="/athena-rw-tab.png?v=2" alt="" className="math-athena reading-athena" />
              <img src="/reading-deco.png" alt="" className="math-mascot-deco-img reading-mascot-deco" />
            </div>
            <button
              type="button"
              className="athena-book-hotspot"
              aria-label="Learn about Athena"
              aria-expanded={athenaFactOpen}
              title="Open Athena's book"
              onPointerDown={(e) => e.stopPropagation()}
              onClick={(e) => {
                e.stopPropagation()
                setAthenaFactOpen((open) => !open)
              }}
            />
            {athenaFactOpen && (
              <div className="athena-fact-bubble" role="dialog" aria-label="About Athena">
                <button
                  type="button"
                  className="athena-fact-close"
                  aria-label="Close"
                  onClick={() => setAthenaFactOpen(false)}
                >
                  <X size={14} />
                </button>
                <div className="athena-fact-eyebrow">From Athena’s book</div>
                <h3>Athena</h3>
                <p>
                  Athena is the Greek goddess of wisdom, courage, and inspiration. She watches over
                  learners who seek knowledge and push themselves to do their best — just like you
                  on the SAT.
                </p>
                <p className="athena-fact-aside">
                  Her symbols are the owl and the olive tree. In this app, she’s your study guide.
                </p>
              </div>
            )}
          </div>

          <header className="math-top">
            <div className="math-hero-copy">
              <div className="math-hero-title-row">
                <div className="math-hero-badge reading-badge" aria-hidden="true">
                  <BookOpen size={22} strokeWidth={2.2} />
                </div>
                <div>
                  <h1>Reading</h1>
                  <p>Build comprehension. Master craft. Ace Reading & Writing.</p>
                </div>
              </div>
            </div>
          </header>

          <div className="math-lower">
            <div className="card math-filters-card">
              <div className="math-filters-head">
                <div className="math-filters-icon reading-filters-icon" aria-hidden="true">
                  <Filter size={20} strokeWidth={2.3} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-athena-navy">Practice with Filters</h3>
                  <p className="mt-0.5 text-sm text-[#6b7894]">Customize your practice and generate the perfect set of questions.</p>
                </div>
              </div>

              <div className="math-filters-grid">
                <div className="math-filter-block math-filter-domains">
                  <div className="math-filter-label">1. Domain</div>
                  <div className="math-domain-multi" role="group" aria-label="Domains">
                    {domains.map((d) => {
                      const on = filterDomains.includes(d.name)
                      return (
                        <button
                          key={d.name}
                          type="button"
                          className={`math-domain-chip reading-chip ${on ? 'on' : ''}`}
                          aria-pressed={on}
                          onClick={() => toggleDomain(d.name)}
                        >
                          {on && <Check size={13} strokeWidth={2.6} />}
                          <span>{d.name}</span>
                        </button>
                      )
                    })}
                  </div>
                  <p className="math-filter-hint">Select one or more Reading & Writing domains.</p>
                </div>

                <div className="math-filter-block">
                  <div className="math-filter-label">2. Difficulty</div>
                  <div className="math-diff-group" role="group" aria-label="Difficulty">
                    {['Easy', 'Medium', 'Hard'].map((level) => {
                      const on = filterDifficulties.includes(level)
                      return (
                        <button
                          key={level}
                          type="button"
                          className={`math-diff-btn reading-diff ${on ? 'on' : ''}`}
                          onClick={() => toggleDifficulty(level)}
                          aria-pressed={on}
                        >
                          {on && <Check size={13} strokeWidth={2.6} />}
                          {level}
                        </button>
                      )
                    })}
                  </div>
                  <p className="math-filter-hint">Select one or more difficulty levels.</p>
                </div>

                <div className="math-filter-block">
                  <div className="math-filter-label">3. Number of Questions</div>
                  <div className="math-count-select">
                    <select value={questionCount} onChange={(e) => setQuestionCount(e.target.value)}>
                      {['5', '10', '15', '20', '25', '30'].map((n) => (
                        <option key={n} value={n}>{n}</option>
                      ))}
                    </select>
                    <ChevronDown size={16} className="math-domain-select-chevron" />
                  </div>
                  <p className="math-filter-hint">Choose how many questions to include.</p>
                </div>

                <div className="math-filter-block math-filter-shuffle">
                  <div>
                    <div className="math-filter-label">4. Shuffle Questions</div>
                    <p className="math-filter-hint">Randomize the order of questions.</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setShuffle((v) => !v)}
                    className={`math-toggle reading-toggle ${shuffle ? 'on' : ''}`}
                    aria-pressed={shuffle}
                    aria-label="Shuffle Questions"
                  >
                    <span />
                  </button>
                </div>
              </div>

              <button className="math-generate-btn reading-generate-btn" onClick={startPractice}>
                <Sparkles size={16} strokeWidth={2.4} />
                Generate Practice
              </button>
            </div>

            <div className="card math-domains-card">
              <h3 className="text-lg font-bold text-athena-navy">Accuracy by Domain</h3>
              <div className="math-domains-list">
                {domains.map((d) => {
                  const Icon = d.icon
                  return (
                  <div key={d.name} className="math-domain-row">
                    <div className="math-domain-icon reading-domain-icon">
                      <Icon size={18} strokeWidth={2.2} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="mb-1.5 flex items-center justify-between gap-3 text-sm">
                        <span className="min-w-0 truncate font-semibold text-athena-navy">{d.name}</span>
                        <span className="flex shrink-0 items-center gap-3">
                          <span className="text-xs font-semibold text-[#7a869e]">{d.done}/{d.total}</span>
                          <span className="font-bold reading-pct">{formatStatPct(d.pct)}</span>
                        </span>
                      </div>
                      <div className="h-2.5 overflow-hidden rounded-full bg-[#e8edf5]">
                        <motion.div
                          className="h-full rounded-full reading-bar-fill"
                          initial={{ width: 0 }}
                          animate={{ width: `${d.pct ?? 0}%` }}
                          transition={{ duration: 0.8 }}
                        />
                      </div>
                    </div>
                  </div>
                )})}
              </div>
            </div>
          </div>
        </div>

        <aside className="math-side">
          {stats.map((s) => (
            <div key={s.label} className={`card math-stat math-stat-${s.tone}`}>
              <div className="math-stat-top">
                <div className="text-xs font-semibold text-[#6b7894]">{s.label}</div>
                <div className="math-stat-icon">{s.icon}</div>
              </div>
              <div className={`math-stat-value ${s.compact ? 'compact' : ''}`}>{s.value}</div>
              <div className="math-stat-sub">{s.sub}</div>
            </div>
          ))}
        </aside>
      </div>
    </div>
  )
}

function MathPage({ profile, onCompleteQuestion, onCompleteSession }) {
  const math = deriveSubjectStats(
    profile.qbankProgress,
    'math',
    MATH_DOMAIN_NAMES,
    mathQuestions,
  )
  const history = profile.progressHistory || []
  const overallActivity = deriveSubjectActivityStats(history, 'math')
  const todayActivity = deriveSubjectActivityStats(history, 'math', { dayKey: localDayKey() })
  const domains = math.domains.map((d) => ({
    ...d,
    icon: d.name === 'Algebra' ? FunctionSquare
      : d.name === 'Advanced Math' ? Radical
      : d.name.includes('Data') ? BarChart3
      : Triangle,
  }))
  const [shuffle, setShuffle] = useState(false)
  const [filterDomains, setFilterDomains] = useState(['Algebra'])
  const [filterDifficulties, setFilterDifficulties] = useState(['Medium'])
  const [questionCount, setQuestionCount] = useState('20')
  const [session, setSession] = useState(null)

  const toggleDomain = (name) => {
    setFilterDomains((prev) => {
      if (prev.includes(name)) {
        if (prev.length === 1) return prev
        return prev.filter((d) => d !== name)
      }
      return [...prev, name]
    })
  }

  const toggleDifficulty = (level) => {
    setFilterDifficulties((prev) => {
      if (prev.includes(level)) {
        if (prev.length === 1) return prev
        return prev.filter((d) => d !== level)
      }
      return [...prev, level]
    })
  }

  const stats = [
    {
      label: 'Accuracy',
      value: formatStatPct(math.accuracy),
      sub: isValidStatNumber(todayActivity.accuracy)
        ? `${todayActivity.accuracy}% today`
        : 'N/A today',
      icon: <Target size={18} />,
      tone: 'green',
    },
    {
      label: 'Questions Answered',
      value: math.answered,
      sub: `${todayActivity.answered} today`,
      icon: <ClipboardList size={18} />,
      tone: 'blue',
    },
    {
      label: 'Avg. Time / Question',
      value: formatAvgTime(overallActivity.avgTimeSec),
      sub: isValidStatNumber(todayActivity.avgTimeSec)
        ? `${formatAvgTime(todayActivity.avgTimeSec)} today`
        : 'N/A today',
      icon: <Clock size={18} />,
      tone: 'purple',
    },
    {
      label: 'Weakest Domain',
      value: math.weakestDomain || 'Not enough data',
      sub: math.weakestDomain ? 'Improve here!' : 'Need attempts in 2+ domains',
      icon: <AlertTriangle size={18} />,
      tone: 'orange',
      compact: true,
    },
  ]

  const startPractice = () => {
    const primary = filterDomains[0] || 'Algebra'
    setSession({
      domains: filterDomains,
      domain: filterDomains.length > 1 ? `${filterDomains.length} Domains` : primary,
      topic: filterDomains.length > 1 ? filterDomains.join(' · ') : (primary === 'Algebra' ? 'Linear Equations' : 'Core Skills'),
      difficulty: filterDifficulties,
      difficulties: filterDifficulties,
      count: Number(questionCount) || 20,
      shuffle,
      feedbackMode: 'deferred',
      source: 'set',
      excludeIds: [...completedQuestionIds(profile.qbankProgress, 'math')],
    })
  }

  if (session) {
    return (
      <MathPracticeSession
        config={session}
        onEnd={() => setSession(null)}
        onCompleteQuestion={onCompleteQuestion}
        onCompleteSession={onCompleteSession}
      />
    )
  }

  return (
    <div className="math-page">
      <div className="math-shell">
        <div className="math-primary">
          <div className="math-mascot" aria-hidden="true">
            <img src="/athena-math.png" alt="" className="math-athena" />
            <img src="/math-deco.png?v=2" alt="" className="math-mascot-deco-img" />
          </div>

          <header className="math-top">
            <div className="math-hero-copy">
              <div className="math-hero-title-row">
                <div className="math-hero-badge" aria-hidden="true">
                  <Calculator size={22} strokeWidth={2.2} />
                </div>
                <div>
                  <h1>Math</h1>
                  <p>Build skills. Solve problems. Master the SAT.</p>
                </div>
              </div>
            </div>
          </header>

          <div className="math-lower">
            <div className="card math-filters-card">
              <div className="math-filters-head">
                <div className="math-filters-icon" aria-hidden="true">
                  <Filter size={20} strokeWidth={2.3} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-athena-navy">Practice with Filters</h3>
                  <p className="mt-0.5 text-sm text-[#6b7894]">Customize your practice and generate the perfect set of questions.</p>
                </div>
              </div>

              <div className="math-filters-grid">
                <div className="math-filter-block math-filter-domains">
                  <div className="math-filter-label">1. Domain</div>
                  <div className="math-domain-multi" role="group" aria-label="Domains">
                    {domains.map((d) => {
                      const on = filterDomains.includes(d.name)
                      return (
                        <button
                          key={d.name}
                          type="button"
                          className={`math-domain-chip ${on ? 'on' : ''}`}
                          aria-pressed={on}
                          onClick={() => toggleDomain(d.name)}
                        >
                          {on && <Check size={13} strokeWidth={2.6} />}
                          <span>{d.name}</span>
                        </button>
                      )
                    })}
                  </div>
                  <p className="math-filter-hint">Select one or more domains to practice.</p>
                </div>

                <div className="math-filter-block">
                  <div className="math-filter-label">2. Difficulty</div>
                  <div className="math-diff-group" role="group" aria-label="Difficulty">
                    {['Easy', 'Medium', 'Hard'].map((level) => {
                      const on = filterDifficulties.includes(level)
                      return (
                        <button
                          key={level}
                          type="button"
                          className={`math-diff-btn ${on ? 'on' : ''}`}
                          onClick={() => toggleDifficulty(level)}
                          aria-pressed={on}
                        >
                          {on && <Check size={13} strokeWidth={2.6} />}
                          {level}
                        </button>
                      )
                    })}
                  </div>
                  <p className="math-filter-hint">Select one or more difficulty levels.</p>
                </div>

                <div className="math-filter-block">
                  <div className="math-filter-label">3. Number of Questions</div>
                  <div className="math-count-select">
                    <select value={questionCount} onChange={(e) => setQuestionCount(e.target.value)}>
                      {['5', '10', '15', '20', '25', '30'].map((n) => (
                        <option key={n} value={n}>{n}</option>
                      ))}
                    </select>
                    <ChevronDown size={16} className="math-domain-select-chevron" />
                  </div>
                  <p className="math-filter-hint">Choose how many questions to include.</p>
                </div>

                <div className="math-filter-block math-filter-shuffle">
                  <div>
                    <div className="math-filter-label">4. Shuffle Questions</div>
                    <p className="math-filter-hint">Randomize the order of questions.</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setShuffle((v) => !v)}
                    className={`math-toggle ${shuffle ? 'on' : ''}`}
                    aria-pressed={shuffle}
                    aria-label="Shuffle Questions"
                  >
                    <span />
                  </button>
                </div>
              </div>

              <button className="math-generate-btn" onClick={startPractice}>
                <Sparkles size={16} strokeWidth={2.4} />
                Generate Practice
              </button>
            </div>

            <div className="card math-domains-card">
              <h3 className="text-lg font-bold text-athena-navy">Accuracy by Domain</h3>
              <div className="math-domains-list">
                {domains.map((d) => {
                  const Icon = d.icon
                  return (
                  <div key={d.name} className="math-domain-row">
                    <div className="math-domain-icon">
                      <Icon size={18} strokeWidth={2.2} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="mb-1.5 flex items-center justify-between gap-3 text-sm">
                        <span className="min-w-0 truncate font-semibold text-athena-navy">{d.name}</span>
                        <span className="flex shrink-0 items-center gap-3">
                          <span className="text-xs font-semibold text-[#7a869e]">{d.done}/{d.total}</span>
                          <span className="font-bold text-athena-green">{formatStatPct(d.pct)}</span>
                        </span>
                      </div>
                      <div className="h-2.5 overflow-hidden rounded-full bg-[#e8edf5]">
                        <motion.div
                          className="h-full rounded-full bg-athena-green"
                          initial={{ width: 0 }}
                          animate={{ width: `${d.pct ?? 0}%` }}
                          transition={{ duration: 0.8 }}
                        />
                      </div>
                    </div>
                  </div>
                )})}
              </div>
            </div>
          </div>
        </div>

        <aside className="math-side">
          {stats.map((s) => (
            <div key={s.label} className={`card math-stat math-stat-${s.tone}`}>
              <div className="math-stat-top">
                <div className="text-xs font-semibold text-[#6b7894]">{s.label}</div>
                <div className="math-stat-icon">{s.icon}</div>
              </div>
              <div className={`math-stat-value ${s.compact ? 'compact' : ''}`}>{s.value}</div>
              <div className="math-stat-sub">{s.sub}</div>
            </div>
          ))}
        </aside>
      </div>
    </div>
  )
}

const DESMOS_API_KEY = '7ad3aa8ec126436495e727c52a77826a'
const FORMULA_SHEET_URL = 'https://satsuite.collegeboard.org/media/pdf/sat-suite-of-assessments-student-guide.pdf'

const MATH_QUESTION_BANK = mathQuestions
const READING_QUESTION_BANK = readingQuestions

function shuffleInPlace(list) {
  for (let i = list.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[list[i], list[j]] = [list[j], list[i]]
  }
  return list
}

/** Take up to `take` items by round-robin across buckets so one group can't dominate. */
function pickRoundRobin(buckets, take, { shuffle = false } = {}) {
  const prepared = buckets
    .map((items) => {
      if (!items?.length) return []
      return shuffle ? shuffleInPlace([...items]) : [...items]
    })
    .filter((bucket) => bucket.length)

  if (!prepared.length) return []
  if (prepared.length === 1) {
    return prepared[0].slice(0, take)
  }

  const selected = []
  let cursor = 0
  while (selected.length < take) {
    let added = false
    for (const bucket of prepared) {
      if (selected.length >= take) break
      if (cursor < bucket.length) {
        selected.push(bucket[cursor])
        added = true
      }
    }
    if (!added) break
    cursor += 1
  }
  return shuffle ? shuffleInPlace(selected) : selected
}

function orderPoolByDomains(items, domainList, shuffle) {
  if (!items.length) return []
  if (domainList.length <= 1) {
    return shuffle ? shuffleInPlace([...items]) : [...items]
  }
  const buckets = domainList.map((domain) => items.filter((q) => q.domain === domain))
  const ordered = pickRoundRobin(buckets, items.length, { shuffle: false })
  // pickRoundRobin may miss items whose domain isn't in domainList; append leftovers.
  if (ordered.length < items.length) {
    const seen = new Set(ordered.map((q) => q.id))
    for (const q of items) {
      if (!seen.has(q.id)) ordered.push(q)
    }
  }
  return shuffle ? shuffleInPlace(ordered) : ordered
}

function completedQuestionIds(progress, subject) {
  return new Set(
    Object.entries(progress || {})
      .filter(([, item]) => item?.subject === subject)
      .map(([id]) => String(id)),
  )
}

function seedCompletedAnswer(question, entry) {
  if (!entry) return null
  if (question?.type === 'spr') {
    if (entry.correct) {
      return question.acceptedAnswers?.[0] ?? question.answer ?? ''
    }
    return '__incorrect__'
  }
  if (entry.correct) return question.answer
  const n = Array.isArray(question?.choices) ? question.choices.length : 4
  for (let i = 0; i < n; i += 1) {
    if (i !== question.answer) return i
  }
  return 0
}

function orderBankPracticeQuestions(pool, progress, subject, { shuffle = false } = {}) {
  // Preserve stable bank numbers from the filtered pool order (1…N)
  const numbered = pool.map((q, i) => ({ ...q, bankNumber: i + 1, practiceIndex: i + 1 }))
  const completedIds = completedQuestionIds(progress, subject)
  const completed = []
  const remaining = []
  for (const q of numbered) {
    if (completedIds.has(String(q.id))) completed.push(q)
    else remaining.push(q)
  }
  if (shuffle) shuffleInPlace(remaining)
  const questions = [...completed, ...remaining]
  const initialAnswers = questions.map((q) => {
    const entry = progress?.[String(q.id)]
    if (!entry || entry.subject !== subject) return null
    return seedCompletedAnswer(q, entry)
  })
  const startIndex = remaining.length
    ? completed.length
    : 0
  return { questions, initialAnswers, startIndex }
}

function pickQuestions(bank, { count, shuffle, domains, difficulties, questions: preset, pools, excludeIds }) {
  if (Array.isArray(preset) && preset.length) {
    const working = shuffle ? shuffleInPlace([...preset]) : [...preset]
    const limited = typeof count === 'number' && count > 0 ? working.slice(0, count) : working
    return limited.map((q, i) => ({ ...q, practiceIndex: i + 1 }))
  }
  const levels = Array.isArray(difficulties)
    ? difficulties
    : (difficulties && difficulties !== 'Any' ? [difficulties] : [])
  const poolList = Array.isArray(pools) ? pools : (pools ? [pools] : [])
  const excluded = excludeIds instanceof Set ? excludeIds : new Set(excludeIds || [])
  const domainList = Array.isArray(domains) ? domains.filter(Boolean) : []
  const inDomains = (q) => !domainList.length || domainList.includes(q.domain)
  const inDifficulty = (q) => !levels.length || !q.difficulty || levels.includes(q.difficulty)
  const inPool = (q) => !poolList.length || poolList.includes(q.pool || DEFAULT_QUESTION_POOL)
  const notDone = (q) => !excluded.has(String(q.id))
  let pool = bank.filter((q) => inDomains(q) && inDifficulty(q) && inPool(q) && notDone(q))
  if (!pool.length) pool = bank.filter((q) => inDomains(q) && inPool(q) && notDone(q))
  if (!pool.length) pool = bank.filter((q) => inPool(q) && notDone(q))
  if (!pool.length) return []

  const take = typeof count === 'number' && count > 0
    ? Math.min(count, pool.length)
    : pool.length

  // Multiple difficulties: round-robin so Hard (majority of the bank) can't dominate.
  // Within each difficulty, also spread across domains when several are selected.
  if (levels.length > 1) {
    const buckets = levels.map((level) => (
      orderPoolByDomains(
        pool.filter((q) => q.difficulty === level),
        domainList,
        shuffle,
      )
    ))
    const undiffed = pool.filter((q) => !q.difficulty)
    if (undiffed.length) {
      buckets.push(orderPoolByDomains(undiffed, domainList, shuffle))
    }
    const selected = pickRoundRobin(buckets, take, { shuffle })
    if (selected.length) {
      return selected.map((q, i) => ({ ...q, practiceIndex: i + 1 }))
    }
  }

  // Multiple domains (single / no difficulty): pull evenly across domains.
  if (domainList.length > 1) {
    const buckets = domainList.map((domain) => pool.filter((q) => q.domain === domain))
    const selected = pickRoundRobin(buckets, take, { shuffle })
    if (selected.length) {
      return selected.map((q, i) => ({ ...q, practiceIndex: i + 1 }))
    }
  }

  const working = shuffle ? shuffleInPlace([...pool]) : [...pool]
  return working.slice(0, take).map((q, i) => ({ ...q, practiceIndex: i + 1 }))
}

function buildPracticeQuestions(count, shuffle, domains, difficulties, questions, pools, excludeIds) {
  return pickQuestions(MATH_QUESTION_BANK, { count, shuffle, domains, difficulties, questions, pools, excludeIds })
}

function buildReadingQuestions(count, shuffle, domains, difficulties, questions, pools, excludeIds) {
  return pickQuestions(READING_QUESTION_BANK, { count, shuffle, domains, difficulties, questions, pools, excludeIds })
}

function formatElapsed(totalSeconds) {
  const h = Math.floor(totalSeconds / 3600)
  const m = Math.floor((totalSeconds % 3600) / 60)
  const s = totalSeconds % 60
  return [h, m, s].map((n) => String(n).padStart(2, '0')).join(':')
}

function loadDesmosApi() {
  if (typeof window !== 'undefined' && window.Desmos) {
    return Promise.resolve(window.Desmos)
  }
  return new Promise((resolve, reject) => {
    const existing = document.querySelector('script[data-desmos-api]')
    if (existing) {
      existing.addEventListener('load', () => resolve(window.Desmos))
      existing.addEventListener('error', () => reject(new Error('Desmos failed to load')))
      return
    }
    const script = document.createElement('script')
    script.src = `https://www.desmos.com/api/v1.11/calculator.js?apiKey=${DESMOS_API_KEY}`
    script.async = true
    script.dataset.desmosApi = 'true'
    script.onload = () => resolve(window.Desmos)
    script.onerror = () => reject(new Error('Desmos failed to load'))
    document.head.appendChild(script)
  })
}

function normalizeSprAnswer(value) {
  return String(value ?? '').trim().toLowerCase().replace(/\s+/g, '')
}

function isAnswerCorrect(question, answer) {
  if (answer == null || answer === '') return null
  if (question?.type === 'spr') {
    const accepted = question.acceptedAnswers?.length
      ? question.acceptedAnswers
      : [question.answer]
    const normalized = normalizeSprAnswer(answer)
    return accepted.some((item) => normalizeSprAnswer(item) === normalized)
  }
  return answer === question?.answer
}

function applyQuestionCompletion(profile, question, answer, subject) {
  if (!question?.id) return profile
  if (answer == null || answer === '') return profile
  const correct = isAnswerCorrect(question, answer)
  if (correct == null) return profile

  const qid = String(question.id)
  const nextProgress = {
    ...(profile.qbankProgress || {}),
    [qid]: {
      subject,
      correct: Boolean(correct),
      domain: question.domain || '',
      skill: question.skill || question.topic || '',
    },
  }

  const reading = deriveSubjectStats(nextProgress, 'reading', READING_DOMAIN_NAMES, readingQuestions)
  const math = deriveSubjectStats(nextProgress, 'math', MATH_DOMAIN_NAMES, mathQuestions)
  const overallAccuracy = deriveOverallAccuracy(nextProgress)

  return {
    ...profile,
    qbankProgress: nextProgress,
    overallAccuracy: overallAccuracy ?? null,
    reading: {
      ...(profile.reading || {}),
      ...reading,
    },
    math: {
      ...(profile.math || {}),
      ...math,
    },
  }
}

function countSkillProgress(progress, subject, domain, skill, questionIds) {
  const idSet = new Set((questionIds || []).map(String))
  const entries = Object.entries(progress || {}).filter(([id, item]) => (
    item.subject === subject
    && item.domain === domain
    && item.skill === skill
    && (!idSet.size || idSet.has(String(id)))
  )).map(([, item]) => item)
  const done = entries.length
  return {
    done,
    accuracy: accuracyFromEntries(entries),
  }
}

function shuffleSessionUnanswered(questions, answers, eliminated, index, missedOnce = [], questionTimes = []) {
  const answeredIdx = []
  const unansweredIdx = []
  questions.forEach((_, i) => {
    const answer = answers[i]
    if (answer == null || answer === '') unansweredIdx.push(i)
    else answeredIdx.push(i)
  })
  shuffleInPlace(unansweredIdx)
  const order = [...answeredIdx, ...unansweredIdx]
  const currentId = questions[index]?.id
  const nextQuestions = order.map((i) => questions[i])
  const nextAnswers = order.map((i) => answers[i])
  const nextEliminated = order.map((i) => (eliminated[i] ? [...eliminated[i]] : []))
  const nextMissedOnce = order.map((i) => Boolean(missedOnce[i]))
  const nextQuestionTimes = order.map((i) => Number(questionTimes[i]) || 0)
  const nextIndex = Math.max(0, nextQuestions.findIndex((q) => q.id === currentId))
  return {
    questions: nextQuestions,
    answers: nextAnswers,
    eliminated: nextEliminated,
    missedOnce: nextMissedOnce,
    questionTimes: nextQuestionTimes,
    index: nextIndex,
  }
}

function PracticeQuestionBankMenu({
  questions,
  index,
  answers,
  missedOnce = [],
  revealResults = true,
  onJump,
  onShuffleUnanswered,
}) {
  const [open, setOpen] = useState(false)
  const [groupAnswered, setGroupAnswered] = useState(true)
  const wrapRef = useRef(null)

  useEffect(() => {
    if (!open) return undefined
    const onPointerDown = (event) => {
      if (wrapRef.current && !wrapRef.current.contains(event.target)) {
        setOpen(false)
      }
    }
    const onKeyDown = (event) => {
      if (event.key === 'Escape') setOpen(false)
    }
    document.addEventListener('pointerdown', onPointerDown)
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('pointerdown', onPointerDown)
      document.removeEventListener('keydown', onKeyDown)
    }
  }, [open])

  const items = useMemo(() => {
    const mapped = questions.map((question, i) => {
      const answer = answers[i]
      const answered = !(answer == null || answer === '')
      const correct = revealResults ? isAnswerCorrect(question, answer) : null
      const retried = revealResults && Boolean(missedOnce[i]) && correct === true
      return {
        i,
        n: question.bankNumber || question.practiceIndex || (i + 1),
        answered,
        correct,
        retried,
      }
    })

    if (!groupAnswered) return mapped
    // Keep completed / answered at the front; labels keep original bank numbers
    const answeredItems = mapped.filter((item) => item.answered)
    const unanswered = mapped.filter((item) => !item.answered)
    return [...answeredItems, ...unanswered]
  }, [questions, answers, missedOnce, groupAnswered, revealResults])

  return (
    <div className={`practice-qbank ${open ? 'open' : ''}`} ref={wrapRef}>
      {open && (
        <div className="practice-qbank-panel" role="dialog" aria-label="Question Bank">
          <div className="practice-qbank-header">
            <h3>Question Bank</h3>
            <div className="practice-qbank-header-actions">
              {typeof onShuffleUnanswered === 'function' && (
                <button
                  type="button"
                  className="practice-qbank-group-btn"
                  title="Shuffle unfinished questions"
                  onClick={() => onShuffleUnanswered()}
                >
                  <Shuffle size={14} strokeWidth={2.2} />
                  Shuffle
                </button>
              )}
              <button
                type="button"
                className={`practice-qbank-group-btn ${groupAnswered ? 'on' : ''}`}
                aria-pressed={groupAnswered}
                onClick={() => setGroupAnswered((v) => !v)}
              >
                <ListFilter size={14} strokeWidth={2.2} />
                Group Answered
              </button>
              <button
                type="button"
                className="practice-qbank-close"
                aria-label="Close question bank"
                onClick={() => setOpen(false)}
              >
                <X size={18} strokeWidth={2.2} />
              </button>
            </div>
          </div>

          <div className="practice-qbank-legend">
            {revealResults ? (
              <>
                <span><i className="leg-correct" /><em>Correct</em></span>
                <span><i className="leg-incorrect" /><em>Incorrect</em></span>
                <span><i className="leg-retry" /><em>Correct (incorrect attempts)</em></span>
              </>
            ) : (
              <>
                <span><i className="leg-answered" /><em>Answered</em></span>
                <span><i className="leg-unanswered" /><em>Unanswered</em></span>
              </>
            )}
          </div>

          <div className="practice-qbank-grid">
            {items.map((item) => {
              const status = !revealResults
                ? (item.answered ? 'answered' : 'unanswered')
                : item.retried
                  ? 'retry'
                  : item.correct === true
                    ? 'correct'
                    : item.correct === false
                      ? 'incorrect'
                      : 'unanswered'
              return (
                <button
                  key={item.i}
                  type="button"
                  className={`practice-qbank-cell ${status} ${item.i === index ? 'current' : ''}`}
                  onClick={() => {
                    onJump(item.i)
                    setOpen(false)
                  }}
                >
                  {item.n}
                  {item.retried ? (
                    <Check size={10} className="practice-qbank-cell-check" strokeWidth={3} />
                  ) : null}
                </button>
              )
            })}
          </div>
        </div>
      )}

      <button
        type="button"
        className="practice-qbank-trigger"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
      >
        <span>{index + 1} of {questions.length}</span>
        {open ? <ChevronDown size={14} /> : <ChevronUp size={14} />}
      </button>
    </div>
  )
}

function normalizeChoice(choice) {
  if (choice == null) return { text: '', image: null }
  if (typeof choice === 'string') return { text: choice, image: null }
  return { text: choice.text || '', image: choice.image || null }
}

function SprAnswerInput({ question, value, revealAnswer, locked = false, onSubmit }) {
  const [draft, setDraft] = useState(() => value ?? '')
  const [checked, setChecked] = useState(() => Boolean(value))

  useEffect(() => {
    setDraft(value ?? '')
    setChecked(Boolean(value))
  }, [question?.id, value])

  const submit = () => {
    if (locked) return
    const next = String(draft ?? '').trim()
    if (!next) return
    setDraft(next)
    setChecked(true)
    onSubmit?.(next)
  }

  const verdict = revealAnswer && checked && draft.trim()
    ? isAnswerCorrect(question, draft.trim())
    : null
  const saved = !revealAnswer && checked && Boolean(String(draft || '').trim())

  return (
    <div className="practice-spr">
      <label className="practice-spr-label" htmlFor={`spr-${question.id}`}>
        Your answer
      </label>
      <div className="practice-spr-row">
        <input
          id={`spr-${question.id}`}
          className={`practice-spr-input ${verdict == null ? (saved ? 'saved' : '') : verdict ? 'ok' : 'bad'}`}
          type="text"
          inputMode="decimal"
          placeholder="Enter a number or fraction"
          value={draft}
          readOnly={locked}
          onChange={(e) => {
            if (locked) return
            setDraft(e.target.value)
            setChecked(false)
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault()
              submit()
            }
          }}
        />
        <button
          type="button"
          className="practice-spr-submit"
          onClick={submit}
          disabled={locked || !String(draft || '').trim()}
        >
          {revealAnswer ? 'Check' : 'Submit'}
        </button>
      </div>
      {verdict != null && (
        <div className={`practice-spr-result ${verdict ? 'ok' : 'bad'}`}>
          {verdict ? 'Correct' : 'Incorrect'}
        </div>
      )}
      {saved && (
        <div className="practice-spr-result saved">Answer saved</div>
      )}
      {revealAnswer && verdict != null && (
        <div className="practice-spr-key">
          Correct answer: {(question.acceptedAnswers || [question.answer]).join(' or ')}
        </div>
      )}
    </div>
  )
}

function choiceDisplayText(choice) {
  const { text, image } = normalizeChoice(choice)
  if (image && (!text || shouldPreferChoiceImage(text))) return ''
  const trimmed = String(text || '').trim()
  if (image && (!trimmed || ['A', 'B', 'C', 'D'].includes(trimmed))) return ''
  return trimmed
}

function shouldPreferChoiceImage(text) {
  const s = String(text || '').trim()
  if (!s) return true
  // short symbolic / numeric OCR leftovers → show image instead
  if (s.length <= 20 && !/[a-zA-Z]{3,}/.test(s)) return true
  return false
}

function renderMathText(text, { asEquation = false } = {}) {
  const raw = String(text ?? '')
  if (!raw) return null
  // Keep prose as plain text with math font via CSS — only specially mark
  // short equation choices so we don't fragment word-problem stems.
  if (!asEquation) return raw

  const equationLike = looksLikeEquation(raw)
    || (/[=+\-−×÷/^]/.test(raw) && raw.length <= 96)

  if (!equationLike) return raw

  const parts = raw.split(/(\$?\d+(?:,\d{3})*(?:\.\d+)?%?|(?<![A-Za-z])[A-Za-z](?![A-Za-z]))/g)
  return parts.map((part, i) => {
    if (!part) return null
    if (/^\$?\d/.test(part) || part.endsWith('%')) {
      return <span key={i} className="math-num">{part}</span>
    }
    if (/^[A-Za-z]$/.test(part)) {
      return <span key={i} className="math-var">{part}</span>
    }
    return <span key={i}>{part}</span>
  })
}

function PracticeExplanationModal({ open, explanation, onClose }) {
  if (!open) return null
  return (
    <div className="practice-modal-backdrop" onClick={onClose} role="presentation">
      <div
        className="practice-modal"
        role="dialog"
        aria-modal="true"
        aria-label="Explanation"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="practice-modal-head">
          <h3>Explanation</h3>
          <button type="button" className="practice-modal-close" onClick={onClose} aria-label="Close">
            <X size={18} />
          </button>
        </div>
        <div className="practice-modal-body">
          {explanation
            ? explanation.split(/\n+/).map((para, i) => <p key={i}>{para}</p>)
            : <p>No explanation is available for this question yet.</p>}
        </div>
      </div>
    </div>
  )
}

function PracticePdfPanel({ pdf, pdfPage, pdfPreview }) {
  if (!pdfPreview && !(pdf && pdfPage)) return null
  const fullSrc = pdf && pdfPage ? `${pdf}#page=${pdfPage}` : null
  return (
    <div className="practice-pdf-inline">
      <div className="practice-pdf-inline-bar">
        <span>Original question{pdfPage ? ` · page ${pdfPage}` : ''}</span>
        {fullSrc && (
          <a
            className="practice-outline-btn compact"
            href={fullSrc}
            target="_blank"
            rel="noreferrer"
          >
            <ExternalLink size={14} />
            Open PDF
          </a>
        )}
      </div>
      {pdfPreview ? (
        <img
          key={pdfPreview}
          className="practice-pdf-inline-image"
          src={pdfPreview}
          alt="Original question from PDF"
        />
      ) : (
        <iframe
          key={fullSrc}
          className="practice-pdf-inline-frame"
          title={`Original PDF page ${pdfPage}`}
          src={fullSrc}
        />
      )}
    </div>
  )
}

/** Full PDF page iframe (used by Reading — no cropped preview). */
function PracticePdfFramePanel({ pdf, pdfPage, tone = 'math' }) {
  if (!pdf || !pdfPage) return null
  const src = `${pdf}#page=${pdfPage}`
  const outlineClass = tone === 'reading'
    ? 'practice-outline-btn compact reading-outline-btn'
    : 'practice-outline-btn compact'
  return (
    <div className="practice-pdf-inline practice-pdf-frame-panel">
      <div className="practice-pdf-inline-bar">
        <span>Original PDF · page {pdfPage}</span>
        <a className={outlineClass} href={src} target="_blank" rel="noreferrer">
          <ExternalLink size={14} />
          Open
        </a>
      </div>
      <iframe
        key={src}
        className="practice-pdf-inline-frame"
        title={`Original PDF page ${pdfPage}`}
        src={src}
      />
    </div>
  )
}

function PracticeResultsModal({ open, questions, answers, onClose, onExit }) {
  if (!open) return null
  const graded = questions.map((q, i) => ({
    q,
    answer: answers[i],
    correct: isAnswerCorrect(q, answers[i]),
  }))
  const answered = graded.filter((g) => g.correct != null)
  const right = answered.filter((g) => g.correct).length
  return (
    <div className="practice-modal-backdrop" onClick={onClose} role="presentation">
      <div className="practice-modal practice-results-modal" role="dialog" aria-modal="true" onClick={(e) => e.stopPropagation()}>
        <div className="practice-modal-head">
          <h3>Practice Results</h3>
          <button type="button" className="practice-modal-close" onClick={onClose} aria-label="Close">
            <X size={18} />
          </button>
        </div>
        <div className="practice-modal-body">
          <p className="practice-results-score">
            {answered.length
              ? `${right} / ${answered.length} correct · ${Math.round((right / answered.length) * 100)}%`
              : `0 / 0 correct · ${STAT_NA}`}
          </p>
          <div className="practice-results-list">
            {graded.map((g, i) => (
              <div key={g.q.id || i} className={`practice-results-row ${g.correct == null ? 'skip' : g.correct ? 'ok' : 'bad'}`}>
                <span>Q{i + 1}</span>
                <span>{g.correct == null ? 'Unanswered' : g.correct ? 'Correct' : 'Incorrect'}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="practice-modal-actions">
          <button type="button" className="practice-outline-btn" onClick={onClose}>Keep practicing</button>
          <button type="button" className="practice-next-btn" onClick={onExit}>Done</button>
        </div>
      </div>
    </div>
  )
}

function looksLikeEquation(line) {
  const s = String(line || '')
  if (s.length > 80) return false
  const ops = (s.match(/[=+\-−×÷/^()]/g) || []).length
  const letters = (s.match(/[A-Za-z]/g) || []).length
  return ops >= 1 && letters <= 24 && s.split(/\s+/).length <= 12
}

function renderPromptLine(line, equations) {
  const parts = String(line).split(/\{\{eq:(\d+)\}\}/)
  if (parts.length === 1) return line
  const nodes = []
  for (let i = 0; i < parts.length; i += 1) {
    if (i % 2 === 0) {
      if (parts[i]) nodes.push(<span key={`t${i}`}>{parts[i]}</span>)
    } else {
      const src = equations[Number(parts[i])]
      if (src) {
        nodes.push(
          <img key={`e${i}`} src={src} alt="Equation" className="practice-inline-eq" />,
        )
      }
    }
  }
  return nodes
}

/** Merge PDF soft-wrapped lines into paragraphs; keep equation lines separate. */
function formatPromptParagraphs(prompt) {
  const lines = String(prompt || '').split(/\n/)
  const paras = []
  let buf = []
  const flush = () => {
    if (buf.length) {
      paras.push(buf.join(' '))
      buf = []
    }
  }
  for (const raw of lines) {
    const line = raw.trim()
    if (!line) {
      flush()
      continue
    }
    if (looksLikeEquation(line) || /\{\{eq:\d+\}\}/.test(line)) {
      flush()
      paras.push(line)
      continue
    }
    buf.push(line)
  }
  flush()
  return paras
}

function PracticeQuestionBody({ question, hideFigure = false, hidePassage = false }) {
  const figure = hideFigure ? null : (question.figure || null)
  const equations = Array.isArray(question.equations) ? question.equations : []
  const passage = hidePassage ? null : question.passage
  const prompt = String(question.prompt || '').trim()
  const promptLines = prompt ? formatPromptParagraphs(prompt) : []

  return (
    <>
      {figure ? (
        <div className="practice-figure-wrap">
          <img src={figure} alt="Figure" className="practice-figure" />
        </div>
      ) : null}
      {passage ? (
        <div className="practice-passage-text">
          {String(passage).split(/\n{2,}/).map((para, i) => (
            <p key={i}>{para}</p>
          ))}
        </div>
      ) : null}
      {promptLines.length ? (
        <div className="practice-prompt">
          {promptLines.map((line, i) => (
            <p key={i} className={looksLikeEquation(line) ? 'practice-eq-line' : undefined}>
              {renderPromptLine(line, equations)}
            </p>
          ))}
        </div>
      ) : equations.length ? (
        <div className="practice-prompt">
          {equations.map((src) => (
            <img key={src} src={src} alt="Equation" className="practice-eq-image" />
          ))}
        </div>
      ) : (
        <p className="practice-prompt">Question text unavailable.</p>
      )}
    </>
  )
}

function PracticeChoiceList({
  question,
  letters,
  selected,
  eliminated,
  feedbackMode,
  reveal,
  locked = false,
  onSelect,
  onEliminate,
}) {
  const showFeedback = Boolean(reveal) && selected != null && selected !== ''
  const correctIdx = typeof question.answer === 'number' ? question.answer : null
  const choices = question.choices?.length ? question.choices : ['', '', '', '']

  return (
    <div className="practice-choices">
      {choices.map((choice, i) => {
        const { image } = normalizeChoice(choice)
        const text = choiceDisplayText(choice)
        const isSelected = selected === i
        const crossed = (eliminated || []).includes(i)
        let state = ''
        if (showFeedback && correctIdx != null) {
          if (i === correctIdx) state = 'is-correct'
          else if (isSelected && i !== correctIdx) state = 'is-wrong'
        }
        return (
          <div
            key={`${question.id}-${letters[i]}`}
            className={`practice-choice ${isSelected ? 'selected' : ''} ${crossed ? 'crossed' : ''} ${state} ${locked ? 'locked' : ''}`}
          >
            <button
              type="button"
              className="practice-choice-main"
              disabled={locked}
              onClick={() => {
                if (!locked) onSelect(i)
              }}
            >
              <span className="practice-choice-letter">{letters[i]}</span>
              <span className="practice-choice-content">
                {text ? <span className="practice-choice-text math-text">{renderMathText(text, { asEquation: true })}</span> : null}
                {!text && image ? <img src={image} alt="" className="practice-choice-image" /> : null}
                {!text && !image ? <span className="practice-choice-text">{letters[i]}</span> : null}
              </span>
            </button>
            <button
              type="button"
              className={`practice-choice-x ${crossed ? 'on' : ''}`}
              aria-label={crossed ? 'Restore answer choice' : 'Cross out answer choice'}
              aria-pressed={crossed}
              disabled={locked}
              onClick={() => {
                if (!locked) onEliminate(i)
              }}
            >
              ×
            </button>
          </div>
        )
      })}
    </div>
  )
}

function MathPracticeSession({ config, onEnd, onCompleteQuestion, onCompleteSession }) {
  const excludeIds = useMemo(
    () => (config.excludeIds instanceof Set ? config.excludeIds : new Set(config.excludeIds || [])),
    [config.excludeIds],
  )
  const builtQuestions = useMemo(
    () => buildPracticeQuestions(
      config.count,
      config.shuffle,
      config.domains,
      config.difficulties || config.difficulty,
      config.questions,
      config.pools,
      excludeIds,
    ),
    [config.count, config.shuffle, config.domains, config.difficulties, config.difficulty, config.questions, config.pools, excludeIds],
  )
  const [sessionQuestions, setSessionQuestions] = useState(null)
  const questions = sessionQuestions || builtQuestions
  const total = questions.length
  const feedbackMode = config.feedbackMode || 'deferred'
  const source = config.source || (feedbackMode === 'immediate' ? 'bank' : 'set')
  const initialIndex = Math.min(
    Math.max(0, config.startIndex || 0),
    Math.max(0, total - 1),
  )
  const [index, setIndex] = useState(initialIndex)
  const [answers, setAnswers] = useState(() => {
    if (Array.isArray(config.initialAnswers) && config.initialAnswers.length === (config.count || config.initialAnswers.length)) {
      return [...config.initialAnswers]
    }
    return Array(config.count || 0).fill(null)
  })
  const [eliminated, setEliminated] = useState(() => Array(config.count || 0).fill(null).map(() => []))
  const [missedOnce, setMissedOnce] = useState(() => Array(config.count || 0).fill(false))
  const [explainOpen, setExplainOpen] = useState(false)
  const [pdfOpen, setPdfOpen] = useState(false)
  const [resultsOpen, setResultsOpen] = useState(false)
  const [reviewMode, setReviewMode] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const [paused, setPaused] = useState(false)
  const [calcOpen, setCalcOpen] = useState(true)
  const [calcMode, setCalcMode] = useState('calculator')
  const [questionTimes, setQuestionTimes] = useState(() => Array(config.count || 0).fill(0))
  const loggedQuestionsRef = useRef(new Set())
  const setReportedRef = useRef(false)
  const answersRef = useRef(answers)
  const elapsedRef = useRef(elapsed)
  const questionsRef = useRef(questions)
  const questionTimesRef = useRef(questionTimes)
  const indexRef = useRef(index)
  const onCompleteSessionRef = useRef(onCompleteSession)
  answersRef.current = answers
  elapsedRef.current = elapsed
  questionsRef.current = questions
  questionTimesRef.current = questionTimes
  indexRef.current = index
  onCompleteSessionRef.current = onCompleteSession

  useEffect(() => {
    setSessionQuestions(null)
    const seeded = Array.isArray(config.initialAnswers) && config.initialAnswers.length === builtQuestions.length
      ? [...config.initialAnswers]
      : Array(builtQuestions.length).fill(null)
    setAnswers(seeded)
    answersRef.current = seeded
    setEliminated(Array(builtQuestions.length).fill(null).map(() => []))
    setMissedOnce(Array(builtQuestions.length).fill(false))
    const times = Array(builtQuestions.length).fill(0)
    setQuestionTimes(times)
    questionTimesRef.current = times
    setIndex(Math.min(Math.max(0, config.startIndex || 0), Math.max(0, builtQuestions.length - 1)))
    setExplainOpen(false)
    setPdfOpen(false)
    setResultsOpen(false)
    setReviewMode(false)
    setElapsed(0)
    elapsedRef.current = 0
    loggedQuestionsRef.current = new Set()
    setReportedRef.current = false
  }, [builtQuestions, config.startIndex, config.initialAnswers])

  useEffect(() => {
    setPdfOpen(false)
  }, [index])

  useEffect(() => {
    if (paused || reviewMode) return undefined
    const id = setInterval(() => {
      setElapsed((t) => {
        const next = t + 1
        elapsedRef.current = next
        return next
      })
      setQuestionTimes((prev) => {
        const next = prev.length === questionsRef.current.length
          ? [...prev]
          : Array(questionsRef.current.length).fill(0).map((_, i) => prev[i] || 0)
        const i = indexRef.current
        next[i] = (next[i] || 0) + 1
        questionTimesRef.current = next
        return next
      })
    }, 1000)
    return () => clearInterval(id)
  }, [paused, reviewMode])

  const currentQuestionElapsed = () => {
    const times = questionTimesRef.current || []
    return Math.max(0, Number(times[indexRef.current]) || 0)
  }

  const reportSetIfNeeded = () => {
    if (source !== 'set' || setReportedRef.current) return
    const qs = questionsRef.current || []
    if (!qs.length) return
    const answers = answersRef.current || []
    const hasAnswered = qs.some((q, i) => isAnswerCorrect(q, answers[i]) != null)
    if (!hasAnswered) return
    setReportedRef.current = true
    onCompleteSessionRef.current?.({
      subject: 'math',
      questions: qs,
      answers,
      elapsed: elapsedRef.current,
      questionTimes: questionTimesRef.current,
      config,
    })
  }

  const shuffleUnanswered = () => {
    const next = shuffleSessionUnanswered(questions, answers, eliminated, index, missedOnce, questionTimes)
    setSessionQuestions(next.questions)
    setAnswers(next.answers)
    answersRef.current = next.answers
    setEliminated(next.eliminated)
    setMissedOnce(next.missedOnce)
    setQuestionTimes(next.questionTimes)
    questionTimesRef.current = next.questionTimes
    setIndex(next.index)
  }

  if (!total) {
    return (
      <div className="practice-page">
        <div className="card practice-question-card" style={{ padding: 24 }}>
          <h2 style={{ margin: '0 0 8px', color: '#12346f' }}>No questions left</h2>
          <p style={{ margin: '0 0 16px', color: '#687590' }}>
            You’ve already completed every question that matches these filters.
          </p>
          <button type="button" className="practice-outline-btn" onClick={onEnd}>
            Back
          </button>
        </div>
      </div>
    )
  }

  const current = questions[index]
  const progressPct = ((index + 1) / questions.length) * 100
  const letters = ['A', 'B', 'C', 'D']
  const difficultyLabel = current?.difficulty
    || (Array.isArray(config.difficulties)
      ? (config.difficulties.length === 1 ? config.difficulties[0] : config.difficulties.join(' · '))
      : (config.difficulty || 'Medium'))
  const diffLevel = current?.difficulty === 'Easy' || difficultyLabel === 'Easy'
    ? 1
    : current?.difficulty === 'Hard' || difficultyLabel === 'Hard'
      ? 3
      : 2

  const revealFeedback = feedbackMode === 'immediate' || reviewMode
  const answersLocked = source === 'set' && reviewMode
  const answered = answers[index] != null && answers[index] !== ''
  const verdict = revealFeedback && answered ? isAnswerCorrect(current, answers[index]) : null

  const recordAnswer = (value) => {
    if (answersLocked) return
    setAnswers((prev) => {
      const next = [...prev]
      next[index] = value
      answersRef.current = next
      return next
    })
    if (!current) return
    if (isAnswerCorrect(current, value) === false) {
      setMissedOnce((prev) => {
        const next = [...prev]
        next[index] = true
        return next
      })
    }
    const qid = String(current.id)
    const firstLog = source === 'bank' && !loggedQuestionsRef.current.has(qid)
    if (firstLog) loggedQuestionsRef.current.add(qid)
    onCompleteQuestion?.(current, value, 'math', {
      source,
      logHistory: firstLog,
      updateProgress: source === 'bank',
      elapsed: currentQuestionElapsed(),
    })
  }

  const selectChoice = (choiceIdx) => {
    recordAnswer(choiceIdx)
  }

  const toggleEliminate = (choiceIdx) => {
    if (answersLocked) return
    setEliminated((prev) => {
      const next = prev.map((row) => [...row])
      const row = next[index]
      next[index] = row.includes(choiceIdx) ? row.filter((x) => x !== choiceIdx) : [...row, choiceIdx]
      return next
    })
  }

  const handleEnd = () => {
    if (feedbackMode === 'deferred' && !reviewMode) {
      reportSetIfNeeded()
      setResultsOpen(true)
      setReviewMode(true)
      return
    }
    onEnd?.()
  }

  return (
    <div className="practice-page">
      <div className="practice-topbar">
        <div className="practice-topic">
          <div className="practice-topic-domain">{config.domain}</div>
          <div className="practice-topic-sub">{current.skill || current.topic || config.topic}</div>
        </div>

        <div className="practice-progress-block">
          <div className="practice-progress-label">Question {index + 1} of {questions.length}</div>
          <div className="practice-progress-track">
            <div className="practice-progress-fill" style={{ width: `${progressPct}%` }} />
          </div>
        </div>

        <div className="practice-meta-right">
          <div className="practice-diff" title={difficultyLabel}>
            <span className="practice-diff-bars" aria-hidden="true">
              {[1, 2, 3].map((n) => (
                <i key={n} className={n <= diffLevel ? 'on' : ''} />
              ))}
            </span>
            <span>{current?.difficulty || difficultyLabel}</span>
          </div>
          <div className="practice-timer">
            <Clock size={15} />
            <div>
              <div className="practice-timer-value">
                {formatElapsed(source === 'bank' ? (questionTimes[index] || 0) : elapsed)}
              </div>
              <div className="practice-timer-label">
                {source === 'bank' ? 'Question Time' : 'Time Elapsed'}
              </div>
            </div>
          </div>
          <a
            className="practice-outline-btn"
            href={FORMULA_SHEET_URL}
            target="_blank"
            rel="noreferrer"
          >
            <FileText size={15} />
            Reference Sheet
          </a>
          <button
            type="button"
            className="practice-outline-btn"
            onClick={() => setPaused((v) => !v)}
          >
            <Pause size={15} />
            {paused ? 'Resume' : 'Pause'}
          </button>
        </div>
      </div>

      <div className={`practice-split ${calcOpen ? '' : 'calc-closed'}`}>
        {calcOpen && (
          <div className="practice-calc-card card">
            <div className="practice-calc-header">
              <div className="practice-calc-tabs" role="tablist">
                <button
                  type="button"
                  role="tab"
                  className={`practice-calc-tab ${calcMode === 'calculator' ? 'on' : ''}`}
                  aria-selected={calcMode === 'calculator'}
                  onClick={() => setCalcMode('calculator')}
                >
                  Calculator
                </button>
                <button
                  type="button"
                  role="tab"
                  className={`practice-calc-tab ${calcMode === 'graphing' ? 'on' : ''}`}
                  aria-selected={calcMode === 'graphing'}
                  onClick={() => setCalcMode('graphing')}
                >
                  Graphing
                </button>
              </div>
              <div className="practice-calc-actions">
                <button
                  type="button"
                  className="practice-icon-btn"
                  title="Pop Out"
                  aria-label="Pop Out"
                  onClick={() => window.open('https://www.desmos.com/calculator', '_blank', 'noopener,noreferrer')}
                >
                  <ExternalLink size={15} />
                </button>
                <button
                  type="button"
                  className="practice-icon-btn"
                  title="Close"
                  aria-label="Close calculator"
                  onClick={() => setCalcOpen(false)}
                >
                  <X size={15} />
                </button>
              </div>
            </div>
            <DesmosEmbed mode={calcMode} />
            <div className="practice-desmos-credit">powered by desmos</div>
          </div>
        )}

        <div className="card practice-question-card">
          <div className="practice-q-toolbar">
            <div className="practice-q-left">
              <span className="practice-q-number">{index + 1}</span>
              {verdict != null && (
                <span className={`practice-verdict ${verdict ? 'ok' : 'bad'}`}>
                  {verdict ? 'Correct' : 'Incorrect'}
                </span>
              )}
            </div>
            <div className="practice-q-right">
              <button type="button" className="practice-text-btn">Report</button>
              {current?.pdfPreview && (
                <button
                  type="button"
                  className={`practice-outline-btn compact ${pdfOpen ? 'active' : ''}`}
                  aria-pressed={pdfOpen}
                  title="View original PDF question"
                  onClick={() => setPdfOpen((v) => !v)}
                >
                  <FileText size={14} />
                  PDF
                </button>
              )}
              {!calcOpen && (
                <button
                  type="button"
                  className="practice-outline-btn compact"
                  onClick={() => setCalcOpen(true)}
                >
                  <Calculator size={14} />
                  Calculator
                </button>
              )}
            </div>
          </div>

          {pdfOpen && current?.pdfPreview ? (
            <PracticePdfPanel
              pdf={current.pdf}
              pdfPage={current.pdfPage}
              pdfPreview={current.pdfPreview}
            />
          ) : (
            <>
              <PracticeQuestionBody question={current} />

              {current.type === 'spr' ? (
                <SprAnswerInput
                  key={current.id}
                  question={current}
                  value={answers[index] ?? ''}
                  revealAnswer={revealFeedback}
                  locked={answersLocked}
                  onSubmit={(value) => recordAnswer(value)}
                />
              ) : (
                <PracticeChoiceList
                  question={current}
                  letters={letters}
                  selected={answers[index]}
                  eliminated={eliminated[index]}
                  feedbackMode={feedbackMode}
                  reveal={revealFeedback}
                  locked={answersLocked}
                  onSelect={selectChoice}
                  onEliminate={toggleEliminate}
                />
              )}
            </>
          )}
        </div>
      </div>

      <div className="practice-footer">
        <div className="practice-footer-left">
          <PracticeQuestionBankMenu
            questions={questions}
            index={index}
            answers={answers}
            missedOnce={missedOnce}
            revealResults={revealFeedback}
            onJump={setIndex}
            onShuffleUnanswered={answersLocked ? undefined : shuffleUnanswered}
          />
          <button
            type="button"
            className="practice-outline-btn"
            disabled={!answered || !revealFeedback}
            onClick={() => setExplainOpen(true)}
          >
            <List size={15} />
            Explanation
          </button>
        </div>
        <div className="practice-footer-right">
          <button
            type="button"
            className="practice-prev-btn"
            disabled={index === 0}
            onClick={() => setIndex((i) => Math.max(0, i - 1))}
          >
            Previous
          </button>
          <button
            type="button"
            className="practice-next-btn"
            disabled={index >= questions.length - 1}
            onClick={() => setIndex((i) => Math.min(questions.length - 1, i + 1))}
          >
            Next <ChevronRight size={16} />
          </button>
          <button
            type="button"
            className={`practice-end-inline ${source === 'bank' || (reviewMode && source === 'set') ? 'exit' : ''}`}
            onClick={handleEnd}
          >
            {source === 'bank' || (reviewMode && source === 'set') ? 'Exit' : 'End'}
          </button>
        </div>
      </div>

      <PracticeExplanationModal
        open={explainOpen}
        explanation={current?.explanation}
        onClose={() => setExplainOpen(false)}
      />
      <PracticeResultsModal
        open={resultsOpen}
        questions={questions}
        answers={answers}
        onClose={() => setResultsOpen(false)}
        onExit={() => onEnd?.()}
      />
    </div>
  )
}

function DesmosEmbed({ mode }) {
  const hostRef = useRef(null)
  const calcRef = useRef(null)

  useEffect(() => {
    let disposed = false

    loadDesmosApi()
      .then((Desmos) => {
        if (disposed || !hostRef.current) return
        if (calcRef.current) {
          calcRef.current.destroy()
          calcRef.current = null
        }
        hostRef.current.innerHTML = ''
        if (mode === 'graphing' || mode === 'calculator') {
          calcRef.current = Desmos.GraphingCalculator(hostRef.current, {
            expressions: true,
            settingsMenu: true,
            zoomButtons: true,
          })
        } else {
          calcRef.current = Desmos.ScientificCalculator(hostRef.current, {
            degreeMode: true,
          })
        }
      })
      .catch(() => {})

    return () => {
      disposed = true
      if (calcRef.current) {
        calcRef.current.destroy()
        calcRef.current = null
      }
    }
  }, [mode])

  return <div className="practice-desmos-host" ref={hostRef} />
}

function ReadingPracticeSession({ config, onEnd, onCompleteQuestion, onCompleteSession }) {
  const excludeIds = useMemo(
    () => (config.excludeIds instanceof Set ? config.excludeIds : new Set(config.excludeIds || [])),
    [config.excludeIds],
  )
  const builtQuestions = useMemo(
    () => buildReadingQuestions(
      config.count,
      config.shuffle,
      config.domains,
      config.difficulties || config.difficulty,
      config.questions,
      config.pools,
      excludeIds,
    ),
    [config.count, config.shuffle, config.domains, config.difficulties, config.difficulty, config.questions, config.pools, excludeIds],
  )
  const [sessionQuestions, setSessionQuestions] = useState(null)
  const questions = sessionQuestions || builtQuestions
  const total = questions.length
  const feedbackMode = config.feedbackMode || 'deferred'
  const source = config.source || (feedbackMode === 'immediate' ? 'bank' : 'set')
  const initialIndex = Math.min(
    Math.max(0, config.startIndex || 0),
    Math.max(0, total - 1),
  )
  const [index, setIndex] = useState(initialIndex)
  const [answers, setAnswers] = useState(() => {
    if (Array.isArray(config.initialAnswers) && config.initialAnswers.length) {
      return [...config.initialAnswers]
    }
    return Array(config.count || 0).fill(null)
  })
  const [eliminated, setEliminated] = useState(() => Array(config.count || 0).fill(null).map(() => []))
  const [missedOnce, setMissedOnce] = useState(() => Array(config.count || 0).fill(false))
  const [explainOpen, setExplainOpen] = useState(false)
  const [pdfOpen, setPdfOpen] = useState(false)
  const [resultsOpen, setResultsOpen] = useState(false)
  const [reviewMode, setReviewMode] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const [paused, setPaused] = useState(false)
  const [questionTimes, setQuestionTimes] = useState(() => Array(config.count || 0).fill(0))
  const loggedQuestionsRef = useRef(new Set())
  const setReportedRef = useRef(false)
  const answersRef = useRef(answers)
  const elapsedRef = useRef(elapsed)
  const questionsRef = useRef(questions)
  const questionTimesRef = useRef(questionTimes)
  const indexRef = useRef(index)
  const onCompleteSessionRef = useRef(onCompleteSession)
  answersRef.current = answers
  elapsedRef.current = elapsed
  questionsRef.current = questions
  questionTimesRef.current = questionTimes
  indexRef.current = index
  onCompleteSessionRef.current = onCompleteSession

  useEffect(() => {
    setSessionQuestions(null)
    const seeded = Array.isArray(config.initialAnswers) && config.initialAnswers.length === builtQuestions.length
      ? [...config.initialAnswers]
      : Array(builtQuestions.length).fill(null)
    setAnswers(seeded)
    answersRef.current = seeded
    setEliminated(Array(builtQuestions.length).fill(null).map(() => []))
    setMissedOnce(Array(builtQuestions.length).fill(false))
    const times = Array(builtQuestions.length).fill(0)
    setQuestionTimes(times)
    questionTimesRef.current = times
    setIndex(Math.min(Math.max(0, config.startIndex || 0), Math.max(0, builtQuestions.length - 1)))
    setExplainOpen(false)
    setPdfOpen(false)
    setResultsOpen(false)
    setReviewMode(false)
    setElapsed(0)
    elapsedRef.current = 0
    loggedQuestionsRef.current = new Set()
    setReportedRef.current = false
  }, [builtQuestions, config.startIndex, config.initialAnswers])

  useEffect(() => {
    setPdfOpen(false)
  }, [index])

  useEffect(() => {
    if (paused || reviewMode) return undefined
    const id = setInterval(() => {
      setElapsed((t) => {
        const next = t + 1
        elapsedRef.current = next
        return next
      })
      setQuestionTimes((prev) => {
        const next = prev.length === questionsRef.current.length
          ? [...prev]
          : Array(questionsRef.current.length).fill(0).map((_, i) => prev[i] || 0)
        const i = indexRef.current
        next[i] = (next[i] || 0) + 1
        questionTimesRef.current = next
        return next
      })
    }, 1000)
    return () => clearInterval(id)
  }, [paused, reviewMode])

  const currentQuestionElapsed = () => {
    const times = questionTimesRef.current || []
    return Math.max(0, Number(times[indexRef.current]) || 0)
  }

  const reportSetIfNeeded = () => {
    if (source !== 'set' || setReportedRef.current) return
    const qs = questionsRef.current || []
    if (!qs.length) return
    const answers = answersRef.current || []
    const hasAnswered = qs.some((q, i) => isAnswerCorrect(q, answers[i]) != null)
    if (!hasAnswered) return
    setReportedRef.current = true
    onCompleteSessionRef.current?.({
      subject: 'reading',
      questions: qs,
      answers,
      elapsed: elapsedRef.current,
      questionTimes: questionTimesRef.current,
      config,
    })
  }

  const shuffleUnanswered = () => {
    const next = shuffleSessionUnanswered(questions, answers, eliminated, index, missedOnce, questionTimes)
    setSessionQuestions(next.questions)
    setAnswers(next.answers)
    answersRef.current = next.answers
    setEliminated(next.eliminated)
    setMissedOnce(next.missedOnce)
    setQuestionTimes(next.questionTimes)
    questionTimesRef.current = next.questionTimes
    setIndex(next.index)
  }

  if (!total) {
    return (
      <div className="practice-page">
        <div className="card practice-question-card" style={{ padding: 24 }}>
          <h2 style={{ margin: '0 0 8px', color: '#12346f' }}>No questions left</h2>
          <p style={{ margin: '0 0 16px', color: '#687590' }}>
            You’ve already completed every question that matches these filters.
          </p>
          <button type="button" className="practice-outline-btn" onClick={onEnd}>
            Back
          </button>
        </div>
      </div>
    )
  }

  const current = questions[index]
  const progressPct = ((index + 1) / questions.length) * 100
  const letters = ['A', 'B', 'C', 'D']
  const difficultyLabel = current?.difficulty
    || (Array.isArray(config.difficulties)
      ? (config.difficulties.length === 1 ? config.difficulties[0] : config.difficulties.join(' · '))
      : (config.difficulty || 'Medium'))
  const diffLevel = current?.difficulty === 'Easy' || difficultyLabel === 'Easy'
    ? 1
    : current?.difficulty === 'Hard' || difficultyLabel === 'Hard'
      ? 3
      : 2

  const revealFeedback = feedbackMode === 'immediate' || reviewMode
  const answersLocked = source === 'set' && reviewMode
  const answered = answers[index] != null && answers[index] !== ''
  const verdict = revealFeedback && answered ? isAnswerCorrect(current, answers[index]) : null

  const selectChoice = (choiceIdx) => {
    if (answersLocked) return
    setAnswers((prev) => {
      const next = [...prev]
      next[index] = choiceIdx
      answersRef.current = next
      return next
    })
    if (!current) return
    if (isAnswerCorrect(current, choiceIdx) === false) {
      setMissedOnce((prev) => {
        const next = [...prev]
        next[index] = true
        return next
      })
    }
    const qid = String(current.id)
    const firstLog = source === 'bank' && !loggedQuestionsRef.current.has(qid)
    if (firstLog) loggedQuestionsRef.current.add(qid)
    onCompleteQuestion?.(current, choiceIdx, 'reading', {
      source,
      logHistory: firstLog,
      updateProgress: source === 'bank',
      elapsed: currentQuestionElapsed(),
    })
  }

  const toggleEliminate = (choiceIdx) => {
    if (answersLocked) return
    setEliminated((prev) => {
      const next = prev.map((row) => [...row])
      const row = next[index]
      next[index] = row.includes(choiceIdx) ? row.filter((x) => x !== choiceIdx) : [...row, choiceIdx]
      return next
    })
  }

  const handleEnd = () => {
    if (feedbackMode === 'deferred' && !reviewMode) {
      reportSetIfNeeded()
      setResultsOpen(true)
      setReviewMode(true)
      return
    }
    onEnd?.()
  }

  return (
    <div className="practice-page reading-practice">
      <div className="practice-topbar">
        <div className="practice-topic">
          <div className="practice-topic-domain">{config.domain}</div>
          <div className="practice-topic-sub">{current.skill || current.topic || config.topic}</div>
        </div>

        <div className="practice-progress-block">
          <div className="practice-progress-label">Question {index + 1} of {questions.length}</div>
          <div className="practice-progress-track">
            <div className="practice-progress-fill reading-progress-fill" style={{ width: `${progressPct}%` }} />
          </div>
        </div>

        <div className="practice-meta-right">
          <div className="practice-diff" title={difficultyLabel}>
            <span className="practice-diff-bars reading-diff-bars" aria-hidden="true">
              {[1, 2, 3].map((n) => (
                <i key={n} className={n <= diffLevel ? 'on' : ''} />
              ))}
            </span>
            <span>{current?.difficulty || difficultyLabel}</span>
          </div>
          <div className="practice-timer">
            <Clock size={15} />
            <div>
              <div className="practice-timer-value">
                {formatElapsed(source === 'bank' ? (questionTimes[index] || 0) : elapsed)}
              </div>
              <div className="practice-timer-label">
                {source === 'bank' ? 'Question Time' : 'Time Elapsed'}
              </div>
            </div>
          </div>
          <button
            type="button"
            className="practice-outline-btn reading-outline-btn"
            onClick={() => setPaused((v) => !v)}
          >
            <Pause size={15} />
            {paused ? 'Resume' : 'Pause'}
          </button>
        </div>
      </div>

      <div className="practice-split reading-split">
        <div className="card practice-passage-card">
          {pdfOpen && current?.pdf && current?.pdfPage != null ? (
            <PracticePdfFramePanel pdf={current.pdf} pdfPage={current.pdfPage} tone="reading" />
          ) : (
            <>
              <div className="practice-passage-label">{current.passageTitle || 'Passage'}</div>
              <div className="practice-passage-body">
                {current.source ? (
                  <p className="practice-passage-source">{current.source}</p>
                ) : null}
                {current.figure ? (
                  <div className="practice-figure-wrap reading-figure-wrap">
                    <img src={current.figure} alt="Passage figure" className="practice-figure reading-figure" />
                  </div>
                ) : null}
                {(current.passage || '')
                  .split(/\n{2,}/)
                  .map((para) => para.trim())
                  .filter(Boolean)
                  .map((para, i) => (
                    <p key={i}>{para}</p>
                  ))}
              </div>
            </>
          )}
        </div>

        <div className="card practice-question-card">
          <div className="practice-q-toolbar">
            <div className="practice-q-left">
              <span className="practice-q-number reading-q-number">{index + 1}</span>
              {verdict != null && (
                <span className={`practice-verdict ${verdict ? 'ok' : 'bad'}`}>
                  {verdict ? 'Correct' : 'Incorrect'}
                </span>
              )}
            </div>
            <div className="practice-q-right">
              <button type="button" className="practice-text-btn reading-text-btn">Report</button>
              {current?.pdf && current?.pdfPage != null && (
                <button
                  type="button"
                  className={`practice-outline-btn compact reading-outline-btn ${pdfOpen ? 'active' : ''}`}
                  aria-pressed={pdfOpen}
                  title="View original PDF page"
                  onClick={() => setPdfOpen((v) => !v)}
                >
                  <FileText size={14} />
                  PDF
                </button>
              )}
            </div>
          </div>

          <PracticeQuestionBody question={current} hideFigure hidePassage />

          <PracticeChoiceList
            question={current}
            letters={letters}
            selected={answers[index]}
            eliminated={eliminated[index]}
            feedbackMode={feedbackMode}
            reveal={revealFeedback}
            locked={answersLocked}
            onSelect={selectChoice}
            onEliminate={toggleEliminate}
          />
        </div>
      </div>

      <div className="practice-footer">
        <div className="practice-footer-left">
          <PracticeQuestionBankMenu
            questions={questions}
            index={index}
            answers={answers}
            missedOnce={missedOnce}
            revealResults={revealFeedback}
            onJump={setIndex}
            onShuffleUnanswered={answersLocked ? undefined : shuffleUnanswered}
          />
          <button
            type="button"
            className="practice-outline-btn reading-outline-btn"
            disabled={!answered || !revealFeedback}
            onClick={() => setExplainOpen(true)}
          >
            <List size={15} />
            Explanation
          </button>
        </div>
        <div className="practice-footer-right">
          <button
            type="button"
            className="practice-prev-btn reading-prev-btn"
            disabled={index === 0}
            onClick={() => setIndex((i) => Math.max(0, i - 1))}
          >
            Previous
          </button>
          <button
            type="button"
            className="practice-next-btn reading-next-btn"
            disabled={index >= questions.length - 1}
            onClick={() => setIndex((i) => Math.min(questions.length - 1, i + 1))}
          >
            Next <ChevronRight size={16} />
          </button>
          <button
            type="button"
            className={`practice-end-inline ${source === 'bank' || (reviewMode && source === 'set') ? 'exit' : ''}`}
            onClick={handleEnd}
          >
            {source === 'bank' || (reviewMode && source === 'set') ? 'Exit' : 'End'}
          </button>
        </div>
      </div>

      <PracticeExplanationModal
        open={explainOpen}
        explanation={current?.explanation}
        onClose={() => setExplainOpen(false)}
      />
      <PracticeResultsModal
        open={resultsOpen}
        questions={questions}
        answers={answers}
        onClose={() => setResultsOpen(false)}
        onExit={() => onEnd?.()}
      />
    </div>
  )
}

function ProgressQuestionReview({ open, subject, questionId, answer, onClose }) {
  if (!open) return null
  const question = lookupQuestion(questionId, subject)
  const letters = ['A', 'B', 'C', 'D']
  const verdict = question ? isAnswerCorrect(question, answer) : null

  return createPortal(
    <div className="practice-modal-backdrop progress-question-backdrop" onClick={onClose} role="presentation">
      <div
        className="practice-modal practice-results-modal progress-question-modal"
        role="dialog"
        aria-modal="true"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="practice-modal-head">
          <h3>{subject === 'math' ? 'Math Question' : 'Reading & Writing Question'}</h3>
          <button type="button" className="practice-modal-close" onClick={onClose} aria-label="Close">
            <X size={18} />
          </button>
        </div>
        <div className="practice-modal-body">
          {!question ? (
            <p className="progress-empty">This question is no longer available in the bank.</p>
          ) : (
            <>
              <div className="progress-review-meta">
                <span>{[question.domain, question.skill || question.topic].filter(Boolean).join(' · ')}</span>
                {verdict != null && (
                  <span className={`practice-verdict ${verdict ? 'ok' : 'bad'}`}>
                    {verdict ? 'Correct' : 'Incorrect'}
                  </span>
                )}
                {verdict == null && (answer == null || answer === '') && (
                  <span className="practice-verdict">Unanswered</span>
                )}
              </div>
              <PracticeQuestionBody question={question} />
              {question.type === 'spr' ? (
                <SprAnswerInput
                  key={`${question.id}-review`}
                  question={question}
                  value={answer ?? ''}
                  revealAnswer
                  onSubmit={() => {}}
                />
              ) : (
                <PracticeChoiceList
                  question={question}
                  letters={letters}
                  selected={typeof answer === 'number' ? answer : null}
                  eliminated={[]}
                  feedbackMode="immediate"
                  reveal
                  onSelect={() => {}}
                  onEliminate={() => {}}
                />
              )}
              {question.explanation ? (
                <div className="progress-review-explain">
                  <strong>Explanation</strong>
                  <p>{question.explanation}</p>
                </div>
              ) : null}
            </>
          )}
        </div>
        <div className="practice-modal-actions">
          <button type="button" className="practice-next-btn" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>,
    document.body,
  )
}

function ProgressPage({ profile }) {
  const history = profile.progressHistory || []
  const sets = history.filter((item) => item.type === 'set')
  const bankLines = history.filter((item) => item.type === 'bank')
  const { streak, bestStreak } = computeStreakFromHistory(history)
  const displayBest = bestStreak
  const [expandedSetId, setExpandedSetId] = useState(null)
  const [review, setReview] = useState(null)

  const weekDays = useMemo(() => {
    const labels = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
    const today = new Date()
    const daySet = new Set(history.map((item) => localDayKey(item.createdAt)).filter(Boolean))
    // Build Mon–Sun of current week
    const dow = (today.getDay() + 6) % 7 // Monday = 0
    return labels.map((label, i) => {
      const d = new Date(today)
      d.setDate(today.getDate() - dow + i)
      const key = localDayKey(d)
      return { label, key, active: daySet.has(key), isToday: key === localDayKey(today) }
    })
  }, [history])

  const openQuestion = (subject, questionId, answer) => {
    if (!questionId) return
    setReview({ subject, questionId, answer: answer ?? null })
  }

  return (
    <div className="progress-page">
      <header className="progress-hero">
        <div className="progress-hero-badge" aria-hidden="true">
          <Trophy size={22} strokeWidth={2.1} />
        </div>
        <div>
          <h1>Progress</h1>
          <p>Practice set reports, question bank activity, and your study streak.</p>
        </div>
      </header>

      <div className="progress-summary">
        <div className="card progress-summary-card">
          <div className="progress-summary-label">Current Streak</div>
          <div className="progress-summary-value accent-orange">{streak}<span>days</span></div>
          <div className="progress-week">
            {weekDays.map((d) => (
              <div key={d.key} className={`progress-week-day ${d.active ? 'on' : ''} ${d.isToday ? 'today' : ''}`}>
                <span>{d.label}</span>
                <i>{d.active ? '✓' : ''}</i>
              </div>
            ))}
          </div>
        </div>
        <div className="card progress-summary-card">
          <div className="progress-summary-label">Best Streak</div>
          <div className="progress-summary-value">{displayBest}<span>days</span></div>
          <div className="progress-summary-sub">Longest consecutive practice stretch</div>
        </div>
        <div className="card progress-summary-card">
          <div className="progress-summary-label">Practice Sets</div>
          <div className="progress-summary-value">{sets.length}</div>
          <div className="progress-summary-sub">Finished from Math / Reading tabs</div>
        </div>
        <div className="card progress-summary-card">
          <div className="progress-summary-label">Bank Questions</div>
          <div className="progress-summary-value">{bankLines.length}</div>
          <div className="progress-summary-sub">Answered from Question Bank</div>
        </div>
      </div>

      <section className="card progress-history-card">
        <div className="progress-history-head">
          <h2>Question History</h2>
          <span>{history.length ? `${history.length} entries` : STAT_NA}</span>
        </div>

        {!history.length ? (
          <div className="progress-empty">
            Finish a Math or Reading practice set for a full report, or answer Question Bank items for compact activity lines.
          </div>
        ) : (
          <div className="progress-history-list">
            {history.map((entry) => (
              entry.type === 'set' ? (
                <article key={entry.id} className={`progress-set-tile ${entry.subject === 'math' ? 'math' : 'reading'}`}>
                  <button
                    type="button"
                    className="progress-set-toggle"
                    onClick={() => setExpandedSetId((id) => (id === entry.id ? null : entry.id))}
                    aria-expanded={expandedSetId === entry.id}
                  >
                    <div className="progress-set-top">
                      <div className="progress-set-icon" aria-hidden="true">
                        {entry.subject === 'math' ? <Calculator size={16} /> : <BookOpen size={16} />}
                      </div>
                      <div className="progress-set-copy">
                        <h3>{entry.title}</h3>
                        <p>{entry.sub}</p>
                      </div>
                      <div className="progress-set-metrics">
                        <span><em>Score</em> <strong>{formatStatPct(entry.accuracy)}</strong></span>
                        <span><em>Correct</em> <strong>{entry.correct}/{entry.total}</strong></span>
                        <span><em>Time</em> <strong>{entry.elapsed ? formatElapsed(entry.elapsed) : STAT_NA}</strong></span>
                      </div>
                      <div className="progress-set-when">{formatHistoryWhen(entry.createdAt)}</div>
                      <ChevronDown
                        size={16}
                        className={`progress-set-chevron ${expandedSetId === entry.id ? 'open' : ''}`}
                      />
                    </div>
                  </button>
                  {expandedSetId === entry.id && (
                    <div className="progress-set-items">
                      {(entry.items || []).length ? (
                        entry.items.map((item, i) => (
                          <button
                            key={`${entry.id}-${item.questionId || i}`}
                            type="button"
                            className={`progress-set-item ${item.correct == null ? 'skip' : item.correct ? 'ok' : 'bad'}`}
                            onClick={() => openQuestion(entry.subject, item.questionId, item.answer)}
                          >
                            <span>Q{i + 1}</span>
                            <span className="progress-set-item-sub">
                              {[item.domain, item.skill].filter(Boolean).join(' · ') || 'Open question'}
                            </span>
                            <span className="progress-set-item-result">
                              {item.correct == null ? 'Unanswered' : item.correct ? 'Correct' : 'Incorrect'}
                            </span>
                            <ChevronRight size={16} />
                          </button>
                        ))
                      ) : (
                        <div className="progress-empty tight">
                          No saved questions for this older set. New sets will list each question here.
                        </div>
                      )}
                    </div>
                  )}
                </article>
              ) : (
                <button
                  key={entry.id}
                  type="button"
                  className={`progress-bank-line ${entry.correct ? 'ok' : 'bad'}`}
                  onClick={() => openQuestion(entry.subject, entry.questionId, entry.answer)}
                >
                  <span className={`progress-bank-dot ${entry.correct ? 'ok' : 'bad'}`} />
                  <div className="progress-bank-copy">
                    <strong>{entry.title}</strong>
                    <span>{entry.sub}</span>
                  </div>
                  {entry.difficulty ? <span className="progress-bank-diff">{entry.difficulty}</span> : null}
                  <span className={`progress-bank-result ${entry.correct ? 'ok' : 'bad'}`}>
                    {entry.correct ? 'Correct' : 'Incorrect'}
                  </span>
                  <time>{formatHistoryWhen(entry.createdAt)}</time>
                  <ChevronRight size={16} className="progress-bank-chevron" />
                </button>
              )
            ))}
          </div>
        )}
      </section>

      <ProgressQuestionReview
        open={Boolean(review)}
        subject={review?.subject}
        questionId={review?.questionId}
        answer={review?.answer}
        onClose={() => setReview(null)}
      />
    </div>
  )
}
function Sidebar({
  page,
  profile,
  onNavigate,
  onOpenProfiles,
  onNewProfile,
  onUpdateProfile,
  onDeleteProfile,
}) {
  const items = [
    ['Dashboard', Home, 'dashboard'], ['Reading & Writing', BookOpen, 'Reading'], ['Math', Calculator, 'Math'], ['Question Bank', ClipboardList, 'Question Bank'],
    ['Practice Tests', CalendarDays, 'Practice Tests'], ['Progress', Trophy, 'Progress'],
    ['Profile Settings', Settings, 'profiles'],
  ]
  const [menuOpen, setMenuOpen] = useState(false)
  const [editOpen, setEditOpen] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const menuRef = useRef(null)
  const best = profileBestScore(profile)

  useEffect(() => {
    if (!menuOpen) return undefined
    const onPointerDown = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) setMenuOpen(false)
    }
    const onKey = (e) => {
      if (e.key === 'Escape') {
        setMenuOpen(false)
        setConfirmDelete(false)
      }
    }
    document.addEventListener('pointerdown', onPointerDown)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('pointerdown', onPointerDown)
      document.removeEventListener('keydown', onKey)
    }
  }, [menuOpen])

  const closeMenu = () => {
    setMenuOpen(false)
    setConfirmDelete(false)
  }

  return (
    <aside className="sidebar">
      <button
        type="button"
        className="sidebar-brand"
        onClick={() => onNavigate('dashboard')}
        title="Dashboard"
      >
        <Brand />
      </button>

      <nav className="sidebar-nav">
        {items.map(([label, Icon, key]) => (
          <button
            key={label}
            onClick={() => onNavigate(key)}
            className={`sidebar-item ${(key === 'dashboard' && page === 'dashboard') || page === key || (key === 'Question Bank' && (page === 'Question Bank Math' || page === 'Question Bank Reading')) ? 'active' : ''}`}
          >
            <Icon size={22} strokeWidth={1.8} /> <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-profile" ref={menuRef}>
        <button
          type="button"
          onClick={() => setMenuOpen((v) => !v)}
          className="sidebar-profile-btn"
          aria-haspopup="menu"
          aria-expanded={menuOpen}
        >
          <div className="sidebar-profile-avatar">
            {profile.name?.[0]?.toUpperCase() || 'A'}
          </div>
          <div className="sidebar-profile-copy">
            <div className="sidebar-profile-name">{profile.name}</div>
            <div className="sidebar-profile-meta">
              {best != null ? `Best ${best}` : 'No best yet'} · {profile.goalScore} Goal
            </div>
          </div>
          <ChevronDown size={16} className={`sidebar-profile-chevron ${menuOpen ? 'open' : ''}`} />
        </button>

        {menuOpen && (
          <div className="profile-menu sidebar-profile-menu" role="menu">
            <div className="profile-menu-summary">
              <div className="profile-menu-name">{profile.name}</div>
              <div className="profile-menu-meta">
                {[profile.grade, profile.school].filter(Boolean).join(' · ') || 'Add grade & school'}
              </div>
              <div className="profile-menu-scores">
                <span>Best <strong>{best ?? '—'}</strong></span>
                <span>Goal <strong>{profile.goalScore ?? '—'}</strong></span>
                {profile.testDate ? <span>Test <strong>{profile.testDate}</strong></span> : null}
              </div>
            </div>

            <button
              type="button"
              role="menuitem"
              className="profile-menu-item"
              onClick={() => {
                closeMenu()
                setEditOpen(true)
              }}
            >
              <PenLine size={16} /> Edit profile & scores
            </button>
            <button
              type="button"
              role="menuitem"
              className="profile-menu-item"
              onClick={() => {
                closeMenu()
                onOpenProfiles()
              }}
            >
              <UserRound size={16} /> Switch profile
            </button>
            <button
              type="button"
              role="menuitem"
              className="profile-menu-item"
              onClick={() => {
                closeMenu()
                onNewProfile()
              }}
            >
              <span className="text-base leading-none">＋</span> New profile
            </button>

            <div className="profile-menu-divider" />

            {!confirmDelete ? (
              <button
                type="button"
                role="menuitem"
                className="profile-menu-item danger"
                onClick={() => setConfirmDelete(true)}
              >
                <Trash2 size={16} /> Delete profile
              </button>
            ) : (
              <div className="profile-menu-confirm">
                <p>Delete <strong>{profile.name}</strong> and all local progress? This cannot be undone.</p>
                <div className="profile-menu-confirm-actions">
                  <button type="button" className="profile-menu-confirm-cancel" onClick={() => setConfirmDelete(false)}>
                    Cancel
                  </button>
                  <button
                    type="button"
                    className="profile-menu-confirm-delete"
                    onClick={() => {
                      closeMenu()
                      onDeleteProfile(profile.id)
                    }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <ProfileEditModal
        open={editOpen}
        profile={profile}
        onClose={() => setEditOpen(false)}
        onSave={(patch) => {
          onUpdateProfile(profile.id, patch)
          setEditOpen(false)
        }}
      />
    </aside>
  )
}

function ScoreProgress({ profile }) {
  const min = 400, max = 1600
  const best = profileBestScore(profile) ?? 400
  const goal = normalizeSatScore(profile.goalScore) ?? 1600
  const pct = Math.max(0, Math.min(100, ((best - min) / (max - min)) * 100))
  const pointsToGo = Math.max(0, goal - best)

  // Hypotenuse: from just past Athena's hand → bullseye center
  const start = { x: 48, y: 22 }
  const end = { x: 214, y: 40 }
  const spearRotate = (Math.atan2(end.y - start.y, end.x - start.x) * 180) / Math.PI - 5

  const [spear, setSpear] = useState(() => ({ ...start, opacity: 0, rotate: spearRotate }))

  useEffect(() => {
    setSpear({ ...start, opacity: 0, rotate: spearRotate })
    const fade = animate(0, 1, {
      duration: 0.08,
      onUpdate: (o) => setSpear((s) => ({ ...s, opacity: o })),
    })
    const flight = animate(0, 1, {
      duration: 0.42,
      ease: [0.15, 0.9, 0.2, 1],
      onUpdate: (t) => {
        setSpear((s) => ({
          ...s,
          x: start.x + (end.x - start.x) * t,
          y: start.y + (end.y - start.y) * t,
          rotate: spearRotate,
        }))
      },
    })
    return () => {
      fade.stop()
      flight.stop()
    }
  }, [pct])

  return (
    <motion.div className="card score-card" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
      <div className="score-card-title">Score Progress</div>

      <div className="score-stage">
        <div className="score-stats">
          <div className="score-stat">
            <div className="score-stat-label current">Best Score</div>
            <div className="score-stat-value current">{best}</div>
          </div>
          <div className="score-stat-divider" />
          <div className="score-stat">
            <div className="score-stat-label">Goal Score</div>
            <div className="score-stat-value goal">{goal}</div>
            <div className="score-stat-sub">{pointsToGo} points to go!</div>
          </div>
        </div>

        <div className="score-playfield">
          <img src="/athena-throwing.png" alt="" className="score-athena" />

          <svg className="score-flight" viewBox="0 0 240 120" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
            <path
              d={`M ${start.x} ${start.y} L ${end.x} ${end.y}`}
              fill="none"
              stroke="#b8c5dc"
              strokeWidth="2"
              strokeDasharray="5 7"
              strokeLinecap="round"
              pathLength="100"
            />
            <g
              opacity={spear.opacity}
              transform={`translate(${spear.x} ${spear.y}) rotate(${spear.rotate})`}
            >
              {/* Tip sits on the path point so the throw ends on the bullseye */}
              <image href="/spear.png" x="-62" y="-7" width="68" height="14" />
            </g>
          </svg>

          <img src="/target.png" alt="" className="score-target" />
        </div>

        <div className="score-bar-section">
          <div className="score-bar-track">
            <motion.div
              className="score-bar-fill"
              initial={{ width: 0 }}
              animate={{ width: `${pct}%` }}
              transition={{ duration: 0.9, delay: 0.1 }}
            />
          </div>
          <div className="score-bar-ticks" aria-hidden="true" />
          <div className="score-bar-labels">
            <span>400</span>
            <span>1000</span>
            <span>1600</span>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

function AccuracyPie({ correct, incorrect }) {
  const total = correct + incorrect
  if (!total) return null

  const size = 112
  const stroke = 18
  const r = (size - stroke) / 2
  const c = 2 * Math.PI * r
  const correctLen = (correct / total) * c
  const incorrectLen = c - correctLen

  return (
    <div className="accuracy-pie-wrap" aria-hidden="true">
      <svg className="accuracy-pie" width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          className="accuracy-pie-track"
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          strokeWidth={stroke}
        />
        {incorrect > 0 && (
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={r}
            fill="none"
            stroke="#e14b4b"
            strokeWidth={stroke}
            strokeLinecap="butt"
            strokeDasharray={`${incorrectLen} ${c}`}
            strokeDashoffset={0}
            transform={`rotate(${(correct / total) * 360 - 90} ${size / 2} ${size / 2})`}
            initial={{ strokeDasharray: `0 ${c}` }}
            animate={{ strokeDasharray: `${incorrectLen} ${c}` }}
            transition={{ duration: 0.85, ease: 'easeOut', delay: 0.15 }}
          />
        )}
        {correct > 0 && (
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={r}
            fill="none"
            stroke="#18a05e"
            strokeWidth={stroke}
            strokeLinecap="butt"
            strokeDasharray={`${correctLen} ${c}`}
            strokeDashoffset={0}
            transform={`rotate(-90 ${size / 2} ${size / 2})`}
            initial={{ strokeDasharray: `0 ${c}` }}
            animate={{ strokeDasharray: `${correctLen} ${c}` }}
            transition={{ duration: 0.85, ease: 'easeOut' }}
          />
        )}
      </svg>
      <div className="accuracy-pie-legend">
        <div className="accuracy-pie-legend-row">
          <span className="accuracy-pie-swatch correct" />
          Correct <strong>{correct}</strong>
        </div>
        <div className="accuracy-pie-legend-row">
          <span className="accuracy-pie-swatch incorrect" />
          Incorrect <strong>{incorrect}</strong>
        </div>
      </div>
    </div>
  )
}

function AccuracyCard({ profile }) {
  const entries = Object.values(profile.qbankProgress || {})
  const correct = entries.filter((item) => item.correct).length
  const incorrect = Math.max(0, entries.length - correct)
  const accuracy = deriveOverallAccuracy(profile.qbankProgress)
  const hasData = isValidStatNumber(accuracy)

  return (
    <div className="card accuracy-card">
      <div className="accuracy-deco" aria-hidden="true">❧</div>
      <div className="text-sm font-bold text-athena-navy">Overall Accuracy</div>
      <div className="mt-1 text-[42px] font-bold leading-none text-athena-green">{formatStatPct(accuracy)}</div>
      <div className="mt-2 text-sm text-[#66738c]">
        Today: {STAT_NA}
      </div>
      {hasData ? (
        <AccuracyPie correct={correct} incorrect={incorrect} />
      ) : (
        <div className="mt-6 text-sm text-[#9aa4b7]">No practice data yet</div>
      )}
    </div>
  )
}

function SectionCard({ title, icon, accent, data, onStart }) {
  const color = accent === 'purple' ? '#7A4AC8' : '#18A05E'
  const tint = accent === 'purple' ? '#f2ecfb' : '#eaf7f0'
  const accuracy = data?.accuracy
  const answered = data?.answered ?? 0
  return (
    <div className="card min-h-[292px]">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-full text-white" style={{ background: color }}>{icon}</div>
          <h3 className="text-lg font-bold text-athena-navy">{title}</h3>
        </div>
        <button className="text-sm font-semibold" style={{ color }}>View All →</button>
      </div>
      <div className="mt-5 grid grid-cols-2">
        <div>
          <div className="text-xs text-[#66738c]">Accuracy</div>
          <div className="mt-1 text-2xl font-bold" style={{ color }}>{formatStatPct(accuracy)}</div>
        </div>
        <div>
          <div className="text-xs text-[#66738c]">Questions Answered</div>
          <div className="mt-1 text-2xl font-bold text-athena-navy">{answered}</div>
        </div>
      </div>
      <div className="mt-4 h-2 rounded-full bg-[#edf0f5]">
        <motion.div
          className="h-2 rounded-full"
          style={{ background: color }}
          initial={{ width: 0 }}
          animate={{ width: `${isValidStatNumber(accuracy) ? accuracy : 0}%` }}
        />
      </div>
      <Tags label="Strengths" items={data.strengths} color={color} tint={tint} />
      <Tags label="Needs Work" items={data.needsWork} color={color} tint={tint} />
      <button
        onClick={onStart}
        className="mt-4 flex w-full items-center justify-center gap-2 rounded-full py-2.5 text-sm font-bold text-white"
        style={{ background: color }}
      >
        <span>Start {title} Practice</span>
        <ChevronRight size={17} />
      </button>
    </div>
  )
}

function Tags({ label, items, color, tint }) {
  return (
    <div className="mt-4">
      <div className="mb-2 text-[11px] text-[#66738c]">{label}</div>
      <div className="flex flex-wrap gap-2">
        {items?.length
          ? items.map((x) => (
            <span key={x} className="rounded-full px-3 py-1 text-[11px] font-medium" style={{ background: tint, color }}>{x}</span>
          ))
          : <span className="text-xs text-[#9aa4b7]">{STAT_NA}</span>}
      </div>
    </div>
  )
}

function RecentActivity({ profile, onViewAll }) {
  const recent = (profile.progressHistory || [])
    .slice(0, 3)
    .map((entry) => ({
      ...historyToActivityItem(entry),
      id: entry.id,
    }))

  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-athena-navy">Recent Activity</h3>
        <button
          type="button"
          className="text-xs font-semibold text-athena-blue"
          onClick={onViewAll}
        >
          View All Activity →
        </button>
      </div>
      <div className="mt-3 divide-y divide-[#edf0f5]">
        {recent.length ? recent.map((a) => (
          <div key={a.id} className="flex items-center gap-3 py-3">
            <CheckCircle2
              size={24}
              className={
                a.tone === 'green'
                  ? 'text-athena-green'
                  : a.tone === 'purple'
                    ? 'text-athena-purple'
                    : 'text-athena-blue'
              }
            />
            <div className="min-w-0 flex-1">
              <div className="truncate text-sm font-bold text-athena-navy">{a.title}</div>
              <div className="text-xs text-[#71809a]">{a.sub}</div>
            </div>
            <div className="text-xs font-bold text-athena-blue">{a.meta}</div>
          </div>
        )) : (
          <div className="py-8 text-center text-sm text-[#8b96aa]">
            Your completed practice will show up here.
          </div>
        )}
      </div>
    </div>
  )
}

function QuickActions() {
  const actions = [
    ['Start Practice Test', ClipboardList, '#2f62d6', '#eef3ff'],
    ['Mixed Practice', Shuffle, '#18a05e', '#edf8f2'],
  ]
  return (
    <div className="card">
      <h3 className="font-bold text-athena-navy">Quick Actions</h3>
      <div className="mt-4 grid grid-cols-2 gap-3">
        {actions.map(([label, Icon, color, bg]) => (
          <button
            key={label}
            className="quick-action-btn rounded-2xl border border-[#e8ebf2] transition hover:-translate-y-1 hover:shadow-md"
            style={{ background: bg }}
          >
            <Icon className="mx-auto shrink-0" size={22} style={{ color }} />
            <span className="quick-action-label" style={{ color: '#12346f' }}>{label}</span>
          </button>
        ))}
      </div>
    </div>
  )
}

function StreakCard({ profile }) {
  const history = profile.progressHistory || []
  const { streak, bestStreak } = computeStreakFromHistory(history)
  const displayStreak = streak
  const displayBest = bestStreak
  const daySet = new Set(history.map((item) => localDayKey(item.createdAt)).filter(Boolean))
  const today = new Date()
  const dow = (today.getDay() + 6) % 7
  const week = ['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((label, i) => {
    const d = new Date(today)
    d.setDate(today.getDate() - dow + i)
    return { label, active: daySet.has(localDayKey(d)) }
  })

  return (
    <div className="card">
      <div className="font-bold text-athena-navy">Current Streak 🔥</div>
      <div className="mt-1 text-[58px] font-bold leading-none text-[#f18700]">
        {displayStreak}<span className="ml-2 text-sm font-bold">days</span>
      </div>
      <div className="mt-5 grid grid-cols-7 gap-2 text-center">
        {week.map((d, i) => (
          <div key={`${d.label}-${i}`}>
            <div className="text-[10px] text-[#748097]">{d.label}</div>
            <div className={`mx-auto mt-2 grid h-7 w-7 place-items-center rounded-full text-[12px] font-bold ${d.active ? 'bg-[#f18700] text-white' : 'border border-[#b9c4d8] text-[#8d99ad]'}`}>
              {d.active ? '✓' : ''}
            </div>
          </div>
        ))}
      </div>
      <div className="mt-5 text-xs text-[#66738c]">Best streak: {displayBest} days</div>
    </div>
  )
}

function UpcomingCard({ profile }) {
  return (
    <div className="card">
      <h3 className="text-lg font-bold text-athena-navy">Upcoming</h3>
      <div className="mt-3 divide-y divide-[#edf0f5]">
        {profile.upcoming.map((u, i)=>(
          <div key={i} className="flex items-center gap-3 py-3">
            <div className="grid h-10 w-10 place-items-center rounded-xl bg-[#eef3ff] text-athena-blue">
              {u.type==='math'?<Calculator size={19}/>:u.type==='reading'?<BookOpen size={19}/>:<CalendarDays size={19}/>}
            </div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-sm font-bold text-athena-navy">{u.title}</div>
              <div className="truncate text-xs text-[#758099]">{u.sub}</div>
            </div>
            <ChevronRight size={18} className="text-[#77859e]" />
          </div>
        ))}
      </div>
      <button className="mt-3 text-xs font-semibold text-athena-blue">View Full Schedule →</button>
    </div>
  )
}

function CoachCard() {
  return (
    <div className="coach-card">
      <div className="coach-bubble">
        Consistency is the key to mastery. You’ve got this!
      </div>
      <div className="coach-figure">
        <img src="/athena-coach.png" alt="Athena coach" className="coach-athena" />
      </div>
    </div>
  )
}

function ProfileDrawer({ open, profiles, onClose, onOpen, onImport, onToast }) {
  const inputRef = useRef(null)

  const exportProfile = (profile) => {
    const blob = new Blob([JSON.stringify({
      format: 'ATHENA_SAT_PROFILE',
      version: FILE_VERSION,
      exportedAt: new Date().toISOString(),
      profile
    }, null, 2)], {type:'application/json'})
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${profile.name.replace(/[^a-z0-9-_]+/gi,'-') || 'profile'}.athena`
    a.click()
    URL.revokeObjectURL(url)
    onToast(`${profile.name}.athena exported`)
  }

  const importFile = async (file) => {
    try {
      const data = JSON.parse(await file.text())
      if (data.format !== 'ATHENA_SAT_PROFILE' || !data.profile?.name) throw new Error('invalid')
      const p = { ...data.profile, id: crypto.randomUUID?.() || `${Date.now()}-${Math.random()}` }
      onImport(p)
    } catch {
      onToast('Could not import that .athena file')
    }
  }

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.button className="fixed inset-0 z-40 bg-[#0d1f3e]/25 backdrop-blur-[2px]" onClick={onClose} initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} />
          <motion.aside className="fixed right-0 top-0 z-50 h-full w-[420px] max-w-[92vw] bg-white p-6 shadow-2xl"
            initial={{x:'100%'}} animate={{x:0}} exit={{x:'100%'}} transition={{type:'spring',stiffness:240,damping:28}}>
            <div className="flex items-start justify-between">
              <div><div className="text-[11px] font-bold tracking-[.17em] text-athena-blue">LOCAL PROFILES</div><h2 className="mt-1 text-2xl font-bold text-athena-navy">Choose a profile</h2></div>
              <button onClick={onClose} className="grid h-9 w-9 place-items-center rounded-full bg-[#f3f5f9]"><X size={20}/></button>
            </div>

            <div className="mt-6 space-y-3">
              {profiles.length ? profiles.map(p => (
                <div key={p.id} className="rounded-2xl border border-[#e2e7f1] p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="font-bold text-athena-navy">{p.name}</div>
                      <div className="text-xs text-[#77839a]">
                        {[
                          p.grade,
                          profileBestScore(p) != null ? `Best ${profileBestScore(p)}` : null,
                          p.goalScore != null ? `${p.goalScore} goal` : null,
                        ].filter(Boolean).join(' · ')}
                      </div>
                    </div>
                    <button onClick={()=>onOpen(p)} className="rounded-full bg-[#eef3ff] px-3 py-2 text-xs font-bold text-athena-blue">Open</button>
                  </div>
                  <button onClick={()=>exportProfile(p)} className="mt-3 flex items-center gap-2 text-xs font-semibold text-[#62718f]"><Save size={15}/> Export .athena</button>
                </div>
              )) : <div className="rounded-2xl border border-dashed border-[#d8e1f1] p-8 text-center text-sm text-[#7b879e]">No saved profiles yet.</div>}
            </div>

            <div className="absolute bottom-6 left-6 right-6 grid grid-cols-2 gap-3">
              <button onClick={()=>inputRef.current?.click()} className="flex items-center justify-center gap-2 rounded-xl border border-[#d5deef] py-3 text-sm font-bold text-athena-blue"><Import size={17}/> Import</button>
              <button onClick={onClose} className="rounded-xl bg-athena-blue py-3 text-sm font-bold text-white">Done</button>
              <input ref={inputRef} type="file" accept=".athena,application/json" className="hidden" onChange={e=>e.target.files?.[0] && importFile(e.target.files[0])}/>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  )
}