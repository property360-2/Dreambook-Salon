.PHONY: help dev migrate seed lint test collect install clean

help:
	@echo "Dreambook Salon - Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Run development server"
	@echo "  make migrate    - Run migrations"
	@echo "  make seed       - Load demo data"
	@echo "  make lint       - Run linters (black, isort, flake8, djlint)"
	@echo "  make test       - Run tests"
	@echo "  make collect    - Collect static files"
	@echo "  make clean      - Clean temporary files"

install:
	pip install -r requirements.txt

dev:
	python manage.py runserver

migrate:
	python manage.py makemigrations
	python manage.py migrate

seed:
	python manage.py seed_demo

lint:
	black --check .
	isort --check-only .
	flake8 .
	djlint templates/ --check

lint-fix:
	black .
	isort .
	djlint templates/ --reformat

test:
	python manage.py test

collect:
	python manage.py collectstatic --noinput

deploy-static: collect
	@echo "Uploading static files to CDN..."
	@echo "Configure your CDN sync command here"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
