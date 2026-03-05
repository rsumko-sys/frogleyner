.PHONY: install run test docker docker-run

# Install Python dependencies
install:
	pip install -r requirements.txt

# Seed the database and start the bot (requires BOT_TOKEN in .env or environment)
run: install
	python seed.py && python main.py

# Run the test suite
test: install
	python -m pytest tests/ -v

# Build the Docker image
docker:
	docker build -t leinerfrog .

# Run the bot in Docker (reads BOT_TOKEN from .env; persists DB in a named volume)
docker-run: docker
	docker run --rm \
		--env-file .env \
		-v leinerfrog-data:/data \
		-e DB_PATH=/data/leinerfrog.db \
		leinerfrog
