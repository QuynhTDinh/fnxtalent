"""
Excel / CSV Parser Utility.
Parses CSV Org Chart files to cluster employees by Role for batch auditing.
"""

import csv
import io

def parse_org_chart_csv(file_content: bytes) -> dict:
    """
    Parses a CSV file containing employee Org Chart data.
    Expected columns: ID, Name, Role, Department (optional), JD (optional)
    
    Returns a dictionary of clustered roles:
    {
        "roles": [
            {
                "title": "Chuyên viên Kỹ thuật",
                "employee_count": 2,
                "employees": [{"id": "E1", "name": "Nguyen A"}],
                "jd": "..."
            }
        ]
    }
    """
    # Decode bytes to string
    try:
        content_str = file_content.decode('utf-8')
    except UnicodeDecodeError:
        content_str = file_content.decode('latin1')
        
    reader = csv.DictReader(io.StringIO(content_str))
    
    # Try mapping column names flexibly
    fieldnames = reader.fieldnames if reader.fieldnames else []
    
    id_col = next((f for f in fieldnames if f.lower() in ['id', 'mã nv', 'employee id']), 'id')
    name_col = next((f for f in fieldnames if f.lower() in ['name', 'tên', 'họ và tên', 'full name']), 'name')
    role_col = next((f for f in fieldnames if f.lower() in ['role', 'chức danh', 'title', 'position']), 'role')
    jd_col = next((f for f in fieldnames if f.lower() in ['jd', 'mô tả công việc', 'description']), 'jd')
    
    clusters = {}
    
    for row in reader:
        role = row.get(role_col, '').strip()
        if not role:
            continue
            
        emp_id = row.get(id_col, '').strip()
        emp_name = row.get(name_col, '').strip()
        jd = row.get(jd_col, '').strip()
        
        if role not in clusters:
            clusters[role] = {
                "title": role,
                "employee_count": 0,
                "employees": [],
                "jd": jd
            }
            
        clusters[role]["employees"].append({
            "id": emp_id,
            "name": emp_name
        })
        clusters[role]["employee_count"] += 1
        
        # Keep longest JD found if multiple exists
        if len(jd) > len(clusters[role]["jd"]):
            clusters[role]["jd"] = jd
            
    # Convert clusters to list
    result = {
        "roles": list(clusters.values())
    }
    
    return result
