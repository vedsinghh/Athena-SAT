import React, { useId } from 'react'

/** Soft illustrated cloud island — full silhouette on every side. */
const Cloud = React.forwardRef(function Cloud({
  className = '',
  variant = 'island',
  children,
  tone = 'ivory',
}, ref) {
  const uid = useId().replace(/:/g, '')
  const gradId = `cg-${uid}`
  const top = tone === 'blue' ? '#f5f9ff' : '#fffefb'
  const bot = tone === 'blue' ? '#e4eefc' : '#f1ebe1'

  return (
    <div ref={ref} className={`ascent-cloud ascent-cloud--${variant} ascent-cloud--${tone} ${className}`}>
      <svg className="ascent-cloud-shape" viewBox="0 0 800 420" aria-hidden="true" preserveAspectRatio="none">
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={top} />
            <stop offset="100%" stopColor={bot} />
          </linearGradient>
        </defs>
        {/* Wide, even cloud with a deep content well */}
        <path
          fill={`url(#${gradId})`}
          d="M90 250
             C40 250 16 210 16 168
             C16 122 52 90 96 86
             C92 42 132 10 186 10
             C220 10 250 26 268 50
             C292 16 340 0 396 0
             C460 0 510 28 532 76
             C556 56 592 46 630 46
             C692 46 738 90 738 144
             C738 162 732 178 722 192
             C752 204 772 232 772 266
             C772 318 728 356 676 356
             C662 356 650 354 638 350
             C620 388 572 416 512 416
             C468 416 430 398 408 370
             C386 396 344 414 296 414
             C236 414 188 384 170 336
             C150 348 124 354 100 354
             C96 320 90 284 90 250 Z"
        />
      </svg>
      {children ? <div className="ascent-cloud-body">{children}</div> : null}
    </div>
  )
})

export default Cloud

export function DriftCloud({ className = '', w = 280, opacity = 0.9 }) {
  return (
    <svg
      className={`ascent-drift ${className}`}
      width={w}
      height={w * 0.48}
      viewBox="0 0 340 160"
      aria-hidden="true"
      style={{ opacity }}
    >
      <path
        fill="rgba(255,250,244,0.88)"
        d="M48 108c-22-2-38-18-38-38 0-24 20-42 44-42 6-22 26-38 50-38 18 0 33 8 42 20 9-12 24-20 42-20 26 0 48 18 52 44 7-5 16-8 26-8 26 0 46 20 46 44 0 24-20 44-46 44H56c-26 0-48-20-48-44 0-5 1-10 3-14 6 2 12 4 18 4 7 0 14-1 19-4z"
      />
    </svg>
  )
}
