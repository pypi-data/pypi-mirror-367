#!/bin/bash
# TMDB CLI Demo Script
# This script demonstrates all the new features

echo "🎬 TMDB CLI Enhanced Features Demo"
echo "=================================="
echo ""

# Check if tmdb command is available (installed via pip)
if command -v tmdb &> /dev/null; then
    TMDB_CMD="tmdb"
    echo "📦 Using installed tmdb command"
elif command -v tmdb-cli &> /dev/null; then
    TMDB_CMD="tmdb-cli"
    echo "📦 Using installed tmdb-cli command"
elif [ -f "./tmdb" ]; then
    TMDB_CMD="./tmdb"
    echo "🔧 Using local development script"
else
    echo "❌ TMDB CLI not found. Please install with: pip install tmdb-cli-enhanced"
    exit 1
fi

echo ""

echo "1. 🔍 Basic Search (still works as before)"
$TMDB_CMD search "inception" | head -20
echo ""

echo "2. 📈 Trending Movies"
$TMDB_CMD trending --type week | head -15
echo ""

echo "3. 🎯 Movie Recommendations by Genre"
$TMDB_CMD recommend --genre "action" | head -20
echo ""

echo "4. 🎯 Movie Recommendations based on Inception"
$TMDB_CMD recommend --movie-id 27205 | head -20
echo ""

echo "5. 📋 Current Watchlist Status"
$TMDB_CMD watchlist
echo ""

echo "6. 🎬 Interactive Browser Help"
$TMDB_CMD browse --help
echo ""

echo "7. 📚 All Available Commands"
$TMDB_CMD --help
echo ""

echo "🎉 Demo Complete!"
echo ""
echo "💡 Try these interactive commands:"
echo "   $TMDB_CMD browse              # Interactive movie browser"
echo "   $TMDB_CMD browse --category top_rated  # Browse top rated movies"
echo "   $TMDB_CMD watchlist           # Manage your personal watchlist"
echo "   $TMDB_CMD recommend --genre horror     # Get horror movie recommendations"
