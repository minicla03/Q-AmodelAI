"use client"

import ReactMarkdown from "react-markdown"
import { cn } from "@/lib/utils"
import { Message } from "@/types/chat"
import { AgentThought } from "./agent-thought"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { User, Bot } from "lucide-react"

interface ChatMessageProps {
  message: Message
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user"

  return (
    <div className={cn("flex gap-4 p-4", isUser ? "flex-row-reverse bg-muted/20" : "")}>
      <Avatar className="h-8 w-8">
        {isUser ? (
          <>
            <AvatarImage src="https://github.com/shadcn.png" />
            <AvatarFallback><User className="h-4 w-4" /></AvatarFallback>
          </>
        ) : (
          <>
            <AvatarImage src="/bot-avatar.png" />
            <AvatarFallback className="bg-primary text-primary-foreground">
              <Bot className="h-4 w-4" />
            </AvatarFallback>
          </>
        )}
      </Avatar>

      <div className={cn("flex flex-col gap-2 max-w-[80%]", isUser ? "items-end" : "items-start")}>
        <div className="flex items-center gap-2">
           <span className="text-sm font-semibold">{isUser ? "You" : "Cognix Agent"}</span>
        </div>

        {message.steps && message.steps.length > 0 && (
          <AgentThought steps={message.steps} />
        )}

        <div className={cn("rounded-lg p-3 text-sm", isUser ? "bg-primary text-primary-foreground" : "bg-card border")}>
          <div className="prose dark:prose-invert max-w-none break-words">
            <ReactMarkdown
              components={{
                // Customize markdown rendering if needed
                p: ({children}) => <p className="mb-2 last:mb-0">{children}</p>
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        </div>

        {message.citations && message.citations.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-1">
            {message.citations.map((citation, index) => (
              <Badge key={index} variant="outline" className="cursor-pointer hover:bg-muted">
                📄 {citation}
              </Badge>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
