"""
Test script for Data Management API endpoints
"""
import requests
import json
import os

BASE_URL = "http://localhost:8002"

def test_list_files():
    """Test listing all files"""
    print("\n" + "="*60)
    print("TEST 1: List all files in data/processed")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/data/list-files")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Success!")
        print(f"Total files: {data['total_count']}")
        print(f"Total size: {data['total_size_mb']} MB")
        print(f"\nFiles:")
        for file in data['files'][:5]:  # Show first 5 files
            print(f"  - {file['filename']}")
            print(f"    Rows: {file.get('rows', 'N/A')}, Columns: {file.get('columns', 'N/A')}")
            print(f"    Size: {file['size_mb']} MB")
            print(f"    Modified: {file['modified_at']}")
    else:
        print(f"❌ Error: {response.text}")
    
    return response.json() if response.status_code == 200 else None


def test_file_info(filename):
    """Test getting file info"""
    print("\n" + "="*60)
    print(f"TEST 2: Get info for file: {filename}")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/data/file-info/{filename}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Success!")
        print(f"Filename: {data['filename']}")
        print(f"Rows: {data['rows']}")
        print(f"Columns: {data['column_count']}")
        print(f"Size: {data['size_mb']} MB")
        print(f"\nColumn names:")
        for col in data['columns'][:10]:  # Show first 10 columns
            print(f"  - {col}")
        
        if data.get('statistics'):
            print(f"\nStatistics:")
            for col, stats in list(data['statistics'].items())[:3]:  # Show first 3
                print(f"  {col}:")
                print(f"    Min: {stats['min']}, Max: {stats['max']}")
                print(f"    Mean: {stats['mean']:.2f}, Median: {stats['median']:.2f}")
        
        print(f"\nFirst row preview:")
        if data.get('preview'):
            print(json.dumps(data['preview'][0], indent=2, ensure_ascii=False))
    else:
        print(f"❌ Error: {response.text}")
    
    return response.json() if response.status_code == 200 else None


def test_upload_file(file_path):
    """Test uploading a file"""
    print("\n" + "="*60)
    print(f"TEST 3: Upload file: {file_path}")
    print("="*60)
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None
    
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/data/upload-csv", files=files)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print(f"\n✅ Success!")
        print(f"Uploaded as: {data['filename']}")
        print(f"Original name: {data['original_filename']}")
        print(f"Rows: {data.get('rows', 'N/A')}")
        print(f"Columns: {data.get('columns', 'N/A')}")
        print(f"Size: {data['size_mb']} MB")
        print(f"Path: {data['path']}")
    else:
        print(f"❌ Error: {response.text}")
    
    return response.json() if response.status_code == 201 else None


def test_api_docs():
    """Check if API docs are accessible"""
    print("\n" + "="*60)
    print("TEST 4: Check API documentation")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/docs")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✅ API docs available at: {BASE_URL}/docs")
    else:
        print(f"❌ Error accessing docs")


def main():
    print("\n" + "🎵"*30)
    print("MUSIC ANALYZER - DATA MANAGEMENT API TESTS")
    print("🎵"*30)
    
    try:
        # Test 1: List files
        files_data = test_list_files()
        
        # Test 2: Get info about first file if any exist
        if files_data and files_data['files']:
            first_file = files_data['files'][0]['filename']
            test_file_info(first_file)
        
        # Test 3: Try to upload a test file (using existing ozen.csv)
        test_csv = "/Users/nuraliserikbay/Desktop/codes/music_analyzer_agent/data/processed/ozen.csv"
        if os.path.exists(test_csv):
            print(f"\n⚠️ Note: Will upload existing file as test (with new timestamp)")
            test_upload_file(test_csv)
        
        # Test 4: Check API docs
        test_api_docs()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED!")
        print("="*60)
        print(f"\n📚 View full API documentation at: {BASE_URL}/docs")
        print(f"📊 View Swagger UI at: {BASE_URL}/docs")
        print(f"📋 View ReDoc at: {BASE_URL}/redoc")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server!")
        print("Make sure the server is running on http://localhost:8000")
        print("Start server with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


if __name__ == "__main__":
    main()

