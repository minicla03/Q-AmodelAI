"use client"

import * as React from "react"
import { ChatInput } from "./chat-input"
import { ChatMessage } from "./chat-message"
import { Message, AgentStep } from "@/types/chat"
import { ScrollArea } from "@/components/ui/scroll-area"

export function ChatInterface() {
  const [messages, setMessages] = React.useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hello! I am Cognix, your AI study assistant. You can ask me questions about your documents, generate flashcards, or take a quiz. How can I help you today?",
    }
  ])
  const [isLoading, setIsLoading] = React.useState(false)
  const scrollRef = React.useRef<HTMLDivElement>(null)

  // Scroll to bottom when messages change
  React.useEffect(() => {
    if (scrollRef.current) {
        // Find the scroll viewport inside ScrollArea which is the one that scrolls
        const viewport = scrollRef.current.querySelector('[data-radix-scroll-area-viewport]');
        if (viewport) {
             viewport.scrollTop = viewport.scrollHeight;
        }
    }
  }, [messages])


  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
    }
    setMessages((prev) => [...prev, userMsg])
    setIsLoading(true)

    // Simulate Agent processing
    const agentMsgId = (Date.now() + 1).toString()
    const initialAgentMsg: Message = {
      id: agentMsgId,
      role: "assistant",
      content: "",
      steps: []
    }
    setMessages((prev) => [...prev, initialAgentMsg])

    // Mock streaming steps
    const steps: AgentStep[] = [
      { id: "s1", description: "Identifying intent...", status: "pending" },
      { id: "s2", description: "Searching vector database...", status: "pending" },
      { id: "s3", description: "Synthesizing answer...", status: "pending" }
    ]

    for (let i = 0; i < steps.length; i++) {
        await new Promise(r => setTimeout(r, 1000));

        setMessages(prev => prev.map(msg => {
            if (msg.id === agentMsgId) {
                const currentSteps = msg.steps || [];
                const updatedSteps = [...currentSteps];

                // Mark previous completed
                if (i > 0) updatedSteps[i-1].status = "completed";

                // Add new step
                updatedSteps.push({...steps[i], status: "in-progress"});

                return { ...msg, steps: updatedSteps };
            }
            return msg;
        }));
    }

    await new Promise(r => setTimeout(r, 1000));

    // Mark last step completed and add content
    setMessages(prev => prev.map(msg => {
        if (msg.id === agentMsgId) {
             const currentSteps = msg.steps || [];
             const updatedSteps = currentSteps.map(s => ({...s, status: "completed" as const}));

             return {
                 ...msg,
                 steps: updatedSteps,
                 content: "Based on the documents provided, the **Observer Pattern** is a behavioral design pattern where an object, known as the subject, maintains a list of its dependents, called observers, and notifies them automatically of any state changes.",
                 citations: ["DesignPatterns.pdf", "LectureNotes_Week3.pdf"]
             };
        }
        return msg;
    }));

    setIsLoading(false)
  }

  return (
    <div className="flex flex-col h-full bg-background">
      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="flex flex-col gap-4 pb-4">
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          {isLoading && messages[messages.length-1].role === "user" && (
               <div className="p-4 text-sm text-muted-foreground animate-pulse">Cognix is thinking...</div>
          )}
        </div>
      </ScrollArea>
      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  )
}
