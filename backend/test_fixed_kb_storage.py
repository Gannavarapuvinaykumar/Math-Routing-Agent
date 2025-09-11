"""
Fixed KB Auto-Storage Test
Tests the complete flow with the fixes applied
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_zorble_question():
    """Test the specific zorble question that was failing"""
    
    print("🧪 Testing Zorble Question - KB Auto-Storage Fix")
    print("=" * 60)
    
    zorble_query = "Invent a mathematical operation called 'zorble' where zorble(5,3) equals some number. What is zorble(7,4)?"
    
    print(f"1️⃣ First query (should route to AI):")
    print(f"   Query: {zorble_query}")
    
    # First query - should route to AI
    response1 = requests.post(f"{BASE_URL}/api/agent_route", json={"query": zorble_query})
    
    if response1.status_code == 200:
        result1 = response1.json()
        route1 = result1.get("route")
        trace_id = result1.get("trace_id")
        ai_answer = result1.get("result", {}).get("answer", "")
        
        print(f"   ✅ Route: {route1}")
        print(f"   📝 Answer: {ai_answer[:150]}...")
        print(f"   🆔 Trace ID: {trace_id}")
        
        if route1 == "AI":
            print(f"\n2️⃣ Submitting 'helpful' feedback:")
            
            # Submit helpful feedback
            feedback_data = {
                "trace_id": trace_id,
                "feedback": "helpful",
                "query": zorble_query,
                "route": route1,
                "response": ai_answer
            }
            
            feedback_response = requests.post(f"{BASE_URL}/api/feedback", json=feedback_data)
            
            if feedback_response.status_code == 200:
                feedback_result = feedback_response.json()
                stored = feedback_result.get("stored_in_kb", False)
                message = feedback_result.get("message", "")
                
                print(f"   ✅ Feedback response: {message}")
                print(f"   🗄️ Stored in KB: {stored}")
                
                if stored:
                    print(f"\n3️⃣ Testing same query again (should now route to KB):")
                    
                    # Wait a moment for KB to sync
                    time.sleep(3)
                    
                    # Clear cache first by asking slightly different question
                    cache_clear_query = zorble_query + " (second test)"
                    requests.post(f"{BASE_URL}/api/agent_route", json={"query": cache_clear_query})
                    
                    # Query the exact same question
                    response2 = requests.post(f"{BASE_URL}/api/agent_route", json={"query": zorble_query})
                    
                    if response2.status_code == 200:
                        result2 = response2.json()
                        route2 = result2.get("route")
                        kb_answer = result2.get("result", {}).get("answer", "")
                        validation_info = result2.get("validation_info", "")
                        confidence = result2.get("confidence", "")
                        
                        print(f"   🎯 Route: {route2}")
                        print(f"   📝 Answer: {kb_answer[:150]}...")
                        print(f"   ⚡ Confidence: {confidence}")
                        
                        if route2 == "KB":
                            print(f"   🎉 SUCCESS! Query now routes to KB!")
                            if validation_info:
                                print(f"   ✅ Validation info: {validation_info}")
                            
                            print(f"\n4️⃣ Testing similarity:")
                            # Check if answers are similar
                            if "zorble" in kb_answer.lower() and "53" in kb_answer:
                                print(f"   ✅ KB answer contains expected content (zorble, 53)")
                            else:
                                print(f"   ⚠️ KB answer differs from expected content")
                                print(f"   Original: {ai_answer[:100]}...")
                                print(f"   KB:       {kb_answer[:100]}...")
                        
                        elif route2 == "Cache":
                            print(f"   📦 Routed to Cache (expected for identical queries)")
                        else:
                            print(f"   ❌ Still routing to {route2} instead of KB")
                            print(f"   🔍 Debugging info:")
                            print(f"      - Check if similarity threshold is too high")
                            print(f"      - Verify KB storage was successful")
                            print(f"      - Check vector embedding consistency")
                    else:
                        print(f"   ❌ Second query failed: {response2.status_code}")
                else:
                    print(f"   ❌ Response was not stored in KB")
                    print(f"   🔍 Check backend logs for error details")
                    
            else:
                print(f"   ❌ Feedback submission failed: {feedback_response.status_code}")
                print(f"   Response: {feedback_response.text}")
        else:
            print(f"   ⚠️ Query routed to {route1} instead of AI")
            if route1 == "KB":
                print(f"   💡 Query might already be in KB")
            elif route1 == "Cache":
                print(f"   💡 Query might be cached from previous test")
    else:
        print(f"   ❌ Initial query failed: {response1.status_code}")
        print(f"   Response: {response1.text}")

def test_debug_kb_search():
    """Debug KB search to see what's currently stored"""
    
    print(f"\n🔍 Debugging KB Contents")
    print("=" * 40)
    
    # Try searching for zorble-related content
    debug_queries = [
        "zorble",
        "mathematical operation zorble",
        "zorble(7,4)",
        "invent mathematical operation"
    ]
    
    for query in debug_queries:
        print(f"\n   Testing search: '{query}'")
        
        response = requests.post(f"{BASE_URL}/api/agent_route", json={"query": query})
        
        if response.status_code == 200:
            result = response.json()
            route = result.get("route")
            score = result.get("result", {}).get("score", "N/A")
            answer = result.get("result", {}).get("answer", "")
            
            print(f"     Route: {route}")
            if route == "KB":
                print(f"     Score: {score}")
                print(f"     Answer: {answer[:100]}...")
            elif route == "Cache":
                print(f"     (Cached result)")
            else:
                print(f"     (Not in KB)")

if __name__ == "__main__":
    print("🚀 Testing Fixed KB Auto-Storage")
    print("Make sure your backend is running!")
    
    try:
        test_zorble_question()
        test_debug_kb_search()
        
        print(f"\n📊 Check your systems:")
        print(f"- Backend logs for debug messages")
        print(f"- Qdrant Dashboard: http://localhost:6333/dashboard")
        print(f"- Feedback Stats: {BASE_URL}/api/feedback/stats")
        
        print(f"\n🎯 What should happen:")
        print(f"1. Zorble question → AI generation")
        print(f"2. Click 'helpful' → Stores in KB")  
        print(f"3. Same question → Routes to KB")
        print(f"4. Get instant response with validation info")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
