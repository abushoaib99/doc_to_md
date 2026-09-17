import os
from markitdown import MarkItDown

# 1. Define your input and output directories
input_dir = "/home/souyeb/Documents/Development/doc_to_md/documents"
output_dir = "/home/souyeb/Documents/Development/doc_to_md/outputs"
os.makedirs(output_dir, exist_ok=True)

# 2. Get all full file paths from the input folder
file_list = [
    os.path.join(input_dir, f) 
    for f in os.listdir(input_dir) 
    if os.path.isfile(os.path.join(input_dir, f))
]

# 3. Initialize MarkItDown
md = MarkItDown()

print(f"Found {len(file_list)} files to convert in '{input_dir}'.")

# 4. Iterate and convert each file
for file_path in file_list:
    file_name = os.path.basename(file_path)
    base_name, _ = os.path.splitext(file_name)
    print("base_name:: ", base_name)
    output_path = os.path.join(output_dir, f"{base_name}.md")

    try:
        result = md.convert(file_path)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result.text_content)
            
        print(f"✓ Converted: {file_name} -> {output_path}")
    except Exception as e:
        print(f"✗ Failed to convert {file_name}: {e}")