@echo off
setlocal

:: ...existing code...

:: Extraction du fichier zip
:extract_files
call :print_header "Extraction des fichiers"

if not exist "tana.zip" (
    call :print_error "Le fichier tana.zip n'a pas ete trouve"
    exit /b 1
)

:: Créer un dossier temporaire pour l'extraction
if not exist "temp_extract" mkdir temp_extract

:: Extraire le contenu
powershell -command "Expand-Archive -Path tana.zip -DestinationPath temp_extract -Force"

:: ...existing code...

:: Fonctions d'utilitaire
:get_compose_cmd
where docker-compose >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "COMPOSE_CMD=docker-compose"
    goto :EOF
)
docker compose version >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "COMPOSE_CMD=docker compose"
    goto :EOF
)
call :print_error "Ni docker-compose ni docker compose n'est disponible"
exit /b 1

:: Vérification des dépendances
:check_dependencies
call :print_header "Verification des dependances"
call :check_command docker
call :get_compose_cmd
call :print_success "Docker et %COMPOSE_CMD% sont installes"
goto :EOF

:: Construction de l'image Docker
:build_docker
call :print_header "Construction de l'image Docker"
call :get_compose_cmd
%COMPOSE_CMD% build
if %ERRORLEVEL% equ 0 (
    call :print_success "Image Docker construite avec succes"
) else (
    call :print_error "Erreur lors de la construction de l'image Docker"
    exit /b 1
)
goto :EOF

:: Démarrage du service
:start_service
call :print_header "Demarrage du service"
call :get_compose_cmd
%COMPOSE_CMD% up -d
if %ERRORLEVEL% equ 0 (
    call :print_success "Service demarre avec succes"
    %COMPOSE_CMD% ps
) else (
    call :print_error "Erreur lors du demarrage du service"
    exit /b 1
)
goto :EOF

:: Arrêt du service
:stop_service
call :print_header "Arret du service"
call :get_compose_cmd
%COMPOSE_CMD% down
if %ERRORLEVEL% equ 0 (
    call :print_success "Service arrete avec succes"
) else (
    call :print_error "Erreur lors de l'arret du service"
    exit /b 1
)
goto :EOF

:: Nettoyage complet
:clean_all
call :print_header "Nettoyage complet"

:: Arrêter les conteneurs
call :get_compose_cmd
%COMPOSE_CMD% down

:: ...existing code...

:: Affichage des logs
:show_logs
call :print_header "Logs du service"
call :get_compose_cmd
%COMPOSE_CMD% logs -f
goto :EOF

:: ...existing code...

endlocal