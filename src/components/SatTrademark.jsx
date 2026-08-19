import React from 'react'

export const SAT_DISCLAIMER =
  'SAT® is a trademark registered by the College Board, which is not affiliated with, and does not endorse, this site.'

export function SatMark({ className }) {
  return <span className={className}>SAT®</span>
}

export function SatDisclaimer({ className }) {
  return <p className={className}>{SAT_DISCLAIMER}</p>
}
