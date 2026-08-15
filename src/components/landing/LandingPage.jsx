import React, { useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { ArrowDown, Menu, X } from 'lucide-react'
import mathQuestions from '../../data/mathQuestions.json'
import readingQuestions from '../../data/readingQuestions.json'
import AuthModal from './AuthModal'
import Cloud, { DriftCloud } from './Cloud'
import './landing.css'

gsap.registerPlugin(ScrollTrigger)

function Brand() {
  return (
    <span className="ascent-brand">
      <img
        className="ascent-brand-mark"
        src="/landing/athena-owl.png"
        alt=""
        aria-hidden="true"
        draggable={false}
      />
      <span className="ascent-brand-text">
        <em>ATHENA</em>
        <span>SAT</span>
      </span>
    </span>
  )
}

function roundDown(value, step) {
  return Math.floor(value / step) * step
}

export default function LandingPage({
  onSignIn,
  onSignUp,
  onSignInWithGoogle,
  onForgotPassword,
  error,
  configured,
}) {
  const rootRef = useRef(null)
  const athenaRef = useRef(null)
  const skyRef = useRef(null)
  const farCloudsRef = useRef(null)
  const midCloudsRef = useRef(null)
  const nearCloudsRef = useRef(null)
  const olympusSectionRef = useRef(null)
  const olympusCopyRef = useRef(null)
  const athenaStageRef = useRef(null)
  const heroCloudRef = useRef(null)

  const [authOpen, setAuthOpen] = useState(false)
  const [authMode, setAuthMode] = useState('signup')
  const [navOpen, setNavOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const [reducedMotion, setReducedMotion] = useState(false)

  const counts = useMemo(() => {
    const total = (mathQuestions?.length || 0) + (readingQuestions?.length || 0)
    return {
      total: roundDown(total, 50),
      skills: 20,
    }
  }, [])

  const openAuth = (mode) => {
    setAuthMode(mode)
    setAuthOpen(true)
    setNavOpen(false)
  }

  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    const apply = () => setReducedMotion(mq.matches)
    apply()
    mq.addEventListener?.('change', apply)
    return () => mq.removeEventListener?.('change', apply)
  }, [])

  useEffect(() => {
    if (!navOpen) return undefined
    const prev = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => { document.body.style.overflow = prev }
  }, [navOpen])

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  // Subtle idle float on shell only
  useEffect(() => {
    if (reducedMotion || !athenaRef.current) return undefined
    const shell = athenaRef.current.querySelector('.ascent-athena-shell')
    if (!shell) return undefined
    const tween = gsap.to(shell, {
      y: 10,
      duration: 3.1,
      yoyo: true,
      repeat: -1,
      ease: 'sine.inOut',
    })
    return () => { tween.kill() }
  }, [reducedMotion])

  useEffect(() => {
    const root = rootRef.current
    if (!root || reducedMotion) return undefined

    const isMobile = () => window.matchMedia('(max-width: 900px)').matches

    const applyScrollMotion = (progress) => {
      const mobile = isMobile()
      const athena = athenaRef.current

      // Start behind the hero cloud, rise through the journey, then peek over the Olympus CTA
      if (athena) {
        const vh = window.innerHeight || 1
        const scrollY = window.scrollY || document.documentElement.scrollTop || 0
        let olympusT = 0
        let riseT = 0
        if (olympusSectionRef.current) {
          const rect = olympusSectionRef.current.getBoundingClientRect()
          olympusT = Math.min(1, Math.max(0, (vh - rect.top) / (vh * 0.95)))
          // Finish the rise just as Olympus docking starts (olympusT ≈ 0.12)
          const dockStart = Math.max(1, rect.top + scrollY - vh * 0.886)
          riseT = Math.min(1, Math.max(0, scrollY / dockStart))
        } else {
          riseT = Math.min(1, progress / 0.82)
        }

        const stage = athenaStageRef.current
        const card = olympusCopyRef.current
        const heroCloud = heroCloudRef.current
        const startScale = mobile ? 1 : 1.06
        const riseScale = mobile ? 0.4 : 0.36
        const dockScale = mobile ? 0.48 : 0.5
        const skyTop = mobile ? 52 : 68
        const heroPeek = mobile ? 0.52 : 0.48
        const dockPeek = mobile ? 0.72 : 0.68

        const t = olympusT < 0.12 ? riseT : Math.min(1, (olympusT - 0.12) / 0.88)
        const scale = olympusT < 0.12
          ? gsap.utils.interpolate(startScale, riseScale, riseT)
          : gsap.utils.interpolate(riseScale, dockScale, t)

        gsap.set(athena, {
          y: 0,
          scale,
          transformOrigin: '50% 0%',
          yPercent: 0,
          xPercent: 0,
          opacity: 1,
          force3D: true,
        })
        const h = athena.getBoundingClientRect().height
        const layoutTop = athena.getBoundingClientRect().top

        let wantTop
        if (olympusT < 0.12) {
          // Use the cloud's rest position so Athena stays in the viewport while the page scrolls
          const cloudTopRest = heroCloud
            ? heroCloud.getBoundingClientRect().top + scrollY
            : skyTop + 180 + h * heroPeek
          const behindTop = cloudTopRest - h * heroPeek
          wantTop = gsap.utils.interpolate(behindTop, skyTop, riseT)
        } else {
          const dockTop = card
            ? card.getBoundingClientRect().top - h * dockPeek
            : skyTop
          wantTop = gsap.utils.interpolate(skyTop, dockTop, t)
        }
        gsap.set(athena, { y: wantTop - layoutTop })
        // 6 = journey, 9 = hero cloud, 10 = ending CTA. Stay between so she is
        // behind only the hero cloud, then in front until the final tile.
        if (stage) stage.style.zIndex = '7'
      }

      if (skyRef.current) {
        // Keep a slight vertical drift for depth; sunset is driven by --ascent-progress
        gsap.set(skyRef.current, { backgroundPosition: `50% ${progress * 40}%` })
      }
      if (root) {
        // Ease sunset in earlier so golden hour arrives mid-journey
        const sunsetT = Math.min(1, Math.max(0, (progress - 0.05) / 0.7))
        const eased = 1 - (1 - sunsetT) ** 1.35
        root.style.setProperty('--ascent-progress', eased.toFixed(4))
      }
      if (farCloudsRef.current && !mobile) {
        gsap.set(farCloudsRef.current, { yPercent: -38 * progress, force3D: true })
      }
      if (midCloudsRef.current) {
        gsap.set(midCloudsRef.current, {
          yPercent: -(mobile ? 48 : 66) * progress,
          force3D: true,
        })
      }
      if (nearCloudsRef.current) {
        gsap.set(nearCloudsRef.current, {
          yPercent: -(mobile ? 72 : 100) * progress,
          force3D: true,
        })
      }
      // Soften parallax clouds as Olympus fills the viewport
      if (olympusSectionRef.current) {
        const rect = olympusSectionRef.current.getBoundingClientRect()
        const vh = window.innerHeight || 1
        const visible = Math.min(1, Math.max(0, (vh - rect.top) / (vh * 0.85)))
        if (nearCloudsRef.current) {
          gsap.set(nearCloudsRef.current, { opacity: Math.max(0, 1 - visible * 1.05) })
        }
        if (midCloudsRef.current) {
          gsap.set(midCloudsRef.current, { opacity: Math.max(0, 1 - visible * 1.02) })
        }
        if (farCloudsRef.current) {
          gsap.set(farCloudsRef.current, { opacity: Math.max(0, 1 - visible * 0.98) })
        }
      }
    }

    let ticking = false
    let lastProgress = -1
    let rafId = 0
    let intervalId = 0
    const readProgress = () => {
      const max = Math.max(1, root.scrollHeight - window.innerHeight)
      const y = window.scrollY || document.documentElement.scrollTop || 0
      return Math.min(1, Math.max(0, y / max))
    }
    const sync = (force = false) => {
      const progress = readProgress()
      if (!force && Math.abs(progress - lastProgress) < 0.0005) return
      lastProgress = progress
      try {
        applyScrollMotion(progress)
      } catch (_) {
        /* keep sync alive */
      }
    }
    const onScroll = () => {
      sync(true)
    }
    const loop = () => {
      sync()
      rafId = window.requestAnimationFrame(loop)
    }

    sync(true)
    window.addEventListener('scroll', onScroll, { passive: true, capture: true })
    document.addEventListener('scroll', onScroll, { passive: true, capture: true })
    window.addEventListener('resize', onScroll)
    rafId = window.requestAnimationFrame(loop)
    // Interval backup — some embedded browsers throttle rAF hard
    intervalId = window.setInterval(() => sync(), 32)

    const ctx = gsap.context(() => {
      gsap.utils.toArray('.ascent-reveal').forEach((node) => {
        gsap.fromTo(node, {
          opacity: 0,
          y: 48,
        }, {
          opacity: 1,
          y: 0,
          duration: 0.9,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: node,
            start: 'top 82%',
            toggleActions: 'play none none reverse',
          },
        })
      })
    }, root)

    const refreshId = window.setTimeout(() => ScrollTrigger.refresh(), 150)

    return () => {
      window.clearTimeout(refreshId)
      window.clearInterval(intervalId)
      window.cancelAnimationFrame(rafId)
      window.removeEventListener('scroll', onScroll, { capture: true })
      document.removeEventListener('scroll', onScroll, { capture: true })
      window.removeEventListener('resize', onScroll)
      ctx.revert()
    }
  }, [reducedMotion])

  useEffect(() => {
    const id = window.setTimeout(() => ScrollTrigger.refresh(), 120)
    return () => window.clearTimeout(id)
  }, [])

  return (
    <div className={`ascent ${reducedMotion ? 'is-reduced' : ''}`} ref={rootRef}>
      <div className="ascent-sky" ref={skyRef} aria-hidden="true" />

      {/* Parallax cloud fields */}
      <div className="ascent-layer ascent-layer-far" ref={farCloudsRef} aria-hidden="true">
        <DriftCloud className="dc dc-a" w={460} opacity={0.5} />
        <DriftCloud className="dc dc-b" w={380} opacity={0.42} />
        <DriftCloud className="dc dc-c" w={520} opacity={0.38} />
      </div>
      <div className="ascent-layer ascent-layer-mid" ref={midCloudsRef} aria-hidden="true">
        <DriftCloud className="dc dc-d" w={400} opacity={0.72} />
        <DriftCloud className="dc dc-e" w={480} opacity={0.68} />
        <DriftCloud className="dc dc-f" w={340} opacity={0.62} />
      </div>
      <div className="ascent-layer ascent-layer-near" ref={nearCloudsRef} aria-hidden="true">
        <DriftCloud className="dc dc-g" w={540} opacity={0.9} />
        <DriftCloud className="dc dc-h" w={420} opacity={0.85} />
      </div>

      {/* One Athena asset, centered — rises with scroll, never swaps */}
      <div className="ascent-athena-stage" ref={athenaStageRef} aria-hidden="true">
        <div className="ascent-athena" ref={athenaRef}>
          <div className="ascent-athena-shell">
            <img
              src="/landing/athena-hero-v6.png"
              alt=""
              className="ascent-athena-pose"
              draggable={false}
            />
          </div>
        </div>
      </div>

      <header className={`ascent-nav ${scrolled ? 'is-stuck' : ''}`}>
        <div className="ascent-nav-inner">
          <a href="#top" className="ascent-nav-brand" aria-label="Athena SAT home">
            <Brand />
          </a>
          <nav className="ascent-nav-links" aria-label="Primary">
            <a href="#story">Journey</a>
            <a href="#features">Practice</a>
            <a href="#path">The Path</a>
            <a href="#olympus">Begin</a>
          </nav>
          <div className="ascent-nav-actions">
            <button type="button" className="ascent-btn ascent-btn-ghost" onClick={() => openAuth('signin')}>
              Log in
            </button>
            <button type="button" className="ascent-btn ascent-btn-gold" onClick={() => openAuth('signup')}>
              Sign up free
            </button>
          </div>
          <button
            type="button"
            className="ascent-nav-toggle"
            aria-label={navOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={navOpen}
            onClick={() => setNavOpen((v) => !v)}
          >
            {navOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
        {navOpen ? (
          <div className="ascent-nav-sheet">
            <a href="#story" onClick={() => setNavOpen(false)}>Journey</a>
            <a href="#features" onClick={() => setNavOpen(false)}>Practice</a>
            <a href="#path" onClick={() => setNavOpen(false)}>The Path</a>
            <a href="#olympus" onClick={() => setNavOpen(false)}>Begin</a>
            <button type="button" className="ascent-btn ascent-btn-ghost ascent-btn-block" onClick={() => openAuth('signin')}>
              Log in
            </button>
            <button type="button" className="ascent-btn ascent-btn-gold ascent-btn-block" onClick={() => openAuth('signup')}>
              Sign up free
            </button>
          </div>
        ) : null}
      </header>

      <main id="top">
        {/* HERO — cloud centered; Athena starts tucked behind it */}
        <section className="ascent-hero">
          <Cloud ref={heroCloudRef} className="ascent-hero-cloud" variant="island" tone="ivory">
            <p className="ascent-kicker">Digital SAT · guided by wisdom</p>
            <h1>Rise to your highest score.</h1>
            <p className="ascent-hero-sub">
              Smart practice. Real progress. Unstoppable you.
            </p>
            <div className="ascent-hero-cta">
              <button type="button" className="ascent-btn ascent-btn-primary ascent-btn-lg" onClick={() => openAuth('signup')}>
                Begin your journey
              </button>
            </div>
          </Cloud>
          <a href="#story" className="ascent-scroll-cue">
            Ascend
            <ArrowDown size={16} />
          </a>
        </section>

        <div className="ascent-journey">
          {/* STORY cloud */}
          <section className="ascent-chapter" id="story">
            <Cloud className="ascent-reveal ascent-story-cloud" variant="island" tone="ivory">
              <div className="ascent-cloud-copy">
                <p className="ascent-chapter-label">What is Athena SAT</p>
                <h2>Your SAT journey, guided by Athena.</h2>
                <p>
                  Practice smarter, understand every miss, and climb toward your target score —
                  one deliberate question at a time.
                </p>
              </div>
              <img src="/landing/owl-perch.png" alt="" className="ascent-owl" />
            </Cloud>
          </section>

          <section className="ascent-wisdom ascent-reveal" aria-label="Wisdom">
            <p>Wisdom is knowing what to practice next.</p>
          </section>

          <section className="ascent-chapter ascent-features" id="features">
            <Cloud className="ascent-reveal feat feat-1" variant="island">
              <h3>Targeted practice</h3>
              <p>Choose the domain, skill, and difficulty you actually need.</p>
            </Cloud>
            <Cloud className="ascent-reveal feat feat-2" variant="island" tone="blue">
              <h3>Real digital SAT–style questions</h3>
              <p>{counts.total.toLocaleString()}+ items that mirror Bluebook mechanics.</p>
            </Cloud>
            <Cloud className="ascent-reveal feat feat-3" variant="island">
              <h3>Progress that names your weak spot</h3>
              <p>Accuracy by domain and skill — so tonight&apos;s set is the right one.</p>
            </Cloud>
            <Cloud className="ascent-reveal feat feat-4" variant="island" tone="blue">
              <h3>Timed sets like test day</h3>
              <p>Timer, mark-for-review, Desmos, and a Bluebook-style review page.</p>
            </Cloud>
          </section>

          <section className="ascent-chapter ascent-stats-band">
            <div className="ascent-reveal ascent-stat-row">
              <div className="ascent-stat-card">
                <div className="ascent-stat-card-top">
                  <strong>{counts.total.toLocaleString()}+</strong>
                </div>
                <div className="ascent-stat-card-bottom">
                  <span>Practice questions</span>
                </div>
              </div>
              <div className="ascent-stat-card">
                <div className="ascent-stat-card-top">
                  <strong>{counts.skills}+</strong>
                </div>
                <div className="ascent-stat-card-bottom">
                  <span>Math &amp; Reading skills</span>
                </div>
              </div>
              <div className="ascent-stat-card">
                <div className="ascent-stat-card-top">
                  <strong>Full</strong>
                </div>
                <div className="ascent-stat-card-bottom">
                  <span>Explanations</span>
                </div>
              </div>
              <div className="ascent-stat-card">
                <div className="ascent-stat-card-top">
                  <strong>$0</strong>
                </div>
                <div className="ascent-stat-card-bottom">
                  <span>Forever free</span>
                </div>
              </div>
            </div>
          </section>

          <section className="ascent-wisdom ascent-reveal">
            <p>Every question takes you higher.</p>
          </section>

          <section className="ascent-chapter ascent-path" id="path">
            <ol className="ascent-path-list">
              {[
                { n: '01', t: 'Choose what to practice', d: 'Domain, skill, difficulty — aim the set.' },
                { n: '02', t: 'Answer & learn', d: 'Instant feedback with explanations that teach.' },
                { n: '03', t: 'Understand mistakes', d: 'History and analytics keep the miss honest.' },
                { n: '04', t: 'Improve your score', d: 'Streaks and weak-spot tracking close the gap.' },
              ].map((step, i) => (
                <li key={step.n} className={`ascent-reveal ascent-path-step step-${i + 1}`}>
                  <Cloud variant="island" tone={i % 2 ? 'blue' : 'ivory'}>
                    <span className="ascent-path-n">{step.n}</span>
                    <h3>{step.t}</h3>
                    <p>{step.d}</p>
                  </Cloud>
                </li>
              ))}
            </ol>
          </section>

          <section className="ascent-wisdom ascent-reveal ascent-wisdom-late">
            <p>Great scores aren&apos;t luck. They&apos;re built.</p>
          </section>
        </div>

        {/* Santorini — original cliffs at the bottom; CTA over the base */}
        <section className="ascent-olympus" id="olympus" ref={olympusSectionRef}>
          <img
            src="/landing/santorini-cliffs.png?v=1"
            alt=""
            className="ascent-olympus-temple ascent-santorini-end"
            aria-hidden="true"
            draggable={false}
          />
          <div className="ascent-olympus-spacer" aria-hidden="true" />
          <div className="ascent-olympus-copy" ref={olympusCopyRef}>
            <p className="ascent-chapter-label ascent-satorini">
              <span className="ascent-sat-mark">SAT</span>HENS
            </p>
            <h2>Your journey starts here.</h2>
            <p>
              Practice smarter. Learn from every miss. Reach your highest score.
            </p>
            <div className="ascent-olympus-actions">
              <button type="button" className="ascent-btn ascent-btn-primary ascent-btn-lg" onClick={() => openAuth('signup')}>
                Begin your journey
              </button>
              <button type="button" className="ascent-btn ascent-btn-quiet ascent-btn-lg" onClick={() => openAuth('signin')}>
                I already have an account
              </button>
            </div>
          </div>
        </section>
      </main>

      <footer className="ascent-footer">
        <div className="ascent-footer-inner">
          <Brand />
          <p className="ascent-disclaimer">
            © {new Date().getFullYear()} Athena SAT. Not affiliated with the College Board.
          </p>
          <div className="ascent-footer-links">
            <button type="button" onClick={() => openAuth('signin')}>Log in</button>
            <button type="button" onClick={() => openAuth('signup')}>Sign up</button>
            <Link to="/privacy">Privacy</Link>
            <Link to="/terms">Terms</Link>
          </div>
        </div>
      </footer>

      <AuthModal
        open={authOpen}
        mode={authMode}
        onModeChange={setAuthMode}
        onClose={() => setAuthOpen(false)}
        onSignIn={onSignIn}
        onSignUp={onSignUp}
        onSignInWithGoogle={onSignInWithGoogle}
        onForgotPassword={onForgotPassword}
        error={error}
        configured={configured}
      />
    </div>
  )
}
