export interface AgentStep {
  id: string
  description: string
  status: "pending" | "in-progress" | "completed"
}

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  steps?: AgentStep[]
  citations?: string[] // URLs or titles of source PDFs
}
