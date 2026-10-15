// Run: node frontend/scripts/check-unknown-reason.mjs (no test framework; plan card v0.60.8).
// An UNKNOWN condition must always show a reason; a missing one reads "alasan tidak tersedia".
import assert from 'node:assert/strict'
import { describeUnknownReason, needsWindowHint, REASON_MISSING } from '../src/utils/unknownReason.ts'

assert.equal(describeUnknownReason(null, true).label, REASON_MISSING)
assert.equal(describeUnknownReason('', true).label, REASON_MISSING)
assert.equal(describeUnknownReason('coverage_incomplete', true).label, 'cakupan tidak lengkap')
assert.equal(describeUnknownReason('coverage_incomplete', true).raw, 'coverage_incomplete')
assert.equal(describeUnknownReason('conflicting_evidence', true).label, 'bukti bertentangan')
assert.equal(describeUnknownReason('not_acquired', true).note, null)
assert.equal(describeUnknownReason('not_acquired', false).note, 'sumber belum tersedia di platform')
// An unknown code is passed through, never dropped.
assert.equal(describeUnknownReason('kode_baru', true).label, 'kode_baru')

assert.equal(needsWindowHint('coverage_incomplete', { window: null, time_binding: 'case_window' }), true)
assert.equal(needsWindowHint('coverage_incomplete', { window: null, operator: 'overlaps_window' }), true)
assert.equal(needsWindowHint('coverage_incomplete', { window: { start: 'a', end: 'b' }, time_binding: 'case_window' }), false)
assert.equal(needsWindowHint('coverage_incomplete', { window: null, time_binding: 'current' }), false)
assert.equal(needsWindowHint('not_acquired', { window: null, time_binding: 'case_window' }), false)

console.log('UNKNOWN-REASON OK')
