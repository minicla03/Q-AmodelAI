import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { BrainCircuit, BookOpen, MessageSquare, ArrowRight, Zap, GraduationCap, Users } from "lucide-react"

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Navigation */}
      <header className="px-6 lg:px-10 h-16 flex items-center justify-between border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <Link href="/" className="flex items-center gap-2 font-bold text-xl">
          <BrainCircuit className="h-6 w-6 text-primary" />
          <span>Cognix</span>
        </Link>
        <nav className="hidden md:flex gap-6 text-sm font-medium">
          <Link href="#features" className="hover:text-primary transition-colors">Features</Link>
          <Link href="#how-it-works" className="hover:text-primary transition-colors">How it Works</Link>
          <Link href="#pricing" className="hover:text-primary transition-colors">Pricing</Link>
        </nav>
        <div className="flex items-center gap-4">
          <Link href="/login">
            <Button variant="ghost" size="sm">Log in</Button>
          </Link>
          <Link href="/register">
            <Button size="sm">Get Started</Button>
          </Link>
        </div>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="py-24 px-6 lg:px-10 flex flex-col items-center text-center max-w-5xl mx-auto space-y-8">
          <div className="space-y-4">
            <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight lg:text-7xl">
              Master any subject with <span className="text-primary">AI-powered</span> learning
            </h1>
            <p className="text-xl text-muted-foreground max-w-[42rem] mx-auto">
              Cognix transforms your documents into an interactive study partner. Chat, quiz, and memorize with the power of Agentic RAG.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row gap-4">
             <Link href="/register">
               <Button size="lg" className="h-12 px-8 text-lg gap-2">
                 Start Learning Now <ArrowRight className="h-4 w-4" />
               </Button>
             </Link>
             <Link href="#demo">
               <Button size="lg" variant="outline" className="h-12 px-8 text-lg">
                 View Demo
               </Button>
             </Link>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-24 bg-muted/50 px-6 lg:px-10">
          <div className="max-w-6xl mx-auto space-y-12">
            <div className="text-center space-y-4">
              <h2 className="text-3xl font-bold tracking-tight">Everything you need to excel</h2>
              <p className="text-muted-foreground text-lg">Our tools are designed to help you understand, retain, and apply knowledge.</p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              <Card className="bg-background border-none shadow-md">
                <CardHeader>
                  <MessageSquare className="h-10 w-10 text-primary mb-2" />
                  <CardTitle>Smart Chat</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Ask questions to your documents. Our Agentic Planner breaks down complex queries and provides sourced answers.
                  </p>
                </CardContent>
              </Card>
              <Card className="bg-background border-none shadow-md">
                <CardHeader>
                  <BookOpen className="h-10 w-10 text-primary mb-2" />
                  <CardTitle>Flashcards</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Automatically generate flashcards from your reading materials. Study with spaced repetition to maximize retention.
                  </p>
                </CardContent>
              </Card>
              <Card className="bg-background border-none shadow-md">
                <CardHeader>
                  <Zap className="h-10 w-10 text-primary mb-2" />
                  <CardTitle>Instant Quizzes</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Test your knowledge with AI-generated quizzes. Get instant feedback and explanations for every answer.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Social Proof / Trust */}
        <section className="py-24 px-6 lg:px-10">
           <div className="max-w-6xl mx-auto flex flex-col items-center gap-8">
             <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center w-full">
                <div className="space-y-2">
                   <h3 className="text-3xl font-bold">10k+</h3>
                   <p className="text-muted-foreground">Students</p>
                </div>
                <div className="space-y-2">
                   <h3 className="text-3xl font-bold">5M+</h3>
                   <p className="text-muted-foreground">Pages Processed</p>
                </div>
                <div className="space-y-2">
                   <h3 className="text-3xl font-bold">500+</h3>
                   <p className="text-muted-foreground">Universities</p>
                </div>
                <div className="space-y-2">
                   <h3 className="text-3xl font-bold">4.9/5</h3>
                   <p className="text-muted-foreground">User Rating</p>
                </div>
             </div>
           </div>
        </section>
      </main>

      <footer className="py-12 px-6 lg:px-10 border-t bg-muted/30">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between gap-8">
          <div className="space-y-4">
             <div className="flex items-center gap-2 font-bold text-lg">
                <BrainCircuit className="h-5 w-5 text-primary" />
                <span>Cognix</span>
             </div>
             <p className="text-sm text-muted-foreground max-w-xs">
               Empowering students and professionals with AI-driven learning tools.
             </p>
          </div>
          <div className="grid grid-cols-2 gap-12 text-sm">
            <div className="space-y-4">
              <h4 className="font-semibold">Product</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li><Link href="#">Features</Link></li>
                <li><Link href="#">Pricing</Link></li>
                <li><Link href="#">Integrations</Link></li>
              </ul>
            </div>
            <div className="space-y-4">
              <h4 className="font-semibold">Company</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li><Link href="#">About</Link></li>
                <li><Link href="#">Blog</Link></li>
                <li><Link href="#">Contact</Link></li>
              </ul>
            </div>
          </div>
        </div>
        <div className="max-w-6xl mx-auto mt-12 pt-8 border-t text-center text-xs text-muted-foreground">
           © {new Date().getFullYear()} Cognix Inc. All rights reserved.
        </div>
      </footer>
    </div>
  )
}
