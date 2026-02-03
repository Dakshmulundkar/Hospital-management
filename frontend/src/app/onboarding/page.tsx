'use client'

import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { 
  CheckCircle, 
  Upload, 
  Users, 
  Settings, 
  TestTube, 
  Bell,
  ArrowRight,
  ArrowLeft,
  Skip,
  Save,
  Shield,
  Heart,
  Activity,
  Brain
} from "lucide-react"

interface OnboardingStep {
  id: number
  title: string
  description: string
  icon: React.ReactNode
  completed: boolean
}

export default function OnboardingPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(1)
  const [completedSteps, setCompletedSteps] = useState<number[]>([])
  
  // Form data for each step
  const [csvUploaded, setCsvUploaded] = useState(false)
  const [bedStressThreshold, setBedStressThreshold] = useState(85)
  const [staffRiskThreshold, setStaffRiskThreshold] = useState(75)
  const [emailAlerts, setEmailAlerts] = useState('')
  const [slackWebhook, setSlackWebhook] = useState('')
  const [testCompleted, setTestCompleted] = useState(false)

  const steps: OnboardingStep[] = [
    {
      id: 1,
      title: "Upload Historical Data",
      description: "Upload your hospital's historical logs to enable AI predictions",
      icon: <Upload className="h-6 w-6" />,
      completed: completedSteps.includes(1)
    },
    {
      id: 2,
      title: "Staff Roster Connection",
      description: "Connect your staff management system (placeholder for future)",
      icon: <Users className="h-6 w-6" />,
      completed: completedSteps.includes(2)
    },
    {
      id: 3,
      title: "Configure Thresholds",
      description: "Set alert thresholds for bed stress and staff risk",
      icon: <Settings className="h-6 w-6" />,
      completed: completedSteps.includes(3)
    },
    {
      id: 4,
      title: "Test Prediction",
      description: "Generate your first prediction to verify the system",
      icon: <TestTube className="h-6 w-6" />,
      completed: completedSteps.includes(4)
    },
    {
      id: 5,
      title: "Enable Alerts",
      description: "Configure email and Slack notifications",
      icon: <Bell className="h-6 w-6" />,
      completed: completedSteps.includes(5)
    }
  ]

  useEffect(() => {
    if (status === "loading") return
    
    if (!session) {
      router.push('/auth/signin')
      return
    }

    // Check if onboarding was already completed
    const onboardingCompleted = localStorage.getItem('onboarding_completed')
    if (onboardingCompleted === 'true') {
      router.push('/(authenticated)/dashboard')
    }

    // Load saved progress
    const savedProgress = localStorage.getItem('onboarding_progress')
    if (savedProgress) {
      const progress = JSON.parse(savedProgress)
      setCurrentStep(progress.currentStep || 1)
      setCompletedSteps(progress.completedSteps || [])
    }
  }, [session, status, router])

  const saveProgress = () => {
    const progress = {
      currentStep,
      completedSteps,
      csvUploaded,
      bedStressThreshold,
      staffRiskThreshold,
      emailAlerts,
      slackWebhook,
      testCompleted
    }
    localStorage.setItem('onboarding_progress', JSON.stringify(progress))
  }

  const completeStep = (stepId: number) => {
    if (!completedSteps.includes(stepId)) {
      setCompletedSteps(prev => [...prev, stepId])
    }
    saveProgress()
  }

  const nextStep = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1)
      saveProgress()
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
      saveProgress()
    }
  }

  const completeOnboarding = () => {
    localStorage.setItem('onboarding_completed', 'true')
    localStorage.removeItem('onboarding_progress')
    router.push('/(authenticated)/dashboard')
  }

  const skipOnboardingProcess = () => {
    localStorage.setItem('onboarding_completed', 'true')
    localStorage.removeItem('onboarding_progress')
    router.push('/(authenticated)/dashboard')
  }

  const handleFileUpload = async (file: File) => {
    // Simulate file upload
    setCsvUploaded(true)
    completeStep(1)
  }

  const runTestPrediction = async () => {
    // Simulate test prediction
    setTestCompleted(true)
    completeStep(4)
  }

  const progress = (completedSteps.length / steps.length) * 100

  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-white to-blue-50/30">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="text-gray-600">Loading onboarding...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50/30 p-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm font-medium mb-4">
            <Shield className="w-4 h-4" />
            Healthcare System Setup
          </div>
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl flex items-center justify-center">
              <Heart className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-3xl font-semibold text-gray-900 tracking-tight">
              Welcome to MedCore Health
            </h1>
          </div>
          <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
            Let's get your Hospital Stress Early Warning System configured in 5 simple steps
          </p>
          <div className="flex items-center justify-center space-x-4 mb-6">
            <Progress value={progress} className="w-80 h-2" />
            <span className="text-sm text-gray-500 font-medium">
              {completedSteps.length} of {steps.length} completed
            </span>
          </div>
        </div>

        {/* Steps Overview */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={`relative ${
                step.id === currentStep ? 'ring-2 ring-blue-500' : ''
              }`}
            >
              <Card className={`cursor-pointer transition-all duration-300 hover:shadow-lg ${
                step.completed ? 'bg-green-50 border-green-200 shadow-md' : 
                step.id === currentStep ? 'bg-blue-50 border-blue-200 shadow-md' : 'hover:bg-gray-50'
              }`}>
                <CardContent className="p-4 text-center">
                  <div className={`mx-auto mb-3 w-12 h-12 rounded-xl flex items-center justify-center ${
                    step.completed ? 'bg-green-100 text-green-600' : 
                    step.id === currentStep ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-400'
                  }`}>
                    {step.completed ? <CheckCircle className="h-6 w-6" /> : step.icon}
                  </div>
                  <h3 className="font-medium text-sm mb-2">{step.title}</h3>
                  <Badge variant={
                    step.completed ? 'default' : 
                    step.id === currentStep ? 'secondary' : 'outline'
                  } className={`text-xs ${
                    step.completed ? 'bg-green-100 text-green-700 border-green-200' :
                    step.id === currentStep ? 'bg-blue-100 text-blue-700 border-blue-200' : ''
                  }`}>
                    {step.completed ? 'Complete' : 
                     step.id === currentStep ? 'Current' : 'Pending'}
                  </Badge>
                </CardContent>
              </Card>
              {index < steps.length - 1 && (
                <ArrowRight className="hidden md:block absolute top-1/2 -right-6 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              )}
            </div>
          ))}
        </div>
        {/* Current Step Content */}
        <Card className="backdrop-blur-sm bg-white/95 border border-gray-100 shadow-2xl rounded-3xl mb-8">
          <CardHeader>
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-blue-100 rounded-2xl flex items-center justify-center">
                {steps[currentStep - 1].icon}
              </div>
              <div>
                <CardTitle className="text-2xl">{steps[currentStep - 1].title}</CardTitle>
                <CardDescription className="text-base">{steps[currentStep - 1].description}</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-8">
            {/* Step 1: CSV Upload */}
            {currentStep === 1 && (
              <div className="space-y-6">
                <div className="p-6 bg-blue-50 rounded-2xl border border-blue-100">
                  <div className="flex items-start gap-3">
                    <Activity className="w-5 h-5 text-blue-600 mt-0.5 shrink-0" />
                    <div>
                      <h4 className="font-medium text-blue-900 mb-2">Data Requirements</h4>
                      <p className="text-blue-800 text-sm leading-relaxed">
                        Upload a CSV file with your hospital's historical data to enable AI predictions.
                        The file should contain: date, admissions, beds_occupied, staff_on_duty, overload_flag
                      </p>
                    </div>
                  </div>
                </div>
                
                {!csvUploaded ? (
                  <div className="border-2 border-dashed border-gray-300 rounded-2xl p-12 text-center hover:border-blue-300 hover:bg-blue-50/50 transition-all duration-300">
                    <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                      <Upload className="h-8 w-8 text-blue-600" />
                    </div>
                    <p className="text-lg font-medium mb-2">Choose a CSV file or drag and drop</p>
                    <p className="text-gray-500 mb-4">Maximum file size: 50MB</p>
                    <input
                      type="file"
                      accept=".csv"
                      onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
                      className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                    />
                  </div>
                ) : (
                  <Alert className="border-green-200 bg-green-50 rounded-2xl">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <AlertDescription className="text-green-700 text-base">
                      CSV file uploaded successfully! Historical data is now available for AI predictions.
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            )}

            {/* Step 2: Staff Roster */}
            {currentStep === 2 && (
              <div className="space-y-6">
                <div className="p-6 bg-purple-50 rounded-2xl border border-purple-100">
                  <div className="flex items-start gap-3">
                    <Users className="w-5 h-5 text-purple-600 mt-0.5 shrink-0" />
                    <div>
                      <h4 className="font-medium text-purple-900 mb-2">Staff Integration</h4>
                      <p className="text-purple-800 text-sm leading-relaxed">
                        Connect your staff management system for real-time staffing data.
                        This feature will be available in a future update.
                      </p>
                    </div>
                  </div>
                </div>
                
                <Alert className="rounded-2xl">
                  <AlertDescription className="text-base">
                    Staff roster integration is planned for the next release. 
                    For now, staff data will be managed through CSV uploads.
                  </AlertDescription>
                </Alert>
                
                <Button 
                  onClick={() => completeStep(2)}
                  className="w-full h-12 bg-purple-600 hover:bg-purple-700 rounded-xl"
                  size="lg"
                >
                  Continue (Skip for Now)
                </Button>
              </div>
            )}

            {/* Step 3: Configure Thresholds */}
            {currentStep === 3 && (
              <div className="space-y-8">
                <div className="p-6 bg-orange-50 rounded-2xl border border-orange-100">
                  <div className="flex items-start gap-3">
                    <Settings className="w-5 h-5 text-orange-600 mt-0.5 shrink-0" />
                    <div>
                      <h4 className="font-medium text-orange-900 mb-2">Alert Configuration</h4>
                      <p className="text-orange-800 text-sm leading-relaxed">
                        Set the thresholds that will trigger alerts when exceeded.
                        These can be adjusted later in the dashboard settings.
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="grid md:grid-cols-2 gap-8">
                  <div className="space-y-4">
                    <label className="block text-sm font-medium text-gray-700">
                      Bed Stress Threshold (%)
                    </label>
                    <div className="relative">
                      <Input
                        type="number"
                        value={bedStressThreshold}
                        onChange={(e) => setBedStressThreshold(Number(e.target.value))}
                        min={50}
                        max={100}
                        className="text-lg h-12 rounded-xl"
                      />
                      <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                        <Badge variant="outline" className="text-red-700 border-red-200">
                          {bedStressThreshold}%
                        </Badge>
                      </div>
                    </div>
                    <p className="text-xs text-gray-600">
                      Alert when bed occupancy exceeds this percentage
                    </p>
                  </div>
                  
                  <div className="space-y-4">
                    <label className="block text-sm font-medium text-gray-700">
                      Staff Risk Threshold
                    </label>
                    <div className="relative">
                      <Input
                        type="number"
                        value={staffRiskThreshold}
                        onChange={(e) => setStaffRiskThreshold(Number(e.target.value))}
                        min={50}
                        max={100}
                        className="text-lg h-12 rounded-xl"
                      />
                      <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                        <Badge variant="outline" className="text-blue-700 border-blue-200">
                          {staffRiskThreshold}
                        </Badge>
                      </div>
                    </div>
                    <p className="text-xs text-gray-600">
                      Alert when staff risk score exceeds this value
                    </p>
                  </div>
                </div>
                
                <Button 
                  onClick={() => completeStep(3)}
                  className="w-full h-12 bg-orange-600 hover:bg-orange-700 rounded-xl"
                  size="lg"
                >
                  Save Thresholds
                </Button>
              </div>
            )}

            {/* Step 4: Test Prediction */}
            {currentStep === 4 && (
              <div className="space-y-6">
                <div className="p-6 bg-green-50 rounded-2xl border border-green-100">
                  <div className="flex items-start gap-3">
                    <Brain className="w-5 h-5 text-green-600 mt-0.5 shrink-0" />
                    <div>
                      <h4 className="font-medium text-green-900 mb-2">AI Prediction Test</h4>
                      <p className="text-green-800 text-sm leading-relaxed">
                        Generate your first prediction to verify the AI system is working correctly
                        and can analyze your hospital data.
                      </p>
                    </div>
                  </div>
                </div>
                
                {!testCompleted ? (
                  <div className="text-center py-12">
                    <div className="w-20 h-20 bg-green-100 rounded-3xl flex items-center justify-center mx-auto mb-6">
                      <TestTube className="h-10 w-10 text-green-600" />
                    </div>
                    <h3 className="text-xl font-semibold mb-3">Ready to test AI predictions</h3>
                    <p className="text-gray-600 mb-6 max-w-md mx-auto">
                      This will generate a sample forecast using your uploaded data
                    </p>
                    <Button onClick={runTestPrediction} size="lg" className="bg-green-600 hover:bg-green-700 rounded-xl">
                      <TestTube className="h-5 w-5 mr-2" />
                      Run Test Prediction
                    </Button>
                  </div>
                ) : (
                  <Alert className="border-green-200 bg-green-50 rounded-2xl">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <AlertDescription className="text-green-700 text-base">
                      Test prediction completed successfully! The AI system is ready to provide accurate forecasts.
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            )}

            {/* Step 5: Enable Alerts */}
            {currentStep === 5 && (
              <div className="space-y-8">
                <div className="p-6 bg-indigo-50 rounded-2xl border border-indigo-100">
                  <div className="flex items-start gap-3">
                    <Bell className="w-5 h-5 text-indigo-600 mt-0.5 shrink-0" />
                    <div>
                      <h4 className="font-medium text-indigo-900 mb-2">Notification Setup</h4>
                      <p className="text-indigo-800 text-sm leading-relaxed">
                        Configure notification channels to receive alerts when thresholds are exceeded.
                        You can modify these settings later in the dashboard.
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Email Recipients (comma-separated)
                    </label>
                    <Input
                      type="email"
                      value={emailAlerts}
                      onChange={(e) => setEmailAlerts(e.target.value)}
                      placeholder="admin@hospital.com, doctor@hospital.com"
                      className="h-12 rounded-xl"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Slack Webhook URL (optional)
                    </label>
                    <Input
                      type="url"
                      value={slackWebhook}
                      onChange={(e) => setSlackWebhook(e.target.value)}
                      placeholder="https://hooks.slack.com/services/..."
                      className="h-12 rounded-xl"
                    />
                  </div>
                </div>
                
                <Button 
                  onClick={() => completeStep(5)}
                  className="w-full h-12 bg-indigo-600 hover:bg-indigo-700 rounded-xl"
                  size="lg"
                >
                  Save Alert Configuration
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <div className="flex space-x-3">
            <Button
              variant="outline"
              onClick={prevStep}
              disabled={currentStep === 1}
              className="rounded-xl"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Previous
            </Button>
            
            <Button
              variant="ghost"
              onClick={skipOnboardingProcess}
              className="rounded-xl"
            >
              <Skip className="h-4 w-4 mr-2" />
              Skip Setup
            </Button>
          </div>

          <div className="flex space-x-3">
            <Button
              variant="outline"
              onClick={saveProgress}
              className="rounded-xl"
            >
              <Save className="h-4 w-4 mr-2" />
              Save Progress
            </Button>
            
            {currentStep < steps.length ? (
              <Button
                onClick={nextStep}
                disabled={!completedSteps.includes(currentStep)}
                className="bg-blue-600 hover:bg-blue-700 rounded-xl"
              >
                Next Step
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            ) : (
              <Button
                onClick={completeOnboarding}
                disabled={completedSteps.length < steps.length}
                className="bg-green-600 hover:bg-green-700 rounded-xl"
              >
                Complete Setup
                <CheckCircle className="h-4 w-4 ml-2" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}