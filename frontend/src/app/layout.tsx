import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { Providers } from "./providers"

const inter = Inter({ 
  subsets: ["latin"],
  weight: ['300', '400', '500', '600', '700'],
  display: 'swap'
})

export const metadata: Metadata = {
  title: "MedCore Health - Hospital Stress Early Warning System",
  description: "AI-powered hospital capacity prediction and alerting system for advanced medical care solutions",
  keywords: "hospital management, medical care, AI predictions, healthcare analytics",
  authors: [{ name: "MedCore Health" }],
  viewport: "width=device-width, initial-scale=1",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} antialiased bg-gradient-to-br from-slate-50 via-white to-blue-50/30`}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
