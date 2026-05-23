const MOBILE_PATTERNS = [
  /(?<![a-zA-Z0-9])(?:\+?86[-\s]?)?1[3-9]\d{9}(?!\d)/g,
  /(?<![a-zA-Z0-9])1[3-9]\d[-\s]?\d{4}[-\s]?\d{4}(?!\d)/g,
  /(?<![a-zA-Z0-9])(?:\+?86[-\s]?)?1[3-9]\d\s\d{4}\s\d{4}(?!\d)/g,
]

function normalizePhone(raw) {
  return raw.replace(/[\s\-\(\)\+\.]/g, '').replace(/^86/, '')
}

function isValidMobile(digits) {
  return digits.length === 11 && /^1[3-9]\d{9}$/.test(digits)
}

export function extractPhones(text) {
  if (text === null || text === undefined) return []

  let str = String(text).trim()

  if (typeof text === 'number' && Number.isFinite(text)) {
    const numStr = String(Math.round(text))
    if (isValidMobile(numStr)) return [numStr]
    return []
  }

  str = str.replace(/[\u200b\u200c\u200d\ufeff]/g, '')

  const phones = new Set()

  for (const pattern of MOBILE_PATTERNS) {
    const regex = new RegExp(pattern.source, pattern.flags)
    for (const match of str.matchAll(regex)) {
      const normalized = normalizePhone(match[0])
      if (isValidMobile(normalized)) {
        phones.add(normalized)
      }
    }
  }

  return [...phones]
}

const HIGHLIGHT_PATTERNS = [
  { regex: /(?<![a-zA-Z0-9])(?:\+?86[-\s]?)?1[3-9]\d{9}(?!\d)/g, cls: 'phone-highlight' },
  { regex: /(?<![a-zA-Z0-9])1[3-9]\d[-\s]?\d{4}[-\s]?\d{4}(?!\d)/g, cls: 'phone-highlight' },
  { regex: /(?<![a-zA-Z0-9])(?:\+?86[-\s]?)?1[3-9]\d\s\d{4}\s\d{4}(?!\d)/g, cls: 'phone-highlight' },
]

export function highlightPhones(text) {
  if (text === null || text === undefined) return escapeHtml(String(text ?? ''))

  let str = String(text).replace(/[\u200b\u200c\u200d\ufeff]/g, '')

  const replacements = []

  for (const { regex, cls } of HIGHLIGHT_PATTERNS) {
    const re = new RegExp(regex.source, regex.flags)
    for (const match of str.matchAll(re)) {
      const normalized = normalizePhone(match[0])
      if (isValidMobile(normalized)) {
        replacements.push({ start: match.index, end: match.index + match[0].length, text: match[0], cls })
      }
    }
  }

  replacements.sort((a, b) => a.start - b.start)

  const filtered = []
  let lastEnd = -1
  for (const r of replacements) {
    if (r.start >= lastEnd) {
      filtered.push(r)
      lastEnd = r.end
    }
  }

  let result = ''
  let pos = 0
  for (const r of filtered) {
    result += escapeHtml(str.slice(pos, r.start))
    result += `<mark class="${r.cls}">${escapeHtml(r.text)}</mark>`
    pos = r.end
  }
  result += escapeHtml(str.slice(pos))

  return result
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

export function formatPhone(phone) {
  const digits = phone.replace(/\D/g, '')
  if (digits.length === 11 && digits.startsWith('1')) {
    return `${digits.slice(0, 3)} ${digits.slice(3, 7)} ${digits.slice(7)}`
  }
  return phone
}

export function guessColumnHasPhones(samples) {
  let count = 0
  for (const sample of samples) {
    if (extractPhones(sample).length > 0) count++
  }
  return count > 0
}
