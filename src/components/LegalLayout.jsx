import React from 'react'
import { Link } from 'react-router-dom'

export default function LegalLayout({ title, updated, children }) {
  return (
    <div className="legal-page">
      <header className="legal-header">
        <Link to="/" className="legal-brand">
          <img src="/favicon.png" alt="" width="32" height="32" className="legal-brand-icon" />
          <span>
            <span className="legal-brand-name">ATHENA SAT</span>
          </span>
        </Link>
        <Link to="/" className="legal-back">← Back to app</Link>
      </header>

      <main className="legal-main">
        <article className="legal-card">
          <p className="legal-updated">{updated ? `Last updated: ${updated}` : 'Admin inbox'}</p>
          <h1>{title}</h1>
          {children}
        </article>
      </main>

      <footer className="legal-footer">
        <p>© {new Date().getFullYear()} Athena SAT</p>
        <div className="legal-footer-links">
          <Link to="/privacy">Privacy</Link>
          <span aria-hidden="true">·</span>
          <Link to="/terms">Terms</Link>
          <span aria-hidden="true">·</span>
          <Link to="/reports">Reports</Link>
        </div>
      </footer>
    </div>
  )
}
