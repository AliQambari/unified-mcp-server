import requests

# Call tools via REST API
response = requests.post("http://localhost:8002/api/tools/add", 
                        json={"arguments": {"a": 15, "b": 27}})
print("Addition:", response.json())

response = requests.post("http://localhost:8002/api/tools/list_tables", 
                        json={"arguments": {"db_type": "postgres", "db_name": "kmp"}})
print("Tables:", response.json())

# Get resources
response = requests.get("http://localhost:8002/api/resources/get_config")
print("Config:", response.json())
