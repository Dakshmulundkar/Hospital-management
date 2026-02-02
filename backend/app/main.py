"""FastAPI application entry point"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from typing import List

from app.services.synthetic_data_generator import SyntheticDataGenerator
from app.services.prediction_engine import PredictionEngine
from app.services.alert_service import AlertService, AlertThresholds
from app.models import HospitalRecord

app = FastAPI(
    title="Hospital Stress Early Warning System",
    description="AI-powered hospital capacity prediction and alerting system",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global data storage (in-memory for demo)
hospital_data: List[HospitalRecord] = []

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main dashboard HTML"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hospital Stress Early Warning System</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            .header {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                margin-bottom: 30px;
                text-align: center;
            }
            .header h1 {
                color: #667eea;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .header p {
                color: #666;
                font-size: 1.1em;
            }
            .status-badge {
                display: inline-block;
                padding: 8px 20px;
                background: #10b981;
                color: white;
                border-radius: 20px;
                font-weight: bold;
                margin-top: 10px;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .card {
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .card h2 {
                color: #667eea;
                margin-bottom: 15px;
                font-size: 1.5em;
            }
            .metric {
                font-size: 3em;
                font-weight: bold;
                color: #764ba2;
                margin: 10px 0;
            }
            .metric-label {
                color: #666;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 10px;
                font-size: 1.1em;
                cursor: pointer;
                transition: transform 0.2s;
                width: 100%;
                margin-top: 10px;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            }
            .btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            .forecast-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }
            .forecast-table th {
                background: #f3f4f6;
                padding: 12px;
                text-align: left;
                font-weight: 600;
                color: #374151;
            }
            .forecast-table td {
                padding: 12px;
                border-bottom: 1px solid #e5e7eb;
            }
            .risk-normal { color: #10b981; font-weight: bold; }
            .risk-high { color: #ef4444; font-weight: bold; }
            .loading {
                text-align: center;
                padding: 20px;
                color: #666;
            }
            .recommendation {
                background: #f9fafb;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 15px;
                border-left: 4px solid #667eea;
            }
            .recommendation h3 {
                color: #374151;
                margin-bottom: 8px;
            }
            .recommendation p {
                color: #6b7280;
                margin-bottom: 5px;
            }
            .recommendation .meta {
                display: flex;
                gap: 15px;
                margin-top: 10px;
                font-size: 0.9em;
            }
            .recommendation .meta span {
                background: white;
                padding: 5px 10px;
                border-radius: 5px;
                color: #667eea;
                font-weight: 600;
            }
            .alert-box {
                background: #fef2f2;
                border: 2px solid #ef4444;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
            }
            .alert-box h3 {
                color: #dc2626;
                margin-bottom: 10px;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            .loading-spinner {
                animation: pulse 1.5s ease-in-out infinite;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 Hospital Stress Early Warning System</h1>
                <p>AI-Powered Hospital Capacity Prediction & Alerting</p>
                <span class="status-badge" id="status">● OPERATIONAL</span>
            </div>

            <div class="grid">
                <div class="card">
                    <h2>📊 Data Management</h2>
                    <p class="metric-label">Hospital Records</p>
                    <div class="metric" id="recordCount">0</div>
                    <button class="btn" onclick="generateData()">Generate Sample Data</button>
                </div>

                <div class="card">
                    <h2>🛏️ Bed Stress</h2>
                    <p class="metric-label">Current Level</p>
                    <div class="metric" id="bedStress">--</div>
                    <p class="metric-label">Status: <span id="bedStatus">Awaiting Data</span></p>
                </div>

                <div class="card">
                    <h2>👥 Staff Risk</h2>
                    <p class="metric-label">Risk Score</p>
                    <div class="metric" id="staffRisk">--</div>
                    <p class="metric-label">Status: <span id="staffStatus">Awaiting Data</span></p>
                </div>
            </div>

            <div id="alertContainer"></div>

            <div class="card">
                <h2>📈 7-Day Bed Demand Forecast</h2>
                <button class="btn" onclick="generateForecast()" id="forecastBtn">Generate Forecast</button>
                <div id="forecastContainer"></div>
            </div>

            <div class="card" style="margin-top: 20px;">
                <h2>💡 Recommendations</h2>
                <button class="btn" onclick="generateRecommendations()" id="recBtn">Generate Recommendations</button>
                <div id="recommendationsContainer"></div>
            </div>
        </div>

        <script>
            let currentData = null;
            let currentForecast = null;

            async function generateData() {
                const btn = event.target;
                btn.disabled = true;
                btn.textContent = 'Generating...';
                
                try {
                    const response = await fetch('/api/generate-data');
                    const data = await response.json();
                    currentData = data;
                    
                    document.getElementById('recordCount').textContent = data.record_count;
                    document.getElementById('status').textContent = '● DATA LOADED';
                    document.getElementById('status').style.background = '#10b981';
                    
                    btn.textContent = 'Regenerate Data';
                } catch (error) {
                    alert('Error generating data: ' + error.message);
                    btn.textContent = 'Generate Sample Data';
                } finally {
                    btn.disabled = false;
                }
            }

            async function generateForecast() {
                if (!currentData) {
                    alert('Please generate sample data first!');
                    return;
                }

                const btn = document.getElementById('forecastBtn');
                btn.disabled = true;
                btn.textContent = 'Generating Forecast...';
                
                const container = document.getElementById('forecastContainer');
                container.innerHTML = '<div class="loading loading-spinner">Analyzing historical patterns...</div>';
                
                try {
                    const response = await fetch('/api/forecast');
                    const data = await response.json();
                    currentForecast = data;
                    
                    // Update metrics
                    const firstDay = data.predictions[0];
                    document.getElementById('bedStress').textContent = firstDay.bed_stress.toFixed(1) + '%';
                    document.getElementById('bedStatus').textContent = firstDay.is_high_risk ? '🚨 HIGH RISK' : '✓ Normal';
                    document.getElementById('bedStatus').className = firstDay.is_high_risk ? 'risk-high' : 'risk-normal';
                    
                    // Check for alerts
                    checkAlerts(firstDay.bed_stress);
                    
                    // Display forecast table
                    let html = '<table class="forecast-table"><thead><tr>';
                    html += '<th>Date</th><th>Predicted Beds</th><th>Bed Stress</th><th>Confidence</th><th>Risk</th>';
                    html += '</tr></thead><tbody>';
                    
                    data.predictions.forEach(pred => {
                        const date = new Date(pred.date).toLocaleDateString();
                        const riskClass = pred.is_high_risk ? 'risk-high' : 'risk-normal';
                        const riskText = pred.is_high_risk ? '🚨 HIGH' : '✓ Normal';
                        html += `<tr>
                            <td>${date}</td>
                            <td>${pred.predicted_beds}</td>
                            <td>${pred.bed_stress.toFixed(1)}%</td>
                            <td>${pred.confidence.toFixed(1)}%</td>
                            <td class="${riskClass}">${riskText}</td>
                        </tr>`;
                    });
                    
                    html += '</tbody></table>';
                    container.innerHTML = html;
                    
                    btn.textContent = 'Refresh Forecast';
                } catch (error) {
                    container.innerHTML = '<div class="loading">Error: ' + error.message + '</div>';
                    btn.textContent = 'Generate Forecast';
                } finally {
                    btn.disabled = false;
                }
            }

            async function generateRecommendations() {
                if (!currentForecast) {
                    alert('Please generate a forecast first!');
                    return;
                }

                const btn = document.getElementById('recBtn');
                btn.disabled = true;
                btn.textContent = 'Generating...';
                
                const container = document.getElementById('recommendationsContainer');
                container.innerHTML = '<div class="loading loading-spinner">Analyzing scenarios...</div>';
                
                try {
                    const response = await fetch('/api/recommendations');
                    const data = await response.json();
                    
                    // Update staff risk
                    document.getElementById('staffRisk').textContent = data.staff_risk.risk_score.toFixed(1);
                    document.getElementById('staffStatus').textContent = data.staff_risk.is_critical ? '🚨 CRITICAL' : '✓ Normal';
                    document.getElementById('staffStatus').className = data.staff_risk.is_critical ? 'risk-high' : 'risk-normal';
                    
                    // Display recommendations
                    let html = '';
                    data.recommendations.forEach((rec, index) => {
                        html += `<div class="recommendation">
                            <h3>${index + 1}. ${rec.title}</h3>
                            <p>${rec.description}</p>
                            <div class="meta">
                                <span>Priority: ${rec.priority}</span>
                                <span>Impact: ${rec.impact_score.toFixed(0)}/100</span>
                                <span>Cost: $${rec.cost_estimate.toLocaleString()}</span>
                                <span>Time: ${rec.implementation_time}</span>
                            </div>
                        </div>`;
                    });
                    
                    container.innerHTML = html;
                    btn.textContent = 'Refresh Recommendations';
                } catch (error) {
                    container.innerHTML = '<div class="loading">Error: ' + error.message + '</div>';
                    btn.textContent = 'Generate Recommendations';
                } finally {
                    btn.disabled = false;
                }
            }

            function checkAlerts(bedStress) {
                const container = document.getElementById('alertContainer');
                if (bedStress > 85) {
                    container.innerHTML = `
                        <div class="alert-box">
                            <h3>🚨 ALERT: Bed Stress Threshold Exceeded</h3>
                            <p>Current bed stress level (${bedStress.toFixed(1)}%) has exceeded the threshold of 85%.</p>
                            <p><strong>Action Required:</strong> Review recommendations and implement mitigation strategies.</p>
                        </div>
                    `;
                } else {
                    container.innerHTML = '';
                }
            }

            // Auto-refresh status every 30 seconds
            setInterval(async () => {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    if (data.status === 'healthy') {
                        document.getElementById('status').textContent = '● OPERATIONAL';
                        document.getElementById('status').style.background = '#10b981';
                    }
                } catch (error) {
                    document.getElementById('status').textContent = '● OFFLINE';
                    document.getElementById('status').style.background = '#ef4444';
                }
            }, 30000);
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/generate-data")
async def generate_data():
    """Generate synthetic hospital data"""
    global hospital_data
    
    generator = SyntheticDataGenerator()
    hospital_data = generator.generate_six_months()
    
    return {
        "status": "success",
        "record_count": len(hospital_data),
        "date_range": {
            "start": hospital_data[0].date.isoformat(),
            "end": hospital_data[-1].date.isoformat()
        },
        "overload_days": sum(1 for r in hospital_data if r.overload_flag)
    }

@app.get("/api/forecast")
async def get_forecast():
    """Generate bed demand forecast"""
    if not hospital_data:
        raise HTTPException(status_code=400, detail="No data available. Generate data first.")
    
    engine = PredictionEngine()
    forecast = engine.forecast_bed_demand(days_ahead=7, historical_data=hospital_data)
    
    return {
        "predictions": [
            {
                "date": pred.date.isoformat(),
                "predicted_beds": pred.predicted_beds,
                "bed_stress": pred.bed_stress,
                "confidence": pred.confidence,
                "is_high_risk": pred.is_high_risk
            }
            for pred in forecast.predictions
        ],
        "overall_confidence": forecast.overall_confidence,
        "generated_at": forecast.generated_at.isoformat()
    }

@app.get("/api/recommendations")
async def get_recommendations():
    """Generate recommendations and staff risk"""
    if not hospital_data:
        raise HTTPException(status_code=400, detail="No data available. Generate data first.")
    
    engine = PredictionEngine()
    
    # Calculate staff risk
    predicted_admissions = int(sum(r.admissions for r in hospital_data[-7:]) / 7)
    current_staff = int(sum(r.staff_on_duty for r in hospital_data[-7:]) / 7)
    historical_overloads = [r for r in hospital_data if r.overload_flag]
    
    staff_risk = engine.calculate_staff_risk(
        predicted_admissions=predicted_admissions,
        current_staff=current_staff,
        historical_overloads=historical_overloads
    )
    
    # Generate recommendations
    recommendations = engine.generate_recommendations(
        bed_stress=85.0,
        staff_risk=staff_risk.risk_score,
        historical_context=hospital_data[-30:]
    )
    
    return {
        "staff_risk": {
            "risk_score": staff_risk.risk_score,
            "confidence": staff_risk.confidence,
            "is_critical": staff_risk.is_critical,
            "contributing_factors": staff_risk.contributing_factors
        },
        "recommendations": [
            {
                "title": rec.title,
                "description": rec.description,
                "rationale": rec.rationale,
                "cost_estimate": rec.cost_estimate,
                "impact_score": rec.impact_score,
                "priority": rec.priority,
                "implementation_time": rec.implementation_time
            }
            for rec in recommendations
        ]
    }
