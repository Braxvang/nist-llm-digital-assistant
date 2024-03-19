#!/bin/bash 

# Author: Braxton VanGundy
# A bash script that will automatically setup everything you need to run the 
# NIST digital assistant.

export MODEL_DIRECTORY=./models
export PYTHON_VENV_DIRECTORY=./venv

# Step 1. Build the Python environment.
# Check for Python first
if ! hash python3; then
    echo "Error could not find Python3 on this system, halting setup."
    exit 1
fi

# Now check to make sure the python found is the correct version
ver=$(python3 -V 2>&1 | sed 's/.* \([0-9]\).\([0-9]\).*/\1\2/')
if [ "$ver" -gt "310" ]; then
    echo "Building python environment ..."
    python3 -m venv $PYTHON_VENV_DIRECTORY
else
    ver=$(python3.11 -V 2>&1 | sed 's/.* \([0-9]\).\([0-9]\).*/\1\2/')
    if [ "$ver" -lt "310" ]; then
        echo "Building python environment ..."
        python3.11 -m venv $PYTHON_VENV_DIRECTORY
    else
        echo "Failed to find compitable version of python, halting setup."
        exit 1
    fi
fi

source $PYTHON_VENV_DIRECTORY/bin/activate
pip install -r requirements.txt
echo "Finished building Python environment."

# Step 2. Extract the NIST embedding file.
echo "Extracting NIST embedding model to $MODEL_DIRECTORY" ...
unzip $MODEL_DIRECTORY/nist_sp800_embeddingsv1.zip -d $MODEL_DIRECTORY

# Step 3. Combine all of the Misral Instruct model pieces back into a single GGUF file for LLAMA CPP.
echo "Reconstructing Mistral instruct 7B V02 in the $MODEL_DIRECTORY directory ..."
cat $MODEL_DIRECTORY/mistral-instruct-v02.* > $MODEL_DIRECTORY/mistral-7b-instruct-v0.2.Q6_K.gguf
echo "Finished reconstructing mistral-instruct, removing fileparts as they are no longer needed."
rm $MODEL_DIRECTORY/mistral-instruct-v02.*

# Provide instructions to the user
echo "The setup has completed.  To run the application, activate the python environment found in \"venv\" then cd into the \"flask_app\" directory and run the command \"flask --app nist_assistant_application run\""
echo "Note: If llama.cpp is not using your GPU, you may have to uninstall llama_cpp_python from the venv and then reinstall it using this command: \"CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir\""

