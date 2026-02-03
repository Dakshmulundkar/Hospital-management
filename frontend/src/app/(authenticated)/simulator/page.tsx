'use client'

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Slider } from "@/components/ui/slider"
import { Progress } from "@/components/ui/progress"
import { 
  Play, 
  RotateCcw, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Shield,
  TestTube,
  Activity,
  Users,
  Bed,
  Brain,
  Zap
} from "lucide-react"

interface ScenarioResult {
  baseline_forecast: {
    predictions: Array<{
      date: string
      predicted_beds: number
      bed_stress: number
      confidence: number
      is_high_risk: boolean
    }>
    overall_confidence: number
  }
  scenario_forecast: {
    predictions: Array<{
      date: string
      predicted_beds: number
      bed_stress: number
      confidence: number
      is_high_risk: boolean
    }>
    overall_confidence: number
  }
  baseline_staff_risk: {
    risk_score: number
    is_critical: boolean
  }
  scenario_staff_risk: {
    risk_score: number
    is_critical: boolean
  }
  impact_summary: string
}

export default function SimulatorPage() {
  const [sickRate, setSickRate] = useState([10]) // 10%
  const [admissionSurge, setAdmissionSurge] = useState([0]) // 0%
  const [scenarioResult, setScenarioResult] = useState<ScenarioResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const runSimulation = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/simulate-scenario`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sick_rate: sickRate[0] / 100, // Convert percentage to decimal
          admission_surge: admissionSurge[0] / 100, // Convert percentage to decimal
          baseline_date: new Date().toISOString()
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Simulation failed')
      }

      const result = await response.json()
      setScenarioResult(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Simulation failed')
    } finally {
      setLoading(false)
    }
  }
  const resetParameters = () => {
    setSickRate([10])
    setAdmissionSurge([0])
    setScenarioResult(null)
    setError(null)
  }

  const getImpactColor = (baseline: number, scenario: number, threshold: number) => {
    const change = scenario - baseline
    if (scenario > threshold || change > 10) return 'text-red-600'
    if (change > 5) return 'text-yellow-600'
    if (change < -5) return 'text-green-600'
    return 'text-gray-600'
  }

  const getImpactIcon = (baseline: number, scenario: number) => {
    const change = scenario - baseline
    if (change > 5) return <TrendingUp className="h-4 w-4 text-red-500" />
    if (change < -5) return <TrendingDown className="h-4 w-4 text-green-500" />
    return null
  }

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="inline-flex items-center gap-2 bg-purple-50 text-purple-700 px-3 py-1 rounded-full text-sm font-medium mb-4">
            <Shield className="w-4 h-4" />
            Scenario Planning & Analysis
          </div>
          <h1 className="text-3xl font-semibold text-gray-900 tracking-tight">
            What-If Scenario Simulator
          </h1>
          <p className="text-gray-600 mt-2">
            Interactive simulation for emergency planning and resource allocation strategies
          </p>
        </div>

        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50 rounded-2xl">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            <AlertTitle className="text-red-800 text-lg">Simulation Error</AlertTitle>
            <AlertDescription className="text-red-700 mt-2">{error}</AlertDescription>
          </Alert>
        )}

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Controls Panel */}
          <div className="lg:col-span-1">
            <Card className="backdrop-blur-sm bg-white/95 border border-gray-100 shadow-xl rounded-3xl sticky top-24">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center">
                    <TestTube className="h-5 w-5 text-purple-600" />
                  </div>
                  <div>
                    <CardTitle className="text-xl">Scenario Parameters</CardTitle>
                    <CardDescription>
                      Adjust parameters to simulate different crisis scenarios
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-8">
                {/* Staff Sick Rate */}
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <label className="text-sm font-medium text-gray-700">Staff Sick Rate</label>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-purple-700 border-purple-200">
                        {sickRate[0]}%
                      </Badge>
                    </div>
                  </div>
                  <Slider
                    value={sickRate}
                    onValueChange={setSickRate}
                    max={50}
                    min={0}
                    step={1}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-2">
                    <span>0%</span>
                    <span>50%</span>
                  </div>
                  <p className="text-xs text-gray-600 mt-2 leading-relaxed">
                    Percentage of staff unable to work due to illness or other factors
                  </p>
                </div>

                {/* Admission Surge */}
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <label className="text-sm font-medium text-gray-700">Admission Surge</label>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-blue-700 border-blue-200">
                        {admissionSurge[0] > 0 ? '+' : ''}{admissionSurge[0]}%
                      </Badge>
                    </div>
                  </div>
                  <Slider
                    value={admissionSurge}
                    onValueChange={setAdmissionSurge}
                    max={100}
                    min={-30}
                    step={5}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-2">
                    <span>-30%</span>
                    <span>+100%</span>
                  </div>
                  <p className="text-xs text-gray-600 mt-2 leading-relaxed">
                    Change in daily admissions compared to normal levels
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="space-y-3 pt-4 border-t border-gray-100">
                  <Button
                    onClick={runSimulation}
                    disabled={loading}
                    className="w-full h-12 bg-purple-600 hover:bg-purple-700 rounded-xl"
                    size="lg"
                  >
                    {loading ? (
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        <span>Running Simulation...</span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2">
                        <Play className="h-5 w-5" />
                        <span>Run Simulation</span>
                      </div>
                    )}
                  </Button>
                  
                  <Button
                    onClick={resetParameters}
                    variant="outline"
                    className="w-full rounded-xl"
                  >
                    <RotateCcw className="h-4 w-4 mr-2" />
                    Reset Parameters
                  </Button>
                </div>

                {/* Parameter Presets */}
                <div className="pt-4 border-t border-gray-100">
                  <p className="text-sm font-medium mb-3 text-gray-700">Quick Scenarios</p>
                  <div className="space-y-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start text-left h-auto py-3 px-4 rounded-xl"
                      onClick={() => {
                        setSickRate([5])
                        setAdmissionSurge([20])
                      }}
                    >
                      <div>
                        <div className="font-medium">Flu Season</div>
                        <div className="text-xs text-gray-500">5% sick, +20% admissions</div>
                      </div>
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start text-left h-auto py-3 px-4 rounded-xl"
                      onClick={() => {
                        setSickRate([15])
                        setAdmissionSurge([50])
                      }}
                    >
                      <div>
                        <div className="font-medium">Emergency Event</div>
                        <div className="text-xs text-gray-500">15% sick, +50% admissions</div>
                      </div>
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start text-left h-auto py-3 px-4 rounded-xl"
                      onClick={() => {
                        setSickRate([25])
                        setAdmissionSurge([80])
                      }}
                    >
                      <div>
                        <div className="font-medium">Crisis Scenario</div>
                        <div className="text-xs text-gray-500">25% sick, +80% admissions</div>
                      </div>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
          {/* Results Panel */}
          <div className="lg:col-span-2">
            {scenarioResult ? (
              <div className="space-y-6">
                {/* Impact Summary */}
                <Card className="backdrop-blur-sm bg-white/95 border border-gray-100 shadow-xl rounded-3xl">
                  <CardHeader>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                        <Brain className="h-5 w-5 text-blue-600" />
                      </div>
                      <CardTitle className="text-xl">AI Impact Analysis</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-2xl border border-blue-100">
                      <pre className="text-sm whitespace-pre-wrap font-medium text-gray-800 leading-relaxed">
                        {scenarioResult.impact_summary}
                      </pre>
                    </div>
                  </CardContent>
                </Card>

                {/* Comparison Metrics */}
                <div className="grid md:grid-cols-2 gap-6">
                  <Card className="backdrop-blur-sm bg-white/95 border border-gray-100 shadow-xl rounded-3xl overflow-hidden group hover:shadow-2xl transition-all duration-300">
                    <div className="absolute inset-0 bg-gradient-to-br from-red-50 to-transparent opacity-50"></div>
                    <CardHeader className="relative">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-red-100 rounded-xl flex items-center justify-center">
                          <Bed className="h-5 w-5 text-red-600" />
                        </div>
                        <CardTitle className="flex items-center space-x-2">
                          <span>Bed Stress Comparison</span>
                          {getImpactIcon(
                            scenarioResult.baseline_forecast.predictions[0]?.bed_stress || 0,
                            scenarioResult.scenario_forecast.predictions[0]?.bed_stress || 0
                          )}
                        </CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent className="relative">
                      <div className="space-y-4">
                        <div className="flex justify-between items-center p-3 bg-white/50 rounded-xl">
                          <span className="text-sm font-medium text-gray-700">Baseline</span>
                          <div className="flex items-center space-x-2">
                            <span className="font-bold text-lg">
                              {scenarioResult.baseline_forecast.predictions[0]?.bed_stress.toFixed(1) || 0}%
                            </span>
                            {(scenarioResult.baseline_forecast.predictions[0]?.bed_stress || 0) > 85 && (
                              <Badge variant="destructive" className="text-xs">High Risk</Badge>
                            )}
                          </div>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-white/50 rounded-xl">
                          <span className="text-sm font-medium text-gray-700">Scenario</span>
                          <div className="flex items-center space-x-2">
                            <span className={`font-bold text-lg ${getImpactColor(
                              scenarioResult.baseline_forecast.predictions[0]?.bed_stress || 0,
                              scenarioResult.scenario_forecast.predictions[0]?.bed_stress || 0,
                              85
                            )}`}>
                              {scenarioResult.scenario_forecast.predictions[0]?.bed_stress.toFixed(1) || 0}%
                            </span>
                            {(scenarioResult.scenario_forecast.predictions[0]?.bed_stress || 0) > 85 && (
                              <Badge variant="destructive" className="text-xs">High Risk</Badge>
                            )}
                          </div>
                        </div>
                        <div className="pt-3 border-t border-gray-200">
                          <div className="flex justify-between items-center">
                            <span className="text-sm font-medium text-gray-700">Impact</span>
                            <span className={`font-bold text-xl ${getImpactColor(
                              scenarioResult.baseline_forecast.predictions[0]?.bed_stress || 0,
                              scenarioResult.scenario_forecast.predictions[0]?.bed_stress || 0,
                              85
                            )}`}>
                              {((scenarioResult.scenario_forecast.predictions[0]?.bed_stress || 0) - 
                                (scenarioResult.baseline_forecast.predictions[0]?.bed_stress || 0)) > 0 ? '+' : ''}
                              {((scenarioResult.scenario_forecast.predictions[0]?.bed_stress || 0) - 
                                (scenarioResult.baseline_forecast.predictions[0]?.bed_stress || 0)).toFixed(1)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="backdrop-blur-sm bg-white/95 border border-gray-100 shadow-xl rounded-3xl overflow-hidden group hover:shadow-2xl transition-all duration-300">
                    <div className="absolute inset-0 bg-gradient-to-br from-green-50 to-transparent opacity-50"></div>
                    <CardHeader className="relative">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center">
                          <Users className="h-5 w-5 text-green-600" />
                        </div>
                        <CardTitle className="flex items-center space-x-2">
                          <span>Staff Risk Comparison</span>
                          {getImpactIcon(
                            scenarioResult.baseline_staff_risk.risk_score,
                            scenarioResult.scenario_staff_risk.risk_score
                          )}
                        </CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent className="relative">
                      <div className="space-y-4">
                        <div className="flex justify-between items-center p-3 bg-white/50 rounded-xl">
                          <span className="text-sm font-medium text-gray-700">Baseline</span>
                          <div className="flex items-center space-x-2">
                            <span className="font-bold text-lg">
                              {scenarioResult.baseline_staff_risk.risk_score.toFixed(1)}
                            </span>
                            {scenarioResult.baseline_staff_risk.is_critical && (
                              <Badge variant="destructive" className="text-xs">Critical</Badge>
                            )}
                          </div>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-white/50 rounded-xl">
                          <span className="text-sm font-medium text-gray-700">Scenario</span>
                          <div className="flex items-center space-x-2">
                            <span className={`font-bold text-lg ${getImpactColor(
                              scenarioResult.baseline_staff_risk.risk_score,
                              scenarioResult.scenario_staff_risk.risk_score,
                              75
                            )}`}>
                              {scenarioResult.scenario_staff_risk.risk_score.toFixed(1)}
                            </span>
                            {scenarioResult.scenario_staff_risk.is_critical && (
                              <Badge variant="destructive" className="text-xs">Critical</Badge>
                            )}
                          </div>
                        </div>
                        <div className="pt-3 border-t border-gray-200">
                          <div className="flex justify-between items-center">
                            <span className="text-sm font-medium text-gray-700">Impact</span>
                            <span className={`font-bold text-xl ${getImpactColor(
                              scenarioResult.baseline_staff_risk.risk_score,
                              scenarioResult.scenario_staff_risk.risk_score,
                              75
                            )}`}>
                              {(scenarioResult.scenario_staff_risk.risk_score - 
                                scenarioResult.baseline_staff_risk.risk_score) > 0 ? '+' : ''}
                              {(scenarioResult.scenario_staff_risk.risk_score - 
                                scenarioResult.baseline_staff_risk.risk_score).toFixed(1)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
                {/* Detailed Forecast Comparison */}
                <Card className="backdrop-blur-sm bg-white/95 border border-gray-100 shadow-xl rounded-3xl">
                  <CardHeader>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center">
                        <Activity className="h-5 w-5 text-indigo-600" />
                      </div>
                      <CardTitle className="text-xl">7-Day Forecast Comparison</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b border-gray-100">
                            <th className="text-left p-3 font-medium text-gray-700">Date</th>
                            <th className="text-left p-3 font-medium text-gray-700">Baseline Beds</th>
                            <th className="text-left p-3 font-medium text-gray-700">Scenario Beds</th>
                            <th className="text-left p-3 font-medium text-gray-700">Baseline Stress</th>
                            <th className="text-left p-3 font-medium text-gray-700">Scenario Stress</th>
                            <th className="text-left p-3 font-medium text-gray-700">Impact</th>
                          </tr>
                        </thead>
                        <tbody>
                          {scenarioResult.baseline_forecast.predictions.map((baseline, index) => {
                            const scenario = scenarioResult.scenario_forecast.predictions[index]
                            const stressChange = scenario.bed_stress - baseline.bed_stress
                            return (
                              <tr key={index} className="border-b border-gray-50 hover:bg-gray-50/50">
                                <td className="p-3 font-medium">
                                  {new Date(baseline.date).toLocaleDateString()}
                                </td>
                                <td className="p-3">{baseline.predicted_beds}</td>
                                <td className="p-3">{scenario.predicted_beds}</td>
                                <td className="p-3">{baseline.bed_stress.toFixed(1)}%</td>
                                <td className="p-3">
                                  <span className={getImpactColor(baseline.bed_stress, scenario.bed_stress, 85)}>
                                    {scenario.bed_stress.toFixed(1)}%
                                  </span>
                                </td>
                                <td className="p-3">
                                  <span className={getImpactColor(baseline.bed_stress, scenario.bed_stress, 85)}>
                                    {stressChange > 0 ? '+' : ''}{stressChange.toFixed(1)}%
                                  </span>
                                </td>
                              </tr>
                            )
                          })}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : (
              <Card className="backdrop-blur-sm bg-white/95 border border-gray-100 shadow-xl rounded-3xl">
                <CardContent className="text-center py-16">
                  <div className="w-20 h-20 bg-purple-100 rounded-3xl flex items-center justify-center mx-auto mb-6">
                    <Play className="h-10 w-10 text-purple-600" />
                  </div>
                  <h3 className="text-xl font-semibold mb-3 text-gray-900">Ready to Simulate</h3>
                  <p className="text-gray-600 mb-6 max-w-md mx-auto leading-relaxed">
                    Adjust the scenario parameters in the control panel and click "Run Simulation" 
                    to see the impact on hospital operations.
                  </p>
                  <div className="grid grid-cols-2 gap-4 max-w-sm mx-auto">
                    <div className="p-4 bg-blue-50 rounded-xl">
                      <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                        <Zap className="h-4 w-4 text-blue-600" />
                      </div>
                      <div className="text-sm font-medium text-blue-900">Real-time</div>
                      <div className="text-xs text-blue-700">Analysis</div>
                    </div>
                    <div className="p-4 bg-green-50 rounded-xl">
                      <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                        <Activity className="h-4 w-4 text-green-600" />
                      </div>
                      <div className="text-sm font-medium text-green-900">Predictive</div>
                      <div className="text-xs text-green-700">Modeling</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}