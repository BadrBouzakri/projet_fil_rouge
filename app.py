from flask import Flask, render_template, request, redirect, url_for, session, flash
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Nécessaire pour les sessions et les messages flash

# Liste des joueurs avec leurs pourcentages de réussite
all_players = {
    "Badr": 70, "Aymane": 90, "Yassine": 80, "Mounir": 60,
    "Luis": 50, "Mehdi": 90, "Tano": 90, "Elie": 85,
    "Jeremy": 80, "Abdelilah": 65, "Malik": 75, "Abdel": 80,
    "Houcine": 70, "Saber": 80, "Sandra": 65, "Nadir": 80,
    "Jalal": 70, "Younes": 80, "Naim": 70, "Meh": 80, "Mehdi le r": 90,
    "Vincent": 70, "Kevin": 70, "Saad": 80, "Aziz": 90, "Abdallah": 70
}

# Fonction d'équilibrage des équipes
def balance_teams(selected_players):
    sorted_players = sorted(selected_players, key=lambda player: all_players[player], reverse=True)
    team1, team2 = [], []
    team1_score, team2_score = 0, 0

    for player in sorted_players:
        if team1_score <= team2_score:
            team1.append(player)
            team1_score += all_players[player]
        else:
            team2.append(player)
            team2_score += all_players[player]
    return team1, team2

# Route principale
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_players = request.form.getlist('players')

        if len(selected_players) != 10:
            flash('Veuillez sélectionner 10 joueurs.')
            return redirect(url_for('index'))

        team1, team2 = balance_teams(selected_players)
        session['team1'], session['team2'] = team1, team2
        return redirect(url_for('teams'))

    return render_template('index.html', all_players=all_players)

# Route pour afficher les équipes
@app.route('/teams')
def teams():
    if 'team1' not in session or 'team2' not in session:
        flash('Les équipes n\'ont pas été générées. Veuillez sélectionner les joueurs.')
        return redirect(url_for('index'))
    return render_template('teams.html', team1=session['team1'], team2=session['team2'])

# Route pour la page de connexion à l'administration
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_console'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect')
            return render_template('admin.html', error=True)

    return render_template('admin.html')

# Console d'administration pour ajouter des joueurs
@app.route('/admin/console', methods=['GET', 'POST'])
def admin_console():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))

    if request.method == 'POST':
        new_player = request.form['player_name']
        new_score = request.form['player_score']

        if new_player and new_score:
            all_players[new_player] = int(new_score)
            flash(f'Le joueur {new_player} a été ajouté avec un score de {new_score}')
            return redirect(url_for('admin_console'))
        else:
            flash('Veuillez entrer un nom et un score valides.')

    return render_template('admin_console.html', players=all_players)

# Route pour se déconnecter de l'administration
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Vous avez été déconnecté de l\'administration.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
