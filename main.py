import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import sqlite3
from pathlib import Path

class UltimateScheduler:
    def __init__(self):
        self.activity_templates = {
            'sholat': {'duration': 1, 'priority': 'high', 'fixed_times': ['05:00', '12:30', '15:30', '18:00', '19:30']},
            'makan': {'duration': 1, 'priority': 'high', 'fixed_times': ['08:00', '12:00', '19:00']},
            'olahraga': {'duration': 1.5, 'priority': 'medium', 'preferred_time': '17:00'},
            'istirahat': {'duration': 0.5, 'priority': 'low', 'flexible': True},
            'break': {'duration': 0.25, 'priority': 'low', 'flexible': True},
            'belajar': {'duration': 2, 'priority': 'high', 'preferred_time': '09:00'},
            'kerja': {'duration': 3, 'priority': 'high', 'preferred_time': '10:00'},
            'meeting': {'duration': 1, 'priority': 'medium', 'preferred_time': '14:00'}
        }
        
        self.time_keywords = {
            'pagi': '08:00',
            'siang': '12:00', 
            'sore': '16:00',
            'malam': '19:00'
        }
        
        self.day_keywords = {
            'hari ini': 0,
            'besok': 1,
            'lusa': 2,
            'minggu depan': 7
        }
        
        self.priority_weights = {
            'high': 3,
            'medium': 2, 
            'low': 1
        }
        
        # Setup database untuk history
        self.setup_database()
    
    def setup_database(self):
        """Setup SQLite database untuk history & analytics"""
        self.db_path = Path("scheduler_history.db")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_text TEXT,
                schedule_data TEXT,
                productivity_score REAL,
                total_hours REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id INTEGER,
                activity_name TEXT,
                duration REAL,
                priority TEXT,
                completed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (schedule_id) REFERENCES schedules (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database setup complete")
    
    def save_schedule_history(self, input_text: str, schedule: List[Dict], metrics: Dict):
        """Save schedule ke database untuk analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Save main schedule
        cursor.execute('''
            INSERT INTO schedules (input_text, schedule_data, productivity_score, total_hours)
            VALUES (?, ?, ?, ?)
        ''', (input_text, json.dumps(schedule), metrics['efficiency_score'], metrics['total_hours']))
        
        schedule_id = cursor.lastrowid
        
        # Save individual activities
        for event in schedule:
            if event['name'] != 'BREAK':
                cursor.execute('''
                    INSERT INTO activities (schedule_id, activity_name, duration, priority)
                    VALUES (?, ?, ?, ?)
                ''', (schedule_id, event['name'], event.get('hours', 1), event.get('priority', 'medium')))
        
        conn.commit()
        conn.close()
        print("💾 Schedule saved to history")
    
    def get_analytics(self) -> Dict:
        """Get productivity analytics dari history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Overall stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_schedules,
                AVG(productivity_score) as avg_efficiency,
                AVG(total_hours) as avg_hours,
                MAX(created_at) as last_created
            FROM schedules
        ''')
        stats = cursor.fetchone()
        
        # Activity frequency
        cursor.execute('''
            SELECT activity_name, COUNT(*) as frequency, AVG(duration) as avg_duration
            FROM activities 
            GROUP BY activity_name 
            ORDER BY frequency DESC
            LIMIT 10
        ''')
        top_activities = cursor.fetchall()
        
        # Daily productivity trend
        cursor.execute('''
            SELECT DATE(created_at) as date, AVG(productivity_score) as daily_efficiency
            FROM schedules
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            LIMIT 7
        ''')
        trends = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_schedules': stats[0],
            'average_efficiency': stats[1] or 0,
            'average_hours': stats[2] or 0,
            'last_activity': stats[3],
            'top_activities': [{'name': act[0], 'frequency': act[1], 'avg_duration': act[2]} for act in top_activities],
            'weekly_trends': [{'date': trend[0], 'efficiency': trend[1]} for trend in trends]
        }
    
    def enhanced_parse(self, sentence: str):
        """SMART PARSER - IMPROVED VERSION"""
        print(f"🧠 Improved Parsing: '{sentence}'")
        
        activities = []
        target_day = 0
        sentence_lower = sentence.lower()
        
        # Simple day detection
        if "besok" in sentence_lower:
            target_day = 1
            print("📅 Detected: besok")
        elif "lusa" in sentence_lower:
            target_day = 2
            print("📅 Detected: lusa")
        elif "minggu depan" in sentence_lower:
            target_day = 7
            print("📅 Detected: minggu depan")
        
        # CLEANER PARSING APPROACH
        # Remove day keywords and split by commas
        clean_sentence = sentence_lower
        for keyword in ['besok', 'lusa', 'minggu depan', 'hari ini', 'saya', 'mau', 'aku', 'ingin']:
            clean_sentence = clean_sentence.replace(keyword, '')
        
        # Split by commas for multiple activities
        activity_strings = [s.strip() for s in clean_sentence.split(',') if s.strip()]
        
        for activity_str in activity_strings:
            # Skip empty strings
            if not activity_str:
                continue
                
            # Default values
            activity_name = activity_str
            hours = 1
            sessions = 1
            
            # Pattern untuk detect "X jam Y sesi"
            jam_sesi_match = re.search(r'(.+?)\s+(\d+)\s*jam\s+(\d+)\s*sesi', activity_str)
            if jam_sesi_match:
                activity_name = jam_sesi_match.group(1).strip()
                hours = int(jam_sesi_match.group(2))
                sessions = int(jam_sesi_match.group(3))
            
            # Pattern untuk detect "X jam"
            elif re.search(r'\d+\s*jam', activity_str):
                jam_match = re.search(r'(.+?)\s+(\d+)\s*jam', activity_str)
                if jam_match:
                    activity_name = jam_match.group(1).strip()
                    hours = int(jam_match.group(2))
            
            # Pattern untuk detect "X sesi" 
            elif re.search(r'\d+\s*sesi', activity_str):
                sesi_match = re.search(r'(.+?)\s+(\d+)\s*sesi', activity_str)
                if sesi_match:
                    activity_name = sesi_match.group(1).strip()
                    sessions = int(sesi_match.group(2))
            
            # Apply template
            activity = self.apply_activity_template(activity_name, hours, sessions, target_day)
            activities.append(activity)
            print(f"   ✅ Detected: {activity_name} - {hours} jam x {sessions} sesi")
        
        # Sort by priority
        activities.sort(key=lambda x: self.priority_weights.get(x.get('priority', 'medium'), 1), reverse=True)
        
        return activities, target_day
    
    def apply_activity_template(self, activity_name: str, hours: int, sessions: int, target_day: int) -> Dict:
        """Apply smart templates dengan priority"""
        activity_lower = activity_name.lower()
        
        for template_name, template in self.activity_templates.items():
            if template_name in activity_lower:
                return {
                    'name': activity_name,
                    'hours': template['duration'],
                    'sessions': sessions,
                    'priority': template['priority'],
                    'type': 'templated',
                    'target_day': target_day,
                    'fixed_times': template.get('fixed_times'),
                    'preferred_time': template.get('preferred_time'),
                    'flexible': template.get('flexible', False)
                }
        
        # Default activity - coba tebak priority dari nama
        priority = 'medium'
        if any(word in activity_lower for word in ['belajar', 'kerja', 'meeting', 'project']):
            priority = 'high'
        elif any(word in activity_lower for word in ['main', 'hiburan', 'social']):
            priority = 'low'
        
        return {
            'name': activity_name,
            'hours': hours,
            'sessions': sessions,
            'priority': priority,
            'type': 'regular',
            'target_day': target_day,
            'flexible': True
        }
    
    def smart_schedule(self, activities: List[Dict], target_day: int = 0) -> List[Dict]:
        """SMART SCHEDULING dengan priority-based multi-day - DEBUG VERSION"""
        print("🎯 Generating Priority-Based Multi-Day Schedule...")
        
        # DEBUG: Cek activities
        print(f"   📋 Activities received: {len(activities)}")
        for act in activities:
            print(f"      - {act['name']}: {act['hours']}h x {act['sessions']}s")
        
        schedules_by_day = {}
        
        # Group activities by day
        for activity in activities:
            day = activity['target_day']
            if day not in schedules_by_day:
                schedules_by_day[day] = []
            schedules_by_day[day].append(activity)
        
        print(f"   📅 Days to process: {list(schedules_by_day.keys())}")
        
        # Generate schedule untuk setiap day
        final_schedule = []
        
        for day_offset, day_activities in schedules_by_day.items():
            print(f"   📅 Processing day +{day_offset} with {len(day_activities)} activities")
            
            # Sort activities by priority untuk day ini
            day_activities.sort(key=lambda x: self.priority_weights.get(x.get('priority', 'medium'), 1), reverse=True)
            
            day_schedule = self.schedule_single_day(day_activities, day_offset)
            print(f"   ✅ Day +{day_offset}: {len(day_schedule)} events created")
            final_schedule.extend(day_schedule)
        
        # Sort seluruh schedule by datetime
        final_schedule.sort(key=lambda x: x['start'])
        
        print(f"   🎉 Final schedule: {len(final_schedule)} total events")
        return final_schedule
    
    def schedule_single_day(self, activities: List[Dict], day_offset: int) -> List[Dict]:
        """Generate schedule untuk single day dengan priority - FIXED VERSION"""
        schedule = []
        current_date = datetime.now().date() + timedelta(days=day_offset)
        
        # Pisahkan fixed vs flexible
        fixed_activities = [a for a in activities if a.get('fixed_times')]
        flexible_activities = [a for a in activities if not a.get('fixed_times')]
        
        # Process fixed activities first
        daily_schedule = {}
        
        for activity in fixed_activities:
            for time_str in activity['fixed_times']:
                fixed_time = datetime.strptime(time_str, "%H:%M").time()
                event_time = datetime.combine(current_date, fixed_time)
                
                event = {
                    'name': activity['name'],
                    'start': event_time.isoformat(),
                    'end': (event_time + timedelta(hours=activity['hours'])).isoformat(),
                    'session': 1,
                    'total_sessions': 1,
                    'type': 'fixed',
                    'priority': activity['priority'],
                    'day_offset': day_offset,
                    'hours': activity['hours']  # ✅ ADD THIS LINE
                }
                
                key = event_time.strftime("%H:%M")
                daily_schedule[key] = event
        
        # Process flexible activities by priority
        current_time = datetime.combine(current_date, datetime.strptime("09:00", "%H:%M").time())
        
        for activity in flexible_activities:
            # Skip conflicts
            while any(self.is_time_conflict(current_time, activity['hours'], fixed_event) 
                    for fixed_event in daily_schedule.values()):
                current_time += timedelta(hours=activity['hours'] + 0.25)
            
            for session in range(activity['sessions']):
                end_time = current_time + timedelta(hours=activity['hours'])
                
                event = {
                    'name': activity['name'],
                    'start': current_time.isoformat(),
                    'end': end_time.isoformat(),
                    'session': session + 1,
                    'total_sessions': activity['sessions'],
                    'type': 'flexible',
                    'priority': activity['priority'],
                    'day_offset': day_offset,
                    'hours': activity['hours']  # ✅ ADD THIS LINE
                }
                
                schedule.append(event)
                
                # Break between sessions
                if session < activity['sessions'] - 1:
                    break_time = end_time + timedelta(minutes=15)
                    schedule.append({
                        'name': "BREAK",
                        'start': end_time.isoformat(),
                        'end': break_time.isoformat(),
                        'session': '-',
                        'total_sessions': '-',
                        'type': 'break',
                        'priority': 'low',
                        'day_offset': day_offset,
                        'hours': 0.25  # ✅ ADD THIS LINE
                    })
                    current_time = break_time
                else:
                    current_time = end_time
        
        # Combine schedules
        day_final = list(daily_schedule.values()) + schedule
        day_final.sort(key=lambda x: x['start'])
        
        return day_final
    
    def is_time_conflict(self, start_time: datetime, duration: float, existing_event: Dict) -> bool:
        """Check time conflict"""
        event_start = datetime.fromisoformat(existing_event['start'])
        event_end = datetime.fromisoformat(existing_event['end'])
        proposed_end = start_time + timedelta(hours=duration)
        
        return not (proposed_end <= event_start or start_time >= event_end)
    
    def calculate_productivity_score(self, schedule: List[Dict]) -> Dict:
        """Hitung productivity metrics dengan priority weighting - FIXED VERSION"""
        productive_hours = 0
        break_hours = 0
        priority_score = 0
        
        for event in schedule:
            # Calculate duration from start and end times
            start_dt = datetime.fromisoformat(event['start'])
            end_dt = datetime.fromisoformat(event['end'])
            duration = (end_dt - start_dt).seconds / 3600  # Convert to hours
            
            if event['name'] == 'BREAK':
                break_hours += duration
            else:
                productive_hours += duration
                # Get hours from event data or use duration as fallback
                event_hours = event.get('hours', duration)
                priority_weight = self.priority_weights.get(event.get('priority', 'medium'), 1)
                priority_score += event_hours * priority_weight
        
        total_weighted_hours = productive_hours * 3  # Max possible score
        
        return {
            'productive_hours': productive_hours,
            'break_hours': break_hours,
            'total_hours': productive_hours + break_hours,
            'priority_score': priority_score,
            'max_priority_score': total_weighted_hours,
            'efficiency_score': productive_hours / (productive_hours + break_hours) if productive_hours + break_hours > 0 else 0,
            'priority_efficiency': priority_score / total_weighted_hours if total_weighted_hours > 0 else 0
        }
    
    def display_schedule(self, schedule: List[Dict], metrics: Dict):
        """Display schedule dengan multi-day support"""
        print("\n" + "🎊" * 50)
        print("🎯 ULTIMATE SCHEDULE - MULTI-DAY & PRIORITY AWARE!")
        print("🎊" * 50)
        
        current_day = None
        
        for event in schedule:
            start_dt = datetime.fromisoformat(event['start'])
            end_dt = datetime.fromisoformat(event['end'])
            
            day_str = start_dt.strftime("%A, %d %B %Y")
            if day_str != current_day:
                current_day = day_str
                print(f"\n📅 {day_str}")
                print("   " + "─" * 40)
            
            start_str = start_dt.strftime("%H:%M")
            end_str = end_dt.strftime("%H:%M")
            
            # Priority emoji
            priority_emoji = {
                'high': '🔥',
                'medium': '✅', 
                'low': '⚡'
            }.get(event.get('priority', 'medium'), '✅')
            
            if event['name'] == "BREAK":
                print(f"   ☕ {start_str} - {end_str} | BREAK TIME")
            else:
                session_info = f"(Sesi {event['session']}/{event['total_sessions']})" if event['total_sessions'] > 1 else ""
                print(f"   {priority_emoji} {start_str} - {end_str} | {event['name'].title()} {session_info}")
        
        print(f"\n📊 PRODUCTIVITY ANALYTICS:")
        print(f"   🎯 Productive Hours: {metrics['productive_hours']:.1f} jam")
        print(f"   ☕ Break Hours: {metrics['break_hours']:.1f} jam")
        print(f"   ⚡ Efficiency Score: {metrics['efficiency_score']:.1%}")
        print(f"   🔥 Priority Score: {metrics['priority_score']:.1f}/{metrics['max_priority_score']:.1f}")
        print(f"   🚀 Priority Efficiency: {metrics['priority_efficiency']:.1%}")
    
    def show_analytics_dashboard(self):
        """Show analytics dashboard dari historical data"""
        analytics = self.get_analytics()
        
        print("\n" + "📈" * 25)
        print("📊 PRODUCTIVITY ANALYTICS DASHBOARD")
        print("📈" * 25)
        
        print(f"\n📅 Overall Stats:")
        print(f"   📋 Total Schedules: {analytics['total_schedules']}")
        print(f"   ⚡ Average Efficiency: {analytics['average_efficiency']:.1%}")
        print(f"   ⏱️ Average Hours/Day: {analytics['average_hours']:.1f} jam")
        print(f"   🕒 Last Activity: {analytics['last_activity']}")
        
        if analytics['top_activities']:
            print(f"\n🏆 Top Activities:")
            for activity in analytics['top_activities'][:5]:
                print(f"   ✅ {activity['name']}: {activity['frequency']}x (avg {activity['avg_duration']:.1f} jam)")
        
        if analytics['weekly_trends']:
            print(f"\n📈 Weekly Trends:")
            for trend in analytics['weekly_trends']:
                print(f"   📅 {trend['date']}: {trend['efficiency']:.1%} efficiency")
    
    def blitz_mode(self, sentence: str):
        """MAIN FUNCTION - ALL FEATURES! - WITH ERROR HANDLING"""
        print("🚀 ULTIMATE BLITZ MODE ACTIVATED!")
        
        try:
            # Step 1: Parse dengan multi-day & priority
            activities, target_day = self.enhanced_parse(sentence)
            
            # FIXED PRINT - No unclosed brackets
            activity_list = [f"{a['name']}({a['priority']})" for a in activities]
            print(f"🎯 Activities: {activity_list}")
            
            # Step 2: Generate Smart Schedule
            print("🔄 Generating schedule...")
            schedule = self.smart_schedule(activities, target_day)
            
            # Check if schedule is empty
            if not schedule:
                print("❌ ERROR: Schedule is empty!")
                return [], {}
            
            print(f"✅ Schedule generated: {len(schedule)} events")
            
            # Step 3: Calculate Metrics
            metrics = self.calculate_productivity_score(schedule)
            
            # Step 4: Display
            self.display_schedule(schedule, metrics)
            
            # Step 5: Save to History
            self.save_schedule_history(sentence, schedule, metrics)
            
            return schedule, metrics
            
        except Exception as e:
            print(f"❌ ERROR in blitz_mode: {e}")
            import traceback
            traceback.print_exc()
            return [], {}

# 🎪 TEST ULTIMATE VERSION
if __name__ == "__main__":
    scheduler = UltimateScheduler()
    
    # Test cases dengan multi-day dan priority
    test_sentences = [
        "besok belajar 2 jam 1 sesi, meeting 1 jam"
    ]
    
    print("🧪 ULTIMATE SCHEDULER TESTING...")
    print("=" * 60)
    
    # Test pertama
    schedule, metrics = scheduler.blitz_mode(test_sentences[0])
    
    # Show analytics
    scheduler.show_analytics_dashboard()
    
    print(f"\n🎉 ULTIMATE DEMO COMPLETE! {len(schedule)} events created!")