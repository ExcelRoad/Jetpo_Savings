"""
Test script to explore Gemelnet API data structure
This script will help us understand what data is available before integrating it
"""
import requests
import json

# Gemelnet resource ID from data.gov.il
RESOURCE_ID = "a30dcbea-a1d2-482c-ae29-8f781f5025fb"
API_URL = f"https://data.gov.il/api/3/action/datastore_search"

def test_api_connection():
    """Test basic API connection and get first few records"""
    print("=" * 80)
    print("Testing Gemelnet API Connection")
    print("=" * 80)

    params = {
        'resource_id': RESOURCE_ID,
        'limit': 5  # Get only 5 records to start
    }

    try:
        print(f"\nFetching data from: {API_URL}")
        print(f"Resource ID: {RESOURCE_ID}")
        print(f"Limit: {params['limit']}")
        print("\nMaking request...")

        response = requests.get(API_URL, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Check if the response was successful
            if data.get('success'):
                result = data.get('result', {})
                records = result.get('records', [])
                fields = result.get('fields', [])
                total = result.get('total', 0)

                print(f"\n[SUCCESS] API Connection Successful!")
                print(f"Total records available: {total:,}")
                print(f"Records fetched: {len(records)}")

                # Print field structure
                print(f"\n" + "=" * 80)
                print("AVAILABLE FIELDS")
                print("=" * 80)
                for i, field in enumerate(fields, 1):
                    field_name = field.get('id', 'N/A')
                    field_type = field.get('type', 'N/A')
                    print(f"{i}. {field_name:<40} Type: {field_type}")

                # Print first record as example
                if records:
                    print(f"\n" + "=" * 80)
                    print("SAMPLE RECORD (First Record)")
                    print("=" * 80)
                    print(json.dumps(records[0], indent=2, ensure_ascii=False))

                    # Print all records for inspection
                    print(f"\n" + "=" * 80)
                    print(f"ALL {len(records)} SAMPLE RECORDS")
                    print("=" * 80)
                    for idx, record in enumerate(records, 1):
                        print(f"\n--- Record {idx} ---")
                        for key, value in record.items():
                            if key != '_id':  # Skip internal ID
                                print(f"  {key}: {value}")

                return True
            else:
                print(f"\n[ERROR] API returned unsuccessful response")
                print(f"Response: {json.dumps(data, indent=2)}")
                return False
        else:
            print(f"\n[ERROR] HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("\n[ERROR] Request timed out")
        return False
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"\n[ERROR] Failed to parse JSON: {e}")
        return False

if __name__ == "__main__":
    success = test_api_connection()

    print("\n" + "=" * 80)
    if success:
        print("[SUCCESS] Test completed successfully!")
        print("\nNext steps:")
        print("1. Review the field structure above")
        print("2. Understand what each field represents")
        print("3. Plan how to map this data to our Fund model")
        print("4. Consider which fields we need for our application")
    else:
        print("[ERROR] Test failed - please review the error messages above")
    print("=" * 80)
