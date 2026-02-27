# 🩺 MédiSym — Diagnostic Symptomatique

Application web Flask de diagnostic médical par symptômes, avec gestion des utilisateurs, abonnements et administration.

---

## 🚀 Démarrage rapide avec Docker

```bash
# 1. Cloner ou décompresser le projet
cd medical-app

# 2. Copier le fichier d'environnement
cp .env.example .env

# 3. Lancer l'application
docker-compose up -d --build

# 4. Accéder à l'application
# → http://localhost:5000
```

**Compte administrateur par défaut :**
- Email : `admin@medisym.com`
- Mot de passe : `Admin@1234`

---

## 🐳 Commandes Docker utiles

```bash
# Démarrer en arrière-plan
docker-compose up -d --build

# Voir les logs en temps réel
docker-compose logs -f web

# Arrêter l'application
docker-compose down

# Arrêter et supprimer les données
docker-compose down -v

# Redémarrer après modification
docker-compose restart web

# Vérifier l'état
docker-compose ps

# Accéder au shell du conteneur
docker-compose exec web /bin/bash
```

---

## 🏃 Démarrage local sans Docker

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python run.py
```

---

## 📁 Structure du projet

```
medical-app/
├── app/
│   ├── __init__.py          # Factory Flask
│   ├── models.py            # Modèles SQLAlchemy (User, Consultation, etc.)
│   ├── diseases.py          # Base de données des 15 maladies
│   ├── routes/
│   │   ├── auth.py          # Connexion / Inscription / Déconnexion
│   │   ├── main.py          # Page principale, consultation, résultats
│   │   └── admin.py         # Panneau d'administration
│   └── templates/
│       ├── base.html        # Template de base (nav, footer, flash)
│       ├── index.html       # Page d'accueil
│       ├── consulter.html   # Formulaire de symptômes
│       ├── results.html     # Résultats du diagnostic
│       ├── dashboard.html   # Tableau de bord utilisateur
│       ├── abonnement.html  # Page d'abonnement Premium
│       ├── limit_reached.html # Page limite visiteur atteinte
│       └── admin/
│           ├── dashboard.html   # Panneau admin principal
│           ├── subscriptions.html # Gestion abonnements
│           └── users.html       # Gestion utilisateurs
├── config.py                # Configuration Flask
├── run.py                   # Point d'entrée
├── requirements.txt         # Dépendances Python
├── Dockerfile               # Image Docker
├── docker-compose.yml       # Orchestration Docker
└── .env.example             # Exemple de variables d'environnement
```

---

## 👤 Système d'utilisateurs

| Plan | Consultations | Prix |
|------|--------------|------|
| Visiteur (sans compte) | 3 essais total | Gratuit |
| Compte gratuit | 10/mois | Gratuit |
| Premium | Illimité | Fixé par l'admin en FCFA |

---

## 🏥 Maladies disponibles (15)

1. Grippe (Influenza)
2. Paludisme (Malaria)
3. Typhoïde
4. Hypertension artérielle
5. Diabète de type 2
6. Gastro-entérite
7. Tuberculose (TB)
8. Infection urinaire (cystite)
9. Anémie
10. Asthme
11. VIH/SIDA
12. Sinusite
13. Hépatite B
14. Dermatite / Eczéma
15. Méningite (urgence médicale)

---

## ⚙️ Panneau d'administration

Accessible via `/admin` après connexion avec le compte admin :
- **Tableau de bord** : statistiques globales
- **Paramètres** : fixer le prix de l'abonnement en FCFA et les instructions de paiement
- **Abonnements** : valider/rejeter les demandes d'abonnement (avec durée configurable)
- **Utilisateurs** : voir tous les utilisateurs, activer/révoquer le Premium manuellement

---

## 🔒 Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `SECRET_KEY` | Clé secrète Flask | (à changer!) |
| `PORT` | Port d'écoute | `5000` |
| `DATABASE_URL` | URL de la base de données | SQLite |
| `FLASK_ENV` | Environnement | `production` |

---

## ⚠️ Avertissement médical

MédiSym est un **outil d'information uniquement**. Il ne remplace en aucun cas une consultation médicale professionnelle. En cas d'urgence ou de symptômes graves, consultez immédiatement un médecin.
