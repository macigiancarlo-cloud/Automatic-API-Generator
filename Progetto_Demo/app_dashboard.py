from flask import Flask, render_template
import sqlite3
import os

app = Flask(__name__)
DB_FILE = 'database.db'
OUTPUT_FOLDER = 'api_generate'
TEMPLATE_FILE = 'template_api.txt'

# Funzione per leggere il template (preso dal vecchio script)
def leggi_template():
    with open(TEMPLATE_FILE, 'r') as f:
        return f.read()

# Funzione per generare il codice (presa dal vecchio script)
def esegui_generazione():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    template_content = leggi_template()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelle = cursor.fetchall()
    
    files_creati = []

    for tabella in tabelle:
        nome_tabella = tabella[0]
        if nome_tabella.startswith('sqlite_'):
            continue

        # Stessa logica di prima per colonne e set
        cursor.execute(f"PRAGMA table_info({nome_tabella})")
        colonne_raw = cursor.fetchall()
        nomi_colonne = []
        for col in colonne_raw:
            if col[5] == 0:
                nomi_colonne.append(col[1])
        
        stringa_colonne = ", ".join(nomi_colonne)
        stringa_placeholder = ", ".join(["?"] * len(nomi_colonne))
        stringa_set = ", ".join([f"{col} = ?" for col in nomi_colonne])
        stringa_colonne_list = str(nomi_colonne)

        # Sostituzioni
        codice_generato = template_content.replace('{{NOME_TABELLA}}', nome_tabella)
        codice_generato = codice_generato.replace('{{COLONNE}}', stringa_colonne)
        codice_generato = codice_generato.replace('{{PLACEHOLDER}}', stringa_placeholder)
        codice_generato = codice_generato.replace('{{SET}}', stringa_set)
        codice_generato = codice_generato.replace('{{COLONNE_LIST}}', stringa_colonne_list)

        # Salvataggio
        nome_file_output = os.path.join(OUTPUT_FOLDER, f"{nome_tabella}_api.py")
        with open(nome_file_output, 'w') as f:
            f.write(codice_generato)
        
        files_creati.append(nome_tabella)

    conn.close()
    return files_creati

# Route Home (Pagina principale)
@app.route('/')
def index():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelle_raw = cursor.fetchall()
    
    lista_tabelle = []
    for t in tabelle_raw:
        nome = t[0]
        if nome.startswith('sqlite_'): continue
        # Prendiamo le colonne per mostrarle
        cursor.execute(f"PRAGMA table_info({nome})")
        colonne = ", ".join([col[1] for col in cursor.fetchall()])
        lista_tabelle.append({'nome': nome, 'colonne': colonne})
    
    conn.close()
    return render_template('index.html', tabelle=lista_tabelle)

# Route Generazione (Pulsante)
@app.route('/genera')
def genera():
    creati = esegui_generazione()
    # Ricarichiamo i dati per mostrare la pagina
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelle_raw = cursor.fetchall()
    lista_tabelle = []
    for t in tabelle_raw:
        nome = t[0]
        if nome.startswith('sqlite_'): continue
        cursor.execute(f"PRAGMA table_info({nome})")
        colonne = ", ".join([col[1] for col in cursor.fetchall()])
        lista_tabelle.append({'nome': nome, 'colonne': colonne})
    conn.close()
    
    return render_template('index.html', tabelle=lista_tabelle, msg=f"Generazione completata! File creati per: {', '.join(creati)}")

if __name__ == '__main__':
    app.run(debug=True, port=5001)
