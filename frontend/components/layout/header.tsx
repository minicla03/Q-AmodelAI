"use client"

import { usePathname } from "next/navigation"
import { ModeToggle } from "@/components/theme-toggle"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Bell } from "lucide-react"

export function Header() {
  const pathname = usePathname()

  // Simple breadcrumb logic
  const segments = pathname.split('/').filter(Boolean)
  const breadcrumbs = segments.map((segment, index) => {
    const isLast = index === segments.length - 1
    const title = segment.charAt(0).toUpperCase() + segment.slice(1)
    return (
      <span key={segment} className="flex items-center">
        <span className="mx-2 text-muted-foreground">/</span>
        <span className={isLast ? "font-semibold text-foreground" : "text-muted-foreground"}>
          {title}
        </span>
      </span>
    )
  })

  return (
    <header className="flex h-16 items-center justify-between border-b bg-background px-6">
      <div className="flex items-center text-sm">
        <span className="font-semibold text-foreground">Cognix</span>
        {breadcrumbs}
      </div>

      <div className="flex items-center gap-4">
        <ModeToggle />
        <Button variant="ghost" size="icon">
           <Bell className="h-5 w-5" />
        </Button>
        <div className="flex items-center gap-2 pl-2 border-l">
            <div className="text-right hidden sm:block">
                <p className="text-sm font-medium leading-none">John Doe</p>
                <p className="text-xs text-muted-foreground">Student</p>
            </div>
            <Avatar>
                <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
                <AvatarFallback>JD</AvatarFallback>
            </Avatar>
        </div>
      </div>
    </header>
  )
}
