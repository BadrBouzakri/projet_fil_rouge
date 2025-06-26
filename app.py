from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Nécessaire pour les sessions et les messages flash

# Liste des joueurs avec leurs pourcentages de réussite
all_players = {
    "Badr": 70, "Aymane": 90, "Yassine": 80, "Mounir": 60,
    "Luis": 50, "Mehdi": 90, "Tano": 90, "Elie": 85,
    "Jeremy": 80, "Abdelilah": 65, "Malik": 75, "Abdel": 80,
    "Houcine": 70, "Saber": 80, "Sandra": 65, "Nadir": 80,
    "Jalal": 70, "Younes": 80, "Naim": 70, "Meh": 80, "Mehdi le r": 90,
    "Vincent": 70, "Kevin": 70, "Saad": 80, "Aziz": 90, "Abdallah": 70,
    "Youssef": 80, "Rachid": 75, "Hicham": 85, "Omar": 90,
    "Khalid": 80, "Sofiane": 70, "Rachid le r": 75, "Yassine le r": 80,
    "Mohamed": 85, "Hassan": 90, "Rachid
}

# Fonction d'équilibrage des équipes avec plusieurs méthodes
def balance_teams(selected_players, method='skill'):
    """
    Équilibre les équipes selon différentes méthodes:
    - 'skill': équilibrage par niveau de compétence (par défaut)
    - 'random': équipes aléatoires
    - 'snake': méthode "serpent" (1-2-2-1) pour un meilleur équilibre
    """
    if method == 'random':
        # Mélange aléatoire
        random_players = selected_players.copy()
        random.shuffle(random_players)
        half = len(random_players) // 2
        return random_players[:half], random_players[half:]
    
    elif method == 'snake':
        # Méthode serpent (1-2-2-1 etc)
        sorted_players = sorted(selected_players, key=lambda player: all_players[player], reverse=True)
        team1, team2 = [], []
        
        for i, player in enumerate(sorted_players):
            if i % 4 == 0 or i % 4 == 3:  # Positions 0, 3, 4, 7, 8, etc.
                team1.append(player)
            else:  # Positions 1, 2, 5, 6, 9, etc.
                team2.append(player)
                
        return team1, team2
    
    else:  # Par défaut: méthode par niveau de compétence
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
                
        # Retourne les équipes et aussi leurs scores totaux pour l'affichage
        return team1, team2, team1_score, team2_score

# Route principale
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_players = request.form.getlist('players')
        team_method = request.form.get('team_method', 'skill')
        
        if len(selected_players) != 10:
            flash('Veuillez sélectionner 10 joueurs.')
            return redirect(url_for('index'))

        if team_method == 'skill':
            team1, team2, team1_score, team2_score = balance_teams(selected_players, 'skill')
            session['team1_score'], session['team2_score'] = team1_score, team2_score
        elif team_method == 'random':
            team1, team2 = balance_teams(selected_players, 'random')
            # Calculer les scores pour l'affichage
            team1_score = sum(all_players[player] for player in team1)
            team2_score = sum(all_players[player] for player in team2)
            session['team1_score'], session['team2_score'] = team1_score, team2_score
        elif team_method == 'snake':
            team1, team2 = balance_teams(selected_players, 'snake')
            # Calculer les scores pour l'affichage
            team1_score = sum(all_players[player] for player in team1)
            team2_score = sum(all_players[player] for player in team2)
            session['team1_score'], session['team2_score'] = team1_score, team2_score

        session['team1'], session['team2'] = team1, team2
        session['team_method'] = team_method
        return redirect(url_for('teams'))

    current_year = datetime.datetime.now().year
    return render_template('index.html', all_players=all_players, current_year=current_year)

# Route pour afficher les équipes
@app.route('/teams')
def teams():
    if 'team1' not in session or 'team2' not in session:
        flash('Les équipes n\'ont pas été générées. Veuillez sélectionner les joueurs.')
        return redirect(url_for('index'))
    
    # Récupérer les scores des équipes et la méthode utilisée
    team1_score = session.get('team1_score', sum(all_players[player] for player in session['team1']))
    team2_score = session.get('team2_score', sum(all_players[player] for player in session['team2']))
    team_method = session.get('team_method', 'skill')
    
    # Calculer le niveau moyen des équipes et leur écart
    team1_avg = round(team1_score / len(session['team1']))
    team2_avg = round(team2_score / len(session['team2']))
    score_diff = abs(team1_score - team2_score)
    balance_percent = round(100 - (score_diff / ((team1_score + team2_score) / 2) * 100))
    
    current_year = datetime.datetime.now().year
    return render_template('teams.html', 
                          team1=session['team1'], 
                          team2=session['team2'], 
                          team1_score=team1_score,
                          team2_score=team2_score,
                          team1_avg=team1_avg,
                          team2_avg=team2_avg,
                          balance_percent=balance_percent,
                          team_method=team_method,
                          all_players=all_players,
                          current_year=current_year)

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

    current_year = datetime.datetime.now().year
    return render_template('admin.html', current_year=current_year)

# Console d'administration pour ajouter ou supprimer des joueurs
@app.route('/admin/console', methods=['GET', 'POST'])
def admin_console():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))

    if request.method == 'POST':
        # Gestion de l'ajout de joueur
        if 'player_name' in request.form:
            new_player = request.form['player_name']
            new_score = request.form['player_score']

            if new_player and new_score:
                all_players[new_player] = int(new_score)
                flash(f'Le joueur {new_player} a été ajouté avec un score de {new_score}')
                return redirect(url_for('admin_console'))
            else:
                flash('Veuillez entrer un nom et un score valides.')
        
        # Gestion de la suppression de joueur
        elif 'delete_player' in request.form:
            player_to_delete = request.form['delete_player']
            if player_to_delete in all_players:
                del all_players[player_to_delete]
                flash(f'Le joueur {player_to_delete} a été supprimé')
                return redirect(url_for('admin_console'))
        
        # Gestion de la modification du score d'un joueur
        elif 'edit_player' in request.form and 'edit_score' in request.form:
            player_to_edit = request.form['edit_player']
            new_score = request.form['edit_score']
            
            if player_to_edit in all_players and new_score:
                all_players[player_to_edit] = int(new_score)
                flash(f'Le score de {player_to_edit} a été mis à jour à {new_score}')
                return redirect(url_for('admin_console'))

    # Trier les joueurs par nom
    sorted_players = dict(sorted(all_players.items()))
    
    current_year = datetime.datetime.now().year
    return render_template('admin_console.html', players=sorted_players, current_year=current_year)

# Route pour se déconnecter de l'administration
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Vous avez été déconnecté de l\'administration.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)