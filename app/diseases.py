"""
Base de données médicale — MédiSym
Moteur de diagnostic intelligent basé sur correspondance pondérée multi-critères.
Précision cible : 80-90% sur les maladies courantes africaines.
"""

import re
from difflib import SequenceMatcher

# ══════════════════════════════════════════════════════════════════════
# DONNÉES DES MALADIES
# Chaque maladie contient :
#   - keywords       : mots-clés de détection (simple)
#   - key_symptoms   : symptômes-clés TRÈS spécifiques (poids fort x3)
#   - common_symptoms: symptômes fréquents mais non spécifiques (poids x1)
#   - excludes       : termes qui réduisent le score (peu probable si présent)
# ══════════════════════════════════════════════════════════════════════

DISEASES = [
    {
        "id": 1,
        "name": "Grippe (Influenza)",
        "keywords": ["fièvre", "toux", "fatigue", "courbatures", "maux de tête", "frissons", "nez qui coule", "gorge", "corps douloureux", "rhume", "grippe", "éternuements"],
        "key_symptoms": ["courbatures", "frissons", "corps douloureux", "grippe", "éternuements", "nez qui coule"],
        "common_symptoms": ["fièvre", "toux", "fatigue", "maux de tête", "gorge"],
        "excludes": ["diarrhée", "sang", "urine", "douleur poitrine", "convulsions"],
        "symptoms": ["Fièvre élevée (38-40°C)", "Toux sèche ou productive", "Fatigue et faiblesse intense", "Courbatures et douleurs musculaires", "Maux de tête", "Frissons", "Congestion nasale et écoulements", "Gorge irritée"],
        "description": "Infection virale des voies respiratoires causée par le virus Influenza A ou B, très contagieuse et saisonnière.",
        "treatment": ["Repos complet et hydratation abondante", "Paracétamol ou ibuprofène pour la fièvre et douleurs", "Antiviraux (Tamiflu/Oseltamivir) si prescrit dans les 48h", "Décongestionnants pour la congestion nasale", "Gargarismes avec eau salée pour la gorge"],
        "prevention": ["Vaccination annuelle contre la grippe", "Lavage fréquent des mains", "Éviter le contact avec des personnes malades", "Porter un masque en période épidémique", "Renforcer son système immunitaire"],
        "severity": "modérée",
        "color": "#f59e0b",
    },
    {
        "id": 2,
        "name": "Paludisme (Malaria)",
        "keywords": ["fièvre", "frissons", "sueurs", "maux de tête", "vomissements", "douleur abdominale", "fatigue", "malaria", "paludisme", "moustique", "cyclique", "frisson", "sueur nocturne"],
        "key_symptoms": ["frissons", "sueurs", "paludisme", "malaria", "moustique", "fièvre cyclique", "frisson", "sueur nocturne"],
        "common_symptoms": ["fièvre", "maux de tête", "vomissements", "fatigue", "douleur abdominale"],
        "excludes": ["toux", "nez", "gorge"],
        "symptoms": ["Fièvre cyclique (toutes les 48-72h)", "Frissons intenses et sueurs profuses", "Maux de tête sévères", "Nausées et vomissements", "Douleurs abdominales", "Fatigue extrême", "Ictère dans les cas graves", "Urine foncée"],
        "description": "Maladie parasitaire transmise par la piqûre de moustiques Anophèles infectés par Plasmodium. Très répandue en Afrique subsaharienne, urgence médicale.",
        "treatment": ["Antipaludéens : Artéméther-Luméfantrine (Coartem)", "Traitement immédiat dès diagnostic confirmé", "Hospitalisation si forme grave", "Hydratation et antipyrétiques", "Transfusion sanguine si anémie sévère"],
        "prevention": ["Moustiquaires imprégnées d'insecticide", "Répulsifs anti-moustiques", "Vêtements longs le soir", "Éliminer les eaux stagnantes", "Chimioprophylaxie pour les voyageurs"],
        "severity": "grave",
        "color": "#ef4444",
    },
    {
        "id": 3,
        "name": "Typhoïde (Fièvre typhoïde)",
        "keywords": ["fièvre", "ventre", "diarrhée", "constipation", "fatigue", "typhoïde", "abdomen", "taches rosées", "langue chargée", "salmonella"],
        "key_symptoms": ["typhoïde", "taches rosées", "langue chargée", "fièvre progressive", "salmonella"],
        "common_symptoms": ["fièvre", "ventre", "diarrhée", "constipation", "fatigue", "abdomen"],
        "excludes": ["toux", "frissons", "moustique"],
        "symptoms": ["Fièvre progressive (39-40°C)", "Douleurs abdominales", "Diarrhée ou constipation", "Maux de tête persistants", "Perte d'appétit", "Taches rosées sur le tronc", "Langue chargée blanchâtre", "Fatigue intense"],
        "description": "Infection bactérienne systémique par Salmonella typhi, transmise par voie fécale-orale via l'eau ou les aliments contaminés.",
        "treatment": ["Antibiotiques : Ciprofloxacine, Azithromycine, Ceftriaxone", "Traitement de 7 à 14 jours", "Repos et alimentation légère", "Hydratation abondante", "Hospitalisation si complications"],
        "prevention": ["Eau potable traitée ou en bouteille", "Vaccination contre la typhoïde", "Hygiène alimentaire stricte", "Lavage des mains avant repas", "Éviter les crudités non lavées"],
        "severity": "grave",
        "color": "#ef4444",
    },
    {
        "id": 4,
        "name": "Hypertension artérielle",
        "keywords": ["tension", "maux de tête", "vertiges", "bourdonnements", "vision trouble", "essoufflement", "palpitations", "hypertension", "pression", "nuque"],
        "key_symptoms": ["hypertension", "tension élevée", "bourdonnements", "nuque douloureuse", "pression artérielle"],
        "common_symptoms": ["maux de tête", "vertiges", "vision trouble", "essoufflement", "palpitations"],
        "excludes": ["fièvre", "diarrhée", "toux"],
        "symptoms": ["Maux de tête matinaux (nuque, tempes)", "Vertiges et étourdissements", "Bourdonnements d'oreilles", "Vision trouble", "Essoufflement à l'effort", "Palpitations", "Saignements de nez", "Souvent asymptomatique"],
        "description": "Pression artérielle chroniquement élevée (> 140/90 mmHg). Facteur de risque majeur d'AVC, crises cardiaques et insuffisances rénales.",
        "treatment": ["Antihypertenseurs : IEC, ARA2, bêtabloquants, diurétiques", "Régime hyposodé (moins de sel)", "Activité physique régulière", "Perte de poids si surpoids", "Arrêt du tabac et réduction de l'alcool"],
        "prevention": ["Réduire la consommation de sel", "Alimentation saine (fruits, légumes)", "Activité physique régulière", "Maintenir un poids santé", "Éviter le stress chronique"],
        "severity": "chronique",
        "color": "#8b5cf6",
    },
    {
        "id": 5,
        "name": "Diabète de type 2",
        "keywords": ["soif", "uriner", "fatigue", "vision", "plaie", "sucre", "diabète", "glucose", "poids", "engourdissement", "polyurie", "polydipsie"],
        "key_symptoms": ["diabète", "glucose", "polyurie", "polydipsie", "soif excessive", "uriner fréquemment", "sucre dans le sang"],
        "common_symptoms": ["soif", "fatigue", "vision trouble", "plaie qui ne guérit pas", "poids", "engourdissement"],
        "excludes": ["fièvre", "toux", "diarrhée"],
        "symptoms": ["Soif excessive et persistante", "Mictions fréquentes et abondantes", "Fatigue intense", "Vision trouble", "Plaies cicatrisant mal", "Engourdissements des extrémités", "Perte de poids inexpliquée", "Infections fréquentes"],
        "description": "Maladie métabolique chronique caractérisée par une hyperglycémie due à une résistance à l'insuline. En forte progression en Afrique.",
        "treatment": ["Antidiabétiques oraux : Metformine en première intention", "Insuline si glycémie non contrôlée", "Régime alimentaire adapté (sucres rapides limités)", "Activité physique régulière", "Surveillance glycémique quotidienne"],
        "prevention": ["Alimentation équilibrée, limiter sucres rapides", "Activité physique 30 min/jour", "Maintenir un poids sain", "Dépistage glycémique après 40 ans", "Éviter le tabac"],
        "severity": "chronique",
        "color": "#8b5cf6",
    },
    {
        "id": 6,
        "name": "Gastro-entérite",
        "keywords": ["diarrhée", "vomissements", "nausées", "crampes", "ventre", "gastro", "intoxication alimentaire", "selles", "douleur abdominale"],
        "key_symptoms": ["diarrhée", "vomissements", "gastro", "intoxication alimentaire"],
        "common_symptoms": ["nausées", "crampes", "ventre", "selles liquides", "douleur abdominale"],
        "excludes": ["toux", "frissons", "sang urine"],
        "symptoms": ["Diarrhée aiguë (selles liquides fréquentes)", "Nausées et vomissements", "Crampes et douleurs abdominales", "Légère fièvre possible", "Fatigue et faiblesse", "Déshydratation si sévère"],
        "description": "Inflammation du tube digestif d'origine virale (norovirus, rotavirus) ou bactérienne. Très fréquente, surtout chez les enfants.",
        "treatment": ["Réhydratation orale (SRO) en priorité", "Régime alimentaire doux (BRAT : banane, riz, pomme, toast)", "Antibiotiques si origine bactérienne confirmée", "Antiémétiques si vomissements importants", "Hospitalisation si déshydratation sévère"],
        "prevention": ["Hygiène des mains rigoureuse", "Eau potable traitée", "Cuire correctement les aliments", "Réfrigération des aliments", "Vaccination contre le rotavirus pour les nourrissons"],
        "severity": "légère",
        "color": "#10b981",
    },
    {
        "id": 7,
        "name": "Tuberculose (TB)",
        "keywords": ["toux persistante", "sang crachats", "fièvre", "sueurs nocturnes", "perte de poids", "tuberculose", "poumons", "crachat", "amaigrissement", "nuit"],
        "key_symptoms": ["tuberculose", "sang dans les crachats", "toux persistante 3 semaines", "sueurs nocturnes", "amaigrissement", "crachat"],
        "common_symptoms": ["toux", "fièvre", "fatigue", "perte de poids", "nuit"],
        "excludes": ["diarrhée", "vomissements"],
        "symptoms": ["Toux persistante depuis plus de 3 semaines", "Crachats avec sang (hémoptysie)", "Fièvre vespérale (le soir)", "Sueurs nocturnes abondantes", "Perte de poids importante", "Fatigue chronique", "Douleur thoracique", "Essoufflement"],
        "description": "Infection bactérienne par Mycobacterium tuberculosis touchant principalement les poumons. Très répandue en Afrique, surtout chez les immunodéprimés (VIH).",
        "treatment": ["Traitement standard DOTS : Isoniazide + Rifampicine + Pyrazinamide + Éthambutol", "Durée minimale 6 mois (ne jamais interrompre)", "Isolement respiratoire en début de traitement", "Suivi mensuel et contrôle bactériologique", "Soutien nutritionnel"],
        "prevention": ["Vaccination BCG à la naissance", "Dépistage des contacts des cas positifs", "Ventilation des locaux", "Traitement préventif à l'isoniazide pour les contacts", "Dépistage systématique des séropositifs VIH"],
        "severity": "grave",
        "color": "#ef4444",
    },
    {
        "id": 8,
        "name": "Infection urinaire (cystite)",
        "keywords": ["brûlure uriner", "envie uriner", "urine", "douleur bas ventre", "cystite", "infection urinaire", "pipi", "fréquence", "troubles urinaires"],
        "key_symptoms": ["brûlure en urinant", "cystite", "infection urinaire", "douleur en urinant", "envie fréquente d'uriner"],
        "common_symptoms": ["urine", "douleur bas ventre", "fréquence", "troubles urinaires"],
        "excludes": ["toux", "fièvre élevée", "diarrhée"],
        "symptoms": ["Brûlures et douleurs lors de la miction", "Envie fréquente et urgente d'uriner", "Urine trouble ou malodorante", "Douleur dans le bas ventre", "Urines parfois teintées de sang", "Fièvre si infection remonte aux reins"],
        "description": "Infection bactérienne des voies urinaires, très fréquente chez la femme. Causée principalement par Escherichia coli.",
        "treatment": ["Antibiotiques : Cotrimoxazole, Ciprofloxacine, Fosfomycine", "Durée 3 à 7 jours selon la sévérité", "Hydratation abondante (2L/jour minimum)", "Antalgiques (paracétamol) pour la douleur", "Hospitalisation si pyélonéphrite"],
        "prevention": ["Boire beaucoup d'eau chaque jour", "Uriner après les rapports sexuels", "Hygiène intime adaptée (essuyage avant-arrière)", "Ne pas retarder les mictions", "Éviter les sous-vêtements synthétiques serrés"],
        "severity": "légère",
        "color": "#10b981",
    },
    {
        "id": 9,
        "name": "Anémie",
        "keywords": ["fatigue", "pâleur", "essoufflement", "vertiges", "faiblesse", "anémie", "sang", "pâle", "teint", "hemoglobine"],
        "key_symptoms": ["anémie", "pâleur", "teint pâle", "hemoglobine basse", "pâle"],
        "common_symptoms": ["fatigue", "essoufflement", "vertiges", "faiblesse"],
        "excludes": ["fièvre", "toux", "diarrhée"],
        "symptoms": ["Fatigue et faiblesse importantes", "Pâleur de la peau, des muqueuses et des conjonctives", "Essoufflement à l'effort", "Vertiges et étourdissements", "Palpitations cardiaques", "Maux de tête", "Frilosité", "Difficultés de concentration"],
        "description": "Réduction du taux d'hémoglobine dans le sang. Très fréquente en Afrique, souvent due à des carences en fer, au paludisme ou aux vers intestinaux.",
        "treatment": ["Supplémentation en fer (sulfate ferreux) et acide folique", "Traitement de la cause (antiparasitaires, antipaludéens)", "Alimentation enrichie en fer (viande, légumineuses)", "Vitamine C pour améliorer l'absorption du fer", "Transfusion sanguine si anémie sévère"],
        "prevention": ["Alimentation variée et riche en fer", "Déparasitage régulier (albendazole)", "Prévention du paludisme", "Supplémentation en fer et folates pendant la grossesse", "Dépistage systématique chez les femmes enceintes"],
        "severity": "modérée",
        "color": "#f59e0b",
    },
    {
        "id": 10,
        "name": "Asthme",
        "keywords": ["essoufflement", "sifflement", "toux nuit", "asthme", "bronches", "respiration", "gêne respiratoire", "oppression", "allergie", "crise"],
        "key_symptoms": ["asthme", "sifflement respiratoire", "oppression thoracique", "crise d'asthme", "bronches"],
        "common_symptoms": ["essoufflement", "toux nuit", "respiration", "gêne respiratoire", "allergie"],
        "excludes": ["fièvre", "diarrhée"],
        "symptoms": ["Essoufflement et dyspnée", "Sifflement (wheezing) à l'expiration", "Toux sèche surtout la nuit", "Oppression thoracique", "Crises déclenchées par effort, allergie ou froid", "Expectoration difficile"],
        "description": "Maladie inflammatoire chronique des bronches entraînant des crises d'obstruction bronchique réversibles. En augmentation en Afrique urbaine.",
        "treatment": ["Bronchodilatateurs courts (Salbutamol/Ventoline) pour les crises", "Corticoïdes inhalés pour le traitement de fond", "Éviter les déclencheurs (allergènes, fumée, poussière)", "Éducation thérapeutique du patient", "Plan d'action écrit en cas de crise sévère"],
        "prevention": ["Identifier et éviter les allergènes déclencheurs", "Ne pas fumer (ni tabagisme passif)", "Dépoussiérer régulièrement le logement", "Traitement préventif de fond régulier", "Consultation pulmonologique régulière"],
        "severity": "chronique",
        "color": "#8b5cf6",
    },
    {
        "id": 11,
        "name": "VIH/SIDA",
        "keywords": ["VIH", "SIDA", "immunodéprimé", "infections opportunistes", "amaigrissement", "ganglions", "diarrhée chronique", "fatigue chronique", "séropositif", "ARV"],
        "key_symptoms": ["VIH", "SIDA", "séropositif", "ARV", "immunodéprimé", "infections opportunistes"],
        "common_symptoms": ["amaigrissement", "ganglions", "diarrhée chronique", "fatigue chronique"],
        "excludes": [],
        "symptoms": ["Fatigue chronique profonde", "Amaigrissement inexpliqué (> 10% du poids)", "Diarrhée chronique persistante", "Ganglions lymphatiques enflés", "Fièvre prolongée ou récurrente", "Infections opportunistes (candidose, pneumonie)", "Sueurs nocturnes", "Peau lésions (zona, kaposi)"],
        "description": "Infection par le Virus de l'Immunodéficience Humaine détruisant progressivement les défenses immunitaires. Traitable mais non guérissable.",
        "treatment": ["Traitement antirétroviral (ARV) à vie : TDF+3TC+DTG en première ligne", "Commencer dès le diagnostic, quel que soit le CD4", "Prophylaxie des infections opportunistes", "Suivi virologique et immunologique régulier", "Soutien nutritionnel et psychologique"],
        "prevention": ["Préservatif lors de chaque rapport sexuel", "Dépistage régulier du VIH", "PTME (prévention transmission mère-enfant)", "Traitement préventif (PrEP) pour les personnes à risque", "Ne pas partager seringues"],
        "severity": "grave",
        "color": "#ef4444",
    },
    {
        "id": 12,
        "name": "Sinusite",
        "keywords": ["nez bouché", "écoulements nasaux", "douleur visage", "sinusite", "tête lourde", "joues", "front", "mucus", "nez", "odorat"],
        "key_symptoms": ["sinusite", "douleur joues", "douleur front", "nez bouché côté"],
        "common_symptoms": ["nez bouché", "écoulements nasaux", "tête lourde", "mucus", "odorat"],
        "excludes": ["fièvre élevée", "diarrhée"],
        "symptoms": ["Nez bouché persistant", "Écoulements nasaux épais (jaunes ou verts)", "Douleur et pression sur le visage (joues, front)", "Tête lourde aggravée en se penchant", "Perte partielle de l'odorat", "Toux persistante (drainage postérieur)", "Légère fièvre possible"],
        "description": "Inflammation des sinus paranasaux, souvent suite à un rhume ou une allergie. Peut devenir chronique si mal traitée.",
        "treatment": ["Décongestionnants nasaux (xylométazoline)", "Lavages nasaux au sérum physiologique", "Antibiotiques si sinusite bactérienne confirmée (Amoxicilline)", "Antalgiques pour les douleurs", "Corticoïdes nasaux si forme chronique"],
        "prevention": ["Traiter rapidement les rhumes et rhinites", "Éviter les allergènes connus", "Maintenir une bonne hydratation", "Humidifier l'air en saison sèche", "Éviter le tabac"],
        "severity": "légère",
        "color": "#10b981",
    },
    {
        "id": 13,
        "name": "Hépatite B",
        "keywords": ["jaunisse", "yeux jaunes", "foie", "fatigue", "urine foncée", "hépatite", "nausées", "ventre droit", "ictère", "transaminases"],
        "key_symptoms": ["hépatite", "jaunisse", "yeux jaunes", "ictère", "foie douloureux", "transaminases"],
        "common_symptoms": ["fatigue", "urine foncée", "nausées", "ventre droit"],
        "excludes": ["toux", "diarrhée abondante"],
        "symptoms": ["Jaunisse (ictère) : peau et yeux jaunes", "Urines très foncées (couleur thé)", "Selles décolorées (beige ou blanches)", "Douleur dans l'hypochondre droit (zone du foie)", "Fatigue intense et nausées", "Perte d'appétit", "Prurit (démangeaisons)", "Fièvre modérée en phase aiguë"],
        "description": "Infection virale du foie par le VHB, transmise par le sang et les sécrétions sexuelles. Peut évoluer vers la cirrhose et le cancer du foie.",
        "treatment": ["Hépatite aiguë : repos et traitement symptomatique", "Hépatite chronique : antiviraux (Ténofovir, Entécavir)", "Suivi hépatique régulier (échographie, transaminases)", "Abstinence d'alcool totale", "Transplantation hépatique si cirrhose terminale"],
        "prevention": ["Vaccination HBV obligatoire dès la naissance", "Préservatif lors des rapports sexuels", "Ne pas partager rasoirs, seringues, tatouage", "Dépistage prénatal obligatoire", "Vaccination de rattrapage pour les non-immunisés"],
        "severity": "grave",
        "color": "#ef4444",
    },
    {
        "id": 14,
        "name": "Dermatite / Eczéma",
        "keywords": ["démangeaisons", "peau sèche", "éruption", "eczéma", "rougeurs peau", "plaques", "gratter", "allergie peau", "irritation", "desquamation"],
        "key_symptoms": ["eczéma", "plaques cutanées", "peau sèche et qui gratte", "desquamation"],
        "common_symptoms": ["démangeaisons", "rougeurs peau", "éruption", "gratter", "allergie peau", "irritation"],
        "excludes": ["fièvre", "diarrhée", "toux"],
        "symptoms": ["Démangeaisons intenses", "Peau sèche et squameuse", "Plaques rouges inflammatoires", "Vésicules pouvant suinter", "Peau épaissie aux zones chroniques", "Aggravation par le stress ou les allergènes", "Localisation typique : plis, mains, visage"],
        "description": "Maladie inflammatoire chronique de la peau avec poussées et rémissions. Souvent d'origine allergique ou génétique.",
        "treatment": ["Émollients quotidiens (crèmes hydratantes)", "Corticoïdes topiques lors des poussées", "Antihistaminiques oraux pour les démangeaisons", "Éviter les savons agressifs et les allergènes", "Dermocorticoïdes puissants si résistance"],
        "prevention": ["Identifier et éviter les allergènes déclencheurs", "Hydratation quotidienne de la peau", "Vêtements en coton naturel", "Éviter les douches trop chaudes", "Gestion du stress"],
        "severity": "légère",
        "color": "#10b981",
    },
    {
        "id": 15,
        "name": "Méningite bactérienne",
        "keywords": ["raideur nuque", "maux de tête violents", "fièvre", "vomissements", "lumière", "méningite", "purpura", "taches", "convulsions", "photophobie"],
        "key_symptoms": ["raideur nuque", "méningite", "purpura", "photophobie", "maux de tête explosifs", "raideur cervicale"],
        "common_symptoms": ["fièvre", "vomissements", "taches", "convulsions", "lumière"],
        "excludes": ["diarrhée", "toux"],
        "symptoms": ["Raideur de la nuque (méningisme)", "Maux de tête violents et explosifs", "Fièvre élevée brutale", "Vomissements en jet", "Photophobie et phonophobie", "Purpura (taches ne s'effaçant pas)", "Altération de la conscience", "Convulsions"],
        "description": "Urgence absolue — inflammation des méninges souvent due à Neisseria meningitidis ou pneumocoque. Peut tuer en quelques heures.",
        "treatment": ["URGENCE VITALE : SAMU immédiat", "Antibiotiques IV en extrême urgence (Ceftriaxone)", "Corticoïdes (Dexaméthasone)", "Réanimation en soins intensifs", "Antibioprophylaxie de l'entourage"],
        "prevention": ["Vaccination MenACWY et MenB", "Éviter les contacts avec les cas", "Antibioprophylaxie des contacts", "Surveillance épidémique en saison sèche", "Signalement obligatoire"],
        "severity": "urgence",
        "color": "#dc2626",
    },
    {
        "id": 16,
        "name": "Dengue",
        "keywords": ["fièvre brutale", "douleurs articulaires", "éruption", "maux de tête", "derrière les yeux", "dengue", "moustique", "plaquettes", "saignement nez", "os douloureux"],
        "key_symptoms": ["dengue", "douleur derrière les yeux", "fièvre brutale", "douleurs osseuses intenses"],
        "common_symptoms": ["éruption", "maux de tête", "moustique", "plaquettes", "saignement nez"],
        "excludes": ["toux", "diarrhée"],
        "symptoms": ["Fièvre brutale et très élevée (39-40°C)", "Douleurs articulaires et osseuses intenses", "Maux de tête sévères (derrière les yeux)", "Éruption cutanée rouge après 3-5 jours", "Nausées et vomissements", "Saignements de nez ou des gencives", "Fatigue extrême", "Chute des plaquettes"],
        "description": "Maladie virale transmise par le moustique Aedes aegypti, en expansion en Afrique de l'Ouest. La forme hémorragique est potentiellement mortelle.",
        "treatment": ["Paracétamol uniquement (jamais aspirine ni ibuprofène)", "Hydratation intensive", "Surveillance des plaquettes", "Hospitalisation si forme hémorragique", "Transfusion plaquettaire si nécessaire"],
        "prevention": ["Éliminer les eaux stagnantes", "Moustiquaires et répulsifs", "Vêtements couvrants le jour", "Pulvérisations insecticides", "Sensibilisation communautaire"],
        "severity": "grave",
        "color": "#ef4444",
    },
    {
        "id": 17,
        "name": "Choléra",
        "keywords": ["diarrhée aqueuse", "vomissements abondants", "déshydratation", "selles liquides", "eau de riz", "choléra", "eau contaminée", "soif intense", "crampes", "yeux enfoncés"],
        "key_symptoms": ["choléra", "diarrhée eau de riz", "déshydratation sévère", "yeux enfoncés", "selles eau de riz"],
        "common_symptoms": ["diarrhée aqueuse", "vomissements abondants", "soif intense", "crampes"],
        "excludes": ["toux", "fièvre élevée"],
        "symptoms": ["Diarrhée aqueuse très abondante (aspect eau de riz)", "Vomissements incessants", "Déshydratation sévère et rapide", "Crampes musculaires douloureuses", "Soif intense et peau sèche", "Yeux enfoncés", "Pouls rapide et faible"],
        "description": "Infection intestinale aiguë par Vibrio cholerae, transmise par l'eau et aliments contaminés. Peut être mortelle en quelques heures sans réhydratation urgente.",
        "treatment": ["Réhydratation orale massive (SRO) en urgence", "Perfusion IV si déshydratation sévère", "Antibiotiques : Azithromycine ou Doxycycline", "Hospitalisation immédiate", "Isolement du patient"],
        "prevention": ["Eau bouillie ou traitée uniquement", "Lavage des mains au savon", "Cuire les aliments correctement", "Vaccination orale anti-choléra", "Assainissement des eaux"],
        "severity": "urgence",
        "color": "#dc2626",
    },
    {
        "id": 18,
        "name": "Fièvre jaune",
        "keywords": ["jaunisse", "fièvre", "saignements", "vomissements noirs", "fièvre jaune", "moustique", "yeux jaunes", "foie", "hémorragie", "vaccin jaune"],
        "key_symptoms": ["fièvre jaune", "vomissements noirs", "jaunisse fébrile", "hémorragie fièvre"],
        "common_symptoms": ["jaunisse", "fièvre", "saignements", "moustique", "yeux jaunes"],
        "excludes": ["toux", "diarrhée"],
        "symptoms": ["Fièvre élevée brutale avec frissons", "Jaunisse (peau et yeux jaunes)", "Vomissements pouvant être sanglants (noirs)", "Saignements multiples (gencives, nez)", "Douleurs abdominales et lombaires", "Ralentissement du pouls paradoxal", "Altération de la conscience dans les formes graves"],
        "description": "Maladie virale hémorragique transmise par les moustiques Aedes. Peut être mortelle dans les formes graves. Vaccin très efficace disponible.",
        "treatment": ["Traitement symptomatique uniquement (pas d'antiviral spécifique)", "Hospitalisation en soins intensifs", "Hydratation, antipyrétiques (pas d'aspirine)", "Transfusions si hémorragies sévères", "Prévention des complications rénales et hépatiques"],
        "prevention": ["Vaccination anti-amarile obligatoire et à vie", "Protection anti-moustiques", "Élimination des gîtes larvaires", "Surveillance épidémiologique active", "Certification vaccinale pour les voyageurs"],
        "severity": "urgence",
        "color": "#dc2626",
    },
    {
        "id": 19,
        "name": "Bilharziose (Schistosomiase)",
        "keywords": ["sang urine", "urine rouge", "démangeaisons baignade", "rivière", "bilharziose", "schistosomiase", "foie gonflé", "rate gonflée", "ver", "eau douce"],
        "key_symptoms": ["bilharziose", "schistosomiase", "sang dans les urines", "démangeaisons après baignade"],
        "common_symptoms": ["urine rouge", "rivière", "foie gonflé", "rate gonflée", "ver"],
        "excludes": ["toux", "vomissements"],
        "symptoms": ["Sang dans les urines (hématurie)", "Démangeaisons cutanées après baignade", "Fièvre et frissons en phase aiguë", "Foie et rate hypertrophiés", "Fatigue chronique et anémie", "Douleurs abdominales"],
        "description": "Maladie parasitaire causée par des vers trématodes contractés dans les eaux douces. Deuxième maladie parasitaire mondiale après le paludisme.",
        "treatment": ["Praziquantel en dose unique (40 mg/kg)", "Très efficace avec peu d'effets secondaires", "Contrôle à 4-6 semaines", "Traitement des complications hépatiques", "Traitement de masse en zones endémiques"],
        "prevention": ["Éviter de se baigner dans les eaux douces stagnantes", "Eau traitée pour se laver", "Contrôle des mollusques hôtes", "Traitement préventif annuel", "Assainissement et eau potable"],
        "severity": "modérée",
        "color": "#f59e0b",
    },
    {
        "id": 20,
        "name": "Pneumonie",
        "keywords": ["toux productive", "fièvre élevée", "essoufflement", "douleur poitrine", "pneumonie", "poumons", "expectorations", "respiration difficile", "crachat jaune", "crachat vert"],
        "key_symptoms": ["pneumonie", "douleur poitrine", "expectorations jaunes vertes", "crachat jaune", "crachat vert"],
        "common_symptoms": ["toux productive", "fièvre élevée", "essoufflement", "poumons", "respiration difficile"],
        "excludes": ["diarrhée", "sang urine"],
        "symptoms": ["Toux productive avec expectorations jaunes ou vertes", "Fièvre élevée avec frissons", "Douleur thoracique à la respiration", "Essoufflement et respiration accélérée", "Fatigue et malaise général", "Crépitements à l'auscultation"],
        "description": "Infection pulmonaire aiguë bactérienne (pneumocoque) ou virale. Cause majeure de mortalité en Afrique, surtout chez les enfants de moins de 5 ans.",
        "treatment": ["Antibiotiques : Amoxicilline ou Amoxicilline-Clavulanate", "Alternative : Azithromycine ou Ceftriaxone", "Hospitalisation si forme sévère", "Oxygénothérapie si SpO2 < 92%", "Hydratation et antipyrétiques"],
        "prevention": ["Vaccination pneumococcique (PCV13)", "Vaccination antigrippale annuelle", "Ne pas fumer", "Bonne ventilation des locaux", "Lavage des mains régulier"],
        "severity": "grave",
        "color": "#ef4444",
    },
    {
        "id": 21,
        "name": "Rougeole",
        "keywords": ["éruption cutanée", "boutons rouges", "fièvre", "toux", "yeux rouges", "taches blanches bouche", "enfant", "rougeole", "conjonctivite", "photophobie"],
        "key_symptoms": ["rougeole", "taches de Koplik", "éruption débutant au visage", "conjonctivite fièvre toux"],
        "common_symptoms": ["fièvre", "toux", "yeux rouges", "boutons rouges", "photophobie"],
        "excludes": ["diarrhée", "sang urine"],
        "symptoms": ["Fièvre élevée (39-40°C)", "Toux sèche persistante", "Yeux rouges et larmoyants", "Taches blanches dans la bouche (Koplik)", "Éruption rouge débutant au visage", "Sensibilité à la lumière", "Écoulements nasaux"],
        "description": "Maladie virale très contagieuse par le Morbillivirus. Peut causer pneumonie, encéphalite, cécité. Évitable par la vaccination ROR.",
        "treatment": ["Paracétamol, repos, hydratation", "Vitamine A (réduit mortalité et complications)", "Antibiotiques si surinfection bactérienne", "Hospitalisation si complications", "Isolement strict"],
        "prevention": ["Vaccination ROR : à 9 mois puis 15-18 mois", "Isolement des cas pendant 5 jours", "Vaccination de rattrapage", "Couverture vaccinale > 95%"],
        "severity": "grave",
        "color": "#ef4444",
    },
    {
        "id": 22,
        "name": "Rage",
        "keywords": ["morsure chien", "morsure animal", "rage", "peur eau", "hydrophobie", "agitation", "animal enragé", "convulsions", "salive abondante", "paralysie"],
        "key_symptoms": ["rage", "hydrophobie", "peur de l'eau", "morsure animal enragé", "agitation extrême"],
        "common_symptoms": ["morsure chien", "morsure animal", "convulsions", "salive abondante", "paralysie"],
        "excludes": [],
        "symptoms": ["Douleur au site de morsure", "Fièvre et anxiété", "Agitation extrême", "Hydrophobie (peur panique de l'eau)", "Aérophobie", "Hypersalivation et spasmes", "Convulsions et paralysie", "Coma puis décès"],
        "description": "Maladie virale mortelle à 100% une fois les symptômes apparus. Transmise par morsure d'animaux infectés. La vaccination post-exposition SAUVE LA VIE.",
        "treatment": ["Lavage immédiat de la plaie au savon 15 minutes", "Vaccination antirabique post-exposition URGENTE (J0, J3, J7, J14)", "Immunoglobulines antirabiques à J0", "Consulter dans les 24h après toute morsure", "Aucun traitement une fois les symptômes apparus"],
        "prevention": ["Vaccination systématique des animaux domestiques", "Éviter les animaux errants", "Vaccination préventive pour les groupes à risque", "Ne jamais retarder la vaccination post-exposition"],
        "severity": "urgence",
        "color": "#dc2626",
    },
    {
        "id": 23,
        "name": "Lèpre (Maladie de Hansen)",
        "keywords": ["taches peau insensibles", "perte sensibilité", "nodules", "déformation mains", "pieds", "lèpre", "nerf", "plaies indolores", "sourcils", "peau épaissie"],
        "key_symptoms": ["lèpre", "taches insensibles", "perte de sensibilité peau", "déformation mains pieds", "nerf insensible"],
        "common_symptoms": ["nodules", "plaies indolores", "sourcils", "peau épaissie"],
        "excludes": ["fièvre", "diarrhée", "toux"],
        "symptoms": ["Taches claires ou rougeâtres insensibles", "Perte progressive de la sensibilité", "Nodules et épaississement cutané", "Déformation des mains et pieds", "Plaies chroniques indolores", "Paralysie musculaire", "Perte des sourcils"],
        "description": "Maladie infectieuse chronique par Mycobacterium leprae. Guérissable si détectée tôt grâce à la polychimiothérapie OMS gratuite.",
        "treatment": ["Polychimiothérapie OMS gratuite : Rifampicine + Clofazimine + Dapsone", "6 mois (paucibacillaire) ou 12 mois (multibacillaire)", "Corticoïdes pour les réactions lépreuses", "Chirurgie reconstructrice si déformations", "Rééducation fonctionnelle"],
        "prevention": ["Dépistage précoce et traitement immédiat", "BCG offre protection partielle", "Chimioprophylaxie des contacts proches", "Amélioration des conditions de vie", "Lutte contre la stigmatisation"],
        "severity": "chronique",
        "color": "#8b5cf6",
    },
    {
        "id": 24,
        "name": "Zona (Herpes Zoster)",
        "keywords": ["douleur unilatérale", "vésicules", "brûlures", "zona", "herpes", "bande", "côté du corps", "douleur nerveuse", "éruption côté", "ruban"],
        "key_symptoms": ["zona", "éruption unilatérale", "vésicules en bande", "douleur nerveuse"],
        "common_symptoms": ["douleur unilatérale", "vésicules", "brûlures", "côté du corps"],
        "excludes": ["diarrhée", "toux", "sang"],
        "symptoms": ["Douleur vive et brûlante sur un seul côté", "Éruption de vésicules en bande (dermatome)", "Démangeaisons et hypersensibilité", "Fièvre modérée et fatigue", "Douleurs pouvant persister après cicatrisation"],
        "description": "Réactivation du virus varicelle-zona (VZV) dormant dans les ganglions nerveux. Surtout chez les personnes âgées ou immunodéprimées.",
        "treatment": ["Antiviraux : Acyclovir ou Valacyclovir dans les 72h", "Antalgiques adaptés (palier 2 ou 3 si douleurs sévères)", "Désinfection locale des vésicules", "Prévention de la névralgie post-zostérienne", "Corticoïdes si zona ophtalmique"],
        "prevention": ["Vaccination anti-zona (Shingrix) pour les plus de 50 ans", "Renforcement immunitaire", "Traitement rapide dès les premiers signes", "Éviter le contact avec les femmes enceintes non immunisées"],
        "severity": "modérée",
        "color": "#f59e0b",
    },
    {
        "id": 25,
        "name": "Intoxication alimentaire",
        "keywords": ["nausées", "vomissements", "diarrhée", "douleur ventre", "intoxication alimentaire", "aliment avarié", "repas", "crampes", "selles", "après manger"],
        "key_symptoms": ["intoxication alimentaire", "après avoir mangé", "aliment suspect", "plusieurs personnes malades"],
        "common_symptoms": ["nausées", "vomissements", "diarrhée", "douleur ventre", "crampes"],
        "excludes": ["fièvre élevée", "sang urine"],
        "symptoms": ["Nausées et vomissements rapides", "Diarrhée aiguë", "Crampes abdominales", "Survenue rapide après un repas suspect", "Fièvre modérée possible", "Faiblesse et malaise général"],
        "description": "Infection ou intoxination suite à la consommation d'aliments contaminés par des bactéries (Salmonella, Staphylocoque) ou leurs toxines.",
        "treatment": ["Réhydratation orale (SRO)", "Diète alimentaire transitoire", "Antibiotiques si origine bactérienne sévère", "Antiémétiques si vomissements importants", "Hospitalisation si déshydratation sévère"],
        "prevention": ["Réfrigération correcte des aliments", "Cuisson suffisante des viandes", "Hygiène des mains lors de la préparation", "Ne pas laisser les aliments à température ambiante", "Eau potable pour cuisiner"],
        "severity": "légère",
        "color": "#10b981",
    },
    {
        "id": 26,
        "name": "Conjonctivite infectieuse",
        "keywords": ["yeux rouges", "conjonctivite", "larmoiement", "yeux collés", "sécrétions yeux", "brûlure yeux", "démangeaison yeux", "pus yeux", "oeil rouge"],
        "key_symptoms": ["conjonctivite", "yeux collés le matin", "sécrétions purulentes oeil"],
        "common_symptoms": ["yeux rouges", "larmoiement", "brûlure yeux", "démangeaison yeux"],
        "excludes": ["fièvre élevée", "diarrhée"],
        "symptoms": ["Rougeur intense d'un ou des deux yeux", "Sécrétions purulentes collant les paupières", "Larmoiement abondant", "Sensation de sable dans l'oeil", "Démangeaisons et brûlures", "Légère sensibilité à la lumière", "Gonflement des paupières"],
        "description": "Inflammation très contagieuse de la conjonctive par bactéries ou virus. Très fréquente en Afrique, favorisée par la chaleur et la poussière.",
        "treatment": ["Collyre antibiotique (Tobramycine, Ciprofloxacine)", "Nettoyage au sérum physiologique", "Collyre antihistaminique si allergique", "Consultation si pas d'amélioration en 3 jours"],
        "prevention": ["Lavage des mains et ne pas se frotter les yeux", "Ne pas partager serviettes ou maquillage", "Éviter le contact avec les personnes atteintes", "Lunettes de protection en zone poussiéreuse"],
        "severity": "légère",
        "color": "#10b981",
    },
    {
        "id": 27,
        "name": "Insuffisance cardiaque",
        "keywords": ["essoufflement couché", "jambes gonflées", "oedème", "essoufflement effort", "coeur", "palpitations", "fatigue extrême", "dyspnée", "nuit couché", "prise de poids"],
        "key_symptoms": ["insuffisance cardiaque", "essoufflement couché", "orthopnée", "oedème des membres inférieurs"],
        "common_symptoms": ["jambes gonflées", "essoufflement effort", "palpitations", "fatigue extrême", "dyspnée"],
        "excludes": ["diarrhée", "toux productive"],
        "symptoms": ["Essoufflement à l'effort puis au repos", "Oedèmes des jambes et chevilles", "Orthopnée (ne peut dormir qu'assis)", "Prise de poids rapide (rétention eau)", "Fatigue extrême", "Palpitations", "Toux sèche nocturne"],
        "description": "Incapacité du coeur à pomper suffisamment de sang. Souvent liée à l'hypertension, au diabète ou aux maladies coronariennes.",
        "treatment": ["Diurétiques (Furosémide) pour éliminer la rétention d'eau", "IEC ou ARA2 pour réduire la charge cardiaque", "Bêtabloquants", "Restriction hydrique et sodée", "Traitement de la cause sous-jacente"],
        "prevention": ["Contrôler hypertension et diabète rigoureusement", "Arrêt du tabac et de l'alcool", "Activité physique adaptée", "Surveillance cardiologique régulière", "Traitement précoce des infections cardiaques"],
        "severity": "chronique",
        "color": "#8b5cf6",
    },
    {
        "id": 28,
        "name": "Trypanosomiase (Maladie du sommeil)",
        "keywords": ["somnolence", "sommeil diurne", "fièvre", "ganglions cou", "confusion", "maladie du sommeil", "mouche tsé-tsé", "troubles neurologiques", "coma", "trypanosomiase"],
        "key_symptoms": ["maladie du sommeil", "trypanosomiase", "mouche tsé-tsé", "somnolence diurne excessive", "signe de Winterbottom"],
        "common_symptoms": ["somnolence", "fièvre", "ganglions cou", "confusion"],
        "excludes": ["toux", "diarrhée"],
        "symptoms": ["Gonflement au site de piqûre de tsé-tsé", "Fièvre intermittente", "Ganglions lymphatiques enflés dans le cou", "Somnolence diurne excessive", "Confusion mentale et troubles du comportement", "Maux de tête intenses", "Troubles du cycle veille-sommeil", "Coma aux stades avancés"],
        "description": "Maladie parasitaire fatale causée par Trypanosoma brucei, transmise par la mouche tsé-tsé. Mortelle sans traitement.",
        "treatment": ["Stade 1 : Pentamidine ou Suramine IV", "Stade 2 neurologique : NECT (Nifurtimox-Éflornithine)", "Hospitalisation spécialisée obligatoire", "Suivi post-traitement 2 ans"],
        "prevention": ["Éviter les zones forestières infestées", "Vêtements longs de couleur neutre", "Répulsifs insecticides", "Pièges à tsé-tsé", "Dépistage actif des populations rurales"],
        "severity": "grave",
        "color": "#ef4444",
    },
    {
        "id": 29,
        "name": "Parotidite (Oreillons)",
        "keywords": ["joue gonflée", "gonflement parotide", "mâchoire douloureuse", "oreillons", "glandes salivaires", "gonflement cou", "douleur avaler", "oreille", "enfant joue"],
        "key_symptoms": ["oreillons", "joue gonflée", "gonflement parotide bilatéral"],
        "common_symptoms": ["mâchoire douloureuse", "glandes salivaires", "douleur avaler", "oreille"],
        "excludes": ["diarrhée", "sang urine"],
        "symptoms": ["Gonflement douloureux des glandes parotides", "Fièvre modérée (38-39°C)", "Douleur à la mastication et déglutition", "Gonflement devant et sous les oreilles", "Maux de tête et fatigue", "Perte d'appétit"],
        "description": "Maladie virale par le paramyxovirus touchant les glandes salivaires. Peut causer méningite, surdité et infertilité masculine.",
        "treatment": ["Paracétamol ou ibuprofène pour fièvre et douleurs", "Compresses froides sur les glandes", "Alimentation molle et liquide", "Repos complet et hydratation"],
        "prevention": ["Vaccination ROR : 9 mois puis 15-18 mois", "Isolement des malades 5 jours", "Lavage fréquent des mains"],
        "severity": "modérée",
        "color": "#f59e0b",
    },
    {
        "id": 30,
        "name": "Cancer du col de l'utérus",
        "keywords": ["saignement vaginal", "douleur pelvis", "rapport douloureux", "cancer col", "pertes vaginales", "HPV", "frottis", "col utérus", "saignement entre règles"],
        "key_symptoms": ["cancer col utérus", "HPV", "saignement post-coïtal", "frottis anormal"],
        "common_symptoms": ["saignement vaginal", "douleur pelvis", "rapport douloureux", "pertes vaginales"],
        "excludes": ["toux", "diarrhée", "fièvre"],
        "symptoms": ["Saignements vaginaux anormaux (entre les règles, après rapport)", "Pertes vaginales inhabituelles et malodorantes", "Douleurs pelviennes chroniques", "Rapports sexuels douloureux", "Douleurs lombaires dans les stades avancés"],
        "description": "Cancer du col utérin causé principalement par le HPV. Première cause de décès par cancer chez la femme africaine. Dépistable et traitable si détecté tôt.",
        "treatment": ["Chirurgie : conisation, hystérectomie selon le stade", "Radiothérapie et chimiothérapie", "Dépistage précoce par frottis cervical (Pap test) ou IVA", "Traitement des lésions précancéreuses par cryothérapie ou LEEP"],
        "prevention": ["Vaccination HPV pour les filles 9-14 ans", "Dépistage par frottis tous les 3 ans dès 25 ans", "Préservatif pour réduire le risque HPV", "Arrêt du tabac"],
        "severity": "grave",
        "color": "#ef4444",
    },
    {
        "id": 31,
        "name": "Drépanocytose (Anémie falciforme)",
        "keywords": ["crise douloureuse os", "anémie sévère", "jaunisse enfant", "drépanocytose", "hémoglobine S", "crises vaso-occlusives", "AVC enfant", "douleur thorax", "gonflement mains pieds bébé", "rate"],
        "key_symptoms": ["drépanocytose", "crises vaso-occlusives", "hémoglobine S", "anémie falciforme"],
        "common_symptoms": ["crise douloureuse os", "jaunisse", "gonflement mains pieds bébé", "rate gonflée"],
        "excludes": ["toux", "diarrhée"],
        "symptoms": ["Crises vaso-occlusives douloureuses aux os, thorax, abdomen", "Anémie chronique sévère", "Jaunisse", "Gonflement douloureux des mains et pieds chez le nourrisson", "Fatigue et essoufflement", "Infections fréquentes", "Rate hypertrophiée", "AVC chez l'enfant"],
        "description": "Maladie génétique héréditaire très répandue en Afrique. Les globules rouges falciformes obstruent les vaisseaux et provoquent des crises douloureuses graves.",
        "treatment": ["Hydroxyurée pour réduire les crises", "Antalgiques puissants pendant les crises", "Hydratation intensive", "Acide folique quotidien à vie", "Transfusions si anémie sévère", "Greffe de moelle osseuse (seul traitement curatif)"],
        "prevention": ["Dépistage néonatal systématique", "Conseil génétique avant grossesse", "Vaccinations complètes", "Pénicilline prophylactique jusqu'à 5 ans", "Éviter déshydratation, froid et altitude"],
        "severity": "chronique",
        "color": "#8b5cf6",
    },
    {
        "id": 32,
        "name": "Ulcère gastrique et Gastrite",
        "keywords": ["brûlure estomac", "douleur épigastre", "acidité", "reflux acide", "nausées", "ulcère", "gastrite", "creux estomac", "helicobacter pylori", "digestion"],
        "key_symptoms": ["ulcère", "gastrite", "helicobacter pylori", "brûlure épigastrique rythmée par les repas"],
        "common_symptoms": ["brûlure estomac", "acidité", "reflux acide", "nausées", "creux estomac"],
        "excludes": ["toux", "sang urine", "fièvre élevée"],
        "symptoms": ["Douleur ou brûlure au creux de l'estomac", "Douleur rythmée par les repas", "Nausées et vomissements", "Ballonnements et gaz", "Reflux acide", "Perte d'appétit", "Selles noires si saignement"],
        "description": "Lésion inflammatoire de la muqueuse gastrique souvent liée à H. pylori ou aux AINS. Très fréquente en Afrique.",
        "treatment": ["Oméprazole 20-40 mg/jour", "Triple thérapie anti-H. pylori si infection", "Antiacides pour soulagement rapide", "Arrêt des AINS et alcool", "Repas fractionnés, éviter épices"],
        "prevention": ["Manger régulièrement, éviter le jeûne", "Réduire alcool et café fort", "Éviter les AINS sans protection gastrique", "Traiter H. pylori si détecté", "Gérer le stress"],
        "severity": "modérée",
        "color": "#f59e0b",
    },
    {
        "id": 33,
        "name": "Insuffisance rénale chronique",
        "keywords": ["reins", "créatinine", "dialyse", "insuffisance rénale", "jambes gonflées", "oedème", "peu d'urines", "hypertension rénale", "protéines urines"],
        "key_symptoms": ["insuffisance rénale", "créatinine élevée", "dialyse", "protéines dans les urines"],
        "common_symptoms": ["jambes gonflées", "peu d'urines", "hypertension rénale", "oedème"],
        "excludes": ["toux", "diarrhée", "fièvre"],
        "symptoms": ["Fatigue et faiblesse progressives", "Gonflement des jambes et pieds", "Urines mousseuses ou peu abondantes", "Hypertension résistante", "Nausées et perte d'appétit sévère", "Démangeaisons généralisées", "Essoufflement", "Confusion aux stades avancés"],
        "description": "Dégradation progressive et irréversible de la fonction rénale, complication du diabète et de l'hypertension non contrôlés.",
        "treatment": ["Contrôle strict de la tension (IEC ou ARA2)", "Régime pauvre en sel, potassium et phosphore", "Traitement de l'anémie associée", "Hémodialyse ou dialyse péritonéale si terminale", "Greffe rénale"],
        "prevention": ["Contrôler diabète et hypertension", "Éviter les AINS prolongés", "Boire 1,5-2 litres d'eau par jour", "Bilan rénal annuel si diabète ou HTA", "Éviter plantes néphrotoxiques"],
        "severity": "chronique",
        "color": "#8b5cf6",
    },
    {
        "id": 34,
        "name": "IST — Gonorrhée et Chlamydia",
        "keywords": ["écoulement génital", "brûlure urinaire", "douleur pelvienne", "gonorrhée", "chlamydia", "pertes anormales", "urètre douloureux", "infertilité", "MST", "IST"],
        "key_symptoms": ["gonorrhée", "chlamydia", "IST", "MST", "écoulement urétral purulent"],
        "common_symptoms": ["brûlure urinaire", "douleur pelvienne", "pertes anormales", "infertilité"],
        "excludes": ["toux", "fièvre élevée", "diarrhée"],
        "symptoms": ["Écoulements purulents du pénis ou du vagin", "Brûlures lors de la miction", "Douleurs pelviennes chez la femme", "Rougeur urétrale", "Douleurs testiculaires chez l'homme", "Souvent asymptomatique", "Fièvre légère si infection pelvienne"],
        "description": "IST bactériennes très fréquentes en Afrique. Non traitées, elles causent infertilité définitive et complications néonatales.",
        "treatment": ["Gonorrhée : Ceftriaxone 500 mg IM dose unique", "Chlamydia : Azithromycine 1g oral dose unique", "Alternative : Doxycycline 100 mg 2x/j 7 jours", "Traitement simultané du ou des partenaires", "Abstinence jusqu'à guérison"],
        "prevention": ["Préservatif systématique", "Dépistage régulier si partenaires multiples", "Traitement simultané des partenaires", "Dépistage prénatal", "Fidélité mutuelle"],
        "severity": "modérée",
        "color": "#f59e0b",
    },
    {
        "id": 35,
        "name": "Cataracte",
        "keywords": ["vue trouble", "vision floue progressive", "éblouissement", "oeil blanc", "cataracte", "cécité progressive", "mauvaise vision nocturne", "halo lumières", "couleurs ternes"],
        "key_symptoms": ["cataracte", "opacification cristallin", "pupille blanche", "vision floue progressive indolore"],
        "common_symptoms": ["vue trouble", "éblouissement", "mauvaise vision nocturne", "halo lumières"],
        "excludes": ["fièvre", "diarrhée", "douleur"],
        "symptoms": ["Vision floue et brumeuse progressive", "Éblouissement et halos autour des lumières", "Difficultés à voir la nuit", "Couleurs altérées", "Double vision dans l'oeil atteint", "Changements fréquents de lunettes", "Pupille blanche ou grisâtre"],
        "description": "Opacification progressive et indolore du cristallin. Première cause de cécité mondiale, très fréquente en Afrique. Guérissable par chirurgie simple.",
        "treatment": ["Chirurgie par phacoémulsification", "Pose d'un implant de cristallin (LIO)", "Intervention ambulatoire de 20-30 minutes", "En attente : lunettes adaptées et bon éclairage"],
        "prevention": ["Lunettes de soleil anti-UV (indice 3-4)", "Contrôle du diabète", "Alimentation riche en antioxydants", "Arrêt du tabac", "Consultation ophtalmologique annuelle après 50 ans"],
        "severity": "chronique",
        "color": "#8b5cf6",
    },
    {
        "id": 36,
        "name": "Coqueluche",
        "keywords": ["toux spasmodique", "quintes toux", "chant du coq", "nourrisson toux", "coqueluche", "vomissements après toux", "toux nocturne", "cyanose toux", "apnée nourrisson"],
        "key_symptoms": ["coqueluche", "toux spasmodique en quintes", "chant du coq", "cyanose après toux nourrisson"],
        "common_symptoms": ["quintes toux", "vomissements après toux", "toux nocturne", "apnée nourrisson"],
        "excludes": ["diarrhée", "sang urine"],
        "symptoms": ["Toux spasmodique violente en quintes", "Reprise inspiratoire sifflante (chant du coq)", "Vomissements après les quintes", "Cyanose chez le nourrisson", "Toux aggravée la nuit", "Apnées dangereuses chez les nourrissons"],
        "description": "Infection bactérienne par Bordetella pertussis. Extrêmement dangereuse et potentiellement mortelle chez les nourrissons non vaccinés.",
        "treatment": ["Azithromycine (traitement de choix)", "Alternative : Clarithromycine ou Cotrimoxazole", "Hospitalisation des nourrissons < 6 mois", "Oxygénothérapie si détresse respiratoire"],
        "prevention": ["Vaccination DTP dès 6 semaines", "Rappels tous les 10 ans", "Vaccination de la femme enceinte", "Isolement strict 3 semaines"],
        "severity": "grave",
        "color": "#ef4444",
    },
    {
        "id": 37,
        "name": "Tétanos",
        "keywords": ["contracture musculaire", "trismus", "mâchoire bloquée", "raideur musculaire", "tétanos", "plaie", "spasme", "dos arqué", "rigidité", "convulsions tétanos"],
        "key_symptoms": ["tétanos", "trismus", "mâchoire bloquée", "opisthotonos", "contractures généralisées"],
        "common_symptoms": ["contracture musculaire", "raideur", "spasme", "dos arqué"],
        "excludes": ["diarrhée", "toux"],
        "symptoms": ["Trismus : mâchoire bloquée, impossibilité d'ouvrir la bouche", "Contractures musculaires douloureuses progressives", "Rigidité de la nuque et du dos", "Spasmes déclenchés par bruit ou lumière", "Dos arqué en arrière (opisthotonos)", "Fièvre modérée", "Risque d'arrêt respiratoire"],
        "description": "Maladie bactérienne grave par toxine de Clostridium tetani pénétrant par une plaie. Potentiellement mortelle, surtout chez le nouveau-né.",
        "treatment": ["Hospitalisation immédiate en soins intensifs", "Immunoglobulines antitétaniques humaines (HTIG)", "Antibiotiques : Métronidazole ou Pénicilline G IV", "Myorelaxants pour contrôler les spasmes", "Nettoyage chirurgical de la plaie"],
        "prevention": ["Vaccination DTP : rappels tous les 10 ans", "Vaccination femme enceinte obligatoire", "Nettoyage et désinfection de toute plaie", "Prophylaxie antitétanique après blessure souillée"],
        "severity": "urgence",
        "color": "#dc2626",
    },
    {
        "id": 38,
        "name": "Filariose lymphatique (Éléphantiasis)",
        "keywords": ["gonflement jambes", "jambes énormes", "éléphantiasis", "filariose", "lymphoedème", "moustique", "ganglions inguinaux", "scrotum gonflé", "peau épaissie jambes"],
        "key_symptoms": ["éléphantiasis", "filariose", "lymphoedème massif", "scrotum hypertrophié"],
        "common_symptoms": ["gonflement jambes", "ganglions inguinaux", "peau épaissie jambes"],
        "excludes": ["toux", "diarrhée"],
        "symptoms": ["Gonflement progressif et massif des jambes ou bras", "Éléphantiasis : membres démesurément gonflés", "Peau épaissie et durcie", "Épisodes de fièvre et frissons", "Ganglions inguinaux enflés", "Hydrocèle chez l'homme"],
        "description": "Maladie parasitaire causée par des filaires transmises par les moustiques affectant le système lymphatique. Très répandue en Afrique tropicale.",
        "treatment": ["Diéthylcarbamazine + Albendazole (traitement OMS)", "Soins locaux : lavage, hydratation, bandages", "Kinésithérapie lymphatique", "Chirurgie pour hydrocèles volumineuses"],
        "prevention": ["Traitement préventif de masse annuel", "Protection anti-moustiques", "Assainissement et élimination gîtes larvaires", "Port de chaussures", "Hygiène rigoureuse des membres atteints"],
        "severity": "chronique",
        "color": "#8b5cf6",
    },
    {
        "id": 39,
        "name": "Onchocercose (Cécité des rivières)",
        "keywords": ["démangeaisons intenses", "nodules sous peau", "perte de vue", "onchocercose", "cécité rivière", "simulie", "mouche noire", "prurit", "lésions oculaires", "rivière rapide"],
        "key_symptoms": ["onchocercose", "cécité des rivières", "simulie", "nodules sous-cutanés fermes"],
        "common_symptoms": ["démangeaisons intenses", "perte de vue", "prurit", "lésions oculaires"],
        "excludes": ["toux", "diarrhée", "fièvre élevée"],
        "symptoms": ["Prurit cutané intense et permanent", "Nodules indurés et indolores sous la peau", "Lésions cutanées chroniques", "Troubles visuels progressifs", "Cécité irréversible aux stades avancés"],
        "description": "Maladie parasitaire par Onchocerca volvulus transmise par les simulies (mouches noires) près des rivières rapides. Deuxième cause de cécité infectieuse mondiale.",
        "treatment": ["Ivermectine (Mectizan) : dose annuelle ou semestrielle", "Programme de traitement de masse OMS gratuit", "Doxycycline contre la bactérie Wolbachia symbiote", "Exérèse chirurgicale des nodules si nécessaire"],
        "prevention": ["Éviter les zones de rivières rapides en zone endémique", "Répulsifs insecticides", "Vêtements couvrants", "Participation au traitement préventif de masse"],
        "severity": "grave",
        "color": "#ef4444",
    },
    {
        "id": 40,
        "name": "Paludisme cérébral (Malaria grave)",
        "keywords": ["convulsions paludisme", "coma malaria", "paludisme grave", "malaria cérébrale", "fièvre convulsions enfant", "perte connaissance malaria", "anémie sévère malaria", "urines noires malaria"],
        "key_symptoms": ["paludisme cérébral", "malaria grave", "coma fébrile", "convulsions fièvre enfant", "urines noires malaria"],
        "common_symptoms": ["convulsions", "coma", "fièvre très élevée", "anémie sévère"],
        "excludes": ["toux", "diarrhée"],
        "symptoms": ["Convulsions répétées chez l'enfant", "Altération de la conscience jusqu'au coma", "Fièvre très élevée et incontrôlable", "Anémie sévère", "Détresse respiratoire", "Urines noires (hémoglobinurie)", "Hypoglycémie sévère"],
        "description": "Forme la plus grave du paludisme à Plasmodium falciparum avec atteinte cérébrale. Urgence vitale absolue avec mortalité élevée sans traitement immédiat.",
        "treatment": ["URGENCE : artésunate IV en soins intensifs", "Alternative : quinine IV si artésunate non disponible", "Traitement des convulsions et de l'hypoglycémie", "Transfusion sanguine si anémie sévère", "Assistance ventilatoire si détresse respiratoire"],
        "prevention": ["Moustiquaire imprégnée toutes les nuits", "Chimioprophylaxie pour les voyageurs", "Traitement préventif intermittent femme enceinte", "Consulter immédiatement tout épisode fébrile chez l'enfant"],
        "severity": "urgence",
        "color": "#dc2626",
    },
    {
        "id": 41,
        "name": "Leishmaniose",
        "keywords": ["plaie chronique", "ulcère cutané chronique", "rate gonflée", "fièvre prolongée", "leishmaniose", "phlébotome", "amaigrissement", "foie hypertrophie", "kala-azar"],
        "key_symptoms": ["leishmaniose", "kala-azar", "ulcère indolore chronique", "fièvre irrégulière et rate gonflée"],
        "common_symptoms": ["plaie chronique", "rate gonflée", "fièvre prolongée", "amaigrissement"],
        "excludes": ["toux", "diarrhée"],
        "symptoms": ["Ulcère indolore et chronique ne guérissant pas (forme cutanée)", "Fièvre prolongée et irrégulière (forme viscérale)", "Gonflement important du foie et de la rate", "Amaigrissement et cachexie", "Anémie sévère", "Hyperpigmentation cutanée"],
        "description": "Maladie parasitaire par Leishmania transmise par les phlébotomes. La forme viscérale (kala-azar) est mortelle sans traitement.",
        "treatment": ["Antimoniate de méglumine (Glucantime) IM", "Amphotéricine B liposomale (référence actuelle)", "Miltefosine orale (alternative)", "Durée 28-30 jours selon la forme"],
        "prevention": ["Protection contre les phlébotomes (répulsifs, moustiquaires fines)", "Éviter les sorties au crépuscule", "Vêtements couvrants", "Lutte anti-vectorielle"],
        "severity": "grave",
        "color": "#ef4444",
    },
    {
        "id": 42,
        "name": "Ankylostomiase (Vers intestinaux)",
        "keywords": ["vers intestinaux", "anémie enfant", "démangeaisons pieds", "ankylostome", "parasites intestinaux", "ventre gonflé enfant", "pica", "mange terre", "larves peau"],
        "key_symptoms": ["vers intestinaux", "ankylostome", "pica (mange la terre)", "anémie sévère chez l'enfant"],
        "common_symptoms": ["démangeaisons pieds", "ventre gonflé enfant", "larves peau"],
        "excludes": ["toux", "fièvre élevée"],
        "symptoms": ["Prurit et éruption au point d'entrée cutanée", "Douleurs épigastriques et crampes", "Diarrhée ou selles noires", "Anémie ferriprive sévère", "Pica : envie de manger de la terre", "Abdomen distendu chez l'enfant", "Retard de croissance"],
        "description": "Infestation par des ankylostomes pénétrant par la peau nue. Très fréquente chez les enfants en Afrique, cause majeure d'anémie.",
        "treatment": ["Albendazole 400 mg en dose unique", "Alternative : Mébendazole 500 mg dose unique", "Traitement de l'anémie : fer oral et acide folique", "Contrôle à 4 semaines"],
        "prevention": ["Porter des chaussures pour éviter le sol", "Utiliser des latrines", "Lavage des mains avant les repas", "Déparasitage semestriel des enfants"],
        "severity": "modérée",
        "color": "#f59e0b",
    },
    {
        "id": 43,
        "name": "Hernie inguinale",
        "keywords": ["bosse aine", "hernie aine", "gonflement aine", "hernie inguinale", "douleur aine effort", "bosse disparaît allongé", "abdomen", "chirurgie hernie", "étranglement hernie"],
        "key_symptoms": ["hernie inguinale", "bosse aine disparaissant en position allongée", "tuméfaction inguinale réductible"],
        "common_symptoms": ["bosse aine", "douleur aine effort", "gonflement aine"],
        "excludes": ["fièvre", "toux", "diarrhée"],
        "symptoms": ["Bosse ou gonflement visible à l'aine", "Douleur ou gêne à l'aine à l'effort", "Bosse disparaissant en position allongée", "Sensation de lourdeur", "Douleur soudaine intense si étranglement", "Nausées si hernie étranglée"],
        "description": "Protrusion d'une partie de l'intestin à travers la paroi abdominale au niveau de l'aine. Très fréquente en Afrique. L'étranglement est une urgence chirurgicale.",
        "treatment": ["Chirurgie : herniorraphie (seul traitement curatif)", "Urgence chirurgicale si hernie étranglée", "Ceintures de maintien uniquement en attente", "Hospitalisation brève, récupération rapide"],
        "prevention": ["Éviter le port de lourdes charges répétées", "Traiter toux chronique et constipation", "Maintenir un poids sain", "Consulter rapidement à l'apparition d'une bosse"],
        "severity": "modérée",
        "color": "#f59e0b",
    },
    {
        "id": 44,
        "name": "Dépression",
        "keywords": ["tristesse profonde", "déprime", "dépression", "perte d'envie", "idées noires", "pleurs", "insomnie", "fatigue morale", "pensées négatives", "sans espoir", "isolement"],
        "key_symptoms": ["dépression", "tristesse persistante plus de 2 semaines", "idées noires", "perte d'intérêt total"],
        "common_symptoms": ["perte d'envie", "pleurs", "insomnie", "fatigue morale", "isolement"],
        "excludes": ["fièvre", "toux", "diarrhée"],
        "symptoms": ["Tristesse profonde et persistante (plus de 2 semaines)", "Perte totale d'intérêt pour les activités habituelles", "Fatigue intense et manque d'énergie", "Troubles du sommeil (insomnie ou hypersomnie)", "Difficultés de concentration", "Sentiment de dévalorisation", "Perte ou gain d'appétit", "Pensées de mort dans les formes sévères"],
        "description": "Trouble psychiatrique très fréquent, souvent non diagnostiqué en Afrique. La dépression est une maladie traitable. En cas d'idées suicidaires, une aide est disponible.",
        "treatment": ["Psychothérapie : thérapie cognitive et comportementale (TCC)", "Antidépresseurs si forme modérée à sévère (Fluoxétine)", "Soutien social et familial", "Activité physique régulière", "Consultation psychiatrique ou psychologique"],
        "prevention": ["Parler de ses difficultés à des proches", "Maintenir des liens sociaux", "Activité physique régulière", "Consulter un professionnel de santé mentale", "Techniques de relaxation et pleine conscience"],
        "severity": "modérée",
        "color": "#f59e0b",
    },
    {
        "id": 45,
        "name": "AVC (Accident vasculaire cérébral)",
        "keywords": ["paralysie soudaine", "visage asymétrique", "bras faiblesse soudaine", "parole trouble", "AVC", "attaque cérébrale", "hémiplégie", "aphasie", "maux de tête brutal", "vision double soudaine"],
        "key_symptoms": ["AVC", "paralysie soudaine", "hémiplégie", "aphasie", "attaque cérébrale", "maux de tête en coup de tonnerre"],
        "common_symptoms": ["visage asymétrique", "bras faiblesse soudaine", "parole trouble", "vision double soudaine"],
        "excludes": ["toux", "diarrhée", "fièvre"],
        "symptoms": ["Paralysie ou faiblesse soudaine d'un côté", "Asymétrie du visage (bouche déviée)", "Troubles soudains de la parole", "Perte de vision soudaine", "Maux de tête brutaux et intenses", "Perte d'équilibre", "Confusion soudaine", "Perte de conscience"],
        "description": "Interruption brutale de la circulation cérébrale. Urgence absolue : chaque minute compte pour limiter les séquelles. Appeler le SAMU immédiatement.",
        "treatment": ["URGENCE ABSOLUE : SAMU et hospitalisation immédiate", "AVC ischémique : thrombolyse IV dans les 4h30", "Thrombectomie mécanique si disponible", "Aspirine si thrombolyse non possible", "Rééducation neurologique intensive"],
        "prevention": ["Contrôler hypertension artérielle rigoureusement", "Arrêter définitivement le tabac", "Traiter diabète et cholestérol", "Activité physique et poids sain", "Consulter immédiatement à tout signe neurologique brutal"],
        "severity": "urgence",
        "color": "#dc2626",
    },
]


# ══════════════════════════════════════════════════════════════════════
# MOTEUR DE DIAGNOSTIC INTELLIGENT
# Algorithme multi-critères avec pondération :
#   - Symptômes-clés spécifiques  : poids x3
#   - Symptômes communs           : poids x1
#   - Termes exclusifs présents   : pénalité -50%
#   - Similarité phonétique/partielle
#   - Normalisation du score (0-100)
# ══════════════════════════════════════════════════════════════════════

# Synonymes et variantes orthographiques fréquentes
SYNONYMS = {
    "mal de tête": "maux de tête",
    "mal de ventre": "douleur abdominale",
    "mal au ventre": "douleur abdominale",
    "douleur au ventre": "douleur abdominale",
    "ventre douloureux": "douleur abdominale",
    "nez bouché": "congestion nasale",
    "nez qui coule": "écoulements nasaux",
    "se sentir faible": "fatigue",
    "perte de poids": "amaigrissement",
    "grosses fièvres": "fièvre élevée",
    "forte fièvre": "fièvre élevée",
    "piqûre moustique": "moustique",
    "manger terre": "pica",
    "pipi brûle": "brûlure en urinant",
    "faire pipi souvent": "uriner fréquemment",
    "envie d'uriner souvent": "uriner fréquemment",
    "diarrhée liquide": "diarrhée aqueuse",
    "selles liquides": "diarrhée aqueuse",
    "beaucoup vomir": "vomissements abondants",
    "envie de vomir": "nausées",
    "yeux qui piquent": "démangeaison yeux",
    "dos qui fait mal": "douleur dorsale",
    "difficulté à respirer": "essoufflement",
    "toux sèche": "toux",
    "toux avec crachat": "toux productive",
    "crachat du sang": "sang dans les crachats",
    "urine qui brûle": "brûlure en urinant",
    "paralysie": "hémiplégie",
    "bouche tordue": "visage asymétrique",
    "bouche déviée": "visage asymétrique",
    "frissons": "frissons",
    "sueurs la nuit": "sueurs nocturnes",
    "transpiration nuit": "sueurs nocturnes",
    "grossesse": "enceinte",
    "mal aux reins": "douleur lombaire",
    "vertiges": "étourdissements",
}

def normalize_text(text: str) -> str:
    """Normalise le texte : minuscules, accents simplifiés, synonymes."""
    text = text.lower().strip()
    # Appliquer les synonymes
    for src, tgt in SYNONYMS.items():
        text = text.replace(src, tgt)
    return text


def partial_match(keyword: str, text: str) -> float:
    """Retourne un score de correspondance entre 0 et 1."""
    keyword = keyword.lower()
    text = text.lower()

    # Match exact
    if keyword in text:
        return 1.0

    # Match par racine (les 5 premiers caractères)
    if len(keyword) >= 5:
        root = keyword[:5]
        if root in text:
            return 0.7

    # Match par mots individuels
    words = keyword.split()
    if len(words) > 1:
        matched_words = sum(1 for w in words if len(w) > 3 and w in text)
        if matched_words == len(words):
            return 0.9
        elif matched_words >= len(words) - 1 and len(words) >= 2:
            return 0.6

    # Similarité floue si le mot est long (> 6 chars)
    if len(keyword) >= 6:
        for word in text.split():
            ratio = SequenceMatcher(None, keyword, word).ratio()
            if ratio >= 0.85:
                return 0.8

    return 0.0


def find_diseases(symptom_text: str, top_n: int = 3) -> list:
    """
    Moteur de diagnostic multi-critères.
    Retourne les top_n maladies les plus probables avec score de confiance 0-100.
    """
    normalized = normalize_text(symptom_text)
    results = []

    for disease in DISEASES:
        score = 0.0
        matched_keywords = []
        matched_key = []
        matched_common = []

        # ── Symptômes-clés (poids fort x3) ──────────────────
        for kw in disease.get("key_symptoms", []):
            match = partial_match(kw, normalized)
            if match > 0:
                weight = 3.0 * match
                score += weight
                matched_key.append(kw)
                if kw not in matched_keywords:
                    matched_keywords.append(kw)

        # ── Symptômes communs (poids normal x1) ─────────────
        for kw in disease.get("common_symptoms", []):
            match = partial_match(kw, normalized)
            if match > 0:
                weight = 1.0 * match
                score += weight
                matched_common.append(kw)
                if kw not in matched_keywords:
                    matched_keywords.append(kw)

        # ── Mots-clés généraux (legacy, poids x0.8) ─────────
        for kw in disease.get("keywords", []):
            if kw not in disease.get("key_symptoms", []) and kw not in disease.get("common_symptoms", []):
                match = partial_match(kw, normalized)
                if match > 0:
                    score += 0.8 * match
                    if kw not in matched_keywords:
                        matched_keywords.append(kw)

        if score == 0:
            continue

        # ── Pénalité pour termes exclusifs ───────────────────
        penalty = 1.0
        for ex in disease.get("excludes", []):
            if partial_match(ex, normalized) > 0:
                penalty *= 0.5  # -50% par terme exclusif présent

        score *= penalty

        # ── Calcul de la confiance (normalisé 0-95) ──────────
        max_possible = (
            3.0 * len(disease.get("key_symptoms", [])) +
            1.0 * len(disease.get("common_symptoms", [])) +
            0.8 * max(0, len(disease.get("keywords", [])) - len(disease.get("key_symptoms", [])) - len(disease.get("common_symptoms", [])))
        )
        if max_possible > 0:
            raw_confidence = (score / max_possible) * 100
        else:
            raw_confidence = 0

        # Boost si beaucoup de symptômes-clés matchés
        key_ratio = len(matched_key) / max(1, len(disease.get("key_symptoms", [])))
        if key_ratio >= 0.5:
            raw_confidence = min(raw_confidence * 1.15, 95)

        confidence = min(int(raw_confidence), 95)

        if confidence < 5:
            continue

        results.append({
            **disease,
            "score": round(score, 2),
            "confidence": confidence,
            "matched_keywords": matched_keywords[:8],
            "matched_key_symptoms": matched_key,
        })

    # Tri par score décroissant
    results.sort(key=lambda x: x["score"], reverse=True)

    # Normaliser pour que le top résultat aille vers 85-90%
    if results:
        top_score = results[0]["score"]
        if top_score > 0:
            for r in results:
                raw = (r["score"] / top_score) * 90
                # Garder un minimum de 15% pour les résultats qui apparaissent
                r["confidence"] = max(15, min(90, int(raw)))
            # Le premier résultat : 85-92% selon la richesse des données
            first = results[0]
            key_ratio = len(first["matched_key_symptoms"]) / max(1, len(first.get("key_symptoms", [])))
            first["confidence"] = min(92, 75 + int(key_ratio * 17))

    return results[:top_n]
