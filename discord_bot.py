import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import id_protector
import asyncio
import datetime

# Charger les variables d'environnement
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Configuration du bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Ajouter une variable pour suivre le propriétaire du bot
owner_user = None

@bot.event
async def on_ready():
    print(f'Bot connecté en tant que {bot.user.name}')
    print('-------------------')
    
    # Configurer le gestionnaire d'alertes
    id_protector.set_alert_handler(alert_handler)
    id_protector.enable_alerts(True)
    
    # Charger le propriétaire s'il est configuré
    await load_owner()

async def load_owner():
    """Charge l'utilisateur propriétaire du bot."""
    global owner_user
    
    if id_protector.load_config():
        owner_id = id_protector.get_owner_id()
        try:
            owner_user = await bot.fetch_user(int(owner_id))
            print(f"Propriétaire chargé: {owner_user.name}#{owner_user.discriminator}")
        except:
            print(f"Impossible de charger l'utilisateur avec l'ID {owner_id}")

def alert_handler(alert_info):
    """
    Gestionnaire d'alertes qui envoie une notification au propriétaire.
    Sera appelé par id_protector lorsqu'une tentative suspecte est détectée.
    """
    if owner_user:
        # Créer un message d'alerte basé sur les informations
        message = f"⚠️ **ALERTE DE SÉCURITÉ** ⚠️\n\n"
        message += f"Une tentative d'utilisation de votre token a été détectée!\n"
        message += f"**Horodatage:** {alert_info['timestamp']}\n"
        message += f"**ID Discord:** {alert_info['discord_id']}\n"
        message += f"**Résultat:** {alert_info['result']}\n"
        
        if alert_info.get('ip'):
            message += f"**IP:** {alert_info['ip']}\n"
        
        message += "\nSi ce n'est pas vous, votre sécurité peut être compromise. Générez un nouveau token immédiatement!"
        
        # Utiliser asyncio pour envoyer le message de manière asynchrone
        asyncio.create_task(send_alert_to_owner(message))

async def send_alert_to_owner(message):
    """Envoie un message d'alerte au propriétaire."""
    if owner_user:
        try:
            await owner_user.send(message)
            print(f"Alerte envoyée à {owner_user.name}")
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'alerte: {str(e)}")

@bot.command(name='setup')
async def setup_security(ctx, token: str = None):
    """
    Configure la sécurité pour le propriétaire du bot.
    Usage: !setup <token>
    """
    # Vérifier si la commande est exécutée dans un canal privé
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("⚠️ Cette commande ne peut être utilisée que dans un message privé.")
        await ctx.message.delete()
        return
    
    # Vérifier si un token est fourni
    if not token:
        await ctx.send("⚠️ Veuillez fournir un token. Usage: `!setup <token>`")
        return
    
    # Configurer la sécurité
    owner_id = str(ctx.author.id)
    id_protector.setup_security(token, owner_id)
    
    await ctx.send("✅ Configuration terminée. Vous êtes maintenant le propriétaire du bot.")

@bot.command(name='verify')
async def verify_user(ctx, token: str = None):
    """
    Vérifie l'identité d'un utilisateur.
    Usage: !verify <token>
    """
    # Vérifier si la commande est exécutée dans un canal privé
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("⚠️ Cette commande ne peut être utilisée que dans un message privé.")
        await ctx.message.delete()
        return
    
    # Vérifier si un token est fourni
    if not token:
        await ctx.send("⚠️ Veuillez fournir un token. Usage: `!verify <token>`")
        return
    
    # Vérifier l'identité
    user_id = str(ctx.author.id)
    result = id_protector.verify_user(user_id, token)
    
    if result["success"]:
        await ctx.send(f"✅ {result['message']}")
    else:
        await ctx.send(f"❌ {result['message']}")

@bot.command(name='generate')
async def generate_token(ctx):
    """
    Génère un nouveau token sécurisé.
    Usage: !generate
    """
    # Vérifier si la commande est exécutée dans un canal privé
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("⚠️ Cette commande ne peut être utilisée que dans un message privé.")
        await ctx.message.delete()
        return
    
    token = id_protector.generate_secure_token()
    await ctx.send(f"🔑 Votre nouveau token sécurisé est: `{token}`\n⚠️ **IMPORTANT**: Conservez ce token en lieu sûr et ne le partagez jamais!")

@bot.command(name='find_user')
async def find_user(ctx, user_id: str = None, admin_token: str = None):
    """
    Vérifie si un ID utilisateur est enregistré.
    Usage: !find_user <user_id> <admin_token>
    """
    # Vérifier si la commande est exécutée dans un canal privé
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("⚠️ Cette commande ne peut être utilisée que dans un message privé.")
        await ctx.message.delete()
        return
    
    # Vérifier si les paramètres sont fournis
    if not user_id or not admin_token:
        await ctx.send("⚠️ Veuillez fournir un ID utilisateur et votre token admin. Usage: `!find_user <user_id> <admin_token>`")
        return
    
    # Vérifier si l'utilisateur est l'administrateur
    admin_id = str(ctx.author.id)
    if not id_protector.verify_admin(admin_id, admin_token):
        await ctx.send("❌ Accès refusé. Vous n'êtes pas autorisé à effectuer cette action.")
        return
    
    # Vérifier si l'ID utilisateur est enregistré
    is_registered = id_protector.is_registered_user(user_id)
    
    if is_registered:
        await ctx.send(f"✅ L'utilisateur avec l'ID `{user_id}` est enregistré dans le système.")
    else:
        await ctx.send(f"❌ L'utilisateur avec l'ID `{user_id}` n'est pas enregistré dans le système.")

@bot.command(name='list_users')
async def list_users(ctx, admin_token: str = None):
    """
    Liste tous les utilisateurs enregistrés (uniquement pour l'administrateur).
    Usage: !list_users <admin_token>
    """
    # Vérifier si la commande est exécutée dans un canal privé
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("⚠️ Cette commande ne peut être utilisée que dans un message privé.")
        await ctx.message.delete()
        return
    
    # Vérifier si le token admin est fourni
    if not admin_token:
        await ctx.send("⚠️ Veuillez fournir votre token admin. Usage: `!list_users <admin_token>`")
        return
    
    # Vérifier si l'utilisateur est l'administrateur
    admin_id = str(ctx.author.id)
    if not id_protector.verify_admin(admin_id, admin_token):
        await ctx.send("❌ Accès refusé. Vous n'êtes pas autorisé à effectuer cette action.")
        return
    
    # Dans la version actuelle, nous n'avons qu'un seul utilisateur (le propriétaire)
    if not id_protector.load_config():
        await ctx.send("❌ Aucune configuration trouvée.")
        return
    
    await ctx.send(f"👤 Utilisateur enregistré: `{id_protector.get_owner_id()}`")

@bot.command(name='alerts')
async def manage_alerts(ctx, action: str = None):
    """
    Activer ou désactiver les alertes de sécurité.
    Usage: !alerts on|off
    """
    # Vérifier si la commande est exécutée dans un canal privé
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("⚠️ Cette commande ne peut être utilisée que dans un message privé.")
        await ctx.message.delete()
        return
    
    # Vérifier si l'utilisateur est le propriétaire
    if str(ctx.author.id) != id_protector.get_owner_id():
        await ctx.send("❌ Seul le propriétaire peut gérer les alertes.")
        return
    
    if action and action.lower() == "on":
        id_protector.enable_alerts(True)
        await ctx.send("✅ Les alertes de sécurité sont maintenant activées.")
    elif action and action.lower() == "off":
        id_protector.enable_alerts(False)
        await ctx.send("🔕 Les alertes de sécurité sont maintenant désactivées.")
    else:
        await ctx.send("⚠️ Veuillez spécifier 'on' ou 'off'. Usage: `!alerts on` ou `!alerts off`")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"❌ Erreur: {str(error)}")

# Démarrer le bot
if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Erreur: BOT_TOKEN non défini dans le fichier .env")
        exit(1)
    
    # Essayer de charger la configuration existante
    id_protector.load_config()
    
    bot.run(BOT_TOKEN)
