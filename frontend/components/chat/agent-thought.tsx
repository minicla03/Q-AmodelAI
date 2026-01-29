"use client"

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { Loader2, CheckCircle2 } from "lucide-react"

export interface AgentStep {
  id: string
  description: string
  status: "pending" | "in-progress" | "completed"
}

interface AgentThoughtProps {
  steps: AgentStep[]
}

export function AgentThought({ steps }: AgentThoughtProps) {
  if (!steps || steps.length === 0) return null

  return (
    <Accordion type="single" collapsible className="w-full mb-4 border rounded-md px-4 bg-muted/30">
      <AccordionItem value="steps" className="border-0">
        <AccordionTrigger className="hover:no-underline py-3">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
             <Loader2 className="h-4 w-4 animate-spin" />
             <span>Agent Thinking Process</span>
          </div>
        </AccordionTrigger>
        <AccordionContent>
          <div className="flex flex-col gap-3 pl-2 pb-2">
            {steps.map((step) => (
              <div key={step.id} className="flex items-start gap-3 text-sm">
                {step.status === "completed" ? (
                  <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5" />
                ) : (
                  <Loader2 className="h-4 w-4 animate-spin text-blue-500 mt-0.5" />
                )}
                <span className={step.status === "completed" ? "text-foreground" : "text-muted-foreground"}>
                  {step.description}
                </span>
              </div>
            ))}
          </div>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  )
}
