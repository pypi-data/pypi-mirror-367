#!/bin/bash
# Build script for DataTidy documentation

echo "🔧 Building DataTidy Documentation"
echo "================================="

# Check if sphinx is installed
if ! python3 -c "import sphinx" 2>/dev/null; then
    echo "📦 Installing Sphinx and dependencies..."
    pip install sphinx sphinx-rtd-theme myst-parser
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf _build

# Build HTML documentation
echo "🏗️  Building HTML documentation..."
PYTHONPATH=.. sphinx-build -b html . _build/html

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Documentation built successfully!"
    echo "📖 Open _build/html/index.html to view the documentation"
    
    # Try to open documentation if on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "🌐 Opening documentation in browser..."
        open _build/html/index.html
    fi
else
    echo "❌ Documentation build failed"
    exit 1
fi

echo ""
echo "🚀 Documentation Features:"
echo "  • Complete API reference with examples"
echo "  • Enhanced fallback system documentation"
echo "  • Performance analysis and benchmarks"
echo "  • Configuration guides and examples"
echo "  • Production deployment patterns"