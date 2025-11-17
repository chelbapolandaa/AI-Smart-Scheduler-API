from improved import UltimateScheduler

def test_enhanced_features():
    scheduler = UltimateScheduler()
    
    enhanced_test_cases = [
        {
            "name": "TIME CONTEXT + URGENCY",
            "sentence": "besok pagi meeting penting 2 jam, sore belajar AI 3 jam"
        },
        {
            "name": "FLEXIBLE SCHEDULING", 
            "sentence": "setiap hari olahraga flexible waktu, kerja 4 jam, istirahat"
        },
        {
            "name": "URGENT + RELAXED MIX",
            "sentence": "besok urgent presentasi 2 jam, rapat team 1 jam, santai nanti coding 2 jam"
        },
        {
            "name": "SPECIFIC TIME RANGES",
            "sentence": "besok meeting jam 9-11, belajar jam 2-4, olahraga sore"
        }
    ]
    
    for test_case in enhanced_test_cases:
        print(f"\n{'='*70}")
        print(f"🧠 ENHANCED TEST: {test_case['name']}")
        print(f"📝 Input: {test_case['sentence']}")
        print('='*70)
        
        result = scheduler.ultimate_enhanced_blitz_mode(test_case['sentence'])
        
        if result:
            print(f"✅ TEST COMPLETED - {len(result.get('smart_suggestions', []))} smart suggestions generated")
        else:
            print("❌ TEST FAILED")
    
    # Final analytics
    print(f"\n{'='*70}")
    print("📊 FINAL ENHANCED ANALYTICS")
    print('='*70)
    scheduler.show_analytics_dashboard()

if __name__ == "__main__":
    test_enhanced_features()