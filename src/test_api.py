"""
Script untuk testing FastAPI backend
Gunakan script ini untuk memastikan backend berfungsi dengan baik

Usage:
    python test_api.py
"""

import requests
import json
import time
from pathlib import Path

# Konfigurasi
API_BASE_URL = "http://localhost:8000"
TEST_AUDIO_FILE = "test_audio.webm"  # Ganti dengan file audio test Anda

# Warna untuk output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def test_health_check():
    """Test endpoint /api/health"""
    print("\n" + "="*50)
    print_info("Testing Health Check Endpoint...")
    print("="*50)
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status Code: {response.status_code}")
            print_success(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"Status Code: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error("Connection failed! Pastikan backend running di " + API_BASE_URL)
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_root_endpoint():
    """Test endpoint /"""
    print("\n" + "="*50)
    print_info("Testing Root Endpoint...")
    print("="*50)
    
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status Code: {response.status_code}")
            print_success(f"Available Endpoints: {list(data.get('endpoints', {}).keys())}")
            return True
        else:
            print_error(f"Status Code: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_analyze_endpoint(audio_file_path, mode="quick"):
    """Test endpoint /api/analyze"""
    print("\n" + "="*50)
    print_info(f"Testing Analyze Endpoint (mode={mode})...")
    print("="*50)
    
    # Check if file exists
    if not Path(audio_file_path).exists():
        print_warning(f"File {audio_file_path} tidak ditemukan!")
        print_warning("Membuat dummy test untuk validasi endpoint...")
        
        # Create dummy audio data for testing
        dummy_data = b'\x00' * 1024  # 1KB dummy data
        
        try:
            files = {'file': ('test.webm', dummy_data, 'audio/webm')}
            data = {'mode': mode}
            
            print_info("Mengirim request ke server...")
            start_time = time.time()
            
            response = requests.post(
                f"{API_BASE_URL}/api/analyze",
                files=files,
                data=data,
                timeout=30
            )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print_success(f"Status Code: {response.status_code}")
                print_success(f"Processing Time: {elapsed_time:.2f}s")
                print_success(f"Overall Health: {result.get('overall_health')}%")
                print_success(f"Number of Issues: {len(result.get('issues', []))}")
                print_success(f"Vibration Data Points: {len(result.get('vibration_data', []))}")
                
                # Print issues
                if result.get('issues'):
                    print("\n" + Colors.BLUE + "Issues Detected:" + Colors.END)
                    for i, issue in enumerate(result['issues'], 1):
                        print(f"  {i}. [{issue['severity'].upper()}] {issue['component']}")
                        print(f"     {issue['description']}")
                
                return True
            else:
                print_error(f"Status Code: {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False
    
    else:
        # Test with actual audio file
        try:
            with open(audio_file_path, 'rb') as f:
                files = {'file': (Path(audio_file_path).name, f, 'audio/webm')}
                data = {'mode': mode}
                
                print_info(f"File: {audio_file_path}")
                print_info(f"Size: {Path(audio_file_path).stat().st_size / 1024:.2f} KB")
                print_info("Mengirim request ke server...")
                
                start_time = time.time()
                
                response = requests.post(
                    f"{API_BASE_URL}/api/analyze",
                    files=files,
                    data=data,
                    timeout=60
                )
                
                elapsed_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    print_success(f"Status Code: {response.status_code}")
                    print_success(f"Processing Time: {elapsed_time:.2f}s")
                    print_success(f"Overall Health: {result.get('overall_health')}%")
                    print_success(f"Number of Issues: {len(result.get('issues', []))}")
                    print_success(f"Vibration Data Points: {len(result.get('vibration_data', []))}")
                    
                    # Print detailed results
                    print("\n" + Colors.BLUE + "Detailed Results:" + Colors.END)
                    print(json.dumps(result, indent=2))
                    
                    return True
                else:
                    print_error(f"Status Code: {response.status_code}")
                    print_error(f"Response: {response.text}")
                    return False
                    
        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False

def test_history_endpoint():
    """Test endpoint /api/history"""
    print("\n" + "="*50)
    print_info("Testing History Endpoint...")
    print("="*50)
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/history?limit=10", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status Code: {response.status_code}")
            print_success(f"Number of Records: {len(data.get('records', []))}")
            
            if data.get('message'):
                print_warning(f"Message: {data['message']}")
            
            return True
        else:
            print_error(f"Status Code: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_invalid_requests():
    """Test dengan request yang invalid"""
    print("\n" + "="*50)
    print_info("Testing Invalid Requests...")
    print("="*50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Invalid mode
    try:
        print_info("Test 1: Invalid mode parameter")
        files = {'file': ('test.webm', b'\x00' * 1024, 'audio/webm')}
        data = {'mode': 'invalid_mode'}
        response = requests.post(f"{API_BASE_URL}/api/analyze", files=files, data=data)
        
        if response.status_code == 400:
            print_success("Correctly rejected invalid mode")
            tests_passed += 1
        else:
            print_error(f"Expected 400, got {response.status_code}")
    except Exception as e:
        print_error(f"Test 1 failed: {str(e)}")
    
    # Test 2: Missing file
    try:
        print_info("Test 2: Missing file parameter")
        data = {'mode': 'quick'}
        response = requests.post(f"{API_BASE_URL}/api/analyze", data=data)
        
        if response.status_code == 422:  # FastAPI validation error
            print_success("Correctly rejected missing file")
            tests_passed += 1
        else:
            print_error(f"Expected 422, got {response.status_code}")
    except Exception as e:
        print_error(f"Test 2 failed: {str(e)}")
    
    # Test 3: Invalid endpoint
    try:
        print_info("Test 3: Invalid endpoint")
        response = requests.get(f"{API_BASE_URL}/api/invalid_endpoint")
        
        if response.status_code == 404:
            print_success("Correctly returned 404 for invalid endpoint")
            tests_passed += 1
        else:
            print_error(f"Expected 404, got {response.status_code}")
    except Exception as e:
        print_error(f"Test 3 failed: {str(e)}")
    
    print_info(f"Invalid request tests: {tests_passed}/{total_tests} passed")
    return tests_passed == total_tests

def run_all_tests():
    """Jalankan semua tests"""
    print("\n" + "="*60)
    print(Colors.BLUE + "   🧪 TESTING FASTAPI BACKEND   " + Colors.END)
    print("="*60)
    print_info(f"API Base URL: {API_BASE_URL}")
    
    results = {
        'Root Endpoint': test_root_endpoint(),
        'Health Check': test_health_check(),
        'Analyze Quick': test_analyze_endpoint(TEST_AUDIO_FILE, mode='quick'),
        'Analyze Deep': test_analyze_endpoint(TEST_AUDIO_FILE, mode='deep'),
        'History': test_history_endpoint(),
        'Invalid Requests': test_invalid_requests()
    }
    
    # Summary
    print("\n" + "="*60)
    print(Colors.BLUE + "   📊 TEST SUMMARY   " + Colors.END)
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = Colors.GREEN + "PASS" + Colors.END if result else Colors.RED + "FAIL" + Colors.END
        print(f"{test_name}: {status}")
    
    print("\n" + "="*60)
    percentage = (passed / total) * 100
    
    if percentage == 100:
        print_success(f"All tests passed! ({passed}/{total})")
    elif percentage >= 80:
        print_warning(f"Most tests passed ({passed}/{total}) - {percentage:.0f}%")
    else:
        print_error(f"Many tests failed ({passed}/{total}) - {percentage:.0f}%")
    
    print("="*60 + "\n")
    
    # Recommendations
    if not results['Health Check']:
        print_warning("💡 Backend tidak berjalan. Jalankan dengan:")
        print_warning("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    
    if not results['Analyze Quick'] or not results['Analyze Deep']:
        print_warning("💡 Analyze endpoint gagal. Periksa:")
        print_warning("   1. Model ML sudah diload dengan benar")
        print_warning("   2. Dependencies (librosa, numpy) terinstall")
        print_warning("   3. Check logs di terminal backend")

if __name__ == "__main__":
    run_all_tests()
