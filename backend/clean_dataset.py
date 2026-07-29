import os

input_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mahGRs", "GR_combine", "english_all.txt")
output_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mahGRs", "GR_combine", "english_all_cleaned.txt")

def extract_real_department(content_lines):
    # Scan the first 25 lines of the GR content to find the real department name
    for line in content_lines[:25]:
        line_lower = line.lower()
        if "department" in line_lower and "resolution" not in line_lower and "circular" not in line_lower:
            if len(line.split()) <= 15:
                return line.strip()
    return "Unknown Department"

def process_file():
    print(f"Reading from: {input_file}")
    print(f"Writing to: {output_file}")
    
    processed_count = 0
    with open(input_file, "r", encoding="utf-8") as fin, open(output_file, "w", encoding="utf-8") as fout:
        buffer = []
        in_gr = False
        department_line_index = -1
        
        for line in fin:
            if line.startswith("GR No. :"):
                # If we already have a buffered GR, process and write it
                if buffer:
                    content_lines = []
                    header_end = False
                    for b_line in buffer:
                        if header_end and b_line.strip():
                            content_lines.append(b_line)
                        if b_line.startswith("===================================================================================================="):
                            header_end = True
                    
                    real_dept = extract_real_department(content_lines)
                    if department_line_index != -1:
                        buffer[department_line_index] = f"Department : {real_dept}\n"
                    
                    fout.writelines(buffer)
                    processed_count += 1
                    if processed_count % 1000 == 0:
                        print(f"Processed {processed_count} GRs...")
                
                # Start new buffer for the new GR
                buffer = [line]
                in_gr = True
                department_line_index = -1
            elif in_gr:
                buffer.append(line)
                if line.startswith("Department :"):
                    department_line_index = len(buffer) - 1
            else:
                # Write any lines before the very first GR directly
                fout.write(line)
                
        # Process the very last GR in the file
        if buffer:
            content_lines = []
            header_end = False
            for b_line in buffer:
                if header_end and b_line.strip():
                    content_lines.append(b_line)
                if b_line.startswith("===================================================================================================="):
                    header_end = True
            
            real_dept = extract_real_department(content_lines)
            if department_line_index != -1:
                buffer[department_line_index] = f"Department : {real_dept}\n"
            
            fout.writelines(buffer)
            processed_count += 1

    print(f"✅ Successfully cleaned {processed_count} GRs!")
    print(f"File saved to: {output_file}")

if __name__ == "__main__":
    process_file()
