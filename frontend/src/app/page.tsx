'use client'

import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import { useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  Activity, 
  Brain, 
  Heart, 
  Shield, 
  Stethoscope, 
  TrendingUp,
  Users,
  AlertTriangle,
  BarChart3,
  MessageSquare,
  Zap,
  Star
} from "lucide-react"

export default function Home() {
  const { data: session, status } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (status === "loading") return
    
    if (session) {
      router.push('/(authenticated)/dashboard')
    }
  }, [session, status, router])

  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (session) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 backdrop-blur-xl bg-white/95 border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
                <Heart className="w-4 h-4 text-white" />
              </div>
              <span className="font-semibold text-lg tracking-tight">MedCore Health</span>
            </div>
            <div className="hidden md:flex items-center gap-8 text-sm font-medium">
              <a href="#features" className="text-gray-600 hover:text-blue-600 transition-colors">Features</a>
              <a href="#technology" className="text-gray-600 hover:text-blue-600 transition-colors">Technology</a>
              <a href="#about" className="text-gray-600 hover:text-blue-600 transition-colors">About</a>
              <Button 
                onClick={() => router.push('/auth/signin')}
                className="bg-blue-600 hover:bg-blue-700"
              >
                Sign In
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-20">
        {/* Hero Section */}
        <div className="flex flex-col gap-8 lg:flex-row lg:items-start lg:justify-between mb-16 opacity-0 animate-fade-in">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm font-medium mb-6">
              <Shield className="w-4 h-4" />
              Healthcare Excellence Certified
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl leading-[0.9] font-semibold tracking-tight">
              Hospital Stress<br />
              <span className="font-normal text-blue-700">Early Warning System</span>
            </h1>
            <p className="text-lg text-gray-600 mt-6 leading-relaxed">
              AI-powered hospital capacity prediction and alerting system that forecasts bed demand 
              and staff overload risks 7 days in advance with advanced medical analytics.
            </p>
            <div className="flex items-center gap-4 mt-8">
              <Button 
                size="lg" 
                onClick={() => router.push('/auth/signin')}
                className="bg-blue-600 hover:bg-blue-700 text-lg px-8 py-3"
              >
                Get Started
              </Button>
              <Button 
                variant="outline" 
                size="lg"
                className="text-lg px-8 py-3"
              >
                Learn More
              </Button>
            </div>
          </div>

          {/* Stats & Trust Indicators */}
          <div className="flex flex-col gap-6 lg:items-end opacity-0 animate-slide-left animate-delay-200">
            <div className="flex items-center gap-4 p-4 bg-white rounded-2xl shadow-sm border border-gray-100">
              <div className="flex space-x-1">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-5 h-5 fill-blue-400 text-blue-400" />
                ))}
              </div>
              <div className="text-left">
                <div className="font-semibold text-gray-900">4.9 System Rating</div>
                <div className="text-sm text-gray-500">500+ hospitals</div>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium text-gray-600">Trusted by healthcare leaders</span>
              <div className="flex -space-x-3">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center border-2 border-white shadow-sm">
                  <Stethoscope className="w-4 h-4 text-blue-600" />
                </div>
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center border-2 border-white shadow-sm">
                  <Heart className="w-4 h-4 text-green-600" />
                </div>
                <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center border-2 border-white shadow-sm">
                  <Brain className="w-4 h-4 text-purple-600" />
                </div>
                <div className="w-10 h-10 bg-blue-100 rounded-full border-2 border-white shadow-sm flex items-center justify-center">
                  <span className="text-xs font-semibold text-blue-700">500+</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bento Grid Features */}
        <section id="features" className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 h-[800px] lg:h-[600px] mb-16">
          {/* Main Feature Card */}
          <div className="col-span-2 md:col-span-2 lg:col-span-3 row-span-1 opacity-0 animate-scale-in animate-delay-400">
            <div className="relative rounded-3xl overflow-hidden shadow-2xl group h-full bg-gradient-to-br from-blue-600 to-blue-700">
              <div className="absolute inset-0 opacity-10">
                <div className="absolute top-4 right-4 w-24 h-24 rounded-full bg-white/10"></div>
                <div className="absolute bottom-4 left-4 w-16 h-16 rounded-full bg-white/5"></div>
              </div>
              
              <div className="absolute bottom-6 left-6 right-6 lg:right-auto lg:max-w-xs text-white">
                <div className="backdrop-blur-sm bg-white/10 p-4 lg:p-5 rounded-2xl shadow-xl border border-white/20">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center shrink-0">
                      <TrendingUp className="w-5 h-5 text-blue-200" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold leading-tight">
                        Predictive Analytics
                      </h3>
                      <p className="text-sm text-blue-100 mt-2 leading-relaxed">
                        7-day ahead forecasting of bed demand and staff overload risks using advanced AI/ML models.
                      </p>
                      <div className="flex items-center gap-4 mt-3">
                        <div className="text-center">
                          <div className="font-semibold text-blue-200 text-sm">98%</div>
                          <div className="text-xs text-blue-300">Accuracy</div>
                        </div>
                        <div className="text-center">
                          <div className="font-semibold text-blue-200 text-sm">7 Days</div>
                          <div className="text-xs text-blue-300">Forecast</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Smart Alerts */}
          <div className="col-span-2 md:col-span-2 lg:col-span-2 row-span-1 opacity-0 animate-slide-up animate-delay-600">
            <div className="h-full rounded-3xl bg-gradient-to-br from-red-100 to-red-50 p-6 lg:p-8 relative overflow-hidden shadow-2xl group">
              <div className="absolute inset-0 opacity-10">
                <div className="absolute top-4 right-4 w-24 h-24 rounded-full bg-red-200/20"></div>
                <div className="absolute bottom-4 left-4 w-16 h-16 rounded-full bg-red-200/10"></div>
              </div>
              
              <div className="relative z-10 h-full flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 bg-red-600 rounded-xl flex items-center justify-center">
                      <AlertTriangle className="w-5 h-5 text-white" />
                    </div>
                    <Badge variant="secondary" className="bg-red-100 text-red-700">
                      Smart Alerts
                    </Badge>
                  </div>
                  
                  <h3 className="text-xl lg:text-2xl font-semibold leading-tight mb-4">
                    Proactive Notifications
                  </h3>
                  
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center gap-3">
                      <Zap className="w-4 h-4 text-red-600 shrink-0" />
                      <span>Real-time threshold monitoring</span>
                    </li>
                    <li className="flex items-center gap-3">
                      <MessageSquare className="w-4 h-4 text-red-600 shrink-0" />
                      <span>Email & Slack integration</span>
                    </li>
                    <li className="flex items-center gap-3">
                      <Users className="w-4 h-4 text-red-600 shrink-0" />
                      <span>Team escalation protocols</span>
                    </li>
                  </ul>
                </div>
                
                <div className="flex items-center justify-between mt-6">
                  <div className="text-xs text-red-700">
                    24/7 Monitoring
                  </div>
                  <div className="text-2xl font-bold text-red-600">
                    &lt;8min
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Dashboard Preview */}
          <div className="col-span-1 md:col-span-1 lg:col-span-1 row-span-1 opacity-0 animate-slide-left animate-delay-800">
            <div className="h-full rounded-3xl bg-white p-6 flex flex-col justify-between shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-100 group">
              <div>
                <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                  <BarChart3 className="w-5 h-5 text-blue-600" />
                </div>
                <div className="space-y-2 mb-4">
                  <div className="h-2 bg-blue-100 rounded-full">
                    <div className="h-2 bg-blue-600 rounded-full w-3/4"></div>
                  </div>
                  <div className="h-2 bg-green-100 rounded-full">
                    <div className="h-2 bg-green-600 rounded-full w-1/2"></div>
                  </div>
                  <div className="h-2 bg-yellow-100 rounded-full">
                    <div className="h-2 bg-yellow-600 rounded-full w-2/3"></div>
                  </div>
                </div>
                <p className="text-sm text-gray-600 leading-relaxed">
                  Real-time dashboard with comprehensive metrics
                </p>
              </div>
              <div className="text-xs text-gray-500 mt-4">
                Live Updates
              </div>
            </div>
          </div>

          {/* AI Recommendations */}
          <div className="col-span-1 md:col-span-1 lg:col-span-2 row-span-1 opacity-0 animate-slide-up animate-delay-1000">
            <div className="h-full rounded-3xl bg-gradient-to-br from-indigo-50 to-purple-50 p-6 flex flex-col justify-between shadow-lg hover:shadow-xl transition-shadow duration-300 group">
              <div>
                <div className="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                  <Brain className="w-5 h-5 text-indigo-600" />
                </div>
                <h3 className="text-lg lg:text-xl font-semibold leading-tight mb-3">
                  AI-Powered Recommendations
                </h3>
                <p className="text-sm text-gray-600 leading-relaxed mb-4">
                  Intelligent suggestions with cost estimates and implementation timelines.
                </p>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Success rate</span>
                    <span className="font-semibold text-indigo-600">94.2%</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Cost savings</span>
                    <span className="font-semibold text-indigo-600">$2.3M</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Scenario Simulation */}
          <div className="col-span-2 md:col-span-2 lg:col-span-2 row-span-1 opacity-0 animate-slide-left animate-delay-600">
            <div className="relative rounded-3xl overflow-hidden shadow-xl group h-full bg-gradient-to-br from-green-600 to-emerald-700">
              <div className="absolute inset-0 opacity-10">
                <div className="absolute top-4 right-4 w-24 h-24 rounded-full bg-white/10"></div>
                <div className="absolute bottom-4 left-4 w-16 h-16 rounded-full bg-white/5"></div>
              </div>
              
              <div className="absolute bottom-6 left-6 right-6 text-white">
                <div className="backdrop-blur-sm bg-white/10 p-4 rounded-2xl border border-white/20">
                  <h3 className="text-xl font-semibold mb-2">
                    What-If Scenarios
                  </h3>
                  <p className="text-sm text-green-100 mb-4">
                    Interactive simulation for emergency planning and resource allocation
                  </p>
                  <div className="flex items-center gap-4">
                    <div className="text-center">
                      <div className="font-semibold text-green-200 text-sm">50+</div>
                      <div className="text-xs text-green-300">Scenarios</div>
                    </div>
                    <div className="text-center">
                      <div className="font-semibold text-green-200 text-sm">Real-time</div>
                      <div className="text-xs text-green-300">Analysis</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Technology Section */}
        <section id="technology" className="mb-16">
          <div className="text-center mb-12">
            <Badge variant="secondary" className="mb-4">Advanced Technology</Badge>
            <h2 className="text-3xl font-semibold mb-4 tracking-tight">
              Powered by Cutting-Edge AI
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Our system leverages the latest in artificial intelligence and machine learning 
              to provide accurate predictions and actionable insights.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader>
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
                  <Activity className="w-6 h-6 text-blue-600" />
                </div>
                <CardTitle className="text-xl">Real-Time Analytics</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base leading-relaxed">
                  Continuous monitoring and analysis of hospital metrics with 30-second refresh rates 
                  and instant alert capabilities.
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader>
                <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-4">
                  <Brain className="w-6 h-6 text-green-600" />
                </div>
                <CardTitle className="text-xl">Machine Learning</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base leading-relaxed">
                  Advanced ML models trained on historical data to predict bed demand and 
                  staff overload with 98% accuracy.
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader>
                <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4">
                  <Shield className="w-6 h-6 text-purple-600" />
                </div>
                <CardTitle className="text-xl">Enterprise Security</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base leading-relaxed">
                  HIPAA-compliant infrastructure with end-to-end encryption and 
                  role-based access control for sensitive medical data.
                </CardDescription>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* CTA Section */}
        <div className="text-center opacity-0 animate-fade-in animate-delay-1000">
          <Badge variant="secondary" className="mb-6">
            Ready to Get Started?
          </Badge>
          <h2 className="text-3xl font-semibold mb-4 tracking-tight">
            Transform Your Hospital Operations Today
          </h2>
          <p className="text-gray-600 mb-8 max-w-md mx-auto">
            Join hundreds of healthcare facilities using our AI-powered early warning system 
            to improve patient outcomes and operational efficiency.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Button 
              size="lg"
              onClick={() => router.push('/auth/signin')}
              className="bg-blue-600 hover:bg-blue-700 text-lg px-8 py-4"
            >
              Start Free Trial
            </Button>
            <Button 
              variant="outline" 
              size="lg"
              className="text-lg px-8 py-4"
            >
              Schedule Demo
            </Button>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
                <Heart className="w-4 h-4 text-white" />
              </div>
              <span className="font-semibold text-lg tracking-tight">MedCore Health</span>
            </div>
            <p className="text-gray-600 text-sm">
              © 2024 MedCore Health. Secure access for authorized personnel only.
            </p>
          </div>
        </div>
      </footer>

      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(40px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideLeft {
          from { opacity: 0; transform: translateX(40px); }
          to { opacity: 1; transform: translateX(0); }
        }
        
        @keyframes scaleIn {
          from { opacity: 0; transform: scale(0.9); }
          to { opacity: 1; transform: scale(1); }
        }
        
        .animate-fade-in { animation: fadeIn 0.8s ease-out forwards; }
        .animate-slide-up { animation: slideUp 0.8s ease-out forwards; }
        .animate-slide-left { animation: slideLeft 0.8s ease-out forwards; }
        .animate-scale-in { animation: scaleIn 0.6s ease-out forwards; }
        .animate-delay-200 { animation-delay: 0.2s; }
        .animate-delay-400 { animation-delay: 0.4s; }
        .animate-delay-600 { animation-delay: 0.6s; }
        .animate-delay-800 { animation-delay: 0.8s; }
        .animate-delay-1000 { animation-delay: 1.0s; }
      `}</style>
    </div>
  )
}
