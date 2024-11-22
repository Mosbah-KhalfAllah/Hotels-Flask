import os
from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/gesHotels'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(32)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    motdepasse = db.Column(db.String(200), nullable=False)
    tel = db.Column(db.String(20), nullable=True)
    date_naissance = db.Column(db.Date, nullable=False)
    sexe = db.Column(db.String(10), nullable=False)
    adresse = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')

    def __repr__(self):
        return f'<User {self.nom} {self.prenom}>'

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/profil')
def profil():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('profil.html', user=user)
    else:
        flash('Veuillez vous connecter pour accéder à votre profil.', 'warning')
        return redirect(url_for('login'))

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/reservations')
def reservations():
    return render_template('reservations.html')

@app.route('/chambres')
def chambres():
    return render_template('chambres.html')

@app.route('/employes')
def employes():
    if 'user_id' in session and session.get('role') == 'admin':
        return render_template('employes.html')
    else:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('home'))

@app.route('/paiement')
def paiement():
    return render_template('paiement.html')

@app.route('/hotels')
def hotels():
    return render_template('hotels.html')

@app.route('/users')
def users():
    if 'user_id' in session and session.get('role') == 'admin':
        users = User.query.all()
        return render_template('adminDashboard.html', users=users)
    else:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('home'))

@app.route('/users/create', methods=['GET', 'POST'])
def create_user():
    if 'user_id' in session and session.get('role') == 'admin':
        if request.method == 'POST':
            nom = request.form['nom']
            prenom = request.form['prenom']
            email = request.form['email']
            tel = request.form['tel']
            role = request.form['role']
            new_user = User(nom=nom, prenom=prenom, email=email, tel=tel, role=role)
            db.session.add(new_user)
            db.session.commit()
            flash("Utilisateur créé avec succès", "success")
            return redirect(url_for('users'))
        return render_template('create_user.html')
    else:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('home'))

@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    if 'user_id' in session and session.get('role') == 'admin':
        user = User.query.get(id)
        if request.method == 'POST':
            user.nom = request.form['nom']
            user.prenom = request.form['prenom']
            user.email = request.form['email']
            user.tel = request.form['tel']
            user.role = request.form['role']
            db.session.commit()
            flash("Utilisateur mis à jour avec succès", "success")
            return redirect(url_for('users'))
        return render_template('edit_user.html', user=user)
    else:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('home'))

@app.route('/users/delete/<int:id>', methods=['GET'])
def delete_user(id):
    if 'user_id' in session and session.get('role') == 'admin':
        user = User.query.get(id)
        db.session.delete(user)
        db.session.commit()
        flash("Utilisateur supprimé avec succès", "danger")
        return redirect(url_for('admin_dashboard'))
    else:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('home'))


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' in session and session.get('role') == 'admin':
        admin = User.query.filter_by(id=session['user_id']).first()
        users = User.query.all()
        return render_template('adminDashboard.html', users=users, admin=admin)
    else:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        motdepasse = request.form['motdepasse']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.motdepasse, motdepasse):
            session['user_id'] = user.id
            session['nom'] = user.nom
            session['prenom'] = user.prenom
            session['role'] = user.role
            
            flash('Connexion réussie!', 'success')
            
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Échec de la connexion. Vérifiez votre email et votre mot de passe.', 'danger')
    
    return render_template('home.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('nom', None)
    session.pop('prenom', None)
    flash('Vous êtes déconnecté.', 'success')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            nom = request.form['nom']
            prenom = request.form['prenom']
            email = request.form['email']
            motdepasse = generate_password_hash(request.form['motdepasse'])
            tel = request.form['tel']
            date_naissance = datetime.strptime(request.form['date_naissance'], '%Y-%m-%d').date()
            sexe = request.form['sexe']
            adresse = request.form['adresse']

            new_user = User(nom=nom, prenom=prenom, email=email, motdepasse=motdepasse,
                            tel=tel, date_naissance=date_naissance, sexe=sexe, adresse=adresse)
            
            db.session.add(new_user)
            db.session.commit()

            flash("Inscription réussie!", "success")
            return redirect(url_for('home'))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'inscription: {str(e)}", "danger")

    return render_template('home.html')

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        
        if request.method == 'POST':
            user.nom = request.form['nom']
            user.prenom = request.form['prenom']
            user.email = request.form['email']
            user.tel = request.form['tel']
            user.date_naissance = datetime.strptime(request.form['date_naissance'], '%Y-%m-%d').date()
            user.sexe = request.form['sexe']
            user.adresse = request.form['adresse']
            db.session.commit()
            flash('Profil mis à jour avec succès!', 'success')
            return redirect(url_for('profil'))
        
        return render_template('edit_profile.html', user=user)
    else:
        flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
        return redirect(url_for('login'))

@app.route('/conditions')
def conditions():
    return render_template('conditions.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Tables créées avec succès.")
    app.run(debug=True)
