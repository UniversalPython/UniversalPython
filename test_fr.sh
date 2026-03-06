#!/bin/bash

# Configuration
NATIVE_FILE="F:/UniversalPython/test/samples/fr/hello.fr.py"
ENGLISH_FILE="F:/UniversalPython/test/samples/en/conditionals.py"
LANGUAGE="french"
LOG_FILE="test_failures.log"

echo "Starting crash test for $LANGUAGE"

echo "Testing native to english"
python \universalpython\\universalpython.py -sl $LANGUAGE "$NATIVE_FILE" > /dev/null 2> .tmp_err

if [ $? -eq 0 ]; then
    echo "Transpilation didn't crash."
else
    echo "=Transpilation crashed."
    echo "----------------------------------------------------" >> "$LOG_FILE"
    echo "[$(date)] FAIL: Phase 1 ($LANGUAGE)" >> "$LOG_FILE"
    echo "Error Detail:" >> "$LOG_FILE"
    cat .tmp_err >> "$LOG_FILE" 
    echo "----------------------------------------------------" >> "$LOG_FILE"
    rm .tmp_err
    exit 1
fi

echo "Testing english to native"
python \universalpython\\universalpython.py -r -sl $LANGUAGE "$ENGLISH_FILE" > /dev/null 2> .tmp_err

if [ $? -eq 0 ]; then
    echo "Reverse transpilation didn't crash."
else
    echo "Reverse transpilation crashed."
    echo "----------------------------------------------------" >> "$LOG_FILE"
    echo "[$(date)] FAIL: Phase 2 ($LANGUAGE - Reverse)" >> "$LOG_FILE"
    echo "Error Detail:" >> "$LOG_FILE"
    cat .tmp_err >> "$LOG_FILE"
    echo "----------------------------------------------------" >> "$LOG_FILE"
    rm .tmp_err
    exit 1
fi

rm -f .tmp_err
echo "Test complete. No crashes detected."