'use client'

import { useSearchParams } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertTriangle } from "lucide-react"

export default function AuthError() {
  const searchParams = useSearchParams()
  const error = searchParams.get('error')

  const getErrorMessage = (error: string | null) => {
    switch (error) {
      case 'Configuration':
        return 'There is a problem with the server configuration.'
      case 'AccessDenied':
        return 'Access denied. You do not have permission to sign in.'
      case 'Verification':
        return 'The verification token has expired or has already been used.'
      default:
        return 'An error occurred during authentication.'
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-gray-900">
            🏥 Hospital Stress Warning
          </CardTitle>
          <CardDescription>
            Authentication Error
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert className="border-red-200 bg-red-50">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <AlertTitle className="text-red-800">Authentication Failed</AlertTitle>
            <AlertDescription className="text-red-700">
              {getErrorMessage(error)}
            </AlertDescription>
          </Alert>
          
          <Button 
            onClick={() => window.location.href = '/auth/signin'}
            className="w-full"
            size="lg"
          >
            Try Again
          </Button>
          
          <div className="text-center text-sm text-gray-600">
            <p>If the problem persists, contact your system administrator.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}