#!/bin/bash
# Setup script for SimLab development environment

# Exit on error
set -e

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Add uv to the PATH for this session
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source .venv/Scripts/activate
else
    # Unix-like
    source .venv/bin/activate
fi

# Install dependencies
echo "Installing development dependencies..."
uv pip install -e .[dev]

# Create pre-commit hook for formatting and linting
if [ ! -f ".git/hooks/pre-commit" ]; then
    echo "Creating pre-commit hook..."
    mkdir -p .git/hooks
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for formatting and linting

# Run ruff formatter
echo "Running ruff formatter..."
ruff format .

# Run ruff linter
echo "Running ruff linter..."
ruff check .

# Add any changes from formatting
git add -u
EOF
    chmod +x .git/hooks/pre-commit
fi

echo "Development environment setup complete!"
echo "Activate the virtual environment with:"
echo "  source .venv/bin/activate  # Unix-like systems"
echo "  .venv\\Scripts\\activate    # Windows"