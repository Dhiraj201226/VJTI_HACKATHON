import os
from collections import defaultdict

input_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mahGRs", "GR_combine", "english_all_cleaned.txt")
output_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mahGRs", "GR_combine", "english_all_balanced.txt")

def balance_dataset():
    print(f"Reading from: {input_file}")
    
    dept_counts = defaultdict(int)
    processed_count = 0
    kept_count = 0
    
    with open(input_file, "r", encoding="utf-8") as fin, open(output_file, "w", encoding="utf-8") as fout:
        buffer = []
        in_gr = False
        current_dept = "Unknown Department"
        
        for line in fin:
            if line.startswith("GR No. :"):
                if buffer:
                    # Decide whether to keep the previous GR
                    if dept_counts[current_dept] < 200:
                        fout.writelines(buffer)
                        dept_counts[current_dept] += 1
                        kept_count += 1
                    
                    processed_count += 1
                    if processed_count % 5000 == 0:
                        print(f"Scanned {processed_count} GRs... Kept {kept_count} so far.")
                
                buffer = [line]
                in_gr = True
                current_dept = "Unknown Department"
            elif in_gr:
                buffer.append(line)
                if line.startswith("Department :"):
                    current_dept = line.split(":", 1)[1].strip()
            else:
                fout.write(line)
                
        # Process the last GR
        if buffer:
            if dept_counts[current_dept] < 200:
                fout.writelines(buffer)
                dept_counts[current_dept] += 1
                kept_count += 1
            processed_count += 1

    print(f"\n✅ Finished scanning {processed_count} GRs!")
    print(f"🎉 Kept {kept_count} highly diverse GRs (max 200 per department).")
    print(f"File saved to: {output_file}")
    
    # Print department distribution
    print("\nDepartment Breakdown:")
    for dept, count in sorted(dept_counts.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f" - {dept}: {count}")

if __name__ == "__main__":
    balance_dataset()
