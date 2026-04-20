import re

with open('dashboard/taxonomy.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace hardcoded text
content = content.replace('Thang đo 5 cấp độ', 'Thang đo cấp bậc năng lực')
content = content.replace('Taxonomy v2.2.0', 'Taxonomy v2.3 API-Driven')
content = content.replace('Building 21, ABB\n                2016, ABB 4C 2024', 'FNX SSOT System')
content = content.replace('Building 21, ABB 2016, ABB 4C 2024', 'FNX SSOT System')
content = content.replace('v2.2', 'v2.3')

# Extract script block and delete it
script_pattern = re.compile(r'<script>.*?</script>', re.DOTALL)
content = script_pattern.sub('<script src="taxonomy_ui.js"></script>', content)

with open('dashboard/taxonomy.html', 'w', encoding='utf-8') as f:
    f.write(content)
