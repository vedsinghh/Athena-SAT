import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Flag, RefreshCw } from 'lucide-react'
import LegalLayout from '../components/LegalLayout'
import { isReportsAdmin, listQuestionReports } from '../lib/questionReports'
import { supabase } from '../lib/supabase'

function formatWhen(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return String(iso)
  }
}

export default function ReportsPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(true)
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      let nextEmail = ''
      if (supabase) {
        const { data } = await supabase.auth.getUser()
        nextEmail = data?.user?.email || ''
      }
      setEmail(nextEmail)
      const admin = isReportsAdmin(nextEmail)
      const list = await listQuestionReports({ admin })
      setRows(list)
    } catch (err) {
      setError(err?.message || 'Could not load reports')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const admin = isReportsAdmin(email)

  return (
    <LegalLayout title="Question reports" updated="">
      <p>
        Reports submitted from the practice <strong>Report</strong> button land here
        {admin ? ' for every user' : ' for your account'}
        , and also in Supabase → Table Editor → <code>question_reports</code>.
      </p>

      {!email ? (
        <p className="question-report-inbox-note">
          Sign in to view reports. Admins see the full compiled inbox.
        </p>
      ) : (
        <p className="question-report-inbox-note">
          Signed in as <strong>{email}</strong>
          {admin ? ' · admin inbox' : ' · showing your submissions'}
        </p>
      )}

      <div className="question-report-inbox-toolbar">
        <button type="button" className="practice-outline-btn" onClick={load} disabled={loading}>
          <RefreshCw size={14} />
          {loading ? 'Loading…' : 'Refresh'}
        </button>
        <Link to="/" className="practice-text-btn">Open app</Link>
      </div>

      {error ? <p className="question-report-error">{error}</p> : null}

      {!loading && rows.length === 0 ? (
        <p className="question-report-inbox-empty">No reports yet.</p>
      ) : null}

      <div className="question-report-inbox-list">
        {rows.map((row) => (
          <article key={row.id} className="question-report-inbox-card">
            <div className="question-report-inbox-card-top">
              <span className="question-report-inbox-reason">
                <Flag size={14} />
                {row.reason}
              </span>
              <time>{formatWhen(row.created_at)}</time>
            </div>
            <div className="question-report-inbox-meta">
              <span>{row.subject === 'reading' ? 'Reading' : 'Math'}</span>
              <span>ID {row.question_id}</span>
              {row.question_domain ? <span>{row.question_domain}</span> : null}
              {row.user_email ? <span>{row.user_email}</span> : null}
              {row._local ? <span>local backup</span> : null}
            </div>
            {row.details ? <p className="question-report-inbox-details">{row.details}</p> : null}
            {row.question_prompt ? (
              <p className="question-report-inbox-prompt">{row.question_prompt}</p>
            ) : null}
          </article>
        ))}
      </div>
    </LegalLayout>
  )
}
