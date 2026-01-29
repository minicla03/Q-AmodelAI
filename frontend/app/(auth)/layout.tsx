import Link from "next/link"
import { BrainCircuit } from "lucide-react"

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-muted/50 p-4">
      <div className="mb-8">
        <Link href="/" className="flex items-center gap-2 font-bold text-2xl">
          <BrainCircuit className="h-8 w-8 text-primary" />
          <span>Cognix</span>
        </Link>
      </div>
      {children}
    </div>
  )
}
