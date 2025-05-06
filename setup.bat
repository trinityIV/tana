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

endlocal