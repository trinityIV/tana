#!/bin/bash

# Script de configuration et gestion du système de protection d'ID Discord
# Ce script permet d'extraire, configurer, démarrer et arrêter le système Docker

# Couleurs pour une meilleure lisibilité
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonctions d'utilitaire
print_header() {
    echo -e "\n${YELLOW}=== $1 ===${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 n'est pas installé. Veuillez l'installer avant de continuer."
        exit 1
    fi
}

# Vérifie quelle commande docker-compose est disponible
get_compose_cmd() {
    if command -v docker-compose &> /dev/null; then
        echo "docker-compose"
    elif docker compose version &> /dev/null; then
        echo "docker compose"
    else
        print_error "Ni docker-compose ni docker compose n'est disponible"
        exit 1
    fi
}

# Vérification des dépendances
check_dependencies() {
    print_header "Vérification des dépendances"
    check_command docker
    
    # Vérifier docker-compose ou docker compose
    COMPOSE_CMD=$(get_compose_cmd)
    print_success "Docker et $(echo $COMPOSE_CMD) sont installés"
}

# Extraction du fichier zip
extract_files() {
    print_header "Extraction des fichiers"
    
    if [ ! -f "tana.zip" ]; then
        print_error "Le fichier tana.zip n'a pas été trouvé"
        exit 1
    fi
    
    # Créer un dossier temporaire pour l'extraction
    mkdir -p temp_extract
    
    # Extraire le contenu
    unzip -o tana.zip -d temp_extract
    
    # Déplacer les fichiers au bon endroit
    for file in temp_extract/*; do
        cp -r "$file" ./
    done
    
    # Nettoyer
    rm -rf temp_extract
    
    # Rendre les scripts exécutables
    chmod +x *.sh
    
    print_success "Fichiers extraits avec succès"
}

# Configuration du système
configure_system() {
    print_header "Configuration du système"
    
    # Créer le dossier data s'il n'existe pas
    mkdir -p data
    
    # Vérifier si .env existe, sinon le créer
    if [ ! -f ".env" ]; then
        echo "# Token du bot Discord (à obtenir sur https://discord.com/developers/applications)" > .env
        echo "BOT_TOKEN=votre_token_de_bot_discord_ici" >> .env
        echo "" >> .env
        echo "# Chemins de configuration" >> .env
        echo "CONFIG_PATH=/app/data/config.json" >> .env
        echo "LOG_FILE=/app/data/access_attempts.log" >> .env
        
        print_success "Fichier .env créé. Veuillez modifier le token du bot Discord."
    else
        print_success "Fichier .env déjà présent"
    fi
}

# Construction de l'image Docker
build_docker() {
    print_header "Construction de l'image Docker"
    COMPOSE_CMD=$(get_compose_cmd)
    $COMPOSE_CMD build
    if [ $? -eq 0 ]; then
        print_success "Image Docker construite avec succès"
    else
        print_error "Erreur lors de la construction de l'image Docker"
        exit 1
    fi
}

# Démarrage du service
start_service() {
    print_header "Démarrage du service"
    COMPOSE_CMD=$(get_compose_cmd)
    $COMPOSE_CMD up -d
    if [ $? -eq 0 ]; then
        print_success "Service démarré avec succès"
        $COMPOSE_CMD ps
    else
        print_error "Erreur lors du démarrage du service"
        exit 1
    fi
}

# Arrêt du service
stop_service() {
    print_header "Arrêt du service"
    COMPOSE_CMD=$(get_compose_cmd)
    $COMPOSE_CMD down
    if [ $? -eq 0 ]; then
        print_success "Service arrêté avec succès"
    else
        print_error "Erreur lors de l'arrêt du service"
        exit 1
    fi
}

# Nettoyage complet
clean_all() {
    print_header "Nettoyage complet"
    
    # Arrêter les conteneurs
    COMPOSE_CMD=$(get_compose_cmd)
    $COMPOSE_CMD down
    
    # Supprimer les images
    echo "Suppression des images Docker..."
    docker rmi -f $(docker images -q discord-id-protector) 2>/dev/null || true
    
    # Supprimer le dossier data si demandé
    echo -n "Voulez-vous supprimer toutes les données (y/n)? "
    read answer
    if [ "$answer" = "y" ]; then
        rm -rf data
        print_success "Dossier data supprimé"
    fi
    
    print_success "Nettoyage terminé"
}

# Affichage des logs
show_logs() {
    print_header "Logs du service"
    COMPOSE_CMD=$(get_compose_cmd)
    $COMPOSE_CMD logs -f
}

# Menu principal
show_menu() {
    clear
    echo "============================================"
    echo "  Protection d'ID Discord - Gestion Docker  "
    echo "============================================"
    echo "1. Extraire les fichiers du zip"
    echo "2. Configurer le système"
    echo "3. Construire l'image Docker"
    echo "4. Démarrer le service"
    echo "5. Arrêter le service"
    echo "6. Afficher les logs"
    echo "7. Tout nettoyer"
    echo "8. Installation complète (1-4)"
    echo "0. Quitter"
    echo "--------------------------------------------"
    echo -n "Entrez votre choix: "
}

# Traitement des arguments en ligne de commande
if [ $# -ge 1 ]; then
    case "$1" in
        "extract") extract_files ;;
        "configure") configure_system ;;
        "build") build_docker ;;
        "start") start_service ;;
        "stop") stop_service ;;
        "logs") show_logs ;;
        "clean") clean_all ;;
        "install")
            check_dependencies
            extract_files
            configure_system
            build_docker
            start_service
            ;;
        *)
            echo "Usage: $0 [extract|configure|build|start|stop|logs|clean|install]"
            exit 1
            ;;
    esac
    exit 0
fi

# Menu interactif si aucun argument n'est fourni
while true; do
    show_menu
    read choice
    
    case $choice in
        1) extract_files; read -p "Appuyez sur Entrée pour continuer..." ;;
        2) configure_system; read -p "Appuyez sur Entrée pour continuer..." ;;
        3) build_docker; read -p "Appuyez sur Entrée pour continuer..." ;;
        4) start_service; read -p "Appuyez sur Entrée pour continuer..." ;;
        5) stop_service; read -p "Appuyez sur Entrée pour continuer..." ;;
        6) show_logs ;;
        7) clean_all; read -p "Appuyez sur Entrée pour continuer..." ;;
        8)
            check_dependencies
            extract_files
            configure_system
            build_docker
            start_service
            read -p "Appuyez sur Entrée pour continuer..."
            ;;
        0) exit 0 ;;
        *) echo "Choix invalide"; sleep 1 ;;
    esac
done
