import requests
import os

# live testing

BASE_URL = "http://localhost:8000"

def create_test_file():
    """Create a simple test assignment file"""
    test_content = """
    Assignment: Write an essay about climate change
    
    Instructions:
    1. Research the causes of climate change
    2. Discuss the impacts on the environment
    3. Propose solutions
    
    Length: 500 words
    Due date: Next week
    """
    
    with open("test_assignment.txt", "w") as f:
        f.write(test_content)
    
    return "test_assignment.txt"

def test_api_health():
    """Testing if API is running"""
    try:
        response = requests.get(BASE_URL)
        print("API Health Check:")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("-" * 50)
        return True
    except requests.exceptions.ConnectionError:
        print("API is not running")
        return False

def test_with_file():
    """test with file upload"""
    test_file = create_test_file()
    
    try:
        with open(test_file, "rb") as f:
            files = {"assignment_file": (test_file, f, "text/plain")}
            data = {"grade_level": "10th"}
            print("\ntesting file upload")
            response = requests.post(f"{BASE_URL}/generate", files=files, data=data)
            
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\nassignments generated:")
            for i, assignment in enumerate(result['results'], 1):
                print(f"\n Assignment Idea {i} ")
                print(f"Idea: {assignment['assignment_idea']}")
                print(f"Explanation: {assignment['explanation']}")
        else:
            print(f"error: {response.json()}")
            
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    if test_api_health():
        test_with_file()
