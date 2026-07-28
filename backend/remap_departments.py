import os
import re
import difflib
from collections import defaultdict

input_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mahGRs", "GR_combine", "english_all_cleaned.txt")
output_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mahGRs", "GR_combine", "english_all_mapped.txt")

ALLOWED_DEPTS = [
    "Agriculture, Dairy Development, Animal Husbandry and Fisheries Department",
    "Co-operation, Textiles and Marketing Department",
    "Environment Department",
    "Finance Department",
    "Food, Civil Supplies and Consumer Protection Department",
    "General Administration Department",
    "Higher and Technical Education Department",
    "Home Department",
    "Housing Department",
    "Industries, Energy and Labour Department",
    "Information Technology Department",
    "Law and Judiciary Department",
    "Marathi Language Department",
    "Medical Education and Drugs Department",
    "Minorities Development Department",
    "Other Backward Bahujan Welfare Department",
    "Parliamentary Affairs Department",
    "Persons with Disabilities Welfare Department",
    "Planning Department",
    "Public Health Department",
    "Public Works Department",
    "Revenue and Forest Department",
    "Rural Development Department",
    "School Education and Sports Department",
    "Skill Development and Entrepreneurship Department",
    "Social Justice and Special Assistance Department",
    "Soil and Water Conservation Department",
    "Tourism and Cultural Affairs Department",
    "Tribal Development Department",
    "Urban Development Department",
    "Water Resources Department",
    "Water Supply and Sanitation Department",
    "Women and Child Development Department"
]

def clean_string(s):
    s = re.sub(r'[^a-zA-Z0-9\s]', '', s)
    return s.lower().strip()

cleaned_allowed = {clean_string(d): d for d in ALLOWED_DEPTS}

keyword_map = {
    "agriculture": ALLOWED_DEPTS[0],
    "animal husbandry": ALLOWED_DEPTS[0],
    "dairy": ALLOWED_DEPTS[0],
    "fisher": ALLOWED_DEPTS[0],
    "co-operation": ALLOWED_DEPTS[1],
    "cooperation": ALLOWED_DEPTS[1],
    "textile": ALLOWED_DEPTS[1],
    "marketing": ALLOWED_DEPTS[1],
    "environment": ALLOWED_DEPTS[2],
    "climate": ALLOWED_DEPTS[2],
    "finance": ALLOWED_DEPTS[3],
    "food": ALLOWED_DEPTS[4],
    "civil supplies": ALLOWED_DEPTS[4],
    "consumer": ALLOWED_DEPTS[4],
    "general administration": ALLOWED_DEPTS[5],
    "higher": ALLOWED_DEPTS[6],
    "technical education": ALLOWED_DEPTS[6],
    "home": ALLOWED_DEPTS[7],
    "housing": ALLOWED_DEPTS[8],
    "industr": ALLOWED_DEPTS[9],
    "energy": ALLOWED_DEPTS[9],
    "labour": ALLOWED_DEPTS[9],
    "information technology": ALLOWED_DEPTS[10],
    "law": ALLOWED_DEPTS[11],
    "judiciary": ALLOWED_DEPTS[11],
    "marathi": ALLOWED_DEPTS[12],
    "medical": ALLOWED_DEPTS[13],
    "drugs": ALLOWED_DEPTS[13],
    "minorities": ALLOWED_DEPTS[14],
    "minority": ALLOWED_DEPTS[14],
    "backward": ALLOWED_DEPTS[15],
    "bahujan": ALLOWED_DEPTS[15],
    "parliamentary": ALLOWED_DEPTS[16],
    "disabilities": ALLOWED_DEPTS[17],
    "divyang": ALLOWED_DEPTS[17],
    "planning": ALLOWED_DEPTS[18],
    "public health": ALLOWED_DEPTS[19],
    "public works": ALLOWED_DEPTS[20],
    "revenue": ALLOWED_DEPTS[21],
    "forest": ALLOWED_DEPTS[21],
    "rural": ALLOWED_DEPTS[22],
    "school": ALLOWED_DEPTS[23],
    "sports": ALLOWED_DEPTS[23],
    "skill": ALLOWED_DEPTS[24],
    "entrepreneurship": ALLOWED_DEPTS[24],
    "social justice": ALLOWED_DEPTS[25],
    "soil": ALLOWED_DEPTS[26],
    "water conservation": ALLOWED_DEPTS[26],
    "tourism": ALLOWED_DEPTS[27],
    "cultural": ALLOWED_DEPTS[27],
    "tribal": ALLOWED_DEPTS[28],
    "urban": ALLOWED_DEPTS[29],
    "water resources": ALLOWED_DEPTS[30],
    "water supply": ALLOWED_DEPTS[31],
    "sanitation": ALLOWED_DEPTS[31],
    "women": ALLOWED_DEPTS[32],
    "child": ALLOWED_DEPTS[32]
}

def get_best_match(raw_dept):
    raw_clean = clean_string(raw_dept)
    if not raw_clean or raw_clean == "unknown department":
        return None
        
    if raw_clean in cleaned_allowed:
        return cleaned_allowed[raw_clean]
        
    for kw, target_dept in keyword_map.items():
        if kw in raw_clean:
            return target_dept
            
    matches = difflib.get_close_matches(raw_clean, cleaned_allowed.keys(), n=1, cutoff=0.6)
    if matches:
        return cleaned_allowed[matches[0]]
        
    return None

def process():
    dept_counts = defaultdict(int)
    # We want ~11,000 GRs across 33 departments -> approx 333 GRs each
    LIMIT_PER_DEPT = 333
    kept = 0
    scanned = 0
    
    with open(input_file, "r", encoding="utf-8") as fin, open(output_file, "w", encoding="utf-8") as fout:
        buffer = []
        in_gr = False
        department_line_idx = -1
        current_mapped_dept = None
        
        for line in fin:
            if line.startswith("GR No. :"):
                if buffer and current_mapped_dept:
                    if dept_counts[current_mapped_dept] < LIMIT_PER_DEPT:
                        buffer[department_line_idx] = f"Department : {current_mapped_dept}\n"
                        fout.writelines(buffer)
                        dept_counts[current_mapped_dept] += 1
                        kept += 1
                
                buffer = [line]
                in_gr = True
                department_line_idx = -1
                current_mapped_dept = None
                scanned += 1
                
                if scanned % 5000 == 0:
                    print(f"Scanned {scanned} GRs... Kept {kept} so far.")
            elif in_gr:
                buffer.append(line)
                if line.startswith("Department :"):
                    department_line_idx = len(buffer) - 1
                    raw_dept = line.split(":", 1)[1].strip()
                    current_mapped_dept = get_best_match(raw_dept)
            else:
                fout.write(line)
                
        if buffer and current_mapped_dept:
            if dept_counts[current_mapped_dept] < LIMIT_PER_DEPT:
                buffer[department_line_idx] = f"Department : {current_mapped_dept}\n"
                fout.writelines(buffer)
                dept_counts[current_mapped_dept] += 1
                kept += 1
                
    print(f"\nFinished scanning {scanned} GRs!")
    print(f"Kept {kept} GRs cleanly mapped to the 33 official departments.")
    print("\nDepartment Breakdown:")
    for dept, count in sorted(dept_counts.items(), key=lambda x: x[1], reverse=True):
        print(f" - {dept}: {count}")

if __name__ == "__main__":
    process()
