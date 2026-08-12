import React, { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  ArrowRight, BarChart3, BookOpen, Calculator, ChevronDown, Clock, Flame,
  LineChart, Menu, Minus, Plus, Quote, Sparkles, Star, Target, Timer, X,
} from 'lucide-react'
import mathQuestions from '../../data/mathQuestions.json'
import readingQuestions from '../../data/readingQuestions.json'
import AssetSlot from './AssetSlot'
import AuthModal from './AuthModal'
import './landing.css'

const rise = {
  hidden: { opacity: 0, y: 26 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] } },
}

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
}

function Reveal({ children, className = '', delay = 0 }) {
  return (
    <motion.div
      className={className}
      variants={rise}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, amount: 0.25 }}
      transition={{ delay }}
    >
      {children}
    </motion.div>
  )
}

function Brand() {
  return (
    <span className="lp-brand">
      <span className="lp-brand-owl" aria-hidden="true">🦉</span>
      <span className="lp-brand-text">
        <span className="lp-brand-name">ATHENA</span>
        <span className="lp-brand-sub">
          <i /> SAT <i />
        </span>
      </span>
    </span>
  )
}

const FEATURES = [
  {
    icon: BookOpen,
    title: 'Real digital SAT–style questions',
    body: 'Every item mirrors the adaptive Bluebook format — passages, grid-ins, figures, and the same answer mechanics.',
  },
  {
    icon: Timer,
    title: 'Timed sets that feel like test day',
    body: 'Run 10, 20, or full-length modules with a live timer, mark-for-review flags, and a Bluebook-style review page.',
  },
  {
    icon: Calculator,
    title: 'Built-in Desmos calculator',
    body: 'The same graphing calculator you get on the real exam, docked right beside the question.',
  },
  {
    icon: LineChart,
    title: 'Analytics that name your weak spot',
    body: 'Accuracy by domain and skill, so you stop guessing what to study and start fixing what actually costs points.',
  },
  {
    icon: Flame,
    title: 'Streaks that keep you honest',
    body: 'Daily streaks, question counts, and momentum tracking that make consistency the default.',
  },
  {
    icon: Target,
    title: 'Goal score tracking',
    body: 'Set a target, watch the gap close, and see exactly which domains are holding your score down.',
  },
]

const STEPS = [
  {
    n: '01',
    title: 'Create your free account',
    body: 'Email or Google. Takes about fifteen seconds, and your progress syncs across every device.',
  },
  {
    n: '02',
    title: 'Practice the way you learn best',
    body: 'Drill one skill in the Question Bank, or run a timed set that behaves exactly like the real thing.',
  },
  {
    n: '03',
    title: 'Fix what the data exposes',
    body: 'Analytics surface your weakest domains after every session, so your next set is always the right one.',
  },
]

const FAQS = [
  {
    q: 'Is Athena SAT really free?',
    a: 'Yes. Every question, every timed set, and all analytics are free. No card, no trial timer, no paywalled explanations.',
  },
  {
    q: 'Are the questions like the actual digital SAT?',
    a: 'They follow the digital SAT format used in Bluebook: the same domains, skills, question types, grid-in mechanics, and difficulty spread. Athena SAT is independent and not affiliated with the College Board.',
  },
  {
    q: 'Do I need to install anything?',
    a: 'No. Athena runs in your browser on laptops, tablets, and phones, and your progress syncs automatically once you sign in.',
  },
  {
    q: 'Can I practice one skill at a time?',
    a: 'Yes. The Question Bank lets you filter by domain, skill, and difficulty, then practice with instant feedback and full explanations.',
  },
  {
    q: 'What happens to my data?',
    a: 'We store your account and practice progress so it syncs across devices, and we never sell your information. See the privacy policy for details.',
  },
]

const TESTIMONIALS = [
  {
    quote: 'The analytics found the two skills wrecking my Math score in one week. I stopped studying randomly and my score moved.',
    name: 'Priya R.',
    detail: 'Junior · +120 points',
    avatar: '/landing/avatar-1.jpg',
  },
  {
    quote: 'Timed sets feel exactly like Bluebook, down to the review page. Test day was the least surprising part of my week.',
    name: 'Marcus T.',
    detail: 'Senior · 1520',
    avatar: '/landing/avatar-2.jpg',
  },
  {
    quote: 'I use the Question Bank for ten minutes a night. The streak is dumb motivating and my Reading accuracy climbed.',
    name: 'Sofia L.',
    detail: 'Sophomore · +90 points',
    avatar: '/landing/avatar-3.jpg',
  },
]

function roundDown(value, step) {
  return Math.floor(value / step) * step
}

export default function LandingPage({ onSignIn, onSignUp, onSignInWithGoogle, error, configured }) {
  const [authOpen, setAuthOpen] = useState(false)
  const [authMode, setAuthMode] = useState('signin')
  const [navOpen, setNavOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const [openFaq, setOpenFaq] = useState(0)

  const counts = useMemo(() => {
    const total = (mathQuestions?.length || 0) + (readingQuestions?.length || 0)
    return {
      total: roundDown(total, 50),
      math: roundDown(mathQuestions?.length || 0, 25),
      reading: roundDown(readingQuestions?.length || 0, 25),
    }
  }, [])

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    if (!navOpen) return undefined
    const prev = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => { document.body.style.overflow = prev }
  }, [navOpen])

  const openAuth = (mode) => {
    setAuthMode(mode)
    setAuthOpen(true)
    setNavOpen(false)
  }

  return (
    <div className="lp">
      <div className="lp-aurora" aria-hidden="true" />

      <header className={`lp-nav ${scrolled ? 'is-stuck' : ''}`}>
        <div className="lp-nav-inner">
          <a href="#top" className="lp-nav-brand" aria-label="Athena SAT home">
            <Brand />
          </a>

          <nav className="lp-nav-links" aria-label="Primary">
            <a href="#features">Features</a>
            <a href="#how">How it works</a>
            <a href="#product">Inside the app</a>
            <a href="#faq">FAQ</a>
          </nav>

          <div className="lp-nav-actions">
            <button type="button" className="lp-btn lp-btn-ghost" onClick={() => openAuth('signin')}>
              Log in
            </button>
            <button type="button" className="lp-btn lp-btn-primary" onClick={() => openAuth('signup')}>
              Sign up free
            </button>
          </div>

          <button
            type="button"
            className="lp-nav-toggle"
            aria-label={navOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={navOpen}
            onClick={() => setNavOpen((v) => !v)}
          >
            {navOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {navOpen ? (
          <div className="lp-nav-sheet">
            <a href="#features" onClick={() => setNavOpen(false)}>Features</a>
            <a href="#how" onClick={() => setNavOpen(false)}>How it works</a>
            <a href="#product" onClick={() => setNavOpen(false)}>Inside the app</a>
            <a href="#faq" onClick={() => setNavOpen(false)}>FAQ</a>
            <div className="lp-nav-sheet-actions">
              <button type="button" className="lp-btn lp-btn-outline lp-btn-block" onClick={() => openAuth('signin')}>
                Log in
              </button>
              <button type="button" className="lp-btn lp-btn-primary lp-btn-block" onClick={() => openAuth('signup')}>
                Sign up free
              </button>
            </div>
          </div>
        ) : null}
      </header>

      <main id="top">
        {/* ---------------------------------------------------------- HERO */}
        <section className="lp-hero">
          <motion.div className="lp-hero-copy" variants={stagger} initial="hidden" animate="show">
            <motion.div variants={rise} className="lp-pill">
              <Sparkles size={14} />
              Free forever · {counts.total.toLocaleString()}+ practice questions
            </motion.div>

            <motion.h1 variants={rise} className="lp-hero-title">
              The digital SAT prep that
              <span className="lp-underline"> tracks every point.</span>
            </motion.h1>

            <motion.p variants={rise} className="lp-hero-sub">
              Practice real digital SAT–style Math and Reading &amp; Writing questions, run timed
              sets that behave like Bluebook, and watch analytics point straight at the skills
              costing you points.
            </motion.p>

            <motion.div variants={rise} className="lp-hero-cta">
              <button type="button" className="lp-btn lp-btn-primary lp-btn-lg" onClick={() => openAuth('signup')}>
                Start practicing free
                <ArrowRight size={18} />
              </button>
              <a href="#product" className="lp-btn lp-btn-outline lp-btn-lg">
                See inside the app
              </a>
            </motion.div>

            <motion.div variants={rise} className="lp-hero-proof">
              <div className="lp-stars" aria-hidden="true">
                {[0, 1, 2, 3, 4].map((i) => <Star key={i} size={15} fill="currentColor" strokeWidth={0} />)}
              </div>
              <span>Built by students who took the digital SAT — and got tired of guessing what to study.</span>
            </motion.div>
          </motion.div>

          <motion.div
            className="lp-hero-art"
            initial={{ opacity: 0, y: 32, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.75, ease: [0.22, 1, 0.36, 1], delay: 0.1 }}
          >
            <div className="lp-hero-frame">
              <div className="lp-hero-frame-bar" aria-hidden="true">
                <span /><span /><span />
                <em>athenasat.app</em>
              </div>
              <AssetSlot
                src="/landing/hero-dashboard.png"
                alt="Athena SAT dashboard"
                label="Dashboard screenshot"
                spec="1440 × 900 · PNG · screenshot of your dashboard"
                ratio="16 / 10"
                rounded={0}
              />
            </div>

            <motion.div
              className="lp-float lp-float-streak"
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 5.5, repeat: Infinity, ease: 'easeInOut' }}
            >
              <div className="lp-float-icon flame"><Flame size={16} /></div>
              <div>
                <strong>12-day streak</strong>
                <span>Keep it alive</span>
              </div>
            </motion.div>

            <motion.div
              className="lp-float lp-float-accuracy"
              animate={{ y: [0, 12, 0] }}
              transition={{ duration: 6.5, repeat: Infinity, ease: 'easeInOut', delay: 0.6 }}
            >
              <div className="lp-float-icon blue"><BarChart3 size={16} /></div>
              <div>
                <strong>Algebra 84%</strong>
                <span>+9% this week</span>
              </div>
            </motion.div>

            <img src="/athena.png" alt="" className="lp-hero-mascot" />
          </motion.div>
        </section>

        {/* --------------------------------------------------------- STATS */}
        <section className="lp-stats-wrap">
          <Reveal className="lp-stats">
            <div className="lp-stat">
              <strong>{counts.total.toLocaleString()}+</strong>
              <span>Practice questions</span>
            </div>
            <div className="lp-stat">
              <strong>{counts.math.toLocaleString()}+</strong>
              <span>Math items</span>
            </div>
            <div className="lp-stat">
              <strong>{counts.reading.toLocaleString()}+</strong>
              <span>Reading &amp; Writing items</span>
            </div>
            <div className="lp-stat">
              <strong>$0</strong>
              <span>Forever, no card</span>
            </div>
          </Reveal>
        </section>

        {/* ------------------------------------------------------ FEATURES */}
        <section className="lp-section" id="features">
          <Reveal className="lp-section-head">
            <span className="lp-eyebrow">Why Athena</span>
            <h2>Everything you need. Nothing you don&apos;t.</h2>
            <p>
              Most prep tools give you questions and leave you alone with them. Athena tells you
              what the results mean and what to do next.
            </p>
          </Reveal>

          <motion.div
            className="lp-feature-grid"
            variants={stagger}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true, amount: 0.15 }}
          >
            {FEATURES.map(({ icon: Icon, title, body }) => (
              <motion.article key={title} className="lp-feature" variants={rise}>
                <div className="lp-feature-icon"><Icon size={20} strokeWidth={1.9} /></div>
                <h3>{title}</h3>
                <p>{body}</p>
              </motion.article>
            ))}
          </motion.div>
        </section>

        {/* ----------------------------------------------------- HOW IT WORKS */}
        <section className="lp-section lp-section-tint" id="how">
          <Reveal className="lp-section-head">
            <span className="lp-eyebrow">How it works</span>
            <h2>From signup to a smarter study plan in one session.</h2>
          </Reveal>

          <div className="lp-steps">
            {STEPS.map((step, i) => (
              <Reveal key={step.n} className="lp-step" delay={i * 0.08}>
                <span className="lp-step-n">{step.n}</span>
                <h3>{step.title}</h3>
                <p>{step.body}</p>
              </Reveal>
            ))}
            <img src="/athena-coach.png" alt="" className="lp-steps-mascot" />
          </div>
        </section>

        {/* -------------------------------------------------------- PRODUCT */}
        <section className="lp-section" id="product">
          <Reveal className="lp-section-head">
            <span className="lp-eyebrow">Inside the app</span>
            <h2>Practice, drill, and diagnose in one place.</h2>
          </Reveal>

          <Reveal className="lp-showcase">
            <div className="lp-showcase-copy">
              <div className="lp-showcase-icon"><Clock size={20} /></div>
              <h3>Timed practice that mirrors Bluebook</h3>
              <p>
                A live timer, mark-for-review flags, answer eliminator, and the same review page you
                get on test day. When the set ends, every question comes back with a full explanation.
              </p>
              <ul className="lp-check-list">
                <li>Desmos graphing calculator docked beside the question</li>
                <li>Reference sheet one tap away</li>
                <li>Pause, resume, and finish later without losing progress</li>
              </ul>
            </div>
            <div className="lp-showcase-art">
              <AssetSlot
                src="/landing/shot-practice.png"
                alt="Timed practice session"
                label="Practice session screenshot"
                spec="1400 × 900 · PNG · math question + calculator open"
              />
              <img src="/athena-math.png" alt="" className="lp-showcase-mascot" />
            </div>
          </Reveal>

          <Reveal className="lp-showcase lp-showcase-flip">
            <div className="lp-showcase-copy">
              <div className="lp-showcase-icon"><BookOpen size={20} /></div>
              <h3>A question bank you can actually aim</h3>
              <p>
                Filter by domain, skill, and difficulty, then drill with instant feedback. Athena
                remembers what you have already answered so every set stays fresh.
              </p>
              <ul className="lp-check-list">
                <li>Every domain of Math and Reading &amp; Writing</li>
                <li>Instant explanations after each answer</li>
                <li>Original source PDF for any question you want to double-check</li>
              </ul>
            </div>
            <div className="lp-showcase-art">
              <AssetSlot
                src="/landing/shot-qbank.png"
                alt="Question bank"
                label="Question bank screenshot"
                spec="1400 × 900 · PNG · skills list with filters"
              />
              <img src="/athena-rw-tab.png" alt="" className="lp-showcase-mascot" />
            </div>
          </Reveal>

          <Reveal className="lp-showcase">
            <div className="lp-showcase-copy">
              <div className="lp-showcase-icon"><LineChart size={20} /></div>
              <h3>Analytics that end the guesswork</h3>
              <p>
                Accuracy by domain and skill, streak history, and session reports — so the answer to
                &quot;what should I study tonight?&quot; is already on the screen.
              </p>
              <ul className="lp-check-list">
                <li>Weakest-skill detection after every session</li>
                <li>Progress over 3-day, weekly, and all-time ranges</li>
                <li>Review any past question with your original answer</li>
              </ul>
            </div>
            <div className="lp-showcase-art">
              <AssetSlot
                src="/landing/shot-analytics.png"
                alt="Analytics dashboard"
                label="Analytics screenshot"
                spec="1400 × 900 · PNG · accuracy breakdown + streak"
              />
              <img src="/athena-progress.png" alt="" className="lp-showcase-mascot" />
            </div>
          </Reveal>
        </section>

        {/* --------------------------------------------------- TESTIMONIALS */}
        <section className="lp-section lp-section-tint">
          <Reveal className="lp-section-head">
            <span className="lp-eyebrow">Students</span>
            <h2>Built for the people actually taking this test.</h2>
            <p className="lp-note">
              Placeholder quotes — swap these for real student feedback before launch.
            </p>
          </Reveal>

          <motion.div
            className="lp-quotes"
            variants={stagger}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true, amount: 0.2 }}
          >
            {TESTIMONIALS.map((t) => (
              <motion.figure key={t.name} className="lp-quote" variants={rise}>
                <Quote size={20} className="lp-quote-mark" />
                <blockquote>{t.quote}</blockquote>
                <figcaption>
                  <AssetSlot
                    compact
                    src={t.avatar}
                    alt={t.name}
                    label={`${t.name} avatar`}
                    className="lp-quote-avatar"
                    imgClassName="lp-quote-avatar"
                    ratio="1 / 1"
                    rounded={999}
                  />
                  <span>
                    <strong>{t.name}</strong>
                    <em>{t.detail}</em>
                  </span>
                </figcaption>
              </motion.figure>
            ))}
          </motion.div>
        </section>

        {/* ------------------------------------------------------------ FAQ */}
        <section className="lp-section" id="faq">
          <Reveal className="lp-section-head">
            <span className="lp-eyebrow">FAQ</span>
            <h2>Questions, answered.</h2>
          </Reveal>

          <div className="lp-faq">
            {FAQS.map((item, i) => {
              const open = openFaq === i
              return (
                <div key={item.q} className={`lp-faq-item ${open ? 'on' : ''}`}>
                  <button
                    type="button"
                    className="lp-faq-q"
                    aria-expanded={open}
                    onClick={() => setOpenFaq(open ? -1 : i)}
                  >
                    <span>{item.q}</span>
                    {open ? <Minus size={18} /> : <Plus size={18} />}
                  </button>
                  {open ? <p className="lp-faq-a">{item.a}</p> : null}
                </div>
              )
            })}
          </div>
        </section>

        {/* ------------------------------------------------------ FINAL CTA */}
        <section className="lp-cta-wrap">
          <Reveal className="lp-cta">
            <img src="/athena-throwing.png" alt="" className="lp-cta-mascot" />
            <div className="lp-cta-copy">
              <span className="lp-eyebrow gold">Your move</span>
              <h2>Every point you want is on the other side of practice.</h2>
              <p>Create a free account and run your first timed set in under a minute.</p>
              <div className="lp-cta-actions">
                <button type="button" className="lp-btn lp-btn-gold lp-btn-lg" onClick={() => openAuth('signup')}>
                  Create free account
                  <ArrowRight size={18} />
                </button>
                <button type="button" className="lp-btn lp-btn-quiet lp-btn-lg" onClick={() => openAuth('signin')}>
                  I already have one
                </button>
              </div>
            </div>
          </Reveal>
        </section>
      </main>

      <footer className="lp-footer">
        <div className="lp-footer-inner">
          <div className="lp-footer-brand">
            <Brand />
            <p>Digital SAT practice that tells you what to study next. Free, forever.</p>
          </div>

          <div className="lp-footer-cols">
            <div>
              <h4>Product</h4>
              <a href="#features">Features</a>
              <a href="#how">How it works</a>
              <a href="#product">Inside the app</a>
              <a href="#faq">FAQ</a>
            </div>
            <div>
              <h4>Account</h4>
              <button type="button" onClick={() => openAuth('signin')}>Log in</button>
              <button type="button" onClick={() => openAuth('signup')}>Sign up free</button>
            </div>
            <div>
              <h4>Legal</h4>
              <Link to="/privacy">Privacy</Link>
              <Link to="/terms">Terms</Link>
              <Link to="/reports">Report an issue</Link>
            </div>
          </div>
        </div>

        <div className="lp-footer-base">
          <p>© {new Date().getFullYear()} Athena SAT. All rights reserved.</p>
          <p className="lp-disclaimer">
            Not affiliated with, endorsed by, or sponsored by the College Board. SAT is a
            registered trademark of the College Board.
          </p>
        </div>
      </footer>

      <button
        type="button"
        className="lp-scroll-hint"
        aria-label="Scroll to features"
        onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
      >
        <ChevronDown size={18} />
      </button>

      <AuthModal
        open={authOpen}
        mode={authMode}
        onModeChange={setAuthMode}
        onClose={() => setAuthOpen(false)}
        onSignIn={onSignIn}
        onSignUp={onSignUp}
        onSignInWithGoogle={onSignInWithGoogle}
        error={error}
        configured={configured}
      />
    </div>
  )
}
