import { useEffect, useRef } from 'react'

export default function Toggle() {
  const documentRef = useRef(document)

  useEffect(() => {
    const sidebar = documentRef.current.querySelector('#sidebar')!
    const toggle = documentRef.current.querySelector(
      '#sidebar-toggle',
    )! as HTMLInputElement
    const anchors = sidebar.getElementsByTagName('a')
    for (const anchor of anchors) {
      anchor.addEventListener('click', () => {
        if (window.innerWidth <= 768) toggle.checked = !toggle.checked
      })
    }
  }, [])

  return <></>
}
