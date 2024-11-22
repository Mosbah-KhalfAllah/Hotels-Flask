function switchToLoginForm() {
    document.getElementById('signup-form').style.display = 'none';
    document.getElementById('login-form').style.display = 'block';
}

function switchToSignupForm() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('signup-form').style.display = 'block';
}

function validateAndSwitchToLoginForm() {
    const prenom = document.getElementById('prenom').value.trim();
    const nom = document.getElementById('nom').value.trim();
    const tel = document.getElementById('tel').value.trim();
    const dateNaissance = document.getElementById('date_naissance').value.trim();
    const adresse = document.getElementById('adresse').value.trim();
    const email = document.getElementById('email').value.trim();
    const motdepasse = document.getElementById('motdepasse').value.trim();
    const confirmerMotdepasse = document.getElementById('confirmer_motdepasse').value.trim();

    if (!prenom || !nom || !tel || !dateNaissance || !adresse || !email || !motdepasse || !confirmerMotdepasse) {
        alert("Veuillez remplir tous les champs.");
        return;
    }

    if (motdepasse !== confirmerMotdepasse) {
        alert("Les mots de passe ne correspondent pas.");
        return;
    }

    switchToLoginForm();
}