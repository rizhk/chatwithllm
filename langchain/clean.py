with open('requirements.txt', 'r') as f:
    lines = f.readlines()

cleaned = []
for line in lines:
    # Remove everything after "@" including "@"
    package = line.split('@')[0].strip()
    if package:
        cleaned.append(package + '\n')

with open('requirements-clean.txt', 'w') as f:
    f.writelines(cleaned)