#!/bin/bash

REQUIREMENTS="requirements.txt"
UI_DIR="JobAppTracker/QtGUI/ui"
CONFIG_FILE="project.env"

exit_error() {
    echo -e "\e[91mSetup failed. Exiting.\e[0m"
    exit 1
}

if ! source "${CONFIG_FILE}" >/dev/null 2>&1; then
    echo -e "\e[91m[ERROR]\e[0m Could not find ${CONFIG_FILE}."
    exit_error
fi

printf "Checking python installation... "

if ! command -v python3 >/dev/null 2>&1; then
    echo
    echo -e "\e[91m[ERROR]\e[0m Python was not found on PATH"
    echo -e "Please install Python \e[93m${MIN_PY_MAJOR}.${MIN_PY_MINOR}\e[0m or later from \e[94mhttps://www.python.org/downloads/\e[0m"
    exit_error
fi

PY_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PY_MAJOR="${PY_VERSION%%.*}"
PY_MINOR="${PY_VERSION#*.}"
PY_MINOR="${PY_MINOR%%.*}"

if (( PY_MAJOR < MIN_PY_MAJOR)) || { (( PY_MAJOR == MIN_PY_MAJOR )) && (( PY_MINOR < MIN_PY_MINOR )); }; then
    echo
    echo -e "\e[91m[ERROR]\e[0m Python \e[93m${PY_VERSION}\e[0m found, but \e[93m${MIN_PY_MAJOR}.${MIN_PY_MINOR}\e[0m is required."
    exit_error
fi

echo -e "\e[92mOK\e[0m"

printf "Creating virtual environment... "

if [ -f "${VENV_DIR}/bin/python" ]; then
    echo -e "\e[93mAlready exists. Skipping.\e[0m"
else
    if ! python3 -m venv "${VENV_DIR}" >/dev/null 2>&1; then
        echo
        echo -e "\e[91m[ERROR]\e[0m Failed to create virtual environment."
        exit_error
    else
        echo -e "\e[92mOK\e[0m"
    fi
fi

printf "Activating virtual environment... "

VIRTUAL_ENV=""
source "${VENV_DIR}/bin/activate"

if [ -z "${VIRTUAL_ENV}" ]; then
    echo
    echo -e "\e[91m[ERROR]\e[0m Failed to activate virtual environment."
    exit_error
fi

echo -e "\e[92mOK\e[0m"

echo "Installing requirements..."
python3 -m pip install --upgrade pip
if ! pip install -r "${REQUIREMENTS}"; then
    echo -e "\e[91m[ERROR]\e[0m Failed to install requirements."
    exit_error
fi

echo -e "\e[92mOK\e[0m"

printf "Compiling UI files... "

cd "./${UI_DIR}"

for file in *.ui; do
    name="${file%.*}"
    if ! pyuic6 "$file" -o "ui_${name}.py"; then
        echo
        echo -e "\e[91m[ERROR]\e[0m Failed to compile ${file}."
        exit_error
    fi
done

echo -e "\e[92mOK\e[0m"

echo -e "==== \e[92mSetup complete!\e[0m ===="
echo -e "To run the app, just run \e[94mStart.sh\e[0m"
