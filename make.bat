@echo off
if "%1"=="up" goto up
if "%1"=="down" goto down
if "%1"=="test" goto test
if "%1"=="clean" goto clean
goto help

:up
docker-compose up --build -d
goto end

:down
docker-compose down
goto end

:test
docker-compose run --rm app pytest
goto end

:clean
docker-compose down -v
echo Cleaning pycache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
goto end

:help
echo Usage: make [up|down|test|clean]
goto end

:end
