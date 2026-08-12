import { supabase } from './supabase'

const LOCAL_KEY = 'athena_question_reports_v1'

const ADMIN_EMAILS = new Set(
  [
    'support@athenasat.app',
    'vedsingh1208@gmail.com',
    import.meta.env.VITE_ADMIN_EMAIL,
  ]
    .filter(Boolean)
    .map((email) => String(email).trim().toLowerCase()),
)

export const REPORT_REASONS = [
  'Wrong answer / explanation',
  'Typo or formatting issue',
  'Image or figure problem',
  'Question content is unclear',
  'Other',
]

export function isReportsAdmin(email) {
  if (!email) return false
  return ADMIN_EMAILS.has(String(email).trim().toLowerCase())
}

function readLocalReports() {
  try {
    const parsed = JSON.parse(localStorage.getItem(LOCAL_KEY) || '[]')
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function writeLocalReports(rows) {
  try {
    localStorage.setItem(LOCAL_KEY, JSON.stringify(rows.slice(0, 500)))
  } catch {
    /* ignore quota */
  }
}

function buildRow({
  userId,
  userEmail,
  profileName,
  subject,
  question,
  reason,
  details,
}) {
  const prompt = question?.prompt || question?.passage || ''
  return {
    user_id: userId || null,
    user_email: userEmail || null,
    profile_name: profileName || null,
    subject,
    question_id: String(question?.id || 'unknown'),
    question_pool: question?.pool || null,
    question_domain: question?.domain || null,
    question_skill: question?.skill || question?.topic || null,
    question_difficulty: question?.difficulty || null,
    question_prompt: String(prompt).slice(0, 1200),
    reason,
    details: details?.trim() ? details.trim().slice(0, 4000) : null,
    page_url: typeof window !== 'undefined' ? window.location.href : null,
  }
}

export async function submitQuestionReport(payload) {
  let userId = payload.userId || null
  let userEmail = payload.userEmail || null

  if (supabase && (!userId || !userEmail)) {
    try {
      const { data } = await supabase.auth.getUser()
      userId = userId || data?.user?.id || null
      userEmail = userEmail || data?.user?.email || null
    } catch {
      /* ignore */
    }
  }

  const row = buildRow({ ...payload, userId, userEmail })

  if (supabase && userId) {
    const { data, error } = await supabase
      .from('question_reports')
      .insert(row)
      .select('id, created_at')
      .single()

    if (!error) {
      return { ok: true, id: data?.id, source: 'cloud' }
    }

    // Fall through to local backup if table is missing or insert fails
    console.warn('question_reports insert failed; saving locally', error.message)
  }

  const localRow = {
    ...row,
    id: crypto.randomUUID?.() || `local-${Date.now()}`,
    created_at: new Date().toISOString(),
    _local: true,
  }
  const existing = readLocalReports()
  writeLocalReports([localRow, ...existing])
  return { ok: true, id: localRow.id, source: 'local' }
}

export async function listQuestionReports({ admin = false } = {}) {
  const local = readLocalReports()

  if (!supabase) {
    return local.sort((a, b) => String(b.created_at).localeCompare(String(a.created_at)))
  }

  const { data, error } = await supabase
    .from('question_reports')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(admin ? 500 : 100)

  if (error) {
    console.warn('question_reports list failed', error.message)
    return local
  }

  const cloud = Array.isArray(data) ? data : []
  const cloudIds = new Set(cloud.map((r) => r.id))
  const merged = [
    ...cloud,
    ...local.filter((r) => !cloudIds.has(r.id)),
  ]
  return merged.sort((a, b) => String(b.created_at).localeCompare(String(a.created_at)))
}
