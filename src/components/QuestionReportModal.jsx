import React, { useEffect, useState } from 'react'
import { X } from 'lucide-react'
import { REPORT_REASONS, submitQuestionReport } from '../lib/questionReports'

export default function QuestionReportModal({
  open,
  onClose,
  question,
  subject,
  userId,
  userEmail,
  profileName,
  onSubmitted,
}) {
  const [reason, setReason] = useState(REPORT_REASONS[0])
  const [details, setDetails] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!open) return
    setReason(REPORT_REASONS[0])
    setDetails('')
    setBusy(false)
    setError('')
  }, [open, question?.id])

  if (!open || !question) return null

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    if (!reason) {
      setError('Pick a reason for the report.')
      return
    }
    setBusy(true)
    try {
      const result = await submitQuestionReport({
        userId,
        userEmail,
        profileName,
        subject,
        question,
        reason,
        details,
      })
      onSubmitted?.(result)
      onClose?.()
    } catch (err) {
      setError(err?.message || 'Could not send report. Try again.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="practice-modal-backdrop" onClick={onClose} role="presentation">
      <form
        className="practice-modal question-report-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="question-report-title"
        onClick={(e) => e.stopPropagation()}
        onSubmit={submit}
      >
        <div className="practice-modal-head">
          <div>
            <div className="question-report-eyebrow">Help improve Athena</div>
            <h3 id="question-report-title">Report a problem</h3>
          </div>
          <button type="button" className="practice-modal-close" onClick={onClose} aria-label="Close">
            <X size={18} />
          </button>
        </div>

        <div className="practice-modal-body">
          <p className="question-report-meta">
            <strong>{subject === 'reading' ? 'Reading' : 'Math'}</strong>
            {question.id ? <> · ID <code>{question.id}</code></> : null}
            {question.domain ? <> · {question.domain}</> : null}
          </p>

          <label className="question-report-field">
            <span>What&apos;s wrong?</span>
            <select value={reason} onChange={(e) => setReason(e.target.value)} disabled={busy}>
              {REPORT_REASONS.map((item) => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </label>

          <label className="question-report-field">
            <span>Details (optional)</span>
            <textarea
              value={details}
              onChange={(e) => setDetails(e.target.value)}
              placeholder="Anything that helps us fix it — wrong choice, typo, missing figure…"
              rows={4}
              disabled={busy}
              maxLength={4000}
            />
          </label>

          {error ? <p className="question-report-error">{error}</p> : null}
        </div>

        <div className="practice-modal-actions">
          <button type="button" className="practice-outline-btn" onClick={onClose} disabled={busy}>
            Cancel
          </button>
          <button type="submit" className="practice-primary-btn" disabled={busy}>
            {busy ? 'Sending…' : 'Submit report'}
          </button>
        </div>
      </form>
    </div>
  )
}
