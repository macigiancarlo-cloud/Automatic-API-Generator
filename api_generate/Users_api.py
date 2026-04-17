# === ATTENTION: DEMO VERSION ===
# This version generates only 1 table.
# Purchase the full version to unlock all features.
# ==============================

from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def get_connection():
    return sqlite3.connect('database.db')

# --- AUTOMATIC DOCUMENTATION ---
@app.route('/docs', methods=['GET'])
def documentation():
    html = f"""
    <h1>API Documentation: Users</h1>
    <p>Base URL: /Users</p>
    
    <h2>Available Endpoints:</h2>
    <ul>
        <li><b>GET</b> /Users - Read all records</li>
        <li><b>POST</b> /Users - Create a new record</li>
        <li><b>DELETE</b> /Users/&lt;id&gt; - Delete a record</li>
    </ul>
    
    <h3>JSON Example for insertion (POST):</h3>
    <pre>
    {{
        "required_fields": [['nome', 'email']],
        "example": {{
            "nome": "value", "email": "value"
        }}
    }}
    </pre>
    """
    return html

# --- GET ALL (Read all) ---
@app.route('/Users', methods=['GET'])
def api_get_all_Users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users")
    rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

# --- POST (Create new) ---
@app.route('/Users', methods=['POST'])
def api_add_Users():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Users (nome, email) VALUES (?, ?)", tuple(data[col] for col in [['nome', 'email']]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Insert successful"}), 201

# --- DELETE (Delete by ID) ---
@app.route('/Users/<int:id>', methods=['DELETE'])
def api_delete_Users(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Users WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deletion successful"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
