let collapsibleCount = 0

export function getCountId() {
  collapsibleCount += 1
  return `collapsible-${collapsibleCount}` as const
}
