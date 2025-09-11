#!/usr/bin/env python3
"""
Math Routing Agent - Enhanced System Deployment Script
Validates and deploys the complete system with all enhancements
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

class MathAgentDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_path = self.project_root / "backend"
        self.frontend_path = self.project_root / "frontend"
    
    def check_requirements(self):
        """Check if all required tools are installed"""
        print("🔍 Checking system requirements...")
        
        requirements = {
            "python": "python --version",
            "node": "node --version", 
            "npm": "npm --version",
            "docker": "docker --version"
        }
        
        missing = []
        for tool, command in requirements.items():
            try:
                result = subprocess.run(command.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.strip()
                    print(f"  ✅ {tool}: {version}")
                else:
                    missing.append(tool)
            except FileNotFoundError:
                missing.append(tool)
        
        if missing:
            print(f"❌ Missing requirements: {', '.join(missing)}")
            return False
        
        return True
    
    def check_environment_variables(self):
        """Check for required environment variables"""
        print("\n🔑 Checking environment variables...")
        
        required_vars = ["OPENAI_API_KEY", "TAVILY_API_KEY"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
            else:
                print(f"  ✅ {var}: {'*' * 20}...{os.getenv(var)[-4:]}")
        
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            print("\n💡 Create a .env file in the backend directory with:")
            for var in missing_vars:
                print(f"   {var}=your_key_here")
            return False
        
        return True
    
    def install_backend_dependencies(self):
        """Install Python dependencies"""
        print("\n📦 Installing backend dependencies...")
        
        try:
            os.chdir(self.backend_path)
            
            # Install requirements
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("  ✅ Backend dependencies installed")
                return True
            else:
                print(f"❌ Failed to install backend dependencies: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error installing backend dependencies: {e}")
            return False
        finally:
            os.chdir(self.project_root)
    
    def install_frontend_dependencies(self):
        """Install Node.js dependencies"""
        print("\n📦 Installing frontend dependencies...")
        
        try:
            os.chdir(self.frontend_path)
            
            # Install npm packages
            result = subprocess.run(["npm", "install"], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("  ✅ Frontend dependencies installed")
                return True
            else:
                print(f"❌ Failed to install frontend dependencies: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error installing frontend dependencies: {e}")
            return False
        finally:
            os.chdir(self.project_root)
    
    def start_docker_services(self):
        """Start Docker services (Qdrant, Redis, etc.)"""
        print("\n🐳 Starting Docker services...")
        
        try:
            # Start docker-compose services
            result = subprocess.run([
                "docker-compose", "up", "-d", "qdrant", "redis"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("  ✅ Docker services started")
                
                # Wait for services to be ready
                print("  ⏳ Waiting for services to initialize...")
                time.sleep(10)
                
                # Check if Qdrant is accessible
                try:
                    response = requests.get("http://localhost:6333/", timeout=5)
                    if response.status_code == 200:
                        print("  ✅ Qdrant database ready")
                except:
                    print("  ⚠️ Qdrant may need more time to initialize")
                
                return True
            else:
                print(f"❌ Failed to start Docker services: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting Docker services: {e}")
            return False
    
    def start_backend_server(self):
        """Start the FastAPI backend server"""
        print("\n🚀 Starting backend server...")
        
        try:
            os.chdir(self.backend_path)
            
            # Start the backend server in background
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "main:app", 
                "--host", "0.0.0.0", "--port", "8000", "--reload"
            ])
            
            # Wait for server to start
            time.sleep(5)
            
            # Check if server is responsive
            try:
                response = requests.get("http://localhost:8000/", timeout=5)
                if response.status_code == 200:
                    print("  ✅ Backend server running at http://localhost:8000")
                    return process
                else:
                    process.terminate()
                    return None
            except:
                process.terminate()
                return None
                
        except Exception as e:
            print(f"❌ Error starting backend server: {e}")
            return None
        finally:
            os.chdir(self.project_root)
    
    def start_frontend_server(self):
        """Start the React development server"""
        print("\n🎨 Starting frontend server...")
        
        try:
            os.chdir(self.frontend_path)
            
            # Start the frontend server in background
            process = subprocess.Popen(["npm", "run", "dev"])
            
            # Wait for server to start
            time.sleep(8)
            
            # Check if server is responsive
            try:
                response = requests.get("http://localhost:5173/", timeout=5)
                if response.status_code == 200:
                    print("  ✅ Frontend server running at http://localhost:5173")
                    return process
                else:
                    print("  ⚠️ Frontend server may need more time to initialize")
                    return process  # Return anyway, it might still be starting
            except:
                print("  ⚠️ Frontend server may need more time to initialize")
                return process  # Return anyway, it might still be starting
                
        except Exception as e:
            print(f"❌ Error starting frontend server: {e}")
            return None
        finally:
            os.chdir(self.project_root)
    
    def run_system_tests(self):
        """Run comprehensive system tests"""
        print("\n🧪 Running system tests...")
        
        try:
            # Import and run the test system
            from test_system_comprehensive import SystemTester
            
            tester = SystemTester("http://localhost:8000")
            score = tester.run_comprehensive_test()
            
            return score >= 95  # Consider 95+ a success
            
        except Exception as e:
            print(f"❌ Error running system tests: {e}")
            return False
    
    def deploy_system(self):
        """Main deployment process"""
        print("🚀 Math Routing Agent - Enhanced System Deployment")
        print("=" * 60)
        
        deployment_steps = [
            ("Requirements Check", self.check_requirements),
            ("Environment Variables", self.check_environment_variables),
            ("Backend Dependencies", self.install_backend_dependencies),
            ("Frontend Dependencies", self.install_frontend_dependencies),
            ("Docker Services", self.start_docker_services),
        ]
        
        # Run validation steps
        for step_name, step_func in deployment_steps:
            if not step_func():
                print(f"\n❌ Deployment failed at step: {step_name}")
                return False
        
        # Start servers
        backend_process = self.start_backend_server()
        if not backend_process:
            print("\n❌ Failed to start backend server")
            return False
        
        frontend_process = self.start_frontend_server()
        if not frontend_process:
            print("\n❌ Failed to start frontend server")
            backend_process.terminate()
            return False
        
        # Run tests
        print("\n⏳ Waiting for system stabilization...")
        time.sleep(10)
        
        tests_passed = self.run_system_tests()
        
        if tests_passed:
            print("\n🎉 DEPLOYMENT SUCCESSFUL!")
            print("✨ Math Routing Agent Enhanced Edition is now running")
            print("\n🌐 Access Points:")
            print("   Frontend: http://localhost:5173")
            print("   Backend API: http://localhost:8000")
            print("   API Docs: http://localhost:8000/docs")
            print("   System Health: http://localhost:8000/system/health")
            
            print("\n🛑 To stop the system:")
            print("   Press Ctrl+C to stop this script")
            print("   Run: docker-compose down")
            
            try:
                # Keep servers running
                while True:
                    time.sleep(60)
                    # Optional: Periodic health checks
                    try:
                        response = requests.get("http://localhost:8000/system/health", timeout=5)
                        if response.status_code != 200:
                            print("⚠️ System health check failed")
                    except:
                        pass
                        
            except KeyboardInterrupt:
                print("\n🛑 Shutting down system...")
                backend_process.terminate()
                frontend_process.terminate()
                subprocess.run(["docker-compose", "down"], capture_output=True)
                print("✅ System shutdown complete")
        
        else:
            print("\n❌ DEPLOYMENT COMPLETED WITH ISSUES")
            print("🔧 Some tests failed - check logs above")
            backend_process.terminate()
            frontend_process.terminate()
        
        return tests_passed

def main():
    """Main deployment execution"""
    deployer = MathAgentDeployer()
    success = deployer.deploy_system()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
