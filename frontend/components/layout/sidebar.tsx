"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Home,
  MessageSquare,
  BookOpen,
  BrainCircuit,
  FileText,
  Files,
  Settings,
  LogOut
} from "lucide-react"

const sidebarItems = [
  { name: "Dashboard", href: "/dashboard", icon: Home },
  { name: "Chat", href: "/chat", icon: MessageSquare },
  { name: "Flashcards", href: "/flashcards", icon: BookOpen },
  { name: "Quiz", href: "/quiz", icon: BrainCircuit },
  { name: "Notebooks", href: "/notebooks", icon: FileText },
  { name: "Documents", href: "/documents", icon: Files },
]

export function SidebarContent() {
  const pathname = usePathname()

  return (
    <div className="flex h-full flex-col bg-background">
      <div className="p-6 border-b">
        <Link href="/dashboard" className="flex items-center gap-2 font-bold text-xl">
          <BrainCircuit className="h-6 w-6 text-primary" />
          <span>Cognix</span>
        </Link>
      </div>

      <div className="flex-1 overflow-auto py-4">
        <nav className="grid gap-1 px-2">
          {sidebarItems.map((item, index) => (
            <Link
              key={index}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all hover:text-primary",
                pathname === item.href
                  ? "bg-muted text-primary"
                  : "text-muted-foreground"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.name}
            </Link>
          ))}
        </nav>
      </div>

      <div className="p-4 border-t mt-auto">
        <nav className="grid gap-1">
            <Link
              href="/settings"
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-all hover:text-primary"
            >
              <Settings className="h-4 w-4" />
              Settings
            </Link>
             <Link href="/">
               <Button variant="ghost" className="justify-start gap-3 w-full px-3 text-muted-foreground hover:text-primary">
                  <LogOut className="h-4 w-4" />
                  Logout
               </Button>
             </Link>
        </nav>
      </div>
    </div>
  )
}

export function Sidebar() {
  return (
    <div className="hidden md:flex h-screen flex-col border-r w-64">
       <SidebarContent />
    </div>
  )
}
