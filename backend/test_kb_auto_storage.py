"""
Test Script: KB Auto-Storage for Validated Responses
Demonstrates how thumbs up feedback stores web/AI responses in KB
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_kb_auto_storage():
    """Test the KB auto-storage feature for validated responses"""
    
    print("🧪 Testing KB Auto-Storage for Validated Responses")
    print("=" * 60)
    
    # 1. Ask a creative question that will trigger AI generation
    creative_query = "Invent a mathematical operation called 'flurble' and explain its properties"
    
    print(f"1. Asking creative question (should route to AI):")
    print(f"   Query: {creative_query}")
    
    # Make the query
    response = requests.post(f"{BASE_URL}/api/agent_route", json={"query": creative_query})
    
    if response.status_code == 200:
        result = response.json()
        route = result.get("route", "Unknown")
        trace_id = result.get("trace_id", "no_trace")
        ai_response = result.get("result", {}).get("answer", "No answer")
        
        print(f"   ✅ Route: {route}")
        print(f"   📋 Response: {ai_response[:100]}...")
        print(f"   🆔 Trace ID: {trace_id}")
        
        if route in ["AI", "ai_generation"]:
            print("\n2. Submitting positive feedback (👍) to store in KB:")
            
            # Submit thumbs up feedback 
            feedback_data = {
                "trace_id": trace_id,
                "query": creative_query,
                "response": ai_response,
                "route": route,
                "feedback": "👍"
            }
            
            feedback_response = requests.post(f"{BASE_URL}/api/feedback_with_storage", json=feedback_data)
            
            if feedback_response.status_code == 200:
                feedback_result = feedback_response.json()
                stored_in_kb = feedback_result.get("stored_in_kb", False)
                message = feedback_result.get("message", "")
                
                print(f"   ✅ Feedback submitted: {message}")
                print(f"   🗄️ Stored in KB: {stored_in_kb}")
                
                if stored_in_kb:
                    print("\n3. Testing if the response is now in KB:")
                    
                    # Query the same thing again - should now find it in KB
                    second_response = requests.post(f"{BASE_URL}/api/agent_route", json={"query": creative_query})
                    
                    if second_response.status_code == 200:
                        second_result = second_response.json()
                        new_route = second_result.get("route", "Unknown")
                        
                        if new_route == "KB":
                            print(f"   ✅ SUCCESS! Query now routes to KB instead of AI")
                            print(f"   📈 This proves the response was stored successfully!")
                        elif new_route == "Cache":
                            print(f"   ⚠️ Routed to Cache (cached from previous query)")
                            print(f"   💡 Try with a slightly different question to test KB")
                        else:
                            print(f"   ⚠️ Still routing to {new_route}")
                            print(f"   💡 KB storage might take a moment to sync")
                    else:
                        print(f"   ❌ Second query failed: {second_response.status_code}")
                else:
                    print("   ⚠️ Response was not stored in KB")
            else:
                print(f"   ❌ Feedback submission failed: {feedback_response.status_code}")
        else:
            print(f"   ⚠️ Query routed to {route}, not AI - try a more creative question")
    else:
        print(f"   ❌ Initial query failed: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎯 HOW IT WORKS:")
    print("1. Ask a creative question → Routes to AI generation")
    print("2. Click thumbs up (👍) → Response gets stored in KB")
    print("3. Ask same question again → Routes to KB (faster!)")
    print("4. Future users get instant KB answers for validated responses")
    
    print("\n📊 CHECK ANALYTICS:")
    print(f"- Analytics: {BASE_URL}/api/stats")
    print(f"- Qdrant Dashboard: http://localhost:6333/dashboard")
    
    return True

def test_different_scenarios():
    """Test different feedback scenarios"""
    
    print("\n🔬 Testing Different Feedback Scenarios")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "Web Search + Thumbs Up",
            "query": "Latest developments in quantum mathematics",
            "expected_route": "Web",
            "feedback": "👍",
            "should_store": True
        },
        {
            "name": "AI Generation + Thumbs Down", 
            "query": "Create a math game with triangles",
            "expected_route": "AI",
            "feedback": "👎",
            "should_store": False
        },
        {
            "name": "KB Result + Thumbs Up",
            "query": "What is 2 + 2?",
            "expected_route": "KB",
            "feedback": "👍", 
            "should_store": False
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}:")
        print(f"   Query: {scenario['query']}")
        
        # Make query
        response = requests.post(f"{BASE_URL}/api/agent_route", json={"query": scenario['query']})
        
        if response.status_code == 200:
            result = response.json()
            route = result.get("route", "Unknown")
            trace_id = result.get("trace_id", "no_trace")
            answer = result.get("result", {}).get("answer", "No answer")
            
            print(f"   Route: {route}")
            
            # Submit feedback
            feedback_data = {
                "trace_id": trace_id,
                "query": scenario['query'],
                "response": answer,
                "route": route,
                "feedback": scenario['feedback']
            }
            
            feedback_response = requests.post(f"{BASE_URL}/api/feedback_with_storage", json=feedback_data)
            
            if feedback_response.status_code == 200:
                feedback_result = feedback_response.json()
                stored = feedback_result.get("stored_in_kb", False)
                expected_storage = scenario['should_store'] and route in ["Web", "AI"]
                
                if stored == expected_storage:
                    print(f"   ✅ Expected storage behavior: {stored}")
                else:
                    print(f"   ⚠️ Unexpected storage: got {stored}, expected {expected_storage}")
            else:
                print(f"   ❌ Feedback failed: {feedback_response.status_code}")
        else:
            print(f"   ❌ Query failed: {response.status_code}")

if __name__ == "__main__":
    print("🚀 Testing KB Auto-Storage Feature")
    print("Make sure your backend is running at http://localhost:8000")
    print("Press Enter to start testing...")
    input()
    
    try:
        test_kb_auto_storage()
        test_different_scenarios()
        
        print("\n🎉 Testing completed!")
        print("\n💡 Key Benefits:")
        print("- Web/AI responses with 👍 feedback become permanent KB knowledge")
        print("- Future queries get instant KB responses (faster + more reliable)")
        print("- System learns from user validation")
        print("- Knowledge base grows organically from user interactions")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("Make sure your backend is running and try again.")
