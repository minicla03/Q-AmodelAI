import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function RegisterPage() {
  return (
    <Card className="w-full max-w-md">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl font-bold">Create an account</CardTitle>
        <CardDescription>
          Enter your information to create your account
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
            <Label htmlFor="first-name">First name</Label>
            <Input id="first-name" placeholder="John" required />
            </div>
            <div className="space-y-2">
            <Label htmlFor="last-name">Last name</Label>
            <Input id="last-name" placeholder="Doe" required />
            </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" placeholder="m@example.com" required />
        </div>
        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input id="password" type="password" required />
        </div>
      </CardContent>
      <CardFooter className="flex flex-col gap-4">
        <Link href="/dashboard" className="w-full">
            <Button className="w-full">Create account</Button>
        </Link>
        <div className="text-center text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link href="/login" className="text-primary underline-offset-4 hover:underline">
            Log in
          </Link>
        </div>
      </CardFooter>
    </Card>
  )
}
