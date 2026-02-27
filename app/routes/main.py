from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import current_user, login_required
from app.models import db, Consultation, Setting, SubscriptionRequest
from app.diseases import find_diseases, DISEASES
import json
from datetime import datetime, date

main_bp = Blueprint('main', __name__)
GUEST_MAX_USES = 3

def get_guest_uses():
    return session.get('guest_uses', 0)

def increment_guest_uses():
    session['guest_uses'] = session.get('guest_uses', 0) + 1
    session.permanent = True

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/a-propos')
def a_propos():
    return render_template('a_propos.html')

@main_bp.route('/maladies')
def maladies():
    return render_template('maladies.html', diseases=DISEASES)

@main_bp.route('/maladie/<int:disease_id>')
def maladie_detail(disease_id):
    disease = next((d for d in DISEASES if d['id'] == disease_id), None)
    if not disease:
        flash('Maladie introuvable.', 'error')
        return redirect(url_for('main.maladies'))
    return render_template('maladie_detail.html', disease=disease)

@main_bp.route('/consulter', methods=['GET', 'POST'])
def consulter():
    if request.method == 'GET':
        return render_template('consulter.html',
            user=current_user if current_user.is_authenticated else None,
            guest_uses=get_guest_uses(), guest_max=GUEST_MAX_USES)

    symptoms = request.form.get('symptoms', '').strip()
    if not symptoms or len(symptoms) < 10:
        flash('Veuillez décrire vos symptômes plus en détail (minimum 10 caractères).', 'error')
        return redirect(url_for('main.consulter'))

    # Vérification des limites
    if current_user.is_authenticated:
        if not current_user.can_consult():
            flash('Limite de consultations atteinte ce mois. Abonnez-vous pour un accès illimité !', 'error')
            return redirect(url_for('main.abonnement'))
        current_user.monthly_uses += 1
        db.session.commit()
    else:
        if get_guest_uses() >= GUEST_MAX_USES:
            return redirect(url_for('main.limit_reached'))
        increment_guest_uses()

    # Diagnostic par algorithme local
    results = find_diseases(symptoms)

    # Sauvegarde en base
    consultation = Consultation(
        user_id=current_user.id if current_user.is_authenticated else None,
        symptoms_text=symptoms,
        results=json.dumps([{
            "name": r["name"],
            "confidence": r["confidence"],
            "severity": r["severity"]
        } for r in results])
    )
    db.session.add(consultation)
    db.session.commit()

    return render_template('results.html',
        symptoms=symptoms,
        results=results,
        user=current_user if current_user.is_authenticated else None)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    consultations = Consultation.query.filter_by(user_id=current_user.id)\
        .order_by(Consultation.created_at.desc()).limit(5).all()
    price = Setting.get('subscription_price', '5000')
    total = Consultation.query.filter_by(user_id=current_user.id).count()
    return render_template('dashboard.html', user=current_user,
        consultations=consultations, subscription_price=price, total_consultations=total)

@main_bp.route('/historique')
@login_required
def historique():
    consultations = Consultation.query.filter_by(user_id=current_user.id)\
        .order_by(Consultation.created_at.desc()).all()
    today = date.today()
    this_month = Consultation.query.filter(
        Consultation.user_id == current_user.id,
        db.func.strftime('%Y-%m', Consultation.created_at) == today.strftime('%Y-%m')
    ).count()
    return render_template('historique.html', user=current_user,
        consultations=consultations, this_month=this_month)

@main_bp.route('/profil')
@login_required
def profil():
    total = Consultation.query.filter_by(user_id=current_user.id).count()
    return render_template('profil.html', user=current_user, total_consultations=total)

@main_bp.route('/profil/changer-mdp', methods=['POST'])
@login_required
def changer_mdp():
    current_pw = request.form.get('current_password', '')
    new_pw = request.form.get('new_password', '')
    confirm_pw = request.form.get('confirm_password', '')
    if not current_user.check_password(current_pw):
        flash('Mot de passe actuel incorrect.', 'error')
        return redirect(url_for('main.profil'))
    if len(new_pw) < 6:
        flash('Minimum 6 caractères requis.', 'error')
        return redirect(url_for('main.profil'))
    if new_pw != confirm_pw:
        flash('Les mots de passe ne correspondent pas.', 'error')
        return redirect(url_for('main.profil'))
    current_user.set_password(new_pw)
    db.session.commit()
    flash('Mot de passe mis à jour avec succès.', 'success')
    return redirect(url_for('main.profil'))

@main_bp.route('/abonnement', methods=['GET', 'POST'])
@login_required
def abonnement():
    price = Setting.get('subscription_price', '5000')
    payment_info = Setting.get('payment_info', "Contactez l'administrateur.")
    pending = SubscriptionRequest.query.filter_by(user_id=current_user.id, status='pending').first()
    if request.method == 'POST':
        if not pending:
            proof = request.form.get('payment_proof', '')
            req = SubscriptionRequest(user_id=current_user.id, payment_proof=proof)
            db.session.add(req)
            db.session.commit()
            flash("Demande envoyée ! L'administrateur la validera bientôt.", 'success')
        else:
            flash('Demande déjà en attente.', 'info')
        return redirect(url_for('main.abonnement'))
    return render_template('abonnement.html', price=price, payment_info=payment_info, pending=pending)

@main_bp.route('/limite')
def limit_reached():
    return render_template('limit_reached.html')
