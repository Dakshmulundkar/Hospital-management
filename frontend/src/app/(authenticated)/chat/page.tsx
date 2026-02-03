'use client'

import { useState, useRef, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { 
  Send, 
  MessageCircle, 
  Bot, 
  User, 
  Loader2, 
  Shield,
  Brain,
  Activity,
  Lightbulb,
  BarChart3,
  Heart
} from "lucide-react"

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Add welcome message
    if (messages.length === 0) {
      setMessages([{
        id: '1',
        role: 'assistant',
        content: `Hello! I'm your Hospital Stress AI Assistant. I can help you with:

• Current bed stress and staff risk levels
• 7-day forecasts and predictions  
• Recommendations for high-risk situations
• Historical data analysis and trends
• What-if scenario planning
• Clinical insights and operational guidance

What would you like to know about your hospital's capacity?`,
        timestamp: new Date()
      }])
    }
  }, [messages.length])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      // For now, we'll simulate AI responses since we don't have a chat endpoint
      const response = await simulateAIResponse(input.trim())
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your request. Please try again or contact support if the issue persists.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }
  const simulateAIResponse = async (query: string): Promise<string> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))

    const lowerQuery = query.toLowerCase()

    // Simulate different types of responses based on query content
    if (lowerQuery.includes('bed stress') || lowerQuery.includes('bed') || lowerQuery.includes('occupancy')) {
      return `Based on current data analysis:

🛏️ **Current Bed Stress: 72.3%**
- This is within normal operating range (below 85% threshold)
- Trending stable over the past 3 days
- Peak stress typically occurs on Tuesdays and Wednesdays

📈 **7-Day Forecast:**
- Expected to remain between 68-78%
- No high-risk days predicted
- Confidence level: 87%

Would you like me to run a what-if scenario or provide specific recommendations?`
    }

    if (lowerQuery.includes('staff') || lowerQuery.includes('risk') || lowerQuery.includes('overload')) {
      return `Here's your current staff risk assessment:

👥 **Staff Risk Score: 45.2**
- Classification: Normal (below 75 critical threshold)
- Current staff-to-patient ratio: 1:3.2
- No overload events in past 14 days

⚠️ **Risk Factors:**
- Flu season approaching (historical +15% sick rate)
- Weekend coverage typically 20% lower
- Recent overtime hours: 12% above average

💡 **Recommendations:**
1. Consider cross-training additional staff
2. Review weekend scheduling protocols
3. Monitor sick leave trends closely

Need more details on any specific aspect?`
    }

    if (lowerQuery.includes('recommendation') || lowerQuery.includes('suggest') || lowerQuery.includes('action')) {
      return `Based on current hospital conditions, here are my top recommendations:

🎯 **Priority Actions:**

**1. Optimize Discharge Planning** (Impact: 85/100)
- Implement early morning discharge rounds
- Coordinate with post-acute care facilities
- Estimated cost: $5,000 | Timeline: 2 days

**2. Staff Schedule Optimization** (Impact: 70/100)
- Adjust shifts to match admission patterns
- Reduce peak-hour bottlenecks
- Estimated cost: $2,000 | Timeline: 1 week

**3. Bed Management Protocol** (Impact: 65/100)
- Streamline bed turnover process
- Implement real-time bed tracking
- Estimated cost: $15,000 | Timeline: 2 weeks

Would you like detailed implementation steps for any of these recommendations?`
    }

    if (lowerQuery.includes('forecast') || lowerQuery.includes('predict') || lowerQuery.includes('future')) {
      return `📊 **7-Day Hospital Forecast:**

**Tomorrow (Day 1):**
- Predicted beds: 245 (73% stress)
- Staff risk: 42
- Status: Normal ✅

**Day 2-3:**
- Slight increase expected (75-77% stress)
- Tuesday typically sees +8% admissions
- Recommend monitoring closely

**Day 4-7:**
- Gradual decline to 70% stress
- Weekend pattern: -15% admissions
- Confidence: 89%

🔍 **Key Insights:**
- No high-risk days predicted
- Seasonal flu impact minimal so far
- Historical accuracy: 91% for 7-day forecasts

Want me to run a specific scenario or explain the methodology?`
    }

    if (lowerQuery.includes('what if') || lowerQuery.includes('scenario') || lowerQuery.includes('simulate')) {
      return `🎮 **Scenario Simulation Available**

I can help you explore various "what-if" scenarios:

**Common Scenarios:**
- Staff sick rates (5-25%)
- Admission surges (emergency events)
- Seasonal variations (flu, holidays)
- Equipment failures or bed closures

**Example Questions:**
- "What if 15% of staff get sick?"
- "How would a 50% admission surge affect us?"
- "What's our capacity during flu season?"

To run a simulation, either:
1. Visit the Simulator page for interactive controls
2. Tell me specific parameters (e.g., "simulate 20% staff sick rate with 30% more admissions")

What scenario would you like to explore?`
    }

    if (lowerQuery.includes('alert') || lowerQuery.includes('threshold') || lowerQuery.includes('notification')) {
      return `🚨 **Alert System Status:**

**Current Thresholds:**
- Bed Stress: 85% (High Risk)
- Staff Risk: 75 (Critical)

**Alert Channels:**
- Email: ✅ Configured
- Slack: ✅ Active (#hospital-alerts)

**Recent Activity:**
- Last alert: 3 days ago (brief staff risk spike)
- Total alerts this month: 2
- Average response time: 12 minutes

**Alert Configuration:**
- Automatic notifications enabled
- Escalation after 30 minutes
- Include top 3 recommendations

Would you like to:
- Adjust threshold levels?
- Test alert delivery?
- Review alert history?`
    }

    // Default response for general queries
    return `I understand you're asking about "${query}". 

I can help you with various aspects of hospital capacity management:

🏥 **Available Information:**
- Real-time bed stress and staff risk levels
- 7-day forecasts and predictions
- Historical data analysis and trends
- Actionable recommendations
- What-if scenario planning
- Alert configuration and history

📋 **Try asking:**
- "What's our current bed stress level?"
- "Show me the 7-day forecast"
- "What recommendations do you have?"
- "What if 20% of staff get sick?"
- "How are our alert thresholds configured?"

How can I assist you with your hospital's capacity planning?`
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }
  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="inline-flex items-center gap-2 bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full text-sm font-medium mb-4">
            <Shield className="w-4 h-4" />
            AI-Powered Healthcare Assistant
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-semibold text-gray-900 tracking-tight">
                AI Assistant
              </h1>
              <p className="text-gray-600">
                Ask questions about hospital capacity, forecasts, and recommendations
              </p>
            </div>
          </div>
        </div>

        {/* Chat Container */}
        <Card className="backdrop-blur-sm bg-white/95 border border-gray-100 shadow-2xl rounded-3xl overflow-hidden h-[600px] flex flex-col">
          <CardHeader className="border-b border-gray-100 bg-gradient-to-r from-indigo-50 to-purple-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center">
                  <Bot className="h-5 w-5 text-indigo-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Hospital Stress AI</CardTitle>
                  <CardDescription>Natural language interface for healthcare analytics</CardDescription>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1">
                  <Activity className="h-3 w-3 text-green-500" />
                  <span className="text-xs text-gray-600">Online</span>
                </div>
                <Badge variant="secondary" className="bg-green-100 text-green-700 border-green-200">
                  Ready
                </Badge>
              </div>
            </div>
          </CardHeader>

          {/* Messages */}
          <CardContent className="flex-1 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-white to-gray-50/50">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl p-4 ${
                    message.role === 'user'
                      ? 'bg-gradient-to-br from-indigo-600 to-purple-600 text-white shadow-lg'
                      : 'bg-white border border-gray-100 text-gray-900 shadow-md'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
                      message.role === 'user' 
                        ? 'bg-white/20' 
                        : 'bg-indigo-100'
                    }`}>
                      {message.role === 'assistant' ? (
                        <Bot className="h-4 w-4 text-indigo-600" />
                      ) : (
                        <User className="h-4 w-4 text-white" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="whitespace-pre-wrap text-sm leading-relaxed">
                        {message.content}
                      </div>
                      <div className={`text-xs mt-2 ${
                        message.role === 'user' ? 'text-indigo-100' : 'text-gray-500'
                      }`}>
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-100 rounded-2xl p-4 max-w-[80%] shadow-md">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-indigo-100 rounded-xl flex items-center justify-center">
                      <Bot className="h-4 w-4 text-indigo-600" />
                    </div>
                    <div className="flex items-center space-x-2">
                      <Loader2 className="h-4 w-4 animate-spin text-indigo-600" />
                      <span className="text-sm text-gray-600">Analyzing your request...</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </CardContent>

          {/* Input */}
          <div className="border-t border-gray-100 p-4 bg-white">
            <div className="flex space-x-3">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about bed stress, forecasts, recommendations..."
                className="flex-1 rounded-xl border-gray-200 focus:border-indigo-300 focus:ring-indigo-200"
                disabled={loading}
              />
              <Button
                onClick={sendMessage}
                disabled={!input.trim() || loading}
                size="icon"
                className="rounded-xl bg-indigo-600 hover:bg-indigo-700 shrink-0"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-xs text-gray-500 mt-2 text-center">
              Press Enter to send, Shift+Enter for new line
            </p>
          </div>
        </Card>

        {/* Quick Actions */}
        <div className="mt-6">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Quick Questions</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {[
              { icon: BarChart3, text: "What's our current bed stress?", color: "blue" },
              { icon: Activity, text: "Show me the 7-day forecast", color: "green" },
              { icon: Lightbulb, text: "What recommendations do you have?", color: "yellow" },
              { icon: Heart, text: "What if 15% of staff get sick?", color: "red" },
              { icon: MessageCircle, text: "How are alerts configured?", color: "purple" },
              { icon: Brain, text: "Explain the prediction methodology", color: "indigo" }
            ].map((question, index) => {
              const Icon = question.icon
              return (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  className="justify-start text-left h-auto py-3 px-4 rounded-xl border-gray-200 hover:bg-gray-50"
                  onClick={() => setInput(question.text)}
                  disabled={loading}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center bg-${question.color}-100`}>
                      <Icon className={`h-4 w-4 text-${question.color}-600`} />
                    </div>
                    <span className="text-sm">{question.text}</span>
                  </div>
                </Button>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}