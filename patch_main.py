import re

with open('api/main.py', 'r') as f:
    content = f.read()

target = '''        @app.get("/audit")
        async def serve_audit():
            return FileResponse(os.path.join(dashboard_dir, "audit.html"))'''

replacement = '''        @app.get("/audit")
        async def serve_audit():
            return FileResponse(os.path.join(dashboard_dir, "audit.html"))

        @app.get("/taxonomy")
        async def serve_taxonomy():
            return FileResponse(os.path.join(dashboard_dir, "taxonomy.html"))'''

if target in content:
    content = content.replace(target, replacement)
    with open('api/main.py', 'w') as f:
        f.write(content)
    print("Patched successfully")
else:
    print("Target not found")
