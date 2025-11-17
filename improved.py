#FITUR BARU YANG DITAMBAH:
#Advanced NLP Parsing - Lebih akurat
#Recurring Events - Support "setiap senin", "setiap hari"
#Smart Conflict Resolution - Auto detect dan resolve bentrok jadwal

import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
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
        
        self.recurring_keywords = {
            'setiap': 'every',
            'setiap hari': 'daily',
            'setiap minggu': 'weekly', 
            'setiap bulan': 'monthly',
            'senin': 'monday', 'selasa': 'tuesday', 'rabu': 'wednesday',
            'kamis': 'thursday', 'jumat': 'friday', 'sabtu': 'saturday', 'minggu': 'sunday'
        }
        
        self.priority_weights = {
            'high': 3,
            'medium': 2, 
            'low': 1
        }
        
        # Setup database untuk history
        self.setup_database()
    
    def enhanced_time_context(self, sentence: str) -> Dict:
        """Deteksi context waktu yang lebih sophisticated"""
        sentence_lower = sentence.lower()
        time_context = {
            'time_of_day': None,  # pagi, siang, sore, malam
            'flexibility': False,  # apakah waktu flexible
            'urgency': 'normal',   # urgent, normal, relaxed
            'preferred_times': []  # waktu preferred yang disebut
        }
        
        # Time of day detection
        time_keywords = {
            'pagi': 'morning', 'siang': 'afternoon', 
            'sore': 'evening', 'malam': 'night'
        }
        
        for id_word, en_word in time_keywords.items():
            if id_word in sentence_lower:
                time_context['time_of_day'] = en_word
                break
        
        # Flexibility detection
        flexibility_indicators = [
            'bisa kapan saja', 'flexible', 'waktu bebas', 
            'terserah', 'kapan aja', 'bisa disesuaikan'
        ]
        
        for indicator in flexibility_indicators:
            if indicator in sentence_lower:
                time_context['flexibility'] = True
                break
        
        # Urgency detection
        if any(word in sentence_lower for word in ['urgent', 'penting', 'segera', 'harus']):
            time_context['urgency'] = 'high'
        elif any(word in sentence_lower for word in ['santai', 'bisa nanti', 'longgar']):
            time_context['urgency'] = 'low'
        
        # Preferred time ranges
        time_ranges = re.findall(r'(jam\s+(\d+)[\s\-](\d+))', sentence_lower)
        for match in time_ranges:
            time_context['preferred_times'].append({
                'start': int(match[1]),
                'end': int(match[2])
            })
        
        return time_context

    def advanced_activity_analysis(self, activity_name: str) -> Dict:
        """Deep analysis untuk memahami karakteristik activity"""
        activity_lower = activity_name.lower()
        
        analysis = {
            'category': 'general',
            'cognitive_load': 'medium',  # low, medium, high
            'energy_required': 'medium', # low, medium, high  
            'social_interaction': 'none', # none, low, high
            'optimal_duration': None,
            'time_preferences': []
        }
        
        # Category detection
        categories = {
            'learning': ['belajar', 'studi', 'research', 'baca', 'tugas'],
            'work': ['kerja', 'meeting', 'rapat', 'presentasi', 'project'],
            'physical': ['olahraga', 'workout', 'gym', 'lari', 'fitness'],
            'creative': ['desain', 'nulis', 'coding', 'develop', 'buat'],
            'maintenance': ['makan', 'istirahat', 'break', 'sholat', 'mandi']
        }
        
        for category, keywords in categories.items():
            if any(keyword in activity_lower for keyword in keywords):
                analysis['category'] = category
                break
        
        # Cognitive load analysis
        if any(word in activity_lower for word in ['belajar', 'analisis', 'coding', 'strategi']):
            analysis['cognitive_load'] = 'high'
        elif any(word in activity_lower for word in ['meeting', 'rapat', 'diskusi']):
            analysis['cognitive_load'] = 'medium'
        else:
            analysis['cognitive_load'] = 'low'
        
        # Energy requirements
        if any(word in activity_lower for word in ['olahraga', 'workout', 'lari', 'fitness']):
            analysis['energy_required'] = 'high'
        elif any(word in activity_lower for word in ['meeting', 'belajar', 'kerja']):
            analysis['energy_required'] = 'medium'
        else:
            analysis['energy_required'] = 'low'
        
        # Social interaction
        if any(word in activity_lower for word in ['meeting', 'rapat', 'diskusi', 'team']):
            analysis['social_interaction'] = 'high'
        elif any(word in activity_lower for word in ['belajar kelompok', 'collab']):
            analysis['social_interaction'] = 'medium'
        
        # Optimal duration based on category
        optimal_durations = {
            'learning': 2.0,
            'work': 1.5, 
            'physical': 1.5,
            'creative': 3.0,
            'maintenance': 1.0
        }
        analysis['optimal_duration'] = optimal_durations.get(analysis['category'], 1.5)
        
        # Time preferences based on activity type
        if analysis['category'] == 'learning':
            analysis['time_preferences'] = ['morning', 'afternoon']
        elif analysis['category'] == 'physical':
            analysis['time_preferences'] = ['evening', 'morning']
        elif analysis['category'] == 'creative':
            analysis['time_preferences'] = ['night', 'morning']
        elif analysis['category'] == 'work':
            analysis['time_preferences'] = ['afternoon', 'morning']
        
        return analysis
    
    def clean_activity_name(self, activity_name: str, time_context: Dict) -> str:
        """Remove time keywords dari activity name"""
        time_keywords = ['pagi', 'siang', 'sore', 'malam', 'besok', 'lusa', 'urgent', 'penting', 'flexible', 'waktu']
        
        words = activity_name.split()
        cleaned_words = [word for word in words if word.lower() not in time_keywords]
        
        return ' '.join(cleaned_words) if cleaned_words else activity_name

    def context_aware_parse(self, sentence: str) -> Tuple[List[Dict], int, Dict, Dict]:
        """Enhanced parsing dengan context understanding"""
        print(f"🧠 Context-Aware Parsing: '{sentence}'")
        
        # Get time context
        time_context = self.enhanced_time_context(sentence)
        print(f"   ⏰ Time Context: {time_context}")
        
        # Parse activities dengan context (gunakan existing advanced_parse)
        activities, target_day, recurring_pattern = self.advanced_parse(sentence)
        
        # Enhance each activity dengan analysis - FIXED: PASTIKAN INI DI DALAM LOOP!
        for activity in activities:
            activity_analysis = self.advanced_activity_analysis(activity['name'])
            activity['analysis'] = activity_analysis
            
            # Apply context-based adjustments
            if time_context['time_of_day']:
                activity['preferred_time_of_day'] = time_context['time_of_day']
            
            if time_context['flexibility']:
                activity['highly_flexible'] = True
                
            # Adjust duration based on optimal timing
            if activity_analysis['optimal_duration']:
                suggested_duration = activity_analysis['optimal_duration']
                if abs(activity['hours'] - suggested_duration) > 1.0:
                    activity['suggested_duration'] = suggested_duration
            
            # ✅ FIXED: Clean activity name - HARUS DI DALAM LOOP!
            activity['name'] = self.clean_activity_name(activity['name'], time_context)
        
        return activities, target_day, recurring_pattern, time_context
    
    
    def generate_smart_suggestions(self, schedule: List[Dict], activities: List[Dict], time_context: Dict) -> List[str]:
        """Generate intelligent suggestions berdasarkan best practices"""
        suggestions = []
        
        if not schedule:
            return suggestions
        
        # 1. Check for long focus sessions without breaks
        focus_streak = 0
        for i, event in enumerate(schedule):
            if event['name'] == 'BREAK':
                focus_streak = 0
            else:
                focus_streak += event['hours']
                
                if focus_streak >= 3.0:
                    suggestions.append(
                        f"💡 Consider adding break setelah {event['name']} "
                        f"(sudah {focus_streak} jam fokus terus)"
                    )
        
        # 2. Energy level optimization
        morning_energy, afternoon_energy, evening_energy = self.analyze_energy_distribution(schedule)
        
        if morning_energy < 0.3:
            suggestions.append("🌅 Pagi hari underutilized - perfect untuk deep work!")
        if afternoon_energy > 0.6:
            suggestions.append("🏃‍♂️ Siang hari overloaded - consider moving some tasks ke pagi/sore")
        
        # 3. Activity sequencing optimization
        sequencing_issues = self.check_activity_sequencing(schedule)
        suggestions.extend(sequencing_issues)
        
        # 4. Duration optimization
        duration_suggestions = self.optimize_durations(activities, schedule)
        suggestions.extend(duration_suggestions)
        
        # 5. Break optimization
        break_suggestions = self.optimize_breaks(schedule)
        suggestions.extend(break_suggestions)
        
        return suggestions[:5]  # Return top 5 suggestions

    def analyze_energy_distribution(self, schedule: List[Dict]) -> Tuple[float, float, float]:
        """Analyze energy distribution throughout the day"""
        morning_hours = 0
        afternoon_hours = 0 
        evening_hours = 0
        
        for event in schedule:
            if event['name'] == 'BREAK':
                continue
                
            start_hour = int(event['start'][11:13])
            duration = event['hours']
            
            if 6 <= start_hour < 12:
                morning_hours += duration
            elif 12 <= start_hour < 17:
                afternoon_hours += duration
            else:
                evening_hours += duration
        
        total = morning_hours + afternoon_hours + evening_hours
        if total == 0:
            return (0, 0, 0)
            
        return (morning_hours/total, afternoon_hours/total, evening_hours/total)

    def check_activity_sequencing(self, schedule: List[Dict]) -> List[str]:
        """Check untuk optimal activity sequencing"""
        suggestions = []
        
        for i in range(len(schedule) - 1):
            current = schedule[i]
            next_event = schedule[i + 1]
            
            if current['name'] == 'BREAK' or next_event['name'] == 'BREAK':
                continue
                
            current_analysis = current.get('analysis', {})
            next_analysis = next_event.get('analysis', {})
            
            # Avoid high cognitive load back-to-back
            if (current_analysis.get('cognitive_load') == 'high' and 
                next_analysis.get('cognitive_load') == 'high'):
                suggestions.append(
                    f"🧠 Consider break antara {current['name']} dan {next_event['name']} "
                    f"(keduanya high cognitive load)"
                )
            
            # Physical after mental fatigue
            if (current_analysis.get('cognitive_load') == 'high' and 
                next_analysis.get('energy_required') == 'high'):
                suggestions.append(
                    f"💪 Good sequencing! {next_event['name']} setelah {current['name']} "
                    f"bagus untuk refresh mental"
                )
        
        return suggestions

    def optimize_durations(self, activities: List[Dict], schedule: List[Dict]) -> List[str]:
        """Suggest duration optimizations"""
        suggestions = []
        
        for activity in activities:
            if 'suggested_duration' in activity:
                current_duration = activity['hours']
                suggested = activity['suggested_duration']
                
                if abs(current_duration - suggested) > 0.5:
                    suggestions.append(
                        f"⏱️ {activity['name']}: {current_duration} jam → {suggested} jam "
                        f"(optimal untuk {activity['analysis']['category']})"
                    )
        
        return suggestions

    def optimize_breaks(self, schedule: List[Dict]) -> List[str]:
        """Optimize break placement"""
        suggestions = []
        break_count = sum(1 for event in schedule if event['name'] == 'BREAK')
        productive_hours = sum(event['hours'] for event in schedule if event['name'] != 'BREAK')
        
        # Ideal break frequency
        ideal_breaks = max(1, int(productive_hours / 2))
        
        if break_count < ideal_breaks:
            suggestions.append(
                f"☕ Consider adding more breaks ({break_count} → {ideal_breaks} "
                f"untuk {productive_hours} jam produktif)"
            )
        elif break_count > ideal_breaks + 1:
            suggestions.append(
                f"⚡ Terlalu banyak breaks - consider konsolidasi "
                f"({break_count} breaks untuk {productive_hours} jam)"
            )
        
        return suggestions

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
    
    def advanced_parse(self, sentence: str) -> Tuple[List[Dict], int, Dict]:
        """ADVANCED PARSING - FIXED VERSION"""
        print(f"🧠 Advanced Parsing: '{sentence}'")
        
        activities = []
        target_day = 0
        recurring_pattern = None
        sentence_lower = sentence.lower()
        
        # Step 1: Detect recurring pattern
        recurring_pattern = self.detect_recurring_pattern(sentence_lower)
        if recurring_pattern:
            print(f"🔄 Detected recurring pattern: {recurring_pattern}")
            # Remove recurring keywords dari sentence untuk parsing normal
            for keyword in self.recurring_keywords:
                sentence_lower = sentence_lower.replace(keyword, '')
        
        # Step 2: Day detection (FIXED - hanya return integer)
        target_day = self.enhanced_day_detection(sentence_lower)
        
        # Step 3: Enhanced activity parsing (FIXED - clean sentence dari day keywords)
        clean_sentence = sentence_lower
        for day_key in self.day_keywords:
            clean_sentence = clean_sentence.replace(day_key, '')
        
        activities = self.enhanced_activity_parsing(clean_sentence, target_day, recurring_pattern)
        
        return activities, target_day, recurring_pattern
    
    def detect_recurring_pattern(self, sentence: str) -> Optional[Dict]:
        """Detect recurring patterns seperti 'setiap senin', 'setiap hari'"""
        if 'setiap' not in sentence:
            return None
            
        pattern = {}
        
        # Pattern: "setiap senin", "setiap hari jumat"
        day_matches = re.findall(r'setiap\s+(hari\s+)?(senin|selasa|rabu|kamis|jumat|sabtu|minggu)', sentence)
        if day_matches:
            pattern['type'] = 'weekly'
            pattern['days'] = [self.recurring_keywords[day[1]] for day in day_matches]
            return pattern
        
        # Pattern: "setiap hari"
        if 'setiap hari' in sentence:
            pattern['type'] = 'daily'
            return pattern
            
        # Pattern: "setiap minggu"
        if 'setiap minggu' in sentence:
            pattern['type'] = 'weekly'
            pattern['days'] = ['monday']  # Default
            return pattern
            
        return None
    
    def enhanced_day_detection(self, sentence: str) -> int:
        """Improved day detection - FIXED VERSION"""
        day_patterns = {
            'hari ini': 0,
            'besok': 1, 
            'lusa': 2,
            'minggu depan': 7
        }
        
        for pattern, offset in day_patterns.items():
            if pattern in sentence:
                print(f"📅 Detected: {pattern} (day +{offset})")
                return offset
        return 0
    
    def enhanced_activity_parsing(self, sentence: str, target_day: int, recurring_pattern: Optional[Dict]) -> List[Dict]:
        """Enhanced activity parsing dengan better pattern matching"""
        activities = []
        
        # Clean sentence dari common filler words
        filler_words = ['hari', 'ini', 'saya', 'mau', 'aku', 'ingin', 'yang', 'dan', 'dengan', 'akan', 'ingin']
        clean_sentence = sentence
        for word in filler_words:
            clean_sentence = re.sub(r'\b' + word + r'\b', '', clean_sentence)
        
        # Split by commas, "dan", "serta"
        activity_strings = re.split(r'[,\.]|\bdan\b|\bserta\b', clean_sentence)
        
        for activity_str in activity_strings:
            activity_str = activity_str.strip()
            if not activity_str or len(activity_str) < 3:
                continue
                
            # Enhanced pattern matching
            activity_data = self.parse_single_activity(activity_str)
            if activity_data:
                activity_data['target_day'] = target_day
                if recurring_pattern:
                    activity_data['recurring'] = recurring_pattern
                activities.append(activity_data)
                print(f"   ✅ Parsed: {activity_data['name']} - {activity_data['hours']}h x {activity_data['sessions']}s")
        
        # Sort by priority
        activities.sort(key=lambda x: self.priority_weights.get(x.get('priority', 'medium'), 1), reverse=True)
        
        return activities
    
    def parse_single_activity(self, activity_str: str) -> Optional[Dict]:
        """Improved duration parsing"""
        # Pattern: "activity X jam"
        pattern = r'^(.+?)\s+(\d+)\s*jam\s*(?:(\d+)\s*sesi)?$'
        match = re.match(pattern, activity_str)
        
        if match:
            name = match.group(1).strip()
            hours = int(match.group(2))
            sessions = int(match.group(3)) if match.group(3) else 1
            return self.build_activity_data(name, hours, sessions)
        
        """Parse single activity dengan multiple pattern strategies"""
        # Pattern 1: "activity X jam Y sesi"
        pattern1 = r'^(.+?)\s+(\d+)\s*jam\s+(\d+)\s*sesi$'
        match = re.match(pattern1, activity_str)
        if match:
            return self.build_activity_data(match.group(1), int(match.group(2)), int(match.group(3)))
        
        # Pattern 2: "activity X jam"  
        pattern2 = r'^(.+?)\s+(\d+)\s*jam$'
        match = re.match(pattern2, activity_str)
        if match:
            return self.build_activity_data(match.group(1), int(match.group(2)), 1)
        
        # Pattern 3: "activity X sesi"
        pattern3 = r'^(.+?)\s+(\d+)\s*sesi$'
        match = re.match(pattern3, activity_str)
        if match:
            return self.build_activity_data(match.group(1), 1, int(match.group(2)))
        
        # Pattern 4: Single activity (no numbers)
        if re.match(r'^[a-zA-Z\s]+$', activity_str.strip()):
            return self.build_activity_data(activity_str, 1, 1)
        
        return None
    
    def build_activity_data(self, name: str, hours: int, sessions: int) -> Dict:
        """Build activity data dengan template application"""
        activity_data = self.apply_activity_template(name.strip(), hours, sessions, 0)
        return activity_data

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
        
        # Default activity - guess priority from name
        priority = 'medium'
        if any(word in activity_lower for word in ['belajar', 'kerja', 'meeting', 'project', 'ai', 'coding']):
            priority = 'high'
        elif any(word in activity_lower for word in ['main', 'hiburan', 'social', 'game', 'nonton']):
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
    
    def handle_recurring_events(self, activities: List[Dict], recurring_pattern: Dict, days_ahead: int = 7) -> List[Dict]:
        """Generate recurring events untuk beberapa hari ke depan"""
        if not recurring_pattern:
            return activities
            
        print(f"🔄 Generating recurring events for {days_ahead} days...")
        
        all_recurring_events = []
        
        for day_offset in range(days_ahead):
            target_date = datetime.now().date() + timedelta(days=day_offset)
            
            # Check jika hari ini sesuai dengan pattern
            if self.should_schedule_today(target_date, recurring_pattern):
                for activity in activities:
                    if activity.get('recurring'):
                        # Create copy untuk hari ini
                        recurring_activity = activity.copy()
                        recurring_activity['target_day'] = day_offset
                        recurring_activity['recurring_instance'] = True
                        recurring_activity['original_activity'] = activity['name']
                        all_recurring_events.append(recurring_activity)
        
        return all_recurring_events
    
    def should_schedule_today(self, date: datetime.date, pattern: Dict) -> bool:
        """Check jika hari tertentu sesuai dengan recurring pattern"""
        if pattern['type'] == 'daily':
            return True
        elif pattern['type'] == 'weekly':
            day_name = date.strftime('%A').lower()
            return day_name in pattern.get('days', [])
        return False

    def smart_schedule_with_conflict_resolution(self, activities: List[Dict], target_day: int = 0) -> Dict:
        """Smart scheduling dengan conflict resolution"""
        print("🎯 Smart Scheduling with Conflict Resolution...")
        
        # Generate initial schedule
        schedule = self.smart_schedule(activities, target_day)
        
        # Check for conflicts
        conflicts = self.detect_schedule_conflicts(schedule)
        
        resolved_schedule = schedule
        suggestions = []
        
        if conflicts:
            print(f"⚠️  Found {len(conflicts)} conflicts, attempting resolution...")
            resolved_schedule, suggestions = self.resolve_conflicts(schedule, conflicts)
        
        return {
            'schedule': resolved_schedule,
            'conflicts_detected': len(conflicts),
            'suggestions': suggestions,
            'original_schedule': schedule
        }
    
    def detect_schedule_conflicts(self, schedule: List[Dict]) -> List[Dict]:
        """Detect time conflicts dalam schedule"""
        conflicts = []
        
        for i in range(len(schedule)):
            for j in range(i + 1, len(schedule)):
                event1 = schedule[i]
                event2 = schedule[j]
                
                if self.events_overlap(event1, event2):
                    conflicts.append({
                        'event1': event1,
                        'event2': event2,
                        'type': 'time_overlap'
                    })
        
        return conflicts
    
    def events_overlap(self, event1: Dict, event2: Dict) -> bool:
        """Check jika dua events overlap waktu"""
        start1 = datetime.fromisoformat(event1['start'])
        end1 = datetime.fromisoformat(event1['end'])
        start2 = datetime.fromisoformat(event2['start'])
        end2 = datetime.fromisoformat(event2['end'])
        
        return not (end1 <= start2 or start1 >= end2)
    
    def resolve_conflicts(self, schedule: List[Dict], conflicts: List[Dict]) -> Tuple[List[Dict], List[str]]:
        """Resolve conflicts dengan smart suggestions"""
        resolved_schedule = schedule.copy()
        suggestions = []
        
        for conflict in conflicts:
            event1, event2 = conflict['event1'], conflict['event2']
            
            # Generate alternative time slots
            alternatives = self.find_alternative_slots(event1, resolved_schedule)
            
            if alternatives:
                # Apply first alternative
                best_alternative = alternatives[0]
                resolved_schedule = self.move_event_to_slot(resolved_schedule, event1, best_alternative)
                
                suggestions.append(
                    f"📅 Moved '{event1['name']}' to {best_alternative['start_time'].strftime('%H:%M')} "
                    f"karena bentrok dengan '{event2['name']}'"
                )
            else:
                suggestions.append(
                    f"⚠️  Conflict: '{event1['name']}' bentrok dengan '{event2['name']}'. "
                    f"Consider rescheduling manually."
                )
        
        return resolved_schedule, suggestions
    
    def find_alternative_slots(self, event: Dict, schedule: List[Dict]) -> List[Dict]:
        """Cari alternative time slots untuk event"""
        event_duration = event['hours']
        alternatives = []
        
        # Cari gaps dalam schedule
        for i in range(len(schedule) - 1):
            current_end = datetime.fromisoformat(schedule[i]['end'])
            next_start = datetime.fromisoformat(schedule[i+1]['start'])
            gap_hours = (next_start - current_end).seconds / 3600
            
            if gap_hours >= event_duration:
                alternatives.append({
                    'start_time': current_end,
                    'end_time': current_end + timedelta(hours=event_duration),
                    'gap_hours': gap_hours,
                    'reason': 'Available gap'
                })
        
        # Sort by optimal timing (prioritize morning slots)
        alternatives.sort(key=lambda x: x['start_time'].hour)
        
        return alternatives
    
    def move_event_to_slot(self, schedule: List[Dict], event: Dict, new_slot: Dict) -> List[Dict]:
        """Pindahkan event ke slot baru"""
        # Remove event dari schedule lama
        new_schedule = [e for e in schedule if e != event]
        
        # Create event baru dengan waktu baru
        moved_event = event.copy()
        moved_event['start'] = new_slot['start_time'].isoformat()
        moved_event['end'] = new_slot['end_time'].isoformat()
        moved_event['conflict_resolved'] = True
        
        # Add ke schedule baru
        new_schedule.append(moved_event)
        
        # Sort kembali
        new_schedule.sort(key=lambda x: x['start'])
        
        return new_schedule

    def smart_schedule(self, activities: List[Dict], target_day: int = 0) -> List[Dict]:
        """SMART SCHEDULING dengan priority-based multi-day"""
        print("🎯 Generating Priority-Based Multi-Day Schedule...")
        
        schedules_by_day = {}
        
        # Group activities by day
        for activity in activities:
            day = activity['target_day']
            if day not in schedules_by_day:
                schedules_by_day[day] = []
            schedules_by_day[day].append(activity)
        
        # Generate schedule untuk setiap day
        final_schedule = []
        
        for day_offset, day_activities in schedules_by_day.items():
            print(f"📅 Processing day +{day_offset}")
            
            # Sort activities by priority untuk day ini
            day_activities.sort(key=lambda x: self.priority_weights.get(x.get('priority', 'medium'), 1), reverse=True)
            
            day_schedule = self.schedule_single_day(day_activities, day_offset)
            final_schedule.extend(day_schedule)
        
        # Sort seluruh schedule by datetime
        final_schedule.sort(key=lambda x: x['start'])
        
        return final_schedule
    
    def schedule_single_day(self, activities: List[Dict], day_offset: int) -> List[Dict]:
        """Generate schedule untuk single day dengan priority"""
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
                    'hours': activity['hours']
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
                    'hours': activity['hours']
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
                        'hours': 0.25
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
        """Hitung productivity metrics dengan priority weighting"""
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
    
    def enhanced_display_schedule(self, schedule: List[Dict], metrics: Dict, conflicts: int, suggestions: List[str]):
        """Enhanced display dengan conflict information"""
        self.display_schedule(schedule, metrics)
        
        if conflicts > 0:
            print(f"\n⚠️  CONFLICT RESOLUTION:")
            print(f"   Resolved {conflicts} scheduling conflicts")
            for suggestion in suggestions:
                print(f"   💡 {suggestion}")
    
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
    
    def ultimate_blitz_mode(self, sentence: str):
        """ULTIMATE FUNCTION dengan semua enhancements"""
        print("🚀 ULTIMATE BLITZ MODE ACTIVATED!")
        
        try:
            # Step 1: Advanced Parsing dengan recurring detection
            activities, target_day, recurring_pattern = self.advanced_parse(sentence)
            
            # Step 2: Handle recurring events jika ada
            if recurring_pattern:
                activities = self.handle_recurring_events(activities, recurring_pattern)
            
            # Step 3: Smart Scheduling dengan Conflict Resolution
            scheduling_result = self.smart_schedule_with_conflict_resolution(activities, target_day)
            
            schedule = scheduling_result['schedule']
            conflicts = scheduling_result['conflicts_detected']
            suggestions = scheduling_result['suggestions']
            
            # Step 4: Calculate Metrics
            metrics = self.calculate_productivity_score(schedule)
            
            # Step 5: Enhanced Display dengan conflict info
            self.enhanced_display_schedule(schedule, metrics, conflicts, suggestions)
            
            # Step 6: Save to History
            self.save_schedule_history(sentence, schedule, metrics)
            
            return {
                'schedule': schedule,
                'metrics': metrics,
                'conflicts_resolved': conflicts,
                'suggestions': suggestions
            }
            
        except Exception as e:
            print(f"❌ ERROR in ultimate_blitz_mode: {e}")
            import traceback
            traceback.print_exc()
            return {}
        
    def ultimate_enhanced_blitz_mode(self, sentence: str):
        """ULTIMATE FUNCTION dengan enhanced NLP & smart suggestions"""
        print("🚀 ULTIMATE ENHANCED BLITZ MODE ACTIVATED!")
        
        try:
            # Step 1: Context-aware parsing
            activities, target_day, recurring_pattern, time_context = self.context_aware_parse(sentence)
            
            # Step 2: Handle recurring events jika ada
            if recurring_pattern:
                activities = self.handle_recurring_events(activities, recurring_pattern)
            
            # Step 3: Smart Scheduling dengan Conflict Resolution
            scheduling_result = self.smart_schedule_with_conflict_resolution(activities, target_day)
            
            schedule = scheduling_result['schedule']
            conflicts = scheduling_result['conflicts_detected']
            conflict_suggestions = scheduling_result['suggestions']
            
            # Step 4: Generate Smart Suggestions
            smart_suggestions = self.generate_smart_suggestions(schedule, activities, time_context)
            
            # Step 5: Calculate Metrics
            metrics = self.calculate_productivity_score(schedule)
            
            # Step 6: Enhanced Display dengan semua suggestions
            self.ultimate_display_schedule(schedule, metrics, conflicts, conflict_suggestions, smart_suggestions, time_context)
            
            # Step 7: Save to History
            self.save_schedule_history(sentence, schedule, metrics)
            
            return {
                'schedule': schedule,
                'metrics': metrics,
                'conflicts_resolved': conflicts,
                'smart_suggestions': smart_suggestions,
                'time_context': time_context
            }
            
        except Exception as e:
            print(f"❌ ERROR in ultimate_enhanced_blitz_mode: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def ultimate_display_schedule(self, schedule: List[Dict], metrics: Dict, conflicts: int, 
                                conflict_suggestions: List[str], smart_suggestions: List[str], 
                                time_context: Dict):
        """Ultimate display dengan semua enhancements"""
        self.display_schedule(schedule, metrics)
        
        # Display time context
        if time_context['time_of_day']:
            print(f"\n⏰ TIME CONTEXT:")
            print(f"   Preferred time: {time_context['time_of_day']}")
            if time_context['flexibility']:
                print(f"   ⚡ Flexible scheduling available")
            if time_context['urgency'] != 'normal':
                print(f"   🚨 Urgency level: {time_context['urgency']}")
        
        # Display conflict resolution
        if conflicts > 0:
            print(f"\n⚠️  CONFLICT RESOLUTION:")
            print(f"   Resolved {conflicts} scheduling conflicts")
            for suggestion in conflict_suggestions:
                print(f"   💡 {suggestion}")
        
        # Display smart suggestions
        if smart_suggestions:
            print(f"\n🎯 SMART SUGGESTIONS:")
            for i, suggestion in enumerate(smart_suggestions, 1):
                print(f"   {i}. {suggestion}")

# 🎪 TEST ULTIMATE VERSION
if __name__ == "__main__":
    scheduler = UltimateScheduler()
    
    # Test cases dengan fitur baru
    test_sentences = [
        "besok pagi meeting penting 2 jam, sore belajar AI 3 jam",
        "setiap hari olahraga flexible waktu, kerja 4 jam, istirahat",
        "besok urgent presentasi 2 jam, rapat team 1 jam, santai nanti coding 2 jam",
        "besok meeting jam 9-11, belajar jam 2-4, olahraga sore"
    ]
    
    print("🧪 ULTIMATE SCHEDULER WITH ENHANCEMENTS TESTING...")
    print("=" * 70)
    
    # Test pertama
    result = scheduler.ultimate_enhanced_blitz_mode(test_sentences)
    
    # Show analytics
    scheduler.show_analytics_dashboard()
    
    print(f"\n🎉 ULTIMATE ENHANCED DEMO COMPLETE!")