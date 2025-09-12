local-db:
	@echo "Starting local database...";
	@if docker ps -a --format '{{.Names}}' | grep -q "^test-postgres$$"; then \
		echo "Container 'test-postgres' already exists."; \
		read -p "Do you want to replace it? (y/n): " confirm; \
		if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
			echo "Removing existing container..."; \
			docker rm -f test-postgres; \
		else \
			echo "Operation cancelled."; \
			exit 1; \
		fi \
	fi
	@echo "Starting local PostgreSQL container..."
	docker run -d \
		--name test-postgres \
		-e POSTGRES_USER=postgres \
		-e POSTGRES_PASSWORD=password123 \
		-e POSTGRES_DB=testdb \
		-p 5434:5432 \
		postgres:16
	@$(MAKE) check-postgres
	@echo "Running migrations and seeding database..."
	alembic upgrade head

check-postgres:
	@echo "Waiting for PostgreSQL to be ready..."
	@until docker exec test-postgres pg_isready -U postgres; do \
		echo "PostgreSQL is unavailable - sleeping"; \
		sleep 2; \
	done
	@echo "PostgreSQL is ready!"