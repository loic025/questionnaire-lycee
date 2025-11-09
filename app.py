from flask import Flask, request, jsonify, send_from_directory
import csv, os, json
import gspread
from google.oauth2.service_account import Credentials

# ✅ Ajoute ici :
def append_to_google_sheet(data, target="college"):
    try:
        if target == "lycee":
            SHEET_ID = "lEytg3QTMRzu4jYP2QotmVE8XuZCt_l4Ts1Lznf415k"  # ID Google Sheet lycée
        else:
            SHEET_ID = "1VpoN3BzCza5XPxyErQ8BGvNM9lRbnZtSsHQUql-Hikw"  # ID Google Sheet collège

    # Connexion à Google Sheets
    creds = Credentials.from_service_account_file("credentials.json", scopes=[
        "https://www.googleapis.com/auth/spreadsheets"
    ])
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1

        sheet.append_row(list(data.values()))
        print(f"[GOOGLE SHEET] Données envoyées ({target}) ✅")

    except Exception as e:
        print(f"[GOOGLE SHEET] Erreur lors de l'envoi ({target}) ❌ : {e}")

DATA_FILE = 'donnees.csv'
# Tu peux aussi définir ce mot de passe dans Render (Environment Variables) sous RESET_PASSWORD
RESET_PASSWORD = os.environ.get('RESET_PASSWORD', 'enseignant2024')


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/analyse')
def analyse():
    return send_from_directory('.', 'analyse.html')

@app.route('/submit_lycee', methods=['POST'])
def submit_lycee():
    data = request.get_json() or {}
    print(f"[SUBMIT LYCÉE] reçu {len(data)} champs")

    try:
        # On enregistre dans un fichier différent
        if os.path.exists("data_lycee.json"):
            with open("data_lycee.json", "r", encoding="utf-8") as f:
                all_data = json.load(f)
        else:
            all_data = []

        all_data.append(data)

        with open("data_lycee.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        append_to_google_sheet(data, target="lycee")

        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Erreur enregistrement lycée: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/data_lycee')
def data_lycee():
    try:
        if os.path.exists("data_lycee.json"):
            with open("data_lycee.json", "r", encoding="utf-8") as f:
                return jsonify(json.load(f))
        else:
            return jsonify([])
    except Exception as e:
        print(f"Erreur lecture data_lycee: {e}")
        return jsonify({"error": str(e)}), 500



@app.route('/reset_lycee', methods=['POST'])
def reset_lycee():
    payload = request.get_json() or {}
    pwd = payload.get('password', '')
    if pwd != RESET_PASSWORD:
        return jsonify({'status': 'error', 'message': 'Mot de passe incorrect.'}), 403

    # Réinitialise le fichier JSON du lycée
    if os.path.exists("data_lycee.json"):
        os.remove("data_lycee.json")

    return jsonify({'status': 'ok', 'message': 'Fichier lycée réinitialisé.'})


# Route statique pour le logo etc.
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

