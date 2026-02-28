# 🖼️ Guide : Ajouter une Image Hero Principale

## 🎯 **Objectif**
Ajouter une image hero principale qui s'affiche en arrière-plan de la section hero sur la page d'accueil.

## 📍 **Où l'image s'affiche**
- **Page** : Page d'accueil (`/`)
- **Section** : Hero section (en haut de la page)
- **Position** : Arrière-plan derrière le texte et le carousel
- **Opacité** : 30% pour ne pas masquer le contenu

## 🚀 **Comment ajouter l'image**

### **Étape 1 : Accéder à l'admin**
1. Allez sur : `http://127.0.0.1:8000/admin/`
2. Connectez-vous avec vos identifiants

### **Étape 2 : Ouvrir la configuration**
1. Dans le menu **INSCRIPTIONS**, cliquez sur **"Configurations du site"**
2. Si aucune configuration n'existe, cliquez sur **"Ajouter"**
3. Sinon, cliquez sur la configuration existante pour la modifier

### **Étape 3 : Ajouter l'image hero**
1. **Cherchez** la section **"Hero Section"**
2. **Champ "Hero image (upload)"** : Cliquez sur "Choisir un fichier"
3. **Sélectionnez** votre image depuis votre ordinateur
4. **Alternative** : Utilisez le champ "Hero image URL (fallback)" pour une URL

### **Étape 4 : Configurer**
- **Hero badge** : Texte au-dessus du titre
- **Hero titre** : Titre principal
- **Hero titre span** : Partie colorée du titre
- **Hero description** : Texte sous le titre
- **Boutons** : Texte et liens des boutons

### **Étape 5 : Sauvegarder**
1. Cliquez sur **"Sauvegarder"** en bas de la page
2. L'image apparaît immédiatement sur le site

## 📏 **Spécifications recommandées**

### **Dimensions optimales**
- **Largeur** : 1920px minimum
- **Hauteur** : 1080px minimum
- **Ratio** : 16:9 (format paysage)
- **Résolution** : 72dpi (web)

### **Format et poids**
- **Formats** : JPG, PNG, WEBP
- **Poids max** : 2MB
- **Qualité** : 80-90% compression

### **Style visuel**
- **Sujet** : Paysages, architecture, technologie, IA, données
- **Couleurs** : Préférence pour tons bleus, neutres
- **Luminosité** : Claire pour ne pas masquer le texte
- **Composition** : Centre d'intérêt au milieu (couvert par le texte)

## 🎨 **Effet visuel obtenu**

### **Rendu final**
- **Arrière-plan** : Votre image en fond (30% d'opacité)
- **Texte** : Blanc avec ombre, parfaitement lisible
- **Carousel** : Images en avant-plan avec bordures CSIG
- **Slideshow** : Images d'arrière-plan défilantes par-dessus

### **Superposition**
1. **Fond** : Votre image hero (z-index: -1)
2. **Milieu** : Images défilantes (z-index: 0)
3. **Avant** : Texte et carousel (z-index: 2)

## 🔧 **Options avancées**

### **URL alternative**
Si l'upload ne fonctionne pas :
1. **Uploadez** l'image sur un service (Imgur, etc.)
2. **Copiez** l'URL directe
3. **Collez** dans "Hero image URL (fallback)"
4. **Sauvegardez**

### **Sans image**
Si aucun champ n'est rempli :
- **Fond transparent** : Pas d'image de fond
- **Texte blanc** : Toujours lisible
- **Design épuré** : Minimaliste

## 🎯 **Exemples d'utilisation**

### **Image d'entreprise**
- **Photo** : Bâtiment de l'organisation
- **Effet** : Professionnel, institutionnel
- **Recommandé** : Pour présentations officielles

### **Image conceptuelle**
- **Photo** : Visualisation IA, données, réseau
- **Effet** : Moderne, technologique
- **Recommandé** : Pour projets tech

### **Paysage local**
- **Photo** : Paysage guinéen, Conakry
- **Effet** : Local, identitaire
- **Recommandé** : Pour projets nationaux

## ⚡ **Astuces pratiques**

1. **Testez** l'aperçu avant de sauvegarder
2. **Optimisez** l'image pour le web
3. **Vérifiez** la lisibilité du texte
4. **Utilisez** des images avec zones claires au centre
5. **Évitez** les images très sombres ou très chargées

## 🆘 **Dépannage**

### **Image ne s'affiche pas**
- Vérifiez que le fichier est bien uploadé
- Rafraîchissez la page avec `Ctrl + Shift + R`
- Vérifiez le format (JPG/PNG/WEBP)

### **Texte pas lisible**
- Choisissez une image plus claire
- Vérifiez l'opacité (30% recommandée)
- Testez avec différentes images

### **Upload échoue**
- Vérifiez la taille (< 2MB)
- Essayez un autre format
- Utilisez l'URL alternative

---

## 🎉 **Résultat attendu**

Une fois l'image ajoutée :
- ✅ **Image hero** en arrière-plan de la section hero
- ✅ **Texte lisible** avec ombre et contraste
- ✅ **Design professionnel** cohérent CSIG
- ✅ **Responsive** sur tous les appareils

**Votre page d'accueil aura maintenant une image hero personnalisée !** 🚀

---

*Créé le 26 février 2026 pour le projet DounIA*
