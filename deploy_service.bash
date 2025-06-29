#!/bin/bash

# AutoPalmpay Deployment Script for CentOS 8
# This script activates the virtual environment and starts the scheduled jobs

# Navigate to the project directory
cd /home/api_job/autopalmpay || { echo "Error: Project directory not found"; exit 1; }

# Activate the virtual environment
source venv/bin/activate || { echo "Error: Virtual environment activation failed"; exit 1; }

# Start the scheduled jobs in the background
nohup python schedule_example.py > autopalmpay.log 2>&1 &

# Get the process ID
PID=$!
echo "AutoPalmpay scheduled jobs started with PID: $PID"
echo "Log file: /home/api_job/autopalmpay/autopalmpay.log"