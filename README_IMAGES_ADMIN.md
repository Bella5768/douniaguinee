# 📸 Guide d'Administration des Images DounIA

## 🎯 Sections disponibles pour ajouter des images :

### 1. 🖼️ Images Hero (Carousel et Arrière-plan)
- **Modèle** : `HeroImage`
- **URL Admin** : `/admin/inscriptions/heroimage/`
- **Positions** :
  - `gauche` : Images du carousel principal (4 images)
  - `arriere` : Images d'arrière-plan défilantes (5 images)

### 2. 📸 Images Événements DounIA 1 & 2
- **Modèle** : `EvenementImage`
- **URL Admin** : `/admin/inscriptions/evenementimage/`
- **Événements** :
  - `DounIA 1` : Contexte & Enseignements
  - `DounIA 2` : La suite du processus

### 3. 🎨 Images Restitution
- **Modèle** : `RestitutionImage`
- **URL Admin** : `/admin/inscriptions/restitutionimage/`
- **Usage** : Galerie de la page de restitution

### 4. 📊 Images Statistiques
- **Modèle** : `StatsImage`
- **URL Admin** : `/admin/inscriptions/statsimage/`
- **Usage** : Images pour les sections statistiques

### 5. 🏢 Images Ateliers
- **Modèle** : `Atelier`
- **URL Admin** : `/admin/inscriptions/atelier/`
- **Usage** : Images pour chaque atelier thématique

---

## 🚀 Comment ajouter des images :

### Étape 1 : Accéder à l'admin
1. Allez sur : `http://127.0.0.1:8000/admin/`
2. Connectez-vous avec vos identifiants admin

### Étape 2 : Choisir la section
1. Dans le menu "INSCRIPTIONS", choisissez le modèle approprié
2. Cliquez sur "Ajouter" pour créer une nouvelle image

### Étape 3 : Remplir les champs
- **Titre** : Nom descriptif de l'image
- **Image** : Uploader le fichier depuis votre ordinateur
- **URL de l'image** : Alternative (optionnel)
- **Description** : Texte descriptif (optionnel)
- **Ordre** : Numéro pour l'ordre d'affichage
- **Active** : Cocher pour afficher l'image

### Étape 4 : Sauvegarder
1. Cliquez sur "Sauvegarder"
2. L'image sera immédiatement visible sur le site

---

## 📋 Recommandations :

### 📏 Dimensions optimales
- **Hero Images** : 1200x800px (ratio 3:2)
- **Événement Images** : 800x600px (ratio 4:3)
- **Restitution Images** : 1000x750px (ratio 4:3)
- **Stats Images** : 1920x1080px (ratio 16:9)

### 💾 Format et poids
- **Formats** : JPG, PNG, WEBP
- **Poids max** : 2MB par image
- **Compression** : 80-90% qualité

### 🎨 Style visuel
- **Couleurs** : Cohérence avec l'identité CSIG (bleu #003366, or #D4A844)
- **Thème** : Images professionnelles liées à l'IA, la gouvernance, la Guinée
- **Qualité** : Haute résolution, bonne luminosité

---

## 🔧 Configuration des sections :

### DounIA 1 - Images suggérées :
- Photos des ateliers passés
- Infographies des résultats
- Portraits de participants
- Lieux des événements

### DounIA 2 - Images suggérées :
- Visuels de préparation
- Illustrations des thématiques
- Photos des organisateurs
- Supports de communication

### Restitution - Images suggérées :
- Photos synthèse
- Graphiques des recommandations
- Moments clés des ateliers
- Visuels des partenaires

---

## ⚡ Astuces pratiques :

1. **Ordre d'affichage** : Utilisez des nombres (10, 20, 30) pour pouvoir insérer facilement
2. **Cache** : Les images apparaissent immédiatement avec cache-busting automatique
3. **Fallback** : Si l'upload échoue, utilisez le champ URL
4. **Aperçu** : L'admin montre un aperçu de toutes les images
5. **Active/Inactive** : Désactivez temporairement une image sans la supprimer

---

## 🆘 Support :

En cas de problème :
1. Vérifiez le format et la taille du fichier
2. Assurez-vous que l'image est bien "Active"
3. Vérifiez l'ordre d'affichage
4. Rafraîchissez la page avec `Ctrl + Shift + R`

---

*Créé le 26 février 2026 pour le projet DounIA*
