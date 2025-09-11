"""
Quick Test: Verify KB Auto-Storage and Retrieval
Tests that thumbs up feedback stores in KB and subsequent queries find it
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_kb_storage_and_retrieval():
    """Test the complete flow: Query → AI → Thumbs Up → Query Again → KB"""
    
    print("🧪 Testing KB Auto-Storage and Retrieval")
    print("=" * 50)
    
    # Use a unique creative question to avoid cache hits
    unique_id = int(time.time())
    creative_query = f"Invent a mathematical operation called 'zorble{unique_id}' and explain it"
    
    print(f"1️⃣ Testing creative query (should go to AI):")
    print(f"   Query: {creative_query}")
    
    # First query - should route to AI
    response1 = requests.post(f"{BASE_URL}/api/agent_route", json={"query": creative_query})
    
    if response1.status_code == 200:
        result1 = response1.json()
        route1 = result1.get("route")
        trace_id = result1.get("trace_id")
        ai_answer = result1.get("result", {}).get("answer", "")
        
        print(f"   ✅ Route: {route1}")
        print(f"   📝 Answer: {ai_answer[:100]}...")
        
        if route1 in ["AI", "ai_generation"]:
            print(f"\n2️⃣ Submitting thumbs up feedback:")
            
            # Submit positive feedback to store in KB
            feedback_data = {
                "trace_id": trace_id,
                "query": creative_query,
                "response": ai_answer,
                "route": route1,
                "feedback": "👍"
            }
            
            feedback_response = requests.post(f"{BASE_URL}/api/feedback_with_storage", json=feedback_data)
            
            if feedback_response.status_code == 200:
                feedback_result = feedback_response.json()
                stored = feedback_result.get("stored_in_kb", False)
                
                print(f"   ✅ Feedback submitted")
                print(f"   🗄️ Stored in KB: {stored}")
                
                if stored:
                    print(f"\n3️⃣ Testing same query again (should now find in KB):")
                    
                    # Wait a moment for KB to sync
                    time.sleep(2)
                    
                    # Query the exact same question
                    response2 = requests.post(f"{BASE_URL}/api/agent_route", json={"query": creative_query})
                    
                    if response2.status_code == 200:
                        result2 = response2.json()
                        route2 = result2.get("route")
                        kb_answer = result2.get("result", {}).get("answer", "")
                        validation_info = result2.get("validation_info", "")
                        
                        print(f"   🎯 Route: {route2}")
                        print(f"   📝 Answer: {kb_answer[:100]}...")
                        
                        if route2 == "KB":
                            print(f"   🎉 SUCCESS! Query now routes to KB!")
                            if validation_info:
                                print(f"   ✅ Validation info: {validation_info}")
                            
                            # Verify the answers are similar
                            if ai_answer.lower() in kb_answer.lower() or kb_answer.lower() in ai_answer.lower():
                                print(f"   ✅ Content matches original AI response")
                            else:
                                print(f"   ⚠️ Content differs from original AI response")
                                
                        elif route2 == "Cache":
                            print(f"   ⚠️ Routed to Cache (from previous query)")
                            print(f"   💡 This is expected behavior - cache takes priority")
                            
                        else:
                            print(f"   ❌ Still routing to {route2} instead of KB")
                            print(f"   🔍 Possible issues:")
                            print(f"      - KB storage failed silently")
                            print(f"      - Similarity threshold too high")
                            print(f"      - Embedding mismatch")
                    else:
                        print(f"   ❌ Second query failed: {response2.status_code}")
                else:
                    print(f"   ❌ Response was not stored in KB")
                    
            else:
                print(f"   ❌ Feedback submission failed: {feedback_response.status_code}")
        else:
            print(f"   ⚠️ Query routed to {route1} instead of AI")
            print(f"   💡 Try a more creative/novel question")
    else:
        print(f"   ❌ Initial query failed: {response1.status_code}")

def test_similarity_variants():
    """Test if slightly different questions still find the stored KB entry"""
    
    print(f"\n🔍 Testing Similarity Matching")
    print("=" * 40)
    
    base_query = "What is the flurble operation in mathematics?"
    
    variants = [
        "Explain the flurble mathematical operation",
        "Tell me about flurble in math",
        "How does the flurble operation work?",
        "What is flurble operation?"
    ]
    
    for i, variant in enumerate(variants, 1):
        print(f"\n{i}. Testing variant: {variant}")
        
        response = requests.post(f"{BASE_URL}/api/agent_route", json={"query": variant})
        
        if response.status_code == 200:
            result = response.json()
            route = result.get("route")
            score = result.get("result", {}).get("score", "N/A")
            
            print(f"   Route: {route} (Score: {score})")
            
            if route == "KB":
                print(f"   ✅ Found in KB - good similarity matching!")
            elif route == "Cache":
                print(f"   📦 Cache hit")
            else:
                print(f"   ⚠️ Routed to {route} - may need to adjust similarity threshold")

if __name__ == "__main__":
    print("🚀 Quick KB Auto-Storage Test")
    print("Make sure your backend is running!")
    
    try:
        test_kb_storage_and_retrieval()
        test_similarity_variants()
        
        print(f"\n📊 Check your KB:")
        print(f"- Qdrant Dashboard: http://localhost:6333/dashboard")
        print(f"- Look for entries with 'validated_by_user: true'")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
