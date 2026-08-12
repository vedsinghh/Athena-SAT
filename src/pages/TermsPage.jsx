import React from 'react'
import LegalLayout from '../components/LegalLayout'

export default function TermsPage() {
  return (
    <LegalLayout title="Terms of Service" updated="August 12, 2026">
      <p>
        These Terms of Service (&quot;Terms&quot;) govern your use of Athena SAT at{' '}
        <a href="https://athenasat.app">athenasat.app</a>. By creating an account or using the
        service, you agree to these Terms.
      </p>

      <h2>About Athena SAT</h2>
      <p>
        Athena SAT is an independent SAT practice platform. We are not affiliated with, endorsed by,
        or sponsored by the College Board or the SAT exam. Practice content is designed to resemble
        digital SAT-style questions for study purposes only.
      </p>

      <h2>Accounts</h2>
      <ul>
        <li>You must provide accurate account information.</li>
        <li>You are responsible for keeping your login credentials secure.</li>
        <li>You may not share, sell, or misuse another person&apos;s account.</li>
        <li>We may suspend or terminate accounts that violate these Terms.</li>
      </ul>

      <h2>Acceptable use</h2>
      <p>You agree not to:</p>
      <ul>
        <li>attempt to break, scrape, reverse engineer, or overload the service</li>
        <li>copy, redistribute, or resell our question content or materials without permission</li>
        <li>use the service for unlawful, harassing, or fraudulent purposes</li>
        <li>interfere with other users&apos; access to the platform</li>
      </ul>

      <h2>Your content and progress</h2>
      <p>
        You keep ownership of the information you enter (such as profile details). You grant us a
        limited license to store and process that information so we can operate the service and
        display your progress back to you.
      </p>

      <h2>Free service</h2>
      <p>
        Athena SAT is free to start. Features, availability, and limits may change over time. We may
        introduce paid features in the future; if we do, we will describe them clearly before you
        are charged.
      </p>

      <h2>Disclaimer</h2>
      <p>
        THE SERVICE IS PROVIDED &quot;AS IS&quot; AND &quot;AS AVAILABLE.&quot; WE DO NOT GUARANTEE
        ANY PARTICULAR SCORE IMPROVEMENT, EXAM RESULT, OR UNINTERRUPTED ACCESS. STUDY TOOLS ARE FOR
        PRACTICE ONLY AND ARE NOT A SUBSTITUTE FOR OFFICIAL SAT PREPARATION ADVICE FROM QUALIFIED
        EDUCATORS.
      </p>

      <h2>Limitation of liability</h2>
      <p>
        TO THE FULLEST EXTENT PERMITTED BY LAW, ATHENA SAT AND ITS OPERATORS WILL NOT BE LIABLE FOR
        ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF DATA,
        PROFITS, OR GOODWILL, ARISING FROM YOUR USE OF THE SERVICE.
      </p>

      <h2>Termination</h2>
      <p>
        You may stop using Athena SAT at any time. We may suspend or terminate access if you violate
        these Terms or if we discontinue the service. Sections that reasonably should survive
        termination (such as disclaimers and limitations of liability) will remain in effect.
      </p>

      <h2>Changes</h2>
      <p>
        We may update these Terms from time to time. Continued use after changes are posted means you
        accept the updated Terms. The &quot;Last updated&quot; date above reflects the latest version.
      </p>

      <h2>Governing law</h2>
      <p>
        These Terms are governed by the laws of the United States and the State of Washington, without
        regard to conflict-of-law rules, except where prohibited by applicable law.
      </p>

      <h2>Contact</h2>
      <p>
        Questions about these Terms? Email{' '}
        <a href="mailto:support@athenasat.app">support@athenasat.app</a>.
      </p>
    </LegalLayout>
  )
}
