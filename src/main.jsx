import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Analytics } from '@vercel/analytics/react'
import App from './App'
import PrivacyPage from './pages/PrivacyPage'
import ReportsPage from './pages/ReportsPage'
import TermsPage from './pages/TermsPage'
import 'katex/dist/katex.min.css'
import './styles.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route path="/terms" element={<TermsPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/*" element={<App />} />
      </Routes>
      <Analytics />
    </BrowserRouter>
  </React.StrictMode>,
)