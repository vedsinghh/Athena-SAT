import React, { useState } from 'react'
import { ImagePlus } from 'lucide-react'

/**
 * Renders `src` when the asset exists, otherwise a labeled placeholder telling
 * us exactly which file to drop in. Lets the page ship before art is finished.
 */
export default function AssetSlot({
  src,
  alt = '',
  label,
  spec,
  className = '',
  imgClassName = '',
  ratio = '16 / 10',
  rounded = 24,
  compact = false,
}) {
  const [missing, setMissing] = useState(!src)

  if (!missing) {
    return (
      <img
        src={src}
        alt={alt}
        className={`lp-asset-img ${imgClassName} ${className}`}
        loading="lazy"
        onError={() => setMissing(true)}
      />
    )
  }

  return (
    <div
      className={`lp-asset-slot ${compact ? 'is-compact' : ''} ${className}`}
      style={{ aspectRatio: ratio, borderRadius: rounded }}
      role="img"
      aria-label={label || alt || 'Asset placeholder'}
      title={compact && src ? `Add ${src}` : undefined}
    >
      <ImagePlus size={compact ? 16 : 22} strokeWidth={1.8} />
      {compact ? null : (
        <>
          <span className="lp-asset-slot-label">{label || alt}</span>
          {src ? <code className="lp-asset-slot-path">{src}</code> : null}
          {spec ? <span className="lp-asset-slot-spec">{spec}</span> : null}
        </>
      )}
    </div>
  )
}
