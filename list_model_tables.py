import os
import re

model_dir = 'backend/app/models'
tables = []

for f in os.listdir(model_dir):
    if f.endswith('.py') and f != '__init__.py':
        file_path = os.path.join(model_dir, f)
        with open(file_path, 'r') as file:
            content = file.read()
            # Find all __tablename__ = "name" or 'name'
            matches = re.findall(r'__tablename__\s*=\s*[\"\']([^\"\']+)[\"\']', content)
            tables.extend(matches)
            print(f"{f}: {matches}")

print(f"\nTotal tables defined in models: {len(tables)}")
print(f"Unique tables: {sorted(list(set(tables)))}")
