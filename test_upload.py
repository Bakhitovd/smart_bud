import requests
import os

# Test file upload to the Smart Budget Companion API
def test_upload():
    url = "http://localhost:8000/api/upload"
    file_path = "sample_data/2025-07-02_transaction_download.csv"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    try:
        with open(file_path, 'rb') as file:
            files = {'file': (os.path.basename(file_path), file, 'text/csv')}
            response = requests.post(url, files=files)
            
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_upload()
