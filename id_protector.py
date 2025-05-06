# Ce module permet de protéger votre ID Discord contre une utilisation non autorisée.
# Il vérifie que l'ID Discord fourni et un jeton secret correspondent à ceux du propriétaire.
# Pour utiliser ce module :
# 1. Remplacez OWNER_DISCORD_ID par votre véritable ID Discord.
# 2. Remplacez SECRET_TOKEN par un jeton secret connu seulement de vous.
# 3. Utilisez la fonction is_authorized(discord_id, token) pour vérifier l'identité.
# Si la fonction retourne True, l'utilisateur est autorisé. Sinon, l'accès est refusé.

# Module simple de protection d'ID Discord

import hashlib
import os
import time
from typing import Tuple, Optional
import json
import datetime
import logging

# Ne stockez JAMAIS votre token en clair dans le code
# Utilisez plutôt un hash salé de votre token
OWNER_DISCORD_ID = ""  # Remplacez par votre véritable ID Discord
_TOKEN_HASH = None  # Sera défini lors de la configuration
_SALT = None  # Sera défini lors de la configuration
_LAST_AUTH_TIME = 0
_MAX_AUTH_ATTEMPTS = 5
_AUTH_ATTEMPTS = 0
_AUTH_COOLDOWN = 300  # secondes

# Chemins de fichiers pour la persistance
CONFIG_FILE = os.environ.get('CONFIG_PATH', '/app/data/config.json')

# Configurer la journalisation
log_file = os.environ.get('LOG_FILE', '/app/data/access_attempts.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Ajout de variables pour les alertes
_ALERT_ENABLED = True
_ALERT_HANDLER = None

def save_config():
    """Sauvegarde la configuration dans un fichier."""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump({
            'owner_id': OWNER_DISCORD_ID,
            'token_hash': _TOKEN_HASH,
            'salt': _SALT
        }, f)
    print(f"Configuration sauvegardée dans {CONFIG_FILE}")

def load_config():
    """Charge la configuration depuis un fichier."""
    global OWNER_DISCORD_ID, _TOKEN_HASH, _SALT
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            OWNER_DISCORD_ID = config.get('owner_id', OWNER_DISCORD_ID)
            _TOKEN_HASH = config.get('token_hash')
            _SALT = config.get('salt')
        print("Configuration chargée avec succès")
        return True
    except (FileNotFoundError, json.JSONDecodeError):
        print("Aucune configuration trouvée ou fichier invalide")
        return False

def setup_security(token: str, owner_id: str = None) -> None:
    """Configure la sécurité avec votre token secret sans le stocker directement."""
    global _TOKEN_HASH, _SALT, OWNER_DISCORD_ID
    
    if owner_id:
        OWNER_DISCORD_ID = owner_id
    
    _SALT = os.urandom(16).hex()
    _TOKEN_HASH = hashlib.sha256(f"{token}{_SALT}".encode()).hexdigest()
    save_config()
    print("Sécurité configurée. Ne partagez JAMAIS votre token.")

def set_alert_handler(handler_function):
    """
    Définit une fonction de callback pour les alertes.
    La fonction handler doit accepter un dictionnaire avec les infos de tentative.
    """
    global _ALERT_HANDLER
    _ALERT_HANDLER = handler_function

def enable_alerts(enabled=True):
    """Active ou désactive les alertes."""
    global _ALERT_ENABLED
    _ALERT_ENABLED = enabled

def is_authorized(discord_id: str, token: str) -> bool:
    """
    Retourne True si le discord_id et le jeton correspondent aux identifiants du propriétaire.
    Inclut des protections contre les attaques par force brute.
    """
    global _AUTH_ATTEMPTS, _LAST_AUTH_TIME
    
    # Vérifier si le système est configuré
    if _TOKEN_HASH is None or _SALT is None:
        raise RuntimeError("La sécurité n'a pas été configurée. Appelez setup_security d'abord.")
    
    # Protection contre les tentatives multiples
    current_time = time.time()
    if current_time - _LAST_AUTH_TIME < _AUTH_COOLDOWN and _AUTH_ATTEMPTS >= _MAX_AUTH_ATTEMPTS:
        print(f"Trop de tentatives. Réessayez dans {_AUTH_COOLDOWN - (current_time - _LAST_AUTH_TIME):.0f} secondes.")
        return False
    
    if current_time - _LAST_AUTH_TIME > _AUTH_COOLDOWN:
        _AUTH_ATTEMPTS = 0
    
    _LAST_AUTH_TIME = current_time
    _AUTH_ATTEMPTS += 1
    
    # Vérification du token et de l'ID
    token_hash = hashlib.sha256(f"{token}{_SALT}".encode()).hexdigest()
    result = discord_id == OWNER_DISCORD_ID and token_hash == _TOKEN_HASH
    
    # Journaliser la tentative d'authentification
    log_attempt(discord_id, result)
    
    # Envoyer une alerte en cas de tentative infructueuse avec un token soumis
    if not result and token and _ALERT_ENABLED and _ALERT_HANDLER:
        alert_info = {
            "timestamp": datetime.datetime.now().isoformat(),
            "discord_id": discord_id,
            "result": "échec",
            "ip": os.environ.get('REMOTE_ADDR', 'inconnue'),
            "type": "tentative_token"
        }
        _ALERT_HANDLER(alert_info)
    
    if result:
        _AUTH_ATTEMPTS = 0  # Réinitialiser les tentatives après un succès
    
    return result

def log_attempt(discord_id: str, success: bool):
    """Enregistre une tentative d'authentification dans le journal."""
    status = "réussie" if success else "échouée"
    logging.info(f"Tentative d'authentification {status} pour l'ID {discord_id}")

def generate_secure_token() -> str:
    """Génère un token sécurisé pour l'utilisation dans ce système."""
    return os.urandom(24).hex()

def is_registered_user(discord_id: str) -> bool:
    """
    Vérifie si un ID Discord est enregistré dans le système.
    """
    if not load_config():
        return False
    
    return discord_id == OWNER_DISCORD_ID

def verify_admin(discord_id: str, token: str) -> bool:
    """
    Vérifie si l'utilisateur est l'administrateur du système.
    """
    return is_authorized(discord_id, token)

def get_owner_id() -> str:
    """
    Retourne l'ID du propriétaire (pour la liste des utilisateurs).
    """
    return OWNER_DISCORD_ID

# Ajouter une fonction pour faciliter l'intégration avec le bot Discord
def verify_user(discord_id: str, token: str) -> dict:
    """
    Vérifie l'identité d'un utilisateur et retourne un dictionnaire de résultat.
    Utilisé par le bot Discord.
    """
    try:
        if not load_config():
            return {
                "success": False,
                "message": "Configuration non trouvée. Le bot n'est pas configuré."
            }
        
        auth_result = is_authorized(discord_id, token)
        
        if auth_result:
            return {
                "success": True,
                "message": "Authentification réussie. Utilisateur autorisé."
            }
        else:
            return {
                "success": False,
                "message": "Échec de l'authentification. Token ou ID incorrect."
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Erreur lors de la vérification: {str(e)}"
        }

# Exemple d'utilisation:
# 1. Générer un token sécurisé une seule fois
# token = generate_secure_token()
# print(f"Votre token sécurisé (sauvegardez-le en lieu sûr): {token}")
# 
# 2. Configurer la sécurité
# setup_security(token)
# 
# 3. Utiliser la vérification
# if is_authorized("your_discord_id_here", token):
#     print("Accès autorisé")
# else:
#     print("Accès refusé")

# Point d'entrée pour Docker
if __name__ == "__main__":
    import sys
    
    # Charge la configuration existante si disponible
    config_loaded = load_config()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "setup" and len(sys.argv) >= 3:
            # Format: python id_protector.py setup <token> [owner_id]
            token = sys.argv[2]
            owner_id = sys.argv[3] if len(sys.argv) > 3 else OWNER_DISCORD_ID
            setup_security(token, owner_id)
            print(f"Sécurité configurée pour l'ID: {owner_id}")
            
        elif sys.argv[1] == "verify" and len(sys.argv) >= 4:
            # Format: python id_protector.py verify <discord_id> <token>
            discord_id = sys.argv[2]
            token = sys.argv[3]
            
            if not config_loaded:
                print("Erreur: Aucune configuration trouvée. Exécutez 'setup' d'abord.")
                sys.exit(1)
                
            result = is_authorized(discord_id, token)
            print(f"Vérification: {'Succès' if result else 'Échec'}")
            sys.exit(0 if result else 1)
            
        elif sys.argv[1] == "generate":
            # Format: python id_protector.py generate
            token = generate_secure_token()
            print(f"Token généré: {token}")
            print("ATTENTION: Sauvegardez ce token en lieu sûr!")
            
        else:
            print("Commande non reconnue.")
            print("Utilisation:")
            print("  python id_protector.py generate")
            print("  python id_protector.py setup <token> [owner_id]")
            print("  python id_protector.py verify <discord_id> <token>")
    else:
        print("Mode Docker de protection Discord ID")
        print("Utilisation:")
        print("  docker run -v /path/to/data:/app/data image_name generate")
        print("  docker run -v /path/to/data:/app/data image_name setup <token> [owner_id]")
        print("  docker run -v /path/to/data:/app/data image_name verify <discord_id> <token>")
