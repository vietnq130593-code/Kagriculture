'use client'

/**
 * ARENA OBSERVER UI — collapsible runner stderr log.
 */
import { useState } from 'react'
import { Terminal, ChevronDown } from 'lucide-react'
import { Card } from '@/components/ui/card'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

export function RunnerLog({ logs }: { logs: string[] }) {
  const [open, setOpen] = useState(false)
  const count = logs.length

  return (
    <Card className="border-stone-200 shadow-sm">
      <Collapsible open={open} onOpenChange={setOpen} className="p-3 sm:p-4">
        <CollapsibleTrigger className="flex h-11 w-full items-center gap-2 rounded-md px-1 text-left text-sm font-semibold text-stone-700 hover:bg-stone-50">
          <Terminal className="size-4 text-stone-500" aria-hidden="true" />
          Nhật ký runner (stderr)
          <Badge
            variant="secondary"
            className="bg-stone-100 text-stone-500 tabular-nums hover:bg-stone-100"
          >
            {count} dòng
          </Badge>
          <ChevronDown
            className={cn('ml-auto size-4 text-stone-400 transition-transform', open && 'rotate-180')}
            aria-hidden="true"
          />
        </CollapsibleTrigger>
        <CollapsibleContent>
          <div className="arena-scroll mt-2 max-h-40 overflow-y-auto rounded-md border border-stone-800 bg-stone-950 p-2">
            <pre className="whitespace-pre-wrap break-all font-mono text-[11px] leading-relaxed text-stone-300">
              {count === 0 ? '— chưa có log —' : logs.map((l, i) => `${i + 1}\t${l}`).join('\n')}
            </pre>
          </div>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  )
}
