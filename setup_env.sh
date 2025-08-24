#!/bin/bash

# CineGenV5 Environment Setup Script

echo "🎬 CineGenV5 Environment Setup"
echo "================================"

# Set Google Cloud variables
export GOOGLE_CLOUD_PROJECT="recolormystuff"
export GOOGLE_CLOUD_LOCATION="us-central1"

echo "✅ Google Cloud variables set:"
echo "   PROJECT: $GOOGLE_CLOUD_PROJECT"
echo "   LOCATION: $GOOGLE_CLOUD_LOCATION"

# Check if API key is provided as argument
if [ -n "$1" ]; then
    export GOOGLE_API_KEY="$1"
    echo "✅ Google API Key set from argument"
else
    echo ""
    echo "🔑 To set your Google API Key:"
    echo "1. Get your API key from: https://makersuite.google.com/app/apikey"
    echo "2. Run: export GOOGLE_API_KEY='your-api-key-here'"
    echo "3. Or run this script with: ./setup_env.sh your-api-key-here"
    echo ""
    echo "⚠️  Reference image analysis will not be available without the API key"
fi

echo ""
echo "🚀 Ready to run CineGenV5!"
echo "   Run: python main.py"
