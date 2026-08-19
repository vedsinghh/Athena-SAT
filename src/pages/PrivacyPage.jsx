import React from 'react'
import LegalLayout from '../components/LegalLayout'

export default function PrivacyPage() {
  return (
    <LegalLayout title="Privacy Policy" updated="August 12, 2026">
      <p>
        Athena Prep (&quot;we,&quot; &quot;us,&quot; or &quot;our&quot;) operates at{' '}
        <a href="https://athenasat.app">athenasat.app</a>. This policy explains what we collect,
        why we collect it, and how we handle your information when you use our SAT® practice platform.
      </p>

      <h2>Information we collect</h2>
      <ul>
        <li>
          <strong>Account information:</strong> email address and authentication details when you
          create an account or sign in (including through Google).
        </li>
        <li>
          <strong>Profile and practice data:</strong> names or nicknames you enter, goal scores,
          question history, accuracy, streaks, and other progress you generate while using the app.
        </li>
        <li>
          <strong>Technical data:</strong> basic device and usage information such as browser type,
          pages visited, and approximate analytics events to keep the service running reliably.
        </li>
      </ul>

      <h2>How we use information</h2>
      <p>We use your information to:</p>
      <ul>
        <li>create and secure your account</li>
        <li>save and sync your practice progress</li>
        <li>improve the product and fix issues</li>
        <li>respond to support requests</li>
      </ul>
      <p>We do not sell your personal information.</p>

      <h2>Third-party services</h2>
      <p>We rely on trusted providers to operate Athena Prep, including:</p>
      <ul>
        <li>
          <strong>Supabase</strong> — authentication, account storage, and database hosting
        </li>
        <li>
          <strong>Google</strong> — optional sign-in with Google (if you choose that option)
        </li>
        <li>
          <strong>Vercel</strong> — website hosting and performance analytics
        </li>
      </ul>
      <p>
        These providers process data according to their own privacy policies. We only share what is
        needed to provide the service.
      </p>

      <h2>Cookies and local storage</h2>
      <p>
        We use browser storage and similar technologies to keep you signed in and remember your
        preferences and progress. You can clear this data through your browser settings, though you
        may need to sign in again.
      </p>

      <h2>Data retention</h2>
      <p>
        We keep your account and practice data while your account is active. If you delete your
        account or ask us to remove your data, we will delete or anonymize it within a reasonable
        time, except where we must keep certain records for legal or security reasons.
      </p>

      <h2>Children</h2>
      <p>
        Athena Prep is intended for students preparing for the SAT®. If you are under 13, please use
        the service with a parent or guardian&apos;s permission. If you believe we have collected
        information from a child without appropriate consent, contact us and we will remove it.
      </p>

      <h2>Security</h2>
      <p>
        We use industry-standard measures through our infrastructure providers to protect your data.
        No method of transmission or storage is completely secure, but we work to safeguard your
        account and progress.
      </p>

      <h2>Your choices</h2>
      <ul>
        <li>Update profile information inside the app</li>
        <li>Sign out at any time</li>
        <li>Request account or data deletion by emailing us</li>
      </ul>

      <h2>Changes to this policy</h2>
      <p>
        We may update this policy from time to time. We will post the revised version on this page
        and update the &quot;Last updated&quot; date above.
      </p>

      <h2>Contact</h2>
      <p>
        Questions about privacy? Email{' '}
        <a href="mailto:support@athenasat.app">support@athenasat.app</a>.
      </p>
    </LegalLayout>
  )
}
