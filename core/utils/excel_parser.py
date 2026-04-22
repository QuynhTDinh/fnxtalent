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
        
        # --- AUTO-TAGGING ENGINE ---
        role_lower = role.lower()
        group_tag = "Unknown"
        
        # Heuristics for Ban QLDA
        if any(k in role_lower for k in ['dự án', 'qlda', 'project', 'pm']):
            group_tag = "Ban QLDA"
        # Heuristics for Front-line
        elif any(k in role_lower for k in ['kinh doanh', 'bán hàng', 'sales', 'marketing', 'khách hàng', 'truyền thông', 'cs', 'retail']):
            group_tag = "Front-line"
        # Heuristics for Support
        elif any(k in role_lower for k in ['nhân sự', 'hr', 'hành chính', 'admin', 'kế toán', 'tài chính', 'finance', 'pháp chế', 'mua sắm', 'procurement']):
            group_tag = "Support"
        # Default to Operations if technical words or fallback
        elif any(k in role_lower for k in ['kỹ', 'sư', 'vận hành', 'sản xuất', 'scada', 'cơ', 'điện', 'hóa', 'nhà máy', 'operator', 'engineer', 'tech', 'bảo dưỡng']):
            group_tag = "Operations/Technical"
        else:
            # Fallback for PVCFC is likely Operations or Support
            group_tag = "Operations/Technical"
            
        if role not in clusters:
            clusters[role] = {
                "title": role,
                "group_tag": group_tag,
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
