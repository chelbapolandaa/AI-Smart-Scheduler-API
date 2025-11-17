from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
from improved import UltimateScheduler  # Import backend kita

# Initialize FastAPI app
app = FastAPI(
    title="AI Smart Scheduler API",
    description="Intelligent scheduling system dengan NLP-powered context understanding",
    version="2.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scheduler
scheduler = UltimateScheduler()

# Request model
class ScheduleRequest(BaseModel):
    sentence: str

# Response models
class ScheduleResponse(BaseModel):
    success: bool
    schedule: List[Dict]
    metrics: Dict
    conflicts_resolved: int = 0
    smart_suggestions: List[str] = []
    time_context: Dict = {}
    message: str = ""

@app.get("/", response_class=HTMLResponse)
async def root():
    """Homepage dengan modern UI"""
    return """
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Smart Scheduler</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }
            .header h1 {
                font-size: 2.8em;
                margin-bottom: 10px;
                font-weight: 700;
            }
            .header p {
                font-size: 1.3em;
                opacity: 0.9;
                margin-bottom: 20px;
            }
            .badge {
                background: rgba(255,255,255,0.2);
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 0.9em;
                display: inline-block;
                margin: 5px;
            }
            .content {
                padding: 40px;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 40px;
            }
            @media (max-width: 768px) {
                .content {
                    grid-template-columns: 1fr;
                }
            }
            .input-section {
                background: #f8f9fa;
                padding: 30px;
                border-radius: 15px;
            }
            .input-section h2 {
                color: #333;
                margin-bottom: 20px;
                font-size: 1.5em;
            }
            .input-section input {
                width: 100%;
                padding: 15px 20px;
                font-size: 16px;
                border: 2px solid #e1e5e9;
                border-radius: 10px;
                margin-bottom: 15px;
                transition: all 0.3s;
            }
            .input-section input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            .input-section button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 16px;
                border-radius: 10px;
                cursor: pointer;
                transition: transform 0.2s;
                width: 100%;
                font-weight: 600;
            }
            .input-section button:hover {
                transform: translateY(-2px);
            }
            .input-section button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            .examples {
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-top: 20px;
                border: 1px solid #e1e5e9;
            }
            .examples h3 {
                margin-bottom: 15px;
                color: #333;
                font-size: 1.1em;
            }
            .example-item {
                background: #f8f9fa;
                padding: 12px 15px;
                margin: 8px 0;
                border-radius: 8px;
                cursor: pointer;
                border-left: 4px solid #667eea;
                transition: all 0.2s;
                font-size: 0.95em;
            }
            .example-item:hover {
                background: #667eea;
                color: white;
                transform: translateX(5px);
            }
            .results-section {
                background: white;
                padding: 0;
                border-radius: 15px;
                border: 1px solid #e1e5e9;
                max-height: 600px;
                overflow-y: auto;
            }
            .schedule-day {
                border-bottom: 1px solid #e1e5e9;
            }
            .day-header {
                background: #f8f9fa;
                padding: 20px;
                font-weight: bold;
                color: #333;
                font-size: 1.1em;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .event {
                padding: 15px 20px;
                border-bottom: 1px solid #f1f3f4;
                display: flex;
                align-items: center;
                gap: 15px;
            }
            .event:last-child {
                border-bottom: none;
            }
            .event-time {
                font-weight: 600;
                color: #666;
                min-width: 120px;
            }
            .event-name {
                flex: 1;
                font-weight: 500;
            }
            .event-priority {
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.8em;
                font-weight: 600;
            }
            .priority-high { background: #ffe6e6; color: #d63031; }
            .priority-medium { background: #fff4e6; color: #e17055; }
            .priority-low { background: #e6f3ff; color: #0984e3; }
            .break-event { 
                background: #f8f9fa; 
                color: #666;
                font-style: italic;
            }
            .metrics {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px;
                border-radius: 15px;
                margin-top: 20px;
            }
            .metrics h3 {
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            .metric-item {
                display: flex;
                justify-content: space-between;
                margin: 10px 0;
                font-size: 1em;
            }
            .suggestions {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 10px;
                padding: 20px;
                margin-top: 20px;
            }
            .suggestions h3 {
                color: #856404;
                margin-bottom: 15px;
                font-size: 1.1em;
            }
            .suggestion-item {
                background: white;
                padding: 12px 15px;
                margin: 8px 0;
                border-radius: 8px;
                border-left: 4px solid #ffeaa7;
                font-size: 0.95em;
            }
            .loading {
                text-align: center;
                padding: 40px;
                color: #666;
            }
            .loading-spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .context-info {
                background: #e6f3ff;
                border: 1px solid #b3d9ff;
                border-radius: 10px;
                padding: 15px;
                margin: 15px 0;
                font-size: 0.9em;
            }
            .context-badge {
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.8em;
                margin-right: 8px;
                margin-bottom: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 AI Smart Scheduler</h1>
                <p>Jadwalkan hari Anda dengan kecerdasan buatan</p>
                <div>
                    <span class="badge">🧠 NLP Powered</span>
                    <span class="badge">⏰ Smart Scheduling</span>
                    <span class="badge">📊 Analytics</span>
                    <span class="badge">💡 AI Suggestions</span>
                </div>
            </div>
            
            <div class="content">
                <!-- Input Section -->
                <div class="input-section">
                    <h2>📝 Buat Jadwal</h2>
                    <input type="text" id="sentenceInput" 
                           placeholder="Contoh: besok pagi meeting penting 2 jam, sore belajar AI 3 jam"
                           onkeypress="handleKeyPress(event)">
                    <button onclick="schedule()" id="scheduleBtn">Buat Jadwal Cerdas</button>
                    
                    <div class="examples">
                        <h3>💡 Contoh Penggunaan:</h3>
                        <div class="example-item" onclick="useExample(this)">
                            besok pagi meeting penting 2 jam, sore belajar AI 3 jam
                        </div>
                        <div class="example-item" onclick="useExample(this)">
                            setiap hari olahraga flexible waktu, kerja 4 jam, istirahat
                        </div>
                        <div class="example-item" onclick="useExample(this)">
                            besok urgent presentasi 2 jam, rapat team 1 jam, coding 2 jam
                        </div>
                        <div class="example-item" onclick="useExample(this)">
                            lusa meeting jam 9-11, belajar jam 2-4, olahraga sore
                        </div>
                    </div>
                </div>
                
                <!-- Results Section -->
                <div class="results-section" id="resultsSection">
                    <div class="loading" id="loadingSection" style="display: none;">
                        <div class="loading-spinner"></div>
                        <p>AI sedang menganalisis dan membuat jadwal optimal...</p>
                    </div>
                    
                    <div id="resultsContent" style="display: none;">
                        <!-- Results will be populated here by JavaScript -->
                    </div>
                </div>
            </div>
        </div>

        <script>
            function useExample(element) {
                document.getElementById('sentenceInput').value = element.textContent;
            }
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    schedule();
                }
            }
            
            async function schedule() {
                const sentence = document.getElementById('sentenceInput').value.trim();
                const resultsSection = document.getElementById('resultsSection');
                const loadingSection = document.getElementById('loadingSection');
                const resultsContent = document.getElementById('resultsContent');
                const scheduleBtn = document.getElementById('scheduleBtn');
                
                if (!sentence) {
                    alert('Masukkan jadwal yang ingin Anda buat!');
                    return;
                }
                
                // Show loading
                scheduleBtn.disabled = true;
                scheduleBtn.textContent = 'Membuat Jadwal...';
                loadingSection.style.display = 'block';
                resultsContent.style.display = 'none';
                
                try {
                    const response = await fetch('/schedule', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ sentence: sentence })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        displayResults(data);
                    } else {
                        showError(data.message || 'Terjadi kesalahan saat membuat jadwal');
                    }
                } catch (error) {
                    showError('Koneksi error: ' + error);
                } finally {
                    scheduleBtn.disabled = false;
                    scheduleBtn.textContent = 'Buat Jadwal Cerdas';
                    loadingSection.style.display = 'none';
                }
            }
            
            function displayResults(data) {
                const resultsContent = document.getElementById('resultsContent');
                resultsContent.innerHTML = '';
                resultsContent.style.display = 'block';
                
                // Display time context if available
                if (data.time_context && (data.time_context.time_of_day || data.time_context.urgency !== 'normal')) {
                    const contextHtml = createContextHTML(data.time_context);
                    resultsContent.innerHTML += contextHtml;
                }
                
                // Display schedule
                if (data.schedule && data.schedule.length > 0) {
                    const scheduleHtml = createScheduleHTML(data.schedule);
                    resultsContent.innerHTML += scheduleHtml;
                }
                
                // Display metrics
                if (data.metrics) {
                    const metricsHtml = createMetricsHTML(data.metrics);
                    resultsContent.innerHTML += metricsHtml;
                }
                
                // Display smart suggestions
                if (data.smart_suggestions && data.smart_suggestions.length > 0) {
                    const suggestionsHtml = createSuggestionsHTML(data.smart_suggestions);
                    resultsContent.innerHTML += suggestionsHtml;
                }
                
                // Scroll to results
                resultsContent.scrollIntoView({ behavior: 'smooth' });
            }
            
            function createContextHTML(timeContext) {
                let contextHTML = '<div class="context-info">';
                contextHTML += '<h3>⏰ Konteks Waktu</h3>';
                
                if (timeContext.time_of_day) {
                    contextHTML += `<div><span class="context-badge">🕐 Waktu</span> ${timeContext.time_of_day}</div>`;
                }
                if (timeContext.flexibility) {
                    contextHTML += `<div><span class="context-badge">⚡ Fleksibel</span> Waktu dapat disesuaikan</div>`;
                }
                if (timeContext.urgency !== 'normal') {
                    const urgencyText = timeContext.urgency === 'high' ? 'Tinggi' : 'Rendah';
                    const urgencyEmoji = timeContext.urgency === 'high' ? '🚨' : '😌';
                    contextHTML += `<div><span class="context-badge">${urgencyEmoji} Urgensi</span> ${urgencyText}</div>`;
                }
                if (timeContext.preferred_times && timeContext.preferred_times.length > 0) {
                    const times = timeContext.preferred_times.map(t => `jam ${t.start}-${t.end}`).join(', ');
                    contextHTML += `<div><span class="context-badge">🎯 Preferensi</span> ${times}</div>`;
                }
                
                contextHTML += '</div>';
                return contextHTML;
            }
            
            function createScheduleHTML(schedule) {
                let scheduleHTML = '<div class="schedule-container">';
                
                // Group events by day
                const eventsByDay = {};
                schedule.forEach(event => {
                    const date = event.start.split('T')[0];
                    if (!eventsByDay[date]) {
                        eventsByDay[date] = [];
                    }
                    eventsByDay[date].push(event);
                });
                
                // Create day sections
                Object.entries(eventsByDay).forEach(([date, dayEvents]) => {
                    const dateObj = new Date(date + 'T00:00:00');
                    const dayName = dateObj.toLocaleDateString('id-ID', { 
                        weekday: 'long', 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                    });
                    
                    scheduleHTML += `
                        <div class="schedule-day">
                            <div class="day-header">
                                <span>📅 ${dayName}</span>
                                <span>${dayEvents.length} aktivitas</span>
                            </div>
                    `;
                    
                    dayEvents.forEach(event => {
                        const startTime = event.start.split('T')[1].substring(0, 5);
                        const endTime = event.end.split('T')[1].substring(0, 5);
                        const isBreak = event.name === 'BREAK';
                        const priorityClass = isBreak ? '' : `priority-${event.priority || 'medium'}`;
                        const eventClass = isBreak ? 'break-event' : 'event';
                        const emoji = isBreak ? '☕' : 
                                    event.priority === 'high' ? '🔥' : 
                                    event.priority === 'low' ? '⚡' : '✅';
                        
                        scheduleHTML += `
                            <div class="${eventClass}">
                                <div class="event-time">${startTime} - ${endTime}</div>
                                <div class="event-name">${emoji} ${event.name}</div>
                                ${!isBreak ? `<div class="event-priority ${priorityClass}">${event.priority || 'medium'}</div>` : ''}
                            </div>
                        `;
                    });
                    
                    scheduleHTML += '</div>';
                });
                
                scheduleHTML += '</div>';
                return scheduleHTML;
            }
            
            function createMetricsHTML(metrics) {
                return `
                    <div class="metrics">
                        <h3>📊 Analytics Produktivitas</h3>
                        <div class="metric-item">
                            <span>🎯 Jam Produktif:</span>
                            <span>${metrics.productive_hours.toFixed(1)} jam</span>
                        </div>
                        <div class="metric-item">
                            <span>☕ Istirahat:</span>
                            <span>${metrics.break_hours.toFixed(1)} jam</span>
                        </div>
                        <div class="metric-item">
                            <span>⚡ Efisiensi:</span>
                            <span>${(metrics.efficiency_score * 100).toFixed(1)}%</span>
                        </div>
                        <div class="metric-item">
                            <span>🔥 Skor Prioritas:</span>
                            <span>${metrics.priority_score.toFixed(1)}/${metrics.max_priority_score.toFixed(1)}</span>
                        </div>
                    </div>
                `;
            }
            
            function createSuggestionsHTML(suggestions) {
                let suggestionsHTML = '<div class="suggestions">';
                suggestionsHTML += '<h3>💡 Saran Cerdas AI</h3>';
                
                suggestions.forEach((suggestion, index) => {
                    suggestionsHTML += `
                        <div class="suggestion-item">
                            ${index + 1}. ${suggestion}
                        </div>
                    `;
                });
                
                suggestionsHTML += '</div>';
                return suggestionsHTML;
            }
            
            function showError(message) {
                const resultsContent = document.getElementById('resultsContent');
                resultsContent.innerHTML = `
                    <div style="background: #ffe6e6; color: #d63031; padding: 20px; border-radius: 10px; text-align: center;">
                        <h3>❌ Error</h3>
                        <p>${message}</p>
                    </div>
                `;
                resultsContent.style.display = 'block';
            }
        </script>
    </body>
    </html>
    """

@app.post("/schedule", response_model=ScheduleResponse)
async def create_schedule(request: ScheduleRequest):
    """API endpoint untuk membuat schedule dengan enhanced features"""
    try:
        if not request.sentence.strip():
            raise HTTPException(status_code=400, detail="Sentence cannot be empty")
        
        # Use our enhanced backend scheduler
        result = scheduler.ultimate_enhanced_blitz_mode(request.sentence)
        
        if not result:
            return ScheduleResponse(
                success=False,
                schedule=[],
                metrics={},
                message="Failed to generate schedule"
            )
        
        return ScheduleResponse(
            success=True,
            schedule=result.get('schedule', []),
            metrics=result.get('metrics', {}),
            conflicts_resolved=result.get('conflicts_resolved', 0),
            smart_suggestions=result.get('smart_suggestions', []),
            time_context=result.get('time_context', {})
        )
        
    except Exception as e:
        return ScheduleResponse(
            success=False,
            schedule=[],
            metrics={},
            message=str(e)
        )

@app.get("/analytics")
async def get_analytics():
    """Get analytics dashboard data"""
    try:
        analytics = scheduler.get_analytics()
        return {"success": True, "analytics": analytics}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Smart Scheduler API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)