from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, User, Consultation, Setting, SubscriptionRequest
from functools import wraps
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Accès réservé aux administrateurs.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    total_users = User.query.filter_by(is_admin=False).count()
    premium_users = User.query.filter_by(plan='premium', is_admin=False).count()
    total_consultations = Consultation.query.count()
    pending_requests = SubscriptionRequest.query.filter_by(status='pending').count()
    price = Setting.get('subscription_price', '5000')
    payment_info = Setting.get('payment_info', '')
    recent_users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
        total_users=total_users,
        premium_users=premium_users,
        total_consultations=total_consultations,
        pending_requests=pending_requests,
        price=price,
        payment_info=payment_info,
        recent_users=recent_users
    )

@admin_bp.route('/settings', methods=['POST'])
@login_required
@admin_required
def update_settings():
    price = request.form.get('subscription_price', '').strip()
    payment_info = request.form.get('payment_info', '').strip()
    if price:
        Setting.set('subscription_price', price)
    if payment_info:
        Setting.set('payment_info', payment_info)
    flash('Paramètres mis à jour avec succès.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/subscriptions')
@login_required
@admin_required
def subscriptions():
    requests = SubscriptionRequest.query.order_by(SubscriptionRequest.created_at.desc()).all()
    return render_template('admin/subscriptions.html', requests=requests)

@admin_bp.route('/subscription/<int:req_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_subscription(req_id):
    req = SubscriptionRequest.query.get_or_404(req_id)
    duration = int(request.form.get('duration', 30))  # jours
    req.status = 'approved'
    req.user.plan = 'premium'
    req.user.subscription_expires = datetime.utcnow() + timedelta(days=duration)
    db.session.commit()
    flash(f'Abonnement de {req.user.username} approuvé pour {duration} jours.', 'success')
    return redirect(url_for('admin.subscriptions'))

@admin_bp.route('/subscription/<int:req_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_subscription(req_id):
    req = SubscriptionRequest.query.get_or_404(req_id)
    req.status = 'rejected'
    db.session.commit()
    flash(f'Demande de {req.user.username} rejetée.', 'info')
    return redirect(url_for('admin.subscriptions'))

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/user/<int:user_id>/toggle-premium', methods=['POST'])
@login_required
@admin_required
def toggle_premium(user_id):
    user = User.query.get_or_404(user_id)
    if user.plan == 'premium':
        user.plan = 'free'
        user.subscription_expires = None
        flash(f'{user.username} rétrogradé en compte gratuit.', 'info')
    else:
        user.plan = 'premium'
        user.subscription_expires = datetime.utcnow() + timedelta(days=30)
        flash(f'{user.username} promu en compte premium (30 jours).', 'success')
    db.session.commit()
    return redirect(url_for('admin.users'))
