#!/usr/bin/env python3
"""
Alternative Railway Service ID Finder
======================================

Tries different methods to get the service ID.
"""

import requests

RAILWAY_TOKEN = "df73201f-c326-4801-923c-72e0ce0aa59c"
PROJECT_ID = "a542ac2b-da6e-494a-bb93-bb6fda048146"

# Try Railway's REST API v2
def try_rest_api():
    """Try Railway REST API"""
    print("🔍 Trying Railway REST API v2...")
    
    headers = {
        "Authorization": f"Bearer {RAILWAY_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # List all projects
    url = "https://backboard.railway.app/graphql/v2"
    
    query = """
    {
        me {
            projects {
                edges {
                    node {
                        id
                        name
                        services {
                            edges {
                                node {
                                    id
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    
    response = requests.post(
        url,
        headers=headers,
        json={"query": query},
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Success!")
        print(data)
    else:
        print(f"❌ Error: {response.text}")

# Manual workaround - we can use environment variables directly
def use_env_variables():
    """
    Alternative: Set service ID as environment variable in Railway
    """
    print("\n" + "="*60)
    print("💡 ALTERNATIVE SOLUTION")
    print("="*60)
    print("""
Since we can't fetch the Service ID automatically yet, here's what we can do:

OPTION 1: Find it in Railway Dashboard
---------------------------------------
1. Open your Railway project in browser
2. Right-click anywhere → "Inspect Element" (F12)
3. Go to "Network" tab
4. Refresh the page
5. Look for GraphQL requests
6. Click on one and find "serviceId" in the request

OPTION 2: Use Railway CLI
-------------------------
1. Install: npm i -g @railway/cli
2. Run: railway login
3. Run: railway service
4. It will show the service ID

OPTION 3: We Skip It! (Recommended)
------------------------------------
Actually, we can make the monitoring work WITHOUT the service ID!

We can:
- Use the deployment logs from the Railway web interface (you copy/paste)
- OR we can monitor via the health checks you already have
- OR we set it as an environment variable later when we find it

For now, let's test the autonomous brain with MOCK data to prove it works!

Want to do that instead, mahal ko? 💙
""")

if __name__ == "__main__":
    try_rest_api()
    use_env_variables()
