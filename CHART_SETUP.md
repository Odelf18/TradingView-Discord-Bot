# Configuration des graphiques embarqués

Ce guide explique comment configurer les graphiques TradingView embarqués dans le bot Discord.

## Modes disponibles

Le bot supporte **deux modes** pour afficher les graphiques :

### 1. Mode Liens TradingView (Gratuit, par défaut)
- ✅ **100% gratuit**
- ✅ Aucune configuration requise
- ✅ Graphiques TradingView professionnels
- ❌ L'utilisateur doit cliquer sur les liens pour voir les graphiques

### 2. Mode Images Embarquées (Gratuit avec API key)
- ✅ Graphiques affichés directement dans Discord
- ✅ API gratuite (chart-img.com)
- ✅ Meilleure expérience utilisateur
- ⚠️ Nécessite une clé API (gratuite)

## Configuration des images embarquées

### Étape 1 : Obtenir une clé API chart-img.com

1. **Allez sur** [chart-img.com](https://chart-img.com)
2. **Cliquez sur "Get Started" ou "Sign In"**
3. **Connectez-vous avec Google** (authentification rapide)
4. **Accédez à votre Dashboard**
5. **Copiez votre API Key** (elle ressemble à : `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

### Étape 2 : Configurer le bot

Éditez votre fichier `.env` et ajoutez :

```env
# Votre clé API chart-img.com
CHARTIMG_API_KEY=votre_api_key_ici

# Activer les graphiques embarqués
USE_EMBEDDED_CHARTS=true
```

### Étape 3 : Redémarrer le bot

```bash
# Arrêtez le bot (Ctrl+C si lancé en avant-plan)
# Relancez-le
python main.py
```

## Comment ça marche ?

Quand un utilisateur tape `$AAPL` dans Discord :

### Avec images embarquées (CHARTIMG_API_KEY configurée) :
```
┌─────────────────────────────────────┐
│ $AAPL - Apple Inc.                  │
├─────────────────────────────────────┤
│ Prix: $185.42  (+2.3%)              │
│ Volume: 52M                         │
│ Market Cap: $2.87T                  │
│                                     │
│ [IMAGE DU GRAPHIQUE 1D AFFICHÉ]    │
│                                     │
│ 📊 Graphiques: [1H] [4H] [1D]      │
└─────────────────────────────────────┘
```

### Sans API key (mode liens uniquement) :
```
┌─────────────────────────────────────┐
│ $AAPL - Apple Inc.                  │
├─────────────────────────────────────┤
│ Prix: $185.42  (+2.3%)              │
│ Volume: 52M                         │
│ Market Cap: $2.87T                  │
│                                     │
│ 📊 Graphiques: [1H] [4H] [1D]      │
│ (Cliquez pour voir les graphiques) │
└─────────────────────────────────────┘
```

## Intervalles de graphiques

Le bot affiche toujours **3 intervalles** :

- **[1H]** - Graphique 1 heure (pour trading intraday)
- **[4H]** - Graphique 4 heures (pour tendances court terme)
- **[1D]** - Graphique journalier (pour analyse long terme)

**Avec images embarquées :** Le graphique 1D est affiché dans le message, et les 3 liens restent disponibles pour voir les autres intervalles.

**Sans images :** Les 3 liens sont cliquables pour ouvrir TradingView dans le navigateur.

## Désactiver les images embarquées

Si vous préférez utiliser uniquement les liens (même avec une API key), éditez `.env` :

```env
USE_EMBEDDED_CHARTS=false
```

## Paramètres de l'image

Les graphiques embarqués sont configurés pour :
- **Largeur :** 1000px
- **Hauteur :** 500px
- **Thème :** Dark (sombre)
- **Intervalle :** 1 jour (1D)
- **Indicateurs :** Volume

Vous pouvez modifier ces paramètres dans `cogs/stock_ticker.py` :

```python
chart_url = await generate_chart_image_url(
    ticker,
    interval='D',    # '60' (1h), '240' (4h), 'D' (1d)
    width=1000,      # Largeur en pixels
    height=500       # Hauteur en pixels
)
```

## Limites de l'API chart-img.com

### Plan Gratuit :
- **Limite exacte non documentée** par chart-img.com
- Généralement suffisant pour usage personnel et serveurs Discord moyens
- En cas de dépassement, le bot basculera automatiquement sur les liens

### Si vous dépassez les limites :
Le bot continuera de fonctionner normalement mais affichera les liens TradingView au lieu des images embarquées.

## Dépannage

### Les images ne s'affichent pas

1. **Vérifiez votre API key** :
   ```bash
   # Dans .env, vérifiez que :
   CHARTIMG_API_KEY=votre_clé_valide_ici
   # Pas d'espaces avant/après
   # Pas de guillemets
   ```

2. **Vérifiez USE_EMBEDDED_CHARTS** :
   ```bash
   USE_EMBEDDED_CHARTS=true
   # Doit être "true" (en minuscules)
   ```

3. **Redémarrez le bot** :
   ```bash
   # Arrêtez (Ctrl+C) et relancez
   python main.py
   ```

4. **Vérifiez les logs** :
   Le bot affichera des erreurs dans la console si l'API key est invalide.

### Message d'erreur "API key invalid"

- Votre clé API n'est pas valide
- Retournez sur chart-img.com et générez une nouvelle clé
- Assurez-vous de copier la clé complète (format UUID)

### Les liens fonctionnent mais pas les images

- L'API chart-img.com peut être temporairement indisponible
- Vérifiez votre connexion Internet
- Le bot basculera automatiquement sur les liens en cas d'erreur

## Alternative : Mode liens uniquement

Si vous préférez ne pas utiliser chart-img.com, le mode liens est **tout aussi fonctionnel** :

**Avantages des liens :**
- ✅ Aucune dépendance externe
- ✅ Pas de limite d'API
- ✅ Accès aux graphiques TradingView complets (zoom, indicateurs, etc.)
- ✅ Plus rapide (pas d'appel API supplémentaire)

**Pour utiliser uniquement les liens :**
1. Ne configurez pas `CHARTIMG_API_KEY`
2. Ou mettez `USE_EMBEDDED_CHARTS=false`

## Support

Pour plus d'informations :
- **chart-img.com :** [Documentation officielle](https://chart-img.com/docs)
- **TradingView :** [tradingview.com](https://www.tradingview.com)
- **README principal :** [README.md](README.md)

---

**Recommandation :** Commencez avec les liens TradingView (aucune configuration requise), puis ajoutez l'API chart-img.com si vous voulez les images embarquées.
