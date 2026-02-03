'use client'

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  AlertTriangle, 
  Users, 
  Bed, 
  Bell,
  Lightbulb,
  RefreshCw,
  Upload,
  Activity,
  Heart,
  Brain,
  Shield,
  Zap,
  BarChart3,
  TestTube
} from "lucide-react"

interface DashboardData {
  bed_stress_current: number
  staff_risk_current: number
  active_alerts_count: number
  recommendations_count: number
  seven_day_forecast: {
    predictions: Array<{
      date: string
      predicted_beds: number
      bed_stress: number
      confidence: number
      is_high_risk: boolean
    }>
    overall_confidence: number
    generated_at: string
  }
  seven_day_staff_risk: Array<{
    risk_score: number
    confidence: number
    is_critical: boolean
    contributing_factors: string[]
    generated_at: string
  }>
  trend_indicators: {
    bed_stress?: string
    staff_risk?: string
  }
}

interface Recommendation {
  title: string
  description: string
  rationale: string
  cost_estimate: number
  impact_score: number
  priority: number
  implementation_time: string
}

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  useEffect(() => {
    fetchDashboardData()
    
    // Set up polling every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/dashboard-data`)
      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data')
      }
      
      const data = await response.json()
      setDashboardData(data)
      setLastUpdated(new Date())
      
      // Fetch recommendations if there are high risk conditions
      if (data.bed_stress_current > 85 || data.staff_risk_current > 75) {
        fetchRecommendations(data.bed_stress_current, data.staff_risk_current)
      }
      
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const fetchRecommendations = async (bedStress: number, staffRisk: number) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/recommendations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          bed_stress: bedStress,
          staff_risk: staffRisk,
          include_historical: true
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setRecommendations(data.recommendations || [])
      }
    } catch (err) {
      console.error('Failed to fetch recommendations:', err)
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-red-500" />
      case 'down':
        return <TrendingDown className="h-4 w-4 text-green-500" />
      default:
        return <Minus className="h-4 w-4 text-gray-500" />
    }
  }

  const getRiskColor = (value: number, threshold: number) => {
    if (value > threshold) return 'text-red-600'
    if (value > threshold * 0.8) return 'text-yellow-600'
    return 'text-green-600'
  }

  const getRiskBadge = (value: number, threshold: number, criticalLabel: string, normalLabel: string) => {
    if (value > threshold) {
      return <Badge variant="destructive" className="bg-red-100 text-red-700 border-red-200">{criticalLabel}</Badge>
    }
    return <Badge variant="secondary" className="bg-green-100 text-green-700 border-green-200">{normalLabel}</Badge>
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="text-gray-600">Loading healthcare dashboard...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <Alert className="max-w-md border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertTitle className="text-red-800">System Error</AlertTitle>
          <AlertDescription className="text-red-700">{error}</AlertDescription>
        </Alert>
      </div>
    )
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Upload className="h-8 w-8 text-blue-600" />
          </div>
          <h2 className="text-xl font-semibold mb-2 text-gray-900">No Data Available</h2>
          <p className="text-gray-600 mb-6">Upload hospital data to start monitoring capacity and stress levels</p>
          <Button 
            onClick={() => window.location.href = '/(authenticated)/upload'}
            className="bg-blue-600 hover:bg-blue-700"
          >
            Upload Data
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-start">
            <div>
              <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm font-medium mb-4">
                <Shield className="w-4 h-4" />
                Healthcare Analytics Dashboard
              </div>
              <h1 className="text-3xl font-semibold text-gray-900 tracking-tight">
                Hospital Capacity Overview
              </h1>
              <p className="text-gray-600 mt-2">
                Real-time monitoring and predictive analytics for optimal patient care
              </p>
            </div>
            <div className="text-right">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="h-4 w-4 text-green-500" />
                <span className="text-sm text-gray-600">
                  Last updated: {lastUpdated?.toLocaleTimeString()}
                </span>
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={fetchDashboardData}
                className="rounded-xl border-gray-200 hover:bg-blue-50"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </div>

        {/* Critical Alert Banner */}
        {(dashboardData.bed_stress_current > 85 || dashboardData.staff_risk_current > 75) && (
          <Alert className="mb-8 border-red-200 bg-red-50 rounded-2xl">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            <AlertTitle className="text-red-800 text-lg">Critical Alert - Immediate Action Required</AlertTitle>
            <AlertDescription className="text-red-700 mt-2">
              Hospital stress levels have exceeded critical thresholds. Review recommendations and implement mitigation strategies immediately.
            </AlertDescription>
          </Alert>
        )}

        {/* Bento Grid Dashboard */}
        <section className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 h-[600px] mb-8">
          {/* Bed Stress - Main Card */}
          <div className="col-span-2 md:col-span-2 lg:col-span-2 row-span-1">
            <Card className="h-full backdrop-blur-sm bg-white/95 border border-gray-100 shadow-xl rounded-3xl overflow-hidden group hover:shadow-2xl transition-all duration-300">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-transparent opacity-50"></div>
              <CardContent className="relative p-6 h-full flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                      <Bed className="h-6 w-6 text-blue-600" />
                    </div>
                    {getTrendIcon(dashboardData.trend_indicators.bed_stress || 'stable')}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Bed Stress Level</h3>
                  <div className={`text-4xl font-bold mb-3 ${getRiskColor(dashboardData.bed_stress_current, 85)}`}>
                    {dashboardData.bed_stress_current.toFixed(1)}%
                  </div>
                  {getRiskBadge(dashboardData.bed_stress_current, 85, 'HIGH RISK', 'Normal')}
                </div>
                <div className="mt-4">
                  <Progress 
                    value={dashboardData.bed_stress_current} 
                    className="h-3 rounded-full"
                  />
                  <p className="text-xs text-gray-500 mt-2">Threshold: 85% critical</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Staff Risk */}
          <div className="col-span-2 md:col-span-2 lg:col-span-2 row-span-1">
            <Card className="h-full backdrop-blur-sm bg-white/95 border border-gray-100 shadow-xl rounded-3xl overflow-hidden group hover:shadow-2xl transition-all duration-300">
              <div className="absolute inset-0 bg-gradient-to-br from-green-50 to-transparent opacity-50"></div>
              <CardContent className="relative p-6 h-full flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                      <Users className="h-6 w-6 text-green-600" />
                    </div>
                    {getTrendIcon(dashboardData.trend_indicators.staff_risk || 'stable')}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Staff Risk Score</h3>
                  <div className={`text-4xl font-bold mb-3 ${getRiskColor(dashboardData.staff_risk_current, 75)}`}>
                    {dashboardData.staff_risk_current.toFixed(1)}
                  </div>
                  {getRiskBadge(dashboardData.staff_risk_current, 75, 'CRITICAL', 'Normal')}
                </div>
                <div className="mt-4">
                  <Progress 
                    value={dashboardData.staff_risk_current} 
                    className="h-3 rounded-full"
                  />
                  <p className="text-xs text-gray-500 mt-2">Threshold: 75 critical</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Active Alerts */}
          <div className="col-span-1 md:col-span-1 lg:col-span-1 row-span-1">
            <Card className="h-full backdrop-blur-sm bg-white/95 border border-gray-100 shadow-xl rounded-3xl overflow-hidden group hover:shadow-2xl transition-all duration-300">
              <div className="absolute inset-0 bg-gradient-to-br from-red-50 to-transparent opacity-50"></div>
              <CardContent className="relative p-6 h-full flex flex-col justify-center text-center">
                <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                  <Bell className="h-6 w-6 text-red-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  {dashboardData.active_alerts_count}
                </div>
                <p className="text-sm text-gray-600">Active Alerts</p>
              </CardContent>
            </Card>
          </div>

          {/* Recommendations */}
          <div className="col-span-1 md:col-span-1 lg:col-span-1 row-span-1">
            <Card className="h-full backdrop-blur-sm bg-white/95 border border-gray-100 shadow-xl rounded-3xl overflow-hidden group hover:shadow-2xl transition-all duration-300">
              <div className="absolute inset-0 bg-gradient-to-br from-yellow-50 to-transparent opacity-50"></div>
              <CardContent className="relative p-6 h-full flex flex-col justify-center text-center">
                <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                  <Lightbulb className="h-6 w-6 text-yellow-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  {dashboardData.recommendations_count}
                </div>
                <p className="text-sm text-gray-600">Recommendations</p>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Detailed Analytics Tabs */}
        <Tabs defaultValue="forecast" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-white/50 backdrop-blur-sm rounded-2xl p-1">
            <TabsTrigger value="forecast" className="rounded-xl">7-Day Forecast</TabsTrigger>
            <TabsTrigger value="recommendations" className="rounded-xl">AI Recommendations</TabsTrigger>
            <TabsTrigger value="analytics" className="rounded-xl">Advanced Analytics</TabsTrigger>
            <TabsTrigger value="insights" className="rounded-xl">Clinical Insights</TabsTrigger>
          </TabsList>

          <TabsContent value="forecast">
            <Card className="backdrop-blur-sm bg-white/95 border border-gray-100 shadow-xl rounded-3xl">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                    <BarChart3 className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <CardTitle className="text-xl">7-Day Capacity Forecast</CardTitle>
                    <CardDescription>
                      Predictive analytics for bed occupancy and stress levels
                      (Confidence: {dashboardData.seven_day_forecast.overall_confidence.toFixed(1)}%)
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-100">
                        <th className="text-left p-3 font-medium text-gray-700">Date</th>
                        <th className="text-left p-3 font-medium text-gray-700">Predicted Beds</th>
                        <th className="text-left p-3 font-medium text-gray-700">Bed Stress</th>
                        <th className="text-left p-3 font-medium text-gray-700">Confidence</th>
                        <th className="text-left p-3 font-medium text-gray-700">Risk Level</th>
                      </tr>
                    </thead>
                    <tbody>
                      {dashboardData.seven_day_forecast.predictions.map((prediction, index) => (
                        <tr key={index} className="border-b border-gray-50 hover:bg-gray-50/50">
                          <td className="p-3 font-medium">
                            {new Date(prediction.date).toLocaleDateString()}
                          </td>
                          <td className="p-3">{prediction.predicted_beds}</td>
                          <td className="p-3">
                            <span className={getRiskColor(prediction.bed_stress, 85)}>
                              {prediction.bed_stress.toFixed(1)}%
                            </span>
                          </td>
                          <td className="p-3">{prediction.confidence.toFixed(1)}%</td>
                          <td className="p-3">
                            {prediction.is_high_risk ? (
                              <Badge variant="destructive" className="bg-red-100 text-red-700">High Risk</Badge>
                            ) : (
                              <Badge variant="secondary" className="bg-green-100 text-green-700">Normal</Badge>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="recommendations">
            <div className="space-y-4">
              {recommendations.length > 0 ? (
                recommendations.map((rec, index) => (
                  <Card key={index} className="backdrop-blur-sm bg-white/95 border border-gray-100 shadow-xl rounded-3xl overflow-hidden group hover:shadow-2xl transition-all duration-300">
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center">
                            <Brain className="h-5 w-5 text-indigo-600" />
                          </div>
                          <CardTitle className="text-lg">
                            {rec.priority}. {rec.title}
                          </CardTitle>
                        </div>
                        <Badge variant="outline" className="border-indigo-200 text-indigo-700">
                          Priority {rec.priority}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-700 mb-6 leading-relaxed">{rec.description}</p>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-4">
                        <div className="text-center p-4 bg-blue-50 rounded-xl">
                          <div className="text-2xl font-bold text-blue-600 mb-1">
                            {rec.impact_score.toFixed(0)}/100
                          </div>
                          <div className="text-sm text-blue-700 font-medium">Impact Score</div>
                        </div>
                        <div className="text-center p-4 bg-green-50 rounded-xl">
                          <div className="text-2xl font-bold text-green-600 mb-1">
                            ${rec.cost_estimate.toLocaleString()}
                          </div>
                          <div className="text-sm text-green-700 font-medium">Cost Estimate</div>
                        </div>
                        <div className="text-center p-4 bg-purple-50 rounded-xl">
                          <div className="text-2xl font-bold text-purple-600 mb-1">
                            {rec.implementation_time}
                          </div>
                          <div className="text-sm text-purple-700 font-medium">Implementation</div>
                        </div>
                      </div>
                      <details className="group">
                        <summary className="cursor-pointer text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">
                          View Clinical Rationale
                        </summary>
                        <div className="mt-3 p-4 bg-gray-50 rounded-xl border border-gray-100">
                          <p className="text-sm text-gray-700 leading-relaxed">{rec.rationale}</p>
                        </div>
                      </details>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <Card className="backdrop-blur-sm bg-white/95 border border-gray-100 shadow-xl rounded-3xl">
                  <CardContent className="text-center py-12">
                    <div className="w-16 h-16 bg-green-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                      <Lightbulb className="h-8 w-8 text-green-600" />
                    </div>
                    <h3 className="text-lg font-semibold mb-2 text-gray-900">All Systems Normal</h3>
                    <p className="text-gray-600">
                      Current stress levels are within acceptable ranges. No immediate action required.
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          <TabsContent value="analytics">
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="backdrop-blur-sm bg-white/95 border border-gray-100 shadow-xl rounded-3xl">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center">
                      <Activity className="h-5 w-5 text-purple-600" />
                    </div>
                    <CardTitle>System Performance</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Prediction Accuracy</span>
                      <span className="font-semibold text-purple-600">94.2%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Data Quality Score</span>
                      <span className="font-semibold text-purple-600">98.7%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Alert Response Time</span>
                      <span className="font-semibold text-purple-600">&lt;2 min</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="backdrop-blur-sm bg-white/95 border border-gray-100 shadow-xl rounded-3xl">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-orange-100 rounded-xl flex items-center justify-center">
                      <Zap className="h-5 w-5 text-orange-600" />
                    </div>
                    <CardTitle>Quick Actions</CardTitle>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button 
                    variant="outline" 
                    className="w-full justify-start rounded-xl"
                    onClick={() => window.location.href = '/(authenticated)/simulator'}
                  >
                    <TestTube className="h-4 w-4 mr-2" />
                    Run Scenario Simulation
                  </Button>
                  <Button 
                    variant="outline" 
                    className="w-full justify-start rounded-xl"
                    onClick={() => window.location.href = '/(authenticated)/upload'}
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Upload New Data
                  </Button>
                  <Button 
                    variant="outline" 
                    className="w-full justify-start rounded-xl"
                    onClick={() => window.location.href = '/(authenticated)/chat'}
                  >
                    <Brain className="h-4 w-4 mr-2" />
                    Ask AI Assistant
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="insights">
            <Card className="backdrop-blur-sm bg-white/95 border border-gray-100 shadow-xl rounded-3xl">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-teal-100 rounded-xl flex items-center justify-center">
                    <Heart className="h-5 w-5 text-teal-600" />
                  </div>
                  <div>
                    <CardTitle>Clinical Insights & Patterns</CardTitle>
                    <CardDescription>AI-powered analysis of hospital operations</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="p-4 bg-blue-50 rounded-xl border border-blue-100">
                    <h4 className="font-semibold text-blue-900 mb-2">Capacity Trends</h4>
                    <p className="text-blue-800 text-sm leading-relaxed">
                      Peak occupancy typically occurs on Tuesdays and Wednesdays. Consider adjusting staffing schedules accordingly.
                    </p>
                  </div>
                  <div className="p-4 bg-green-50 rounded-xl border border-green-100">
                    <h4 className="font-semibold text-green-900 mb-2">Operational Efficiency</h4>
                    <p className="text-green-800 text-sm leading-relaxed">
                      Discharge planning optimization could reduce average length of stay by 0.8 days, improving bed turnover.
                    </p>
                  </div>
                  <div className="p-4 bg-purple-50 rounded-xl border border-purple-100">
                    <h4 className="font-semibold text-purple-900 mb-2">Predictive Accuracy</h4>
                    <p className="text-purple-800 text-sm leading-relaxed">
                      7-day forecasts show 94% accuracy. Historical patterns indicate seasonal variations in Q1 and Q4.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}