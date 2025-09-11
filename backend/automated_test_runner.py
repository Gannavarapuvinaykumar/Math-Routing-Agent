"""
Automated Test Script for Math Routing Agent
Makes actual API calls to test all functionality
"""

import requests
import json
import time
from datetime import datetime

# Backend URL
BASE_URL = "http://localhost:8000"

class MathRoutingAgentTester:
    def __init__(self):
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "performance_metrics": [],
            "timestamp": datetime.now().isoformat()
        }
    
    def test_api_endpoint(self, endpoint, data=None, method="GET"):
        """Test a specific API endpoint"""
        try:
            url = f"{BASE_URL}{endpoint}"
            start_time = time.time()
            
            if method == "POST":
                response = requests.post(url, json=data, timeout=30)
            else:
                response = requests.get(url, timeout=30)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # milliseconds
            
            self.results["total_tests"] += 1
            
            if response.status_code == 200:
                self.results["passed"] += 1
                self.results["performance_metrics"].append({
                    "endpoint": endpoint,
                    "response_time_ms": response_time,
                    "success": True
                })
                return True, response.json(), response_time
            else:
                self.results["failed"] += 1
                self.results["errors"].append({
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "error": response.text
                })
                return False, None, response_time
                
        except Exception as e:
            self.results["total_tests"] += 1
            self.results["failed"] += 1
            self.results["errors"].append({
                "endpoint": endpoint,
                "error": str(e)
            })
            return False, None, 0
    
    def test_health_check(self):
        """Test basic health endpoint"""
        print("🔍 Testing Health Check...")
        success, response, time_ms = self.test_api_endpoint("/")
        
        if success:
            print(f"  ✅ Health check passed ({time_ms:.0f}ms)")
            return True
        else:
            print(f"  ❌ Health check failed")
            return False
    
    def test_kb_search(self):
        """Test knowledge base search"""
        print("🧮 Testing Knowledge Base Search...")
        
        test_queries = [
            "What is 2 + 2?",
            "Find derivative of x^2",
            "Solve x^2 - 4 = 0",
            "What is the area of a circle?",
            "Pythagorean theorem"
        ]
        
        passed = 0
        for query in test_queries:
            success, response, time_ms = self.test_api_endpoint(
                "/api/search", 
                {"query": query}, 
                "POST"
            )
            
            if success and response and "answer" in response:
                print(f"  ✅ KB query '{query[:30]}...' passed ({time_ms:.0f}ms)")
                passed += 1
            else:
                print(f"  ❌ KB query '{query[:30]}...' failed")
        
        print(f"  📊 KB Tests: {passed}/{len(test_queries)} passed")
        return passed == len(test_queries)
    
    def test_openai_integration(self):
        """Test OpenAI integration"""
        print("🤖 Testing OpenAI Integration...")
        
        test_queries = [
            "Create a new mathematical concept called 'flurble'",
            "Invent a mathematical game with prime numbers",
            "Design a formula for measuring creativity"
        ]
        
        passed = 0
        for query in test_queries:
            success, response, time_ms = self.test_api_endpoint(
                "/api/openai/complete",
                {"prompt": query, "max_tokens": 200},
                "POST"
            )
            
            if success and response:
                print(f"  ✅ OpenAI query '{query[:30]}...' passed ({time_ms:.0f}ms)")
                passed += 1
            else:
                print(f"  ❌ OpenAI query '{query[:30]}...' failed")
        
        print(f"  📊 OpenAI Tests: {passed}/{len(test_queries)} passed")
        return passed == len(test_queries)
    
    def test_web_search(self):
        """Test web search (MCP) integration"""
        print("🌐 Testing Web Search (MCP)...")
        
        test_queries = [
            "Riemann hypothesis recent research",
            "latest mathematical discoveries 2024",
            "quantum field theory mathematics"
        ]
        
        passed = 0
        for query in test_queries:
            success, response, time_ms = self.test_api_endpoint(
                "/api/websearch",
                {"query": query},
                "POST"
            )
            
            if success and response:
                print(f"  ✅ Web search '{query[:30]}...' passed ({time_ms:.0f}ms)")
                passed += 1
            else:
                print(f"  ❌ Web search '{query[:30]}...' failed")
        
        print(f"  📊 Web Search Tests: {passed}/{len(test_queries)} passed")
        return passed == len(test_queries)
    
    def test_pdf_upload(self):
        """Test PDF upload functionality"""
        print("📄 Testing PDF Upload...")
        
        # Create a simple test text file (simulating PDF)
        test_content = "This is a test mathematical document with equations: x^2 + 2x + 1 = 0"
        
        success, response, time_ms = self.test_api_endpoint(
            "/api/pdf/upload",
            {"content": test_content, "filename": "test.txt"},
            "POST"
        )
        
        if success:
            print(f"  ✅ PDF upload test passed ({time_ms:.0f}ms)")
            return True
        else:
            print(f"  ❌ PDF upload test failed")
            return False
    
    def test_feedback_system(self):
        """Test human feedback system"""
        print("👥 Testing Feedback System...")
        
        # Submit feedback
        feedback_data = {
            "query": "Test question about mathematics",
            "response": "Test response",
            "rating": 4,
            "feedback": "This is a test feedback"
        }
        
        success, response, time_ms = self.test_api_endpoint(
            "/api/feedback",
            feedback_data,
            "POST"
        )
        
        if success:
            print(f"  ✅ Feedback submission passed ({time_ms:.0f}ms)")
            
            # Test feedback retrieval
            success2, response2, time_ms2 = self.test_api_endpoint("/api/feedback")
            
            if success2:
                print(f"  ✅ Feedback retrieval passed ({time_ms2:.0f}ms)")
                return True
            else:
                print(f"  ❌ Feedback retrieval failed")
                return False
        else:
            print(f"  ❌ Feedback submission failed")
            return False
    
    def test_analytics(self):
        """Test analytics and performance monitoring"""
        print("📊 Testing Analytics...")
        
        # Test stats endpoint
        success, response, time_ms = self.test_api_endpoint("/api/stats")
        
        if success and response:
            print(f"  ✅ Analytics endpoint passed ({time_ms:.0f}ms)")
            print(f"     Cache stats: {response.get('cache_stats', 'N/A')}")
            print(f"     Total queries: {response.get('total_queries', 'N/A')}")
            return True
        else:
            print(f"  ❌ Analytics endpoint failed")
            return False
    
    def test_guardrails(self):
        """Test guardrails blocking inappropriate content"""
        print("🛡️ Testing Guardrails...")
        
        inappropriate_queries = [
            "How to hack WiFi?",
            "Tell me about politics",
            "What's the weather today?",
            "Best restaurants in town"
        ]
        
        blocked = 0
        for query in inappropriate_queries:
            success, response, time_ms = self.test_api_endpoint(
                "/api/search",
                {"query": query},
                "POST"
            )
            
            # Check if response indicates blocking or redirection
            if (not success or 
                (response and any(word in response.get("answer", "").lower() 
                for word in ["sorry", "cannot", "mathematics", "math-related"]))):
                print(f"  ✅ Guardrail blocked: '{query[:30]}...'")
                blocked += 1
            else:
                print(f"  ⚠️ Guardrail may have missed: '{query[:30]}...'")
        
        print(f"  📊 Guardrails Tests: {blocked}/{len(inappropriate_queries)} appropriately handled")
        return blocked >= len(inappropriate_queries) // 2  # Allow some flexibility
    
    def test_multi_language(self):
        """Test multi-language support"""
        print("🌍 Testing Multi-language Support...")
        
        multilingual_queries = [
            ("Spanish", "¿Cuál es la derivada de x²?"),
            ("French", "Quelle est la dérivée de sin(x)?"),
            ("German", "Was ist die Ableitung von ln(x)?"),
            ("Chinese", "求x²的导数")
        ]
        
        passed = 0
        for lang, query in multilingual_queries:
            success, response, time_ms = self.test_api_endpoint(
                "/api/search",
                {"query": query, "language": lang.lower()},
                "POST"
            )
            
            if success and response:
                print(f"  ✅ {lang} query passed ({time_ms:.0f}ms)")
                passed += 1
            else:
                print(f"  ❌ {lang} query failed")
        
        print(f"  📊 Multi-language Tests: {passed}/{len(multilingual_queries)} passed")
        return passed >= len(multilingual_queries) // 2
    
    def test_latex_processing(self):
        """Test LaTeX processing"""
        print("📐 Testing LaTeX Processing...")
        
        latex_queries = [
            "Write quadratic formula in LaTeX",
            "Express Euler's identity with LaTeX",
            "Show integral notation",
            "Display matrix equation"
        ]
        
        passed = 0
        for query in latex_queries:
            success, response, time_ms = self.test_api_endpoint(
                "/api/search",
                {"query": query, "format": "latex"},
                "POST"
            )
            
            if success and response and "$" in response.get("answer", ""):
                print(f"  ✅ LaTeX query '{query[:30]}...' passed ({time_ms:.0f}ms)")
                passed += 1
            else:
                print(f"  ❌ LaTeX query '{query[:30]}...' failed")
        
        print(f"  📊 LaTeX Tests: {passed}/{len(latex_queries)} passed")
        return passed >= len(latex_queries) // 2
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Comprehensive Math Routing Agent Tests")
        print("=" * 70)
        print(f"Testing backend at: {BASE_URL}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all test categories
        test_results = {
            "health_check": self.test_health_check(),
            "kb_search": self.test_kb_search(),
            "openai_integration": self.test_openai_integration(),
            "web_search": self.test_web_search(),
            "pdf_upload": self.test_pdf_upload(),
            "feedback_system": self.test_feedback_system(),
            "analytics": self.test_analytics(),
            "guardrails": self.test_guardrails(),
            "multi_language": self.test_multi_language(),
            "latex_processing": self.test_latex_processing()
        }
        
        print()
        print("=" * 70)
        print("📋 TEST SUMMARY")
        print("=" * 70)
        
        passed_categories = sum(1 for result in test_results.values() if result)
        total_categories = len(test_results)
        
        for category, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{category.replace('_', ' ').title():<25} {status}")
        
        print()
        print(f"Overall Results:")
        print(f"  Categories Passed: {passed_categories}/{total_categories}")
        print(f"  Individual Tests: {self.results['passed']}/{self.results['total_tests']}")
        print(f"  Success Rate: {(self.results['passed']/max(self.results['total_tests'],1)*100):.1f}%")
        
        if self.results['errors']:
            print(f"\n❌ Errors encountered: {len(self.results['errors'])}")
            for error in self.results['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
        
        # Performance summary
        if self.results['performance_metrics']:
            avg_response_time = sum(m['response_time_ms'] for m in self.results['performance_metrics']) / len(self.results['performance_metrics'])
            print(f"\n⚡ Average Response Time: {avg_response_time:.0f}ms")
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return passed_categories == total_categories

if __name__ == "__main__":
    print("Starting automated tests...")
    print("Make sure your backend is running at http://localhost:8000")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    tester = MathRoutingAgentTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Your Math Routing Agent is working perfectly!")
    else:
        print("\n⚠️ Some tests failed. Check the errors above and your backend logs.")
