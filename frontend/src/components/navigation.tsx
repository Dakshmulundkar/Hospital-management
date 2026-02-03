'use client'

import { useSession, signOut } from "next-auth/react"
import { useRouter, usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { 
  LayoutDashboard, 
  Upload, 
  MessageCircle, 
  TestTube,
  LogOut,
  User,
  Bell,
  Heart,
  Activity
} from "lucide-react"

export default function Navigation() {
  const { data: session } = useSession()
  const router = useRouter()
  const pathname = usePathname()

  const navItems = [
    {
      name: 'Dashboard',
      href: '/(authenticated)/dashboard',
      icon: LayoutDashboard,
      description: 'Real-time monitoring'
    },
    {
      name: 'Upload Data',
      href: '/(authenticated)/upload',
      icon: Upload,
      description: 'CSV data import'
    },
    {
      name: 'Simulator',
      href: '/(authenticated)/simulator',
      icon: TestTube,
      description: 'What-if scenarios'
    },
    {
      name: 'AI Assistant',
      href: '/(authenticated)/chat',
      icon: MessageCircle,
      description: 'Natural language queries'
    }
  ]

  const handleSignOut = async () => {
    await signOut({ callbackUrl: '/' })
  }

  if (!session) return null

  return (
    <nav className="fixed top-0 w-full z-50 backdrop-blur-xl bg-white/95 border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Title */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
                <Heart className="w-4 h-4 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900 tracking-tight">
                  MedCore Health
                </h1>
                <p className="text-xs text-gray-500 -mt-0.5">Early Warning System</p>
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="hidden lg:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              
              return (
                <div key={item.name} className="relative group">
                  <Button
                    variant={isActive ? "default" : "ghost"}
                    onClick={() => router.push(item.href)}
                    className={`flex items-center space-x-2 h-10 px-4 rounded-xl transition-all duration-200 ${
                      isActive 
                        ? "bg-blue-600 text-white shadow-lg" 
                        : "hover:bg-blue-50 hover:text-blue-700"
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span className="font-medium">{item.name}</span>
                  </Button>
                  
                  {/* Tooltip */}
                  <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 px-2 py-1 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap">
                    {item.description}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Mobile Navigation */}
          <div className="lg:hidden flex items-center space-x-1 overflow-x-auto">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              
              return (
                <Button
                  key={item.name}
                  variant={isActive ? "default" : "ghost"}
                  size="sm"
                  onClick={() => router.push(item.href)}
                  className={`flex items-center space-x-1 whitespace-nowrap rounded-lg ${
                    isActive 
                      ? "bg-blue-600 text-white" 
                      : "hover:bg-blue-50 hover:text-blue-700"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span className="text-xs">{item.name}</span>
                </Button>
              )
            })}
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-3">
            {/* System Status */}
            <div className="hidden md:flex items-center gap-2">
              <div className="flex items-center gap-1">
                <Activity className="h-3 w-3 text-green-500" />
                <span className="text-xs text-gray-600">System Online</span>
              </div>
            </div>

            {/* Notifications */}
            <Button variant="ghost" size="icon" className="relative rounded-xl hover:bg-blue-50">
              <Bell className="h-4 w-4" />
              <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full text-xs"></span>
            </Button>

            {/* User Profile */}
            <div className="flex items-center space-x-3 pl-3 border-l border-gray-200">
              <div className="hidden sm:block text-right">
                <p className="text-sm font-medium text-gray-900">
                  {session.user?.name}
                </p>
                <p className="text-xs text-gray-500">
                  Healthcare Professional
                </p>
              </div>
              
              {session.user?.image ? (
                <img
                  src={session.user.image}
                  alt="Profile"
                  className="h-8 w-8 rounded-full border-2 border-gray-200"
                />
              ) : (
                <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center border-2 border-gray-200">
                  <User className="h-4 w-4 text-blue-600" />
                </div>
              )}
            </div>

            {/* Sign Out */}
            <Button
              variant="outline"
              onClick={handleSignOut}
              className="flex items-center space-x-2 rounded-xl border-gray-200 hover:bg-red-50 hover:border-red-200 hover:text-red-700"
            >
              <LogOut className="h-4 w-4" />
              <span className="hidden sm:inline">Sign Out</span>
            </Button>
          </div>
        </div>
      </div>
    </nav>
  )
}