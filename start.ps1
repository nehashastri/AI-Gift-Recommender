#!/usr/bin/env pwsh

# Gift Genius - Quick Start Script
# This script starts the FastAPI server and opens the application

Write-Host "🎁 Starting Gift Genius Chatbot POC..." -ForegroundColor Green
Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ Error: .env file not found!" -ForegroundColor Red
    Write-Host "Please create a .env file with your OpenAI API key:"
    Write-Host ""
    Write-Host "OPENAI_API_KEY=your-key-here"
    Write-Host "EDIBLE_API_URL=https://www.ediblearrangements.com/api/search/"
    exit 1
}

# Check if pixi is available
try {
    pixi --version | Out-Null
}
catch {
    Write-Host "❌ Error: Pixi not found!" -ForegroundColor Red
    Write-Host "Please install Pixi from: https://pixi.sh"
    exit 1
}

Write-Host "✓ Starting API server..." -ForegroundColor Green
Write-Host "  Server: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
pixi run api
