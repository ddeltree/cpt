import { getCountId } from '@/utils/collapsibleCountStore'
import type { ReactNode } from 'react'

export default function Collapsible({
  children,
  label,
}: {
  label: ReactNode
  children: ReactNode
}) {
  const count = getCountId()
  return (
    <>
      <div className="collapsible">
        <input
          type="checkbox"
          id={count}
          className="collapsible-checkbox hidden"
        />
        <label htmlFor={count}>
          <div>
            <span>*</span>
            {label}
          </div>
        </label>
        <div className="collapsible-content px-2">{children}</div>
      </div>

      <style>{`
      .collapsible-content {
        display: none;
      }
      .collapsible-checkbox:checked + label + .collapsible-content {
        display: block;
      }
    `}</style>
    </>
  )
}
