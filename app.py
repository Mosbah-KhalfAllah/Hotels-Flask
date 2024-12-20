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

class Chambre(db.Model):
    __tablename__ = 'chambre'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero = db.Column(db.String(50), nullable=False)
    prix = db.Column(db.Float, nullable=False)
    position = db.Column(db.String(100), nullable=True)
    disponible = db.Column(db.Boolean, default=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    capacite = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Chambre {self.numero} - {self.prix}€>'
    
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    room_type = db.Column(db.Enum('suite', 'deluxe', 'standard'), nullable=False)
    adults = db.Column(db.Integer, nullable=False)
    children = db.Column(db.Integer, default=0)
    special_requests = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_complet = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_reception = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Contact {self.nom_complet} - {self.email}>'

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        nom_complet = request.form.get('nom_complet')
        email = request.form.get('email')
        message = request.form.get('message')

        if not nom_complet or not email or not message:
            flash("Tous les champs sont obligatoires.", "danger")
            return redirect('/home')

        try:
            nouveau_message = Contact(nom_complet=nom_complet, email=email, message=message)
            db.session.add(nouveau_message)
            db.session.commit()
            flash("Votre message a été envoyé avec succès.", "success")
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            flash("Une erreur est survenue.", "danger")
            print(e)

    return render_template('home.html')

@app.route('/adminDashboard')
def adminDashboard():
    if 'user_id' in session and session.get('role') == 'admin':
        admin = User.query.filter_by(id=session['user_id']).first()
        rooms = Chambre.query.all()
        users = User.query.all()
        reservations = Reservation.query.all() 
        return render_template('adminDashboard.html', reservations=reservations, users=users, rooms=rooms, admin=admin)
    else:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('home'))


@app.route('/profil')
def profil():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('profil.html', user=user)
    else:
        flash('Veuillez vous connecter pour accéder à votre profil.', 'warning')
        return redirect(url_for('login'))

@app.route('/reservations', methods=['GET', 'POST'])
def reservations():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        check_in = request.form['check_in']
        check_out = request.form['check_out']
        room_type = request.form['room_type']
        adults = request.form['adults']
        children = request.form['children']
        special_requests = request.form['special_requests']

        reservation = Reservation(full_name=full_name, email=email, check_in=check_in,
                                  check_out=check_out, room_type=room_type, adults=adults,
                                  children=children, special_requests=special_requests)
        db.session.add(reservation)
        db.session.commit()
        flash('Réservation ajoutée avec succès!', 'success')

        return redirect(url_for('reservations'))

    reservations_list = Reservation.query.all()
    return render_template('reservations.html', reservations=reservations_list)

@app.route('/add_reservation', methods=['GET', 'POST'])
def add_reservation():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        check_in = request.form['check_in']
        check_out = request.form['check_out']
        room_type = request.form['room_type']
        adults = int(request.form['adults'])
        children = int(request.form.get('children', 0))
        special_requests = request.form.get('special_requests', '')

        new_reservation = Reservation(
            full_name=full_name,
            email=email,
            check_in=check_in,
            check_out=check_out,
            room_type=room_type,
            adults=adults,
            children=children,
            special_requests=special_requests
        )

        try:
            db.session.add(new_reservation)
            db.session.commit()
            flash('Réservation ajoutée avec succès !', 'success')
            return redirect(url_for('adminDashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'ajout de la réservation : {str(e)}', 'danger')
    
    return render_template('add_reservation.html')

@app.route('/edit_reservation/<int:id>', methods=['GET', 'POST'])
def edit_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    if request.method == 'POST':
        reservation.full_name = request.form['full_name']
        reservation.email = request.form['email']
        reservation.check_in = request.form['check_in']
        reservation.check_out = request.form['check_out']
        reservation.room_type = request.form['room_type']
        reservation.adults = int(request.form['adults'])
        reservation.children = int(request.form.get('children', 0))
        reservation.special_requests = request.form.get('special_requests', '')

        try:
            db.session.commit()
            flash('Réservation mise à jour avec succès !', 'success')
            return redirect(url_for('adminDashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur : {str(e)}', 'danger')

    return render_template('edit_reservation.html', reservation=reservation)

@app.route('/reservation/delete/<int:id>', methods=['POST'])
def delete_reservation(id):
    reservation = Reservation.query.get(id)
    if reservation:
        db.session.delete(reservation)
        db.session.commit()
    return redirect(url_for('adminDashboard'))

@app.route('/chambres')
def chambres():
    chambres = Chambre.query.all()
    chambres_par_categorie = {}
    
    for chambre in chambres:
        if chambre.type not in chambres_par_categorie:
            chambres_par_categorie[chambre.type] = []
        chambres_par_categorie[chambre.type].append(chambre)
    
    return render_template('chambres.html', chambres_par_categorie=chambres_par_categorie)

@app.route('/add_room', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        numero = request.form['numero']
        type_chambre = request.form['type']
        capacite = request.form['capacite']
        prix = request.form['prix']
        position = request.form['position']
        description = request.form['description']
        disponible = request.form.get('disponible') == '1s'

        new_room = Chambre(
            numero=numero,
            type=type_chambre,
            capacite=int(capacite),
            prix=float(prix),
            position=position,
            description=description,
            disponible=disponible
        )

        db.session.add(new_room)
        db.session.commit()

        flash("La chambre a été ajoutée avec succès.", "success")
        return redirect(url_for('adminDashboard'))

    return render_template('add_room.html')

@app.route('/edit_room/<int:id>', methods=['GET', 'POST'])
def edit_room(id):
    room = Chambre.query.get(id)
    
    if not room:
        flash("Chambre non trouvée.", "danger")
        return redirect(url_for('adminDashboard'))

    if request.method == 'POST':
        room.numero = request.form['numero']
        room.prix = request.form['prix']
        room.position = request.form['position']
        room.type = request.form['type']
        room.capacite = request.form['capacite']
        room.description = request.form['description']
        room.disponible = 'disponible' in request.form

        db.session.commit()
        flash("Chambre modifiée avec succès.", "success")
        return redirect(url_for('adminDashboard'))

    return render_template('edit_room.html', room=room)

@app.route('/delete_room/<int:id>', methods=['POST'])
def delete_room(id):
    chambre = Chambre.query.get(id)
    if not chambre:
        flash("Chambre non trouvée.", "danger")
        return redirect(url_for('adminDashboard'))

    db.session.delete(chambre)
    db.session.commit()
    flash("Chambre supprimée avec succès.", "success")
    return redirect(url_for('adminDashboard'))

@app.route('/apropos')
def apropos():
    return render_template('apropos.html')

@app.route('/users')
def users():
    if 'user_id' in session and session.get('role') == 'admin':
        users = User.query.all()
        return render_template('adminDashboard.html', users=users)
    else:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('home'))

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        motdepasse = request.form['motdepasse']
        tel = request.form['tel']
        date_naissance = request.form['date_naissance']
        sexe = request.form['sexe']
        adresse = request.form['adresse']
        role = request.form['role']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Cet email est déjà utilisé. Veuillez en choisir un autre.', 'danger')
            return redirect(url_for('add_user'))

        hashed_password = generate_password_hash(motdepasse, method='pbkdf2:sha256')

        new_user = User(nom=nom, prenom=prenom, email=email, motdepasse=hashed_password,
                        tel=tel, date_naissance=date_naissance, sexe=sexe,
                        adresse=adresse, role=role)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Utilisateur ajouté avec succès.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Une erreur est survenue. Veuillez réessayer.', 'danger')

        return redirect(url_for('adminDashboard'))
    
    return render_template('add_user.html')

@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    user = User.query.get_or_404(id)

    if request.method == 'POST':
        user.nom = request.form['nom']
        user.prenom = request.form['prenom']
        user.email = request.form['email']
        user.tel = request.form['tel']
        user.date_naissance = request.form['date_naissance']
        user.sexe = request.form['sexe']
        user.adresse = request.form['adresse']
        user.role = request.form['role']

        if 'sexe' in request.form:
            user.sexe = request.form['sexe']
        else:
            print("Se variable 'sexe' not found in form")
        
        if request.form['motdepasse']:
            user.motdepasse = generate_password_hash(request.form['motdepasse'])

        try:
            db.session.commit()
            flash("Utilisateur mis à jour avec succès!", "success")
            return redirect(url_for('adminDashboard'))
        except Exception as e:
            db.session.rollback()
            flash("Une erreur est survenue lors de la mise à jour.", "danger")
            print(e)

    return render_template('edit_user.html', user=user)

@app.route('/users/delete/<int:id>', methods=['GET'])
def delete_user(id):
    if 'user_id' in session and session.get('role') == 'admin':
        user = User.query.get(id)
        db.session.delete(user)
        db.session.commit()
        flash("Utilisateur supprimé avec succès", "danger")
        return redirect(url_for('adminDashboard'))
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
                return redirect(url_for('adminDashboard'))
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