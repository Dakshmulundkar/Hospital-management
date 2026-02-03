// Hospital data types for the frontend application

export interface HospitalRecord {
  date: string
  admissions: number
  beds_occupied: number
  staff_on_duty: number
  overload_flag: boolean
}

export interface DailyPrediction {
  date: string
  predicted_beds: number
  bed_stress: number
  confidence: number
  is_high_risk: boolean
}

export interface BedForecast {
  predictions: DailyPrediction[]
  overall_confidence: number
  generated_at: string
}

export interface StaffRiskScore {
  risk_score: number
  confidence: number
  is_critical: boolean
  contributing_factors: string[]
  generated_at: string
}

export interface Recommendation {
  title: string
  description: string
  rationale: string
  cost_estimate: number
  impact_score: number
  priority: number
  implementation_time: string
}

export interface AlertData {
  alert_type: 'bed_stress' | 'staff_risk'
  risk_score: number
  threshold: number
  predictions: DailyPrediction[]
  recommendations: Recommendation[]
  generated_at: string
}

export interface ScenarioRequest {
  sick_rate: number // 0.0 to 0.5
  admission_surge: number // -0.3 to 1.0
  baseline_date: string
}

export interface ScenarioResult {
  baseline_forecast: BedForecast
  scenario_forecast: BedForecast
  baseline_staff_risk: StaffRiskScore
  scenario_staff_risk: StaffRiskScore
  impact_summary: string
}

export interface DashboardData {
  bed_stress_current: number
  staff_risk_current: number
  active_alerts_count: number
  recommendations_count: number
  seven_day_forecast: BedForecast
  seven_day_staff_risk: StaffRiskScore[]
  trend_indicators: {
    bed_stress?: 'up' | 'down' | 'stable'
    staff_risk?: 'up' | 'down' | 'stable'
  }
}

export interface UploadResponse {
  status: string
  record_count: number
  warnings: string[]
  message: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export interface ApiError {
  error: string
  detail: string
  timestamp: string
}

// API Request types
export interface PredictRequest {
  days_ahead?: number
  use_cache?: boolean
}

export interface StaffRiskRequest {
  predicted_admissions: number
  current_staff: number
  use_cache?: boolean
}

export interface RecommendationRequest {
  bed_stress: number
  staff_risk: number
  include_historical?: boolean
}

export interface AlertRequest {
  alert_type: 'bed_stress' | 'staff_risk'
  risk_score: number
  threshold: number
  recipients: string[]
  send_slack?: boolean
}

export interface AlertResponse {
  status: string
  email_sent: boolean
  slack_sent: boolean
  message: string
}

// Utility types
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'
export type TrendDirection = 'up' | 'down' | 'stable'

export interface ValidationResult {
  is_valid: boolean
  errors: string[]
  warnings: string[]
}

// Onboarding types
export interface OnboardingStep {
  id: number
  title: string
  description: string
  completed: boolean
}

export interface OnboardingProgress {
  currentStep: number
  completedSteps: number[]
  csvUploaded: boolean
  bedStressThreshold: number
  staffRiskThreshold: number
  emailAlerts: string
  slackWebhook: string
  testCompleted: boolean
}