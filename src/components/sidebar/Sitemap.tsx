import Collapsible from './Collapsible'
import sitemap from '../../../public/sitemap.json'

export default function Sitemap() {
  return Object.entries(sitemap).map(([key, child]) => (
    <Teste key={key} title={key} value={child as any}></Teste>
  ))
}

function Teste({
  title,
  value,
}: {
  title: string
  value: Record<string, unknown> | undefined
}) {
  const isTree = typeof value === 'object'
  return (
    <Collapsible label={title}>
      {isTree
        ? Object.entries(value).map(([key, child]) => (
            <Teste key={key} title={key} value={child as any} />
          ))
        : undefined}
    </Collapsible>
  )
}
