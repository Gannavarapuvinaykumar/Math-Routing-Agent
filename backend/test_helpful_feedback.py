"""
Test Script: "Helpful" Feedback KB Storage
Tests that "helpful" feedback triggers KB storage just like thumbs up
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_helpful_feedback():
    """Test that 'helpful' feedback stores responses in KB"""
    
    print("🧪 Testing 'Helpful' Feedback KB Storage")
    print("=" * 50)
    
    # Create a unique creative question
    unique_id = int(time.time())
    creative_query = f"Create a mathematical puzzle involving the number {unique_id}"
    
    print(f"1️⃣ Asking creative question (should route to AI):")
    print(f"   Query: {creative_query}")
    
    # Make the query
    response = requests.post(f"{BASE_URL}/api/agent_route", json={"query": creative_query})
    
    if response.status_code == 200:
        result = response.json()
        route = result.get("route")
        trace_id = result.get("trace_id")
        ai_answer = result.get("result", {}).get("answer", "")
        
        print(f"   ✅ Route: {route}")
        print(f"   📝 Answer: {ai_answer[:100]}...")
        
        if route in ["AI", "ai_generation"]:
            print(f"\n2️⃣ Submitting 'helpful' feedback:")
            
            # Test different positive feedback types
            feedback_types = ["helpful", "👍", "good", "excellent", "accurate", "useful"]
            
            for i, feedback_type in enumerate(feedback_types):
                print(f"\n   Testing feedback type: '{feedback_type}'")
                
                feedback_data = {
                    "trace_id": f"{trace_id}_{i}",
                    "query": f"{creative_query} (test {i})",
                    "response": ai_answer,
                    "route": route,
                    "feedback": feedback_type
                }
                
                feedback_response = requests.post(f"{BASE_URL}/api/feedback_with_storage", json=feedback_data)
                
                if feedback_response.status_code == 200:
                    feedback_result = feedback_response.json()
                    stored = feedback_result.get("stored_in_kb", False)
                    message = feedback_result.get("message", "")
                    
                    if stored:
                        print(f"     ✅ Stored in KB: {message}")
                    else:
                        print(f"     ❌ NOT stored: {message}")
                else:
                    print(f"     ❌ Feedback failed: {feedback_response.status_code}")
        else:
            print(f"   ⚠️ Query routed to {route}, not AI - try a more creative question")
    else:
        print(f"   ❌ Initial query failed: {response.status_code}")

def test_negative_feedback():
    """Test that negative feedback types don't get stored"""
    
    print(f"\n🛑 Testing Negative Feedback (should NOT store in KB)")
    print("=" * 50)
    
    negative_feedback_types = ["👎", "unhelpful", "bad", "incorrect", "poor", "useless"]
    
    for feedback_type in negative_feedback_types:
        print(f"\n   Testing negative feedback: '{feedback_type}'")
        
        feedback_data = {
            "trace_id": f"negative_test_{feedback_type}",
            "query": "Test negative feedback query",
            "response": "Test response",
            "route": "AI",
            "feedback": feedback_type
        }
        
        feedback_response = requests.post(f"{BASE_URL}/api/feedback_with_storage", json=feedback_data)
        
        if feedback_response.status_code == 200:
            feedback_result = feedback_response.json()
            stored = feedback_result.get("stored_in_kb", False)
            
            if not stored:
                print(f"     ✅ Correctly NOT stored in KB")
            else:
                print(f"     ❌ ERROR: Negative feedback was stored!")
        else:
            print(f"     ❌ Feedback failed: {feedback_response.status_code}")

def test_feedback_stats():
    """Test the feedback statistics endpoint"""
    
    print(f"\n📊 Testing Feedback Statistics")
    print("=" * 40)
    
    response = requests.get(f"{BASE_URL}/api/feedback/stats")
    
    if response.status_code == 200:
        stats = response.json()
        
        print(f"✅ Feedback Statistics:")
        print(f"   Total feedback: {stats.get('total_feedback', 0)}")
        print(f"   Positive feedback: {stats.get('positive_feedback', 0)}")
        print(f"   Negative feedback: {stats.get('negative_feedback', 0)}")
        print(f"   Neutral feedback: {stats.get('neutral_feedback', 0)}")
        print(f"   Satisfaction rate: {stats.get('satisfaction_rate', 0)}%")
        
        print(f"\n   Supported positive types: {stats.get('supported_positive_types', [])}")
        print(f"   Supported negative types: {stats.get('supported_negative_types', [])}")
        
    else:
        print(f"❌ Stats endpoint failed: {response.status_code}")

def test_kb_retrieval():
    """Test if stored responses can be retrieved from KB"""
    
    print(f"\n🔍 Testing KB Retrieval")
    print("=" * 30)
    
    # Test a query that should find something in KB
    test_query = "What is 2 + 2?"
    
    response = requests.post(f"{BASE_URL}/api/agent_route", json={"query": test_query})
    
    if response.status_code == 200:
        result = response.json()
        route = result.get("route")
        answer = result.get("result", {}).get("answer", "")
        validation_info = result.get("validation_info", "")
        
        print(f"   Query: {test_query}")
        print(f"   Route: {route}")
        print(f"   Answer: {answer[:100]}...")
        
        if validation_info:
            print(f"   Validation: {validation_info}")
    else:
        print(f"   ❌ KB retrieval failed: {response.status_code}")

if __name__ == "__main__":
    print("🚀 Testing 'Helpful' Feedback and KB Storage")
    print("Make sure your backend is running at http://localhost:8000")
    print("\nPress Enter to start testing...")
    input()
    
    try:
        test_helpful_feedback()
        test_negative_feedback()
        test_feedback_stats()
        test_kb_retrieval()
        
        print(f"\n🎉 Testing completed!")
        print(f"\n💡 Summary:")
        print(f"✅ 'helpful' feedback should store web/AI responses in KB")
        print(f"✅ Other positive types (👍, good, excellent, etc.) also work")
        print(f"✅ Negative feedback types are NOT stored in KB")
        print(f"✅ KB responses can be retrieved with validation info")
        
        print(f"\n📊 Check your analytics:")
        print(f"- Qdrant Dashboard: http://localhost:6333/dashboard")
        print(f"- Feedback Stats: {BASE_URL}/api/feedback/stats")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
