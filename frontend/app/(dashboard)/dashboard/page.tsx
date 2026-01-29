import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { MessageSquare, BookOpen, BrainCircuit, Upload } from "lucide-react"

export default function Home() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
         <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground">Welcome back to Cognix. Here&apos;s an overview of your activity.</p>
         </div>
         <Button>
            <Upload className="mr-2 h-4 w-4" /> Upload Document
         </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Link href="/chat">
            <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Start Chat</CardTitle>
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">New Session</div>
                <p className="text-xs text-muted-foreground">Ask questions to your personal AI agent</p>
              </CardContent>
            </Card>
        </Link>
        <Link href="/flashcards">
            <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Study Flashcards</CardTitle>
                <BookOpen className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">12 Decks</div>
                <p className="text-xs text-muted-foreground">Review your concepts</p>
              </CardContent>
            </Card>
        </Link>
        <Link href="/quiz">
            <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Take a Quiz</CardTitle>
                <BrainCircuit className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">Active</div>
                <p className="text-xs text-muted-foreground">Test your knowledge</p>
              </CardContent>
            </Card>
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
            <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                     <div className="flex items-center gap-4">
                        <div className="h-2 w-2 rounded-full bg-green-500" />
                        <div className="flex-1 space-y-1">
                            <p className="text-sm font-medium leading-none">Completed Quiz: Engineering Basics</p>
                            <p className="text-xs text-muted-foreground">2 hours ago</p>
                        </div>
                        <div className="font-medium text-sm">85%</div>
                     </div>
                     <div className="flex items-center gap-4">
                        <div className="h-2 w-2 rounded-full bg-blue-500" />
                        <div className="flex-1 space-y-1">
                            <p className="text-sm font-medium leading-none">Uploaded PDF: DesignPatterns.pdf</p>
                            <p className="text-xs text-muted-foreground">5 hours ago</p>
                        </div>
                     </div>
                </div>
            </CardContent>
        </Card>
      </div>
    </div>
  )
}
