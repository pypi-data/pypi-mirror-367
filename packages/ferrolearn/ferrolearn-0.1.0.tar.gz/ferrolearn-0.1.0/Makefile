.PHONY: help install dev-install test benchmark clean build format lint check-rust check-python check

help:
	@echo "ferrolearn - High-performance ML library powered by Rust"
	@echo ""
	@echo "Available commands:"
	@echo "  make install      - Build and install the package"
	@echo "  make dev-install  - Install with development dependencies"
	@echo "  make test         - Run all tests"
	@echo "  make benchmark    - Run performance benchmarks"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make build        - Build the Rust extension"
	@echo "  make format       - Format code (Rust and Python)"
	@echo "  make lint         - Run linters"
	@echo "  make check        - Run all checks (format, lint, test)"

install:
	@echo "Building and installing ferrolearn..."
	pip install maturin
	maturin develop --release
	pip install -e .

dev-install:
	@echo "Installing development dependencies..."
	pip install maturin pytest numpy scikit-learn matplotlib pandas black ruff mypy
	maturin develop
	pip install -e .

build:
	@echo "Building Rust extension..."
	maturin build --release

test:
	@echo "Running tests..."
	cargo test
	pytest tests/ -v

benchmark:
	@echo "Running benchmarks..."
	python benchmarks/run_benchmarks.py

clean:
	@echo "Cleaning build artifacts..."
	cargo clean
	rm -rf target/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf **/__pycache__
	rm -rf .pytest_cache
	find . -name "*.so" -delete
	find . -name "*.pyc" -delete

format:
	@echo "Formatting code..."
	cargo fmt
	black python/ tests/ benchmarks/

lint:
	@echo "Running linters..."
	cargo clippy -- -D warnings
	ruff check python/ tests/ benchmarks/
	mypy python/ferrolearn --ignore-missing-imports

check-rust:
	@echo "Checking Rust code..."
	cargo fmt -- --check
	cargo clippy -- -D warnings
	cargo test

check-python:
	@echo "Checking Python code..."
	black --check python/ tests/ benchmarks/
	ruff check python/ tests/ benchmarks/
	mypy python/ferrolearn --ignore-missing-imports
	pytest tests/

check: check-rust check-python
	@echo "All checks passed!"

# Development helpers
run-example:
	@echo "Running example..."
	python examples/kmeans_example.py

profile:
	@echo "Profiling K-Means performance..."
	python benchmarks/profile_kmeans.py

docs:
	@echo "Building documentation..."
	cd docs && make html

serve-docs:
	@echo "Serving documentation..."
	cd docs/_build/html && python -m http.server