#!/bin/bash

# Script to add packages from requirements.txt using uv add
uv venv .venv
source .venv/bin/activate
uv init .

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found"
    exit 1
fi

# Read each line from requirements.txt and run uv add
while IFS= read -r package || [ -n "$package" ]; do
    # Skip empty lines and comments
    if [ -z "$package" ] || [[ "$package" =~ ^[[:space:]]*# ]]; then
        continue
    fi

    # Remove leading/trailing whitespace
    package=$(echo "$package" | xargs)

    echo "Adding: $package"
    uv add "$package"

    # Check if the command succeeded
    if [ $? -ne 0 ]; then
        echo "Warning: Failed to add $package"
    fi
done < requirements.txt

echo "Done adding packages from requirements.txt"
