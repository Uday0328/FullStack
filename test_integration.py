"""Full integration test of all endpoints."""
import urllib.request, urllib.parse, json, http.cookiejar

base = "http://127.0.0.1:5000"

print("=" * 50)
print("PORTFOLIO INTEGRATION TEST")
print("=" * 50)

# Test 1: Home page
r = urllib.request.urlopen(base + "/")
body = r.read().decode()
print(f"\n[1] Home page: {r.status} OK")
print(f"    Body length: {len(body)} bytes")
for section in ["hero", "about", "skills", "projects", "publication", "certifications", "contact"]:
    found = f'id="{section}"' in body
    print(f"    Section #{section}: {'FOUND' if found else 'MISSING!'}")

# Test 2: Projects API
r = urllib.request.urlopen(base + "/api/projects")
data = json.loads(r.read())
print(f"\n[2] Projects API: {data['count']} projects")
for p in data["projects"]:
    print(f"    - {p['title']} (featured={p['is_featured']}, status={p['status']})")

# Test 3: Contact API
payload = json.dumps({"name": "IntegrationTest", "email": "test@test.com", "message": "Automated test"}).encode()
req = urllib.request.Request(base + "/api/contact", data=payload, headers={"Content-Type": "application/json"}, method="POST")
r = urllib.request.urlopen(req)
d = json.loads(r.read())
print(f"\n[3] Contact API: success={d['success']}")

# Test 4: Admin login flow
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cj),
    urllib.request.HTTPRedirectHandler()
)

# GET login page first
opener.open(base + "/admin/login")

# POST login
login_data = urllib.parse.urlencode({"username": "admin", "password": "Admin@2026"}).encode()
resp = opener.open(urllib.request.Request(base + "/admin/login", data=login_data, method="POST"))
final_url = resp.geturl()
dash_body = resp.read().decode()

if "admin" in final_url.lower() and "login" not in final_url.lower():
    print(f"\n[4] Admin login: SUCCESS (URL: {final_url})")
    print(f"    Has projects table: {'admin-table' in dash_body}")
    print(f"    Has stats cards: {'admin-stat-card' in dash_body}")
    print(f"    Has messages section: {'Recent Messages' in dash_body}")
else:
    print(f"\n[4] Admin login: FAILED - Final URL: {final_url}")
    print(f"    Body snippet: {dash_body[:300]}")

# Test 5: Admin dashboard direct (note: route is /admin/ not /admin/dashboard)
try:
    resp = opener.open(base + "/admin/")
    dash = resp.read().decode()
    print(f"\n[5] Dashboard access: {resp.status}")
    print(f"    Contains projects: {'Silent Help' in dash}")
except Exception as e:
    print(f"\n[5] Dashboard: ERROR - {e}")

# Test 6: Add project page
try:
    resp = opener.open(base + "/admin/projects/add")
    print(f"\n[6] Add project page: {resp.status}")
except Exception as e:
    print(f"\n[6] Add project: ERROR - {e}")

# Test 7: Messages page
try:
    resp = opener.open(base + "/admin/messages")
    msgs = resp.read().decode()
    print(f"\n[7] Messages page: {resp.status}")
    print(f"    Contains table: {'admin-table' in msgs}")
except Exception as e:
    print(f"\n[7] Messages: ERROR - {e}")

# Test 8: 404 page
try:
    urllib.request.urlopen(base + "/nonexistent")
except urllib.error.HTTPError as e:
    body404 = e.read().decode()
    print(f"\n[8] 404 page: status={e.code}, styled={'404' in body404}")

print("\n" + "=" * 50)
print("ALL TESTS COMPLETE")
print("=" * 50)
