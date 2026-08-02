import os

search_dir = r"C:\Users\dhira"
target = "overleaf"

print("Searching...")
try:
    for root, dirs, files in os.walk(search_dir):
        # Skip some dirs to be fast
        if ".git" in root or "node_modules" in root or "venv" in root:
            continue
        for file in files:
            if file.endswith(".md") or file.endswith(".txt") or file.endswith(".tex"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read().lower()
                        if target in content:
                            print(f"Found in: {path}")
                except Exception:
                    pass
except Exception as e:
    print(e)
print("Done")
