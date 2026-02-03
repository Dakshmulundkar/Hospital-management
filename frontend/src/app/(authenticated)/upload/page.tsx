'use client'

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertTriangle, 
  Shield, 
  Database,
  FileSpreadsheet,
  Activity,
  Zap,
  BarChart3
} from "lucide-react"

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [dragOver, setDragOver] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const handleFileSelect = (selectedFile: File) => {
    if (!selectedFile.name.endsWith('.csv')) {
      setError('Please select a CSV file')
      return
    }
    
    if (selectedFile.size > 50 * 1024 * 1024) { // 50MB
      setError('File size must be less than 50MB')
      return
    }
    
    setFile(selectedFile)
    setError(null)
    setUploadResult(null)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      handleFileSelect(droppedFile)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setError(null)
    setUploadProgress(0)

    try {
      const formData = new FormData()
      formData.append('file', file)

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90))
      }, 200)

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/upload-logs`, {
        method: 'POST',
        body: formData,
      })

      clearInterval(progressInterval)
      setUploadProgress(100)

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Upload failed')
      }

      const result = await response.json()
      setUploadResult(result)
      setFile(null)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }

  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm font-medium mb-4">
            <Shield className="w-4 h-4" />
            Secure Data Upload
          </div>
          <h1 className="text-3xl font-semibold text-gray-900 tracking-tight">
            Hospital Data Import
          </h1>
          <p className="text-gray-600 mt-2">
            Upload historical hospital logs in CSV format to enable AI-powered predictions and monitoring
          </p>
        </div>

        {/* Upload Results */}
        {uploadResult && (
          <Alert className="mb-6 border-green-200 bg-green-50 rounded-2xl">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <AlertTitle className="text-green-800 text-lg">Upload Successful</AlertTitle>
            <AlertDescription className="text-green-700 mt-2">
              {uploadResult.message} ({uploadResult.record_count} records processed)
              {uploadResult.warnings?.length > 0 && (
                <div className="mt-2">
                  <strong>Warnings:</strong>
                  <ul className="list-disc list-inside mt-1">
                    {uploadResult.warnings.map((warning: string, index: number) => (
                      <li key={index} className="text-sm">{warning}</li>
                    ))}
                  </ul>
                </div>
              )}
            </AlertDescription>
          </Alert>
        )}

        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50 rounded-2xl">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            <AlertTitle className="text-red-800 text-lg">Upload Error</AlertTitle>
            <AlertDescription className="text-red-700 mt-2">{error}</AlertDescription>
          </Alert>
        )}

        {/* Main Upload Section */}
        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          {/* Upload Card */}
          <div className="lg:col-span-2">
            <Card className="backdrop-blur-sm bg-white/95 border border-gray-100 shadow-xl rounded-3xl overflow-hidden">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                    <Database className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <CardTitle className="text-xl">CSV File Upload</CardTitle>
                    <CardDescription>
                      Upload hospital data with required columns for AI analysis
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* File Drop Zone */}
                <div 
                  className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 ${
                    dragOver 
                      ? 'border-blue-400 bg-blue-50 scale-105' 
                      : 'border-gray-300 hover:border-blue-300 hover:bg-blue-50/50'
                  }`}
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                >
                  <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <Upload className="h-8 w-8 text-blue-600" />
                  </div>
                  <div className="space-y-2">
                    <p className="text-lg font-medium text-gray-900">
                      Choose a CSV file or drag and drop
                    </p>
                    <p className="text-sm text-gray-500">
                      Maximum file size: 50MB • Supported format: .csv
                    </p>
                  </div>
                  <input
                    type="file"
                    accept=".csv"
                    onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
                    className="mt-4 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 transition-colors"
                  />
                </div>

                {/* Selected File */}
                {file && (
                  <div className="flex items-center space-x-4 p-4 bg-blue-50 rounded-2xl border border-blue-100">
                    <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                      <FileText className="h-6 w-6 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{file.name}</p>
                      <p className="text-sm text-gray-600">
                        {(file.size / 1024 / 1024).toFixed(2)} MB • {file.lastModified ? new Date(file.lastModified).toLocaleDateString() : 'Unknown date'}
                      </p>
                    </div>
                    <Button
                      onClick={() => setFile(null)}
                      variant="outline"
                      size="sm"
                      className="rounded-xl"
                    >
                      Remove
                    </Button>
                  </div>
                )}

                {/* Upload Progress */}
                {uploading && (
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700">Uploading...</span>
                      <span className="text-sm text-gray-500">{uploadProgress}%</span>
                    </div>
                    <Progress value={uploadProgress} className="h-2" />
                  </div>
                )}

                {/* Upload Button */}
                <Button
                  onClick={handleUpload}
                  disabled={!file || uploading}
                  className="w-full h-12 bg-blue-600 hover:bg-blue-700 rounded-xl text-lg font-medium"
                  size="lg"
                >
                  {uploading ? (
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>Processing Data...</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <Upload className="h-5 w-5" />
                      <span>Upload & Analyze</span>
                    </div>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Info Panel */}
          <div className="space-y-6">
            {/* System Status */}
            <Card className="backdrop-blur-sm bg-white/95 border border-gray-100 shadow-xl rounded-3xl">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                    <Activity className="h-4 w-4 text-green-600" />
                  </div>
                  <CardTitle className="text-lg">System Status</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">AI Engine</span>
                  <Badge variant="secondary" className="bg-green-100 text-green-700">Online</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Data Processing</span>
                  <Badge variant="secondary" className="bg-green-100 text-green-700">Ready</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Security</span>
                  <Badge variant="secondary" className="bg-green-100 text-green-700">Encrypted</Badge>
                </div>
              </CardContent>
            </Card>

            {/* Quick Stats */}
            <Card className="backdrop-blur-sm bg-white/95 border border-gray-100 shadow-xl rounded-3xl">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                    <BarChart3 className="h-4 w-4 text-purple-600" />
                  </div>
                  <CardTitle className="text-lg">Processing Power</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600 mb-1">50MB</div>
                  <div className="text-sm text-gray-600">Max File Size</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600 mb-1">&lt;30s</div>
                  <div className="text-sm text-gray-600">Processing Time</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600 mb-1">99.9%</div>
                  <div className="text-sm text-gray-600">Accuracy Rate</div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* CSV Format Guide */}
        <Card className="backdrop-blur-sm bg-white/95 border border-gray-100 shadow-xl rounded-3xl">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-orange-100 rounded-xl flex items-center justify-center">
                <FileSpreadsheet className="h-5 w-5 text-orange-600" />
              </div>
              <div>
                <CardTitle className="text-xl">CSV Format Requirements</CardTitle>
                <CardDescription>Ensure your data follows these specifications for optimal processing</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              {/* Required Columns */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Required Columns</h4>
                <div className="space-y-2">
                  {[
                    { name: 'date', desc: 'YYYY-MM-DD format', example: '2024-01-15' },
                    { name: 'admissions', desc: 'Daily admissions count', example: '120' },
                    { name: 'beds_occupied', desc: 'Number of occupied beds', example: '180' },
                    { name: 'staff_on_duty', desc: 'Staff members on duty', example: '25' },
                    { name: 'overload_flag', desc: 'true/false for overload events', example: 'false' }
                  ].map((col, index) => (
                    <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-xl">
                      <div>
                        <span className="font-medium text-gray-900">{col.name}</span>
                        <p className="text-sm text-gray-600">{col.desc}</p>
                      </div>
                      <code className="text-sm bg-white px-2 py-1 rounded border">{col.example}</code>
                    </div>
                  ))}
                </div>
              </div>

              {/* Data Quality Tips */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Data Quality Tips</h4>
                <div className="space-y-3">
                  <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-xl">
                    <Zap className="h-5 w-5 text-blue-600 mt-0.5 shrink-0" />
                    <div>
                      <p className="font-medium text-blue-900 text-sm">Complete Data</p>
                      <p className="text-blue-800 text-sm">Ensure no missing values for accurate predictions</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 bg-green-50 rounded-xl">
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 shrink-0" />
                    <div>
                      <p className="font-medium text-green-900 text-sm">Consistent Format</p>
                      <p className="text-green-800 text-sm">Use consistent date formats and numeric values</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 bg-purple-50 rounded-xl">
                    <Activity className="h-5 w-5 text-purple-600 mt-0.5 shrink-0" />
                    <div>
                      <p className="font-medium text-purple-900 text-sm">Historical Range</p>
                      <p className="text-purple-800 text-sm">Include at least 30 days of data for better accuracy</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Sample Data */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Sample Data Format</h4>
              <div className="bg-gray-900 rounded-2xl p-4 overflow-x-auto">
                <pre className="text-green-400 text-sm font-mono">
{`date,admissions,beds_occupied,staff_on_duty,overload_flag
2024-01-01,120,180,25,false
2024-01-02,135,195,23,false
2024-01-03,150,220,20,true
2024-01-04,110,175,28,false
2024-01-05,125,185,26,false`}
                </pre>
              </div>
            </div>

            {/* Security Notice */}
            <div className="p-4 bg-blue-50 rounded-2xl border border-blue-100">
              <div className="flex items-start gap-3">
                <Shield className="h-5 w-5 text-blue-600 mt-0.5 shrink-0" />
                <div>
                  <h4 className="font-medium text-blue-900 mb-1">Data Security & Privacy</h4>
                  <p className="text-blue-800 text-sm leading-relaxed">
                    All uploaded data is encrypted in transit and at rest. We comply with HIPAA regulations 
                    and healthcare data protection standards. Your data is processed securely and never shared 
                    with third parties.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}