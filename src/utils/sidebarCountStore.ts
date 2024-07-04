let collapsibleCount = 0
let sidebarLinkCount = 0

export function getCountId() {
  collapsibleCount += 1
  return `collapsible-${collapsibleCount}` as const
}

export function getSidebarLinkCountId() {
  sidebarLinkCount += 1
  return `link-${sidebarLinkCount}` as const
}

export function resetCounters() {
  collapsibleCount = 0
  sidebarLinkCount = 0
}
