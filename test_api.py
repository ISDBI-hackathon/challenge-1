import requests
import json

def test_accounting_api():
    url = "http://localhost:8000/generate-entries"
    
    # Test case 1: Ijarah MBT
    payload = {
        "input_text": """On 1 January 2019 Alpha Islamic bank (Lessee) entered into an Ijarah MBT arrangement with Super Generators for Ijarah of a heavy-duty generator purchase by Super Generators at a price of USD 450,000. Super Generators has also paid USD 12,000 as import tax and US 30,000 for freight charges. The Ijarah Term is 02 years and expected residual value at the end USD 5,000. At the end of Ijarah Term, it is highly likely that the option of transfer of ownership of the underlying asset to the lessee shall be exercised through purchase at a price of USD 3,000. Alpha Islamic Bank will amortize the right of use on yearly basis and it is required to pay yearly rental of USD 300,000.""",
        "fas_standard": "FAS32"
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Pretty print the response
        print("\nResponse Status:", response.status_code)
        print("\nResponse Headers:", json.dumps(dict(response.headers), indent=2))
        print("\nResponse Body:", json.dumps(response.json(), indent=2))
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response text: {e.response.text}")

if __name__ == "__main__":
    test_accounting_api() 