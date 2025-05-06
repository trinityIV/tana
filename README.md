# Protection d'ID Discord

Ce projet fournit un système sécurisé pour protéger votre ID Discord contre une utilisation non autorisée, soit par un script de ligne de commande, soit par un bot Discord.

## Installation facile

Utilisez les scripts d'installation automatique :

### Pour Linux/macOS
```bash
# Exécution via le menu interactif
./setup.sh

# OU installation complète automatique
./setup.sh install
```

### Pour Windows
```batch
# Exécution via le menu interactif
setup.bat

# OU installation complète automatique
setup.bat install
```

## Commandes du script d'installation

Les scripts `setup.sh` et `setup.bat` supportent les commandes suivantes :

- `extract` - Extrait les fichiers du zip
- `configure` - Configure le système (crée le .env)
- `build` - Construit l'image Docker
- `start` - Démarre le service
- `stop` - Arrête le service
- `logs` - Affiche les logs en temps réel
- `clean` - Nettoie complètement l'installation
- `install` - Installation complète (1-4)

## Installation manuelle avec Docker

### Construction de l'image

```bash
docker build -t discord-id-protector .
```

### Utilisation du Bot Discord

1. **Créer une application Discord**:
   - Visitez [Discord Developer Portal](https://discord.com/developers/applications)
   - Créez une nouvelle application et un bot
   - Copiez le token du bot et ajoutez-le dans votre fichier `.env`

2. **Inviter le bot sur votre serveur**:
   - Utilisez le lien OAuth2 avec les permissions `bot` et `applications.commands`
   - Ajoutez les permissions de base : envoyer des messages, lire les messages, etc.

3. **Interagir avec le bot (via messages privés uniquement)**:
   - `!generate` - Générer un nouveau token sécurisé
   - `!setup <token>` - Configurer votre ID Discord comme propriétaire
   - `!verify <token>` - Vérifier votre identité avec le token
   - `!find_user <user_id> <admin_token>` - Vérifier si un utilisateur est enregistré (admin uniquement)
   - `!list_users <admin_token>` - Lister les utilisateurs enregistrés (admin uniquement)
   - `!alerts on|off` - Activer ou désactiver les alertes de sécurité

## Sécurité

- Le token n'est jamais stocké en clair, seulement son hash salé
- Protection contre les attaques par force brute
- Alertes en temps réel en cas de tentative non autorisée
- Commandes sensibles uniquement disponibles en messages privés
- Données persistantes dans un volume Docker
