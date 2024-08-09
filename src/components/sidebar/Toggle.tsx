import { useEffect } from 'react'

export default function Toggle() {
  useEffect(() => {
    const sidebar = document.querySelector('#sidebar')!
    const toggle = document.querySelector(
      '#sidebar-toggle',
    )! as HTMLInputElement
    const anchors = sidebar.getElementsByTagName('a')
    for (const anchor of anchors) {
      anchor.addEventListener('click', () => {
        toggle.checked = !toggle.checked
      })
    }
  }, [])
  return <></>
}
