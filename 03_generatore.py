import sqlite3
import os

# File names
DB_FILE = 'database.db'
TEMPLATE_FILE = 'template_api.txt'
OUTPUT_FOLDER = 'api_generate'

# --- DEMO VERSION LIMITS ---
MAX_TABLES = 1
WATERMARK_DEMO = "# === ATTENTION: DEMO VERSION ===\n# This version generates only 1 table.\n# Purchase the full version to unlock all features.\n# ==============================\n\n"
# -----------------------------

# Create output folder if it doesn't exist
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)
    print("Output folder created.")

# Read the template
with open(TEMPLATE_FILE, 'r') as f:
    template_content = f.read()

# Connect to DB
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Ask DB for table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

tables_generated = 0

# Generate code for each table
for table in tables:
    table_name = table[0]
    
    # Ignore system tables
    if table_name.startswith('sqlite_'):
        continue

    # --- DEMO LIMIT CHECK ---
    if tables_generated >= MAX_TABLES:
        print(f"(!) DEMO LIMIT REACHED: Table '{table_name}' was NOT generated.")
        continue
    # ------------------------

    print(f"Analyzing table: {table_name}")

    # 1. Get column info
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_raw = cursor.fetchall()
    
    # 2. Extract column names
    column_names = []
    for col in columns_raw:
        if col[5] == 0: column_names.append(col[1])

    # 3. Build dynamic strings
    str_columns = ", ".join(column_names)
    str_placeholder = ", ".join(["?"] * len(column_names))
    str_set = ", ".join([f"{col} = ?" for col in column_names])
    str_columns_list = str(column_names)
    
    # JSON Example
    json_example_parts = []
    for col in column_names:
        json_example_parts.append(f'"{col}": "value"')
    str_json_example = ", ".join(json_example_parts)

    # Replace placeholders in template
    generated_code = template_content.replace('{{NOME_TABELLA}}', table_name)
    generated_code = generated_code.replace('{{COLONNE}}', str_columns)
    generated_code = generated_code.replace('{{PLACEHOLDER}}', str_placeholder)
    generated_code = generated_code.replace('{{SET}}', str_set)
    generated_code = generated_code.replace('{{COLONNE_LIST}}', str_columns_list)
    generated_code = generated_code.replace('{{JSON_EXAMPLE}}', str_json_example)

    # --- ADD DEMO WATERMARK ---
    generated_code = WATERMARK_DEMO + generated_code
    # --------------------------

    # Save the new file
    output_filename = os.path.join(OUTPUT_FOLDER, f"{table_name}_api.py")
    
    with open(output_filename, 'w') as f:
        f.write(generated_code)
        
    print(f"   File created: {output_filename}")
    
    tables_generated += 1

conn.close()

# --- FINAL DEMO MESSAGE ---
if tables_generated >= MAX_TABLES:
    print("\n" + "="*40)
    print("NOTIFICATION: You are using the DEMO VERSION.")
    print(f"The limit is {MAX_TABLES} table(s) generated.")
    print("Purchase the full version to generate all tables.")
    print("="*40 + "\n")
# --------------------------
