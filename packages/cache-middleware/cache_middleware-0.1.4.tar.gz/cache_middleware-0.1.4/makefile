# Variables
PROFILE="pak"
DOMAIN="impalah"
AWS_REGION="us-east-1"
REGISTRY_URI="public.ecr.aws/e2b2x4l7"
REPOSITORY_NAME="cache-middleware"
PLATFORM="linux/amd64"
BUILDER_NAME="mybuilder"
PART ?= patch  # can be overwritten with: make bump-version PART=minor

# Delete the virtual environment and force a sync
venv:
	rm -rf .venv && \
	echo "✅ Deleted virtual environment" && \
	uv sync && \
	echo "✅ Created virtual environment" && \
	uvx --from=toml-cli toml get --toml-path=pyproject.toml project.version

# Bump patch/minor/major version
bump-version:
	@v=$$(uvx --from=toml-cli toml get --toml-path=pyproject.toml project.version) && \
	echo "🔧 Current version: $$v" && \
	uvx --from bump2version bumpversion --allow-dirty --current-version "$$v" $(PART) pyproject.toml && \
	echo "✅ Version bumped to new $(PART)"

# Build python package
build: bump-version
	uv build

# Clean build artifacts
clean:
	rm -rf dist *.egg-info build && \
	echo "✅ Cleaned build artifacts"

# Publish package on PyPI (use UV_PYPI_TOKEN or .pypirc for authentication)
publish: build
	uv publish

# Publish on TestPyPI
publish-test: build
	uv publish --repository testpypi

# Build docker image
docker-build: bump-version
	@BASE_VERSION=$$(uvx --from=toml-cli toml get --toml-path=pyproject.toml project.version) && \
	echo "✅ Bumped version to $$BASE_VERSION" && \
	if docker buildx inspect $(BUILDER_NAME) >/dev/null 2>&1; then \
		echo "✅ Builder '$(BUILDER_NAME)' exists. Activating..."; \
		docker buildx use $(BUILDER_NAME); \
	else \
		echo "⚠️  Builder '$(BUILDER_NAME)' not found. Creating..."; \
		docker buildx create --name $(BUILDER_NAME) --use; \
	fi && \
	docker buildx inspect $(BUILDER_NAME) --bootstrap && \
	aws --profile $(PROFILE) ecr-public get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(REGISTRY_URI) && \
	docker run --rm --privileged multiarch/qemu-user-static --reset -p yes && \
	docker buildx build \
		--provenance=false \
		--progress=plain \
		--platform $(PLATFORM) \
		-t $(REGISTRY_URI)/$(DOMAIN)/$(REPOSITORY_NAME):$$BASE_VERSION \
		-f Dockerfile \
		--push .

# Alias for all the Python package release cycle
release: clean build publish

# Alias for all the Docker image release cycle
docker-release: docker-build

# Development utilities
# Ruff lint (style, imports, common errors)
lint:
	uv run ruff check src

# Sort imports
format:
	uv run ruff format src
	uv run ruff check --fix src

# Typing with mypy
type-check:
	uv run mypy src

# Bandit security scan
security-check:
	uv run bandit -r src

# Full review
check: lint format type-check security-check


# Test execution	
test:
	uv run pytest -v --tb=short --doctest-modules --disable-warnings --maxfail=1 --junitxml=junit.xml --cov-report term-missing --cov-report html:coverage_html_report --cov-report xml:coverage.xml --cov-config=.coveragerc --cov src tests

# Documentation commands
docs:
	uv run sphinx-build docs_source docs

docs-clean:
	rm -rf docs && \
	echo "✅ Cleaned documentation output"

docs-serve:
	uv run python -m http.server 8080 --directory docs

docs-rebuild: docs-clean docs
