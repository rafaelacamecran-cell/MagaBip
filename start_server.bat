@echo off
:: Navega para o diretório do projeto
cd /d "d:\Meus projetos\MagaBip"

:: Ativa o ambiente virtual
call .venv\Scripts\activate

:: Inicia o servidor Flask (ajuste o arquivo de entrada se não for run.py)
python run.py

pause
