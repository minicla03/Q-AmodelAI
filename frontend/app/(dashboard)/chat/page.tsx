import { ChatInterface } from "@/components/chat/chat-interface"

export default function ChatPage() {
  return (
    <div className="h-full flex flex-col">
      <div className="mb-4">
        <h1 className="text-2xl font-bold tracking-tight">AI Assistant</h1>
        <p className="text-muted-foreground">Ask questions about your documents and get instant answers.</p>
      </div>
      <div className="flex-1 border rounded-lg overflow-hidden shadow-sm bg-card">
        <ChatInterface />
      </div>
    </div>
  )
}
