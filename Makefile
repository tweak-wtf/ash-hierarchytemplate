build:
	@echo "🐍 Creating addon to upload onto server"
	python3 create_package.py

	@echo "🛠️\tBuilding docker images for processor"
	poetry dockerize -vvV --ansi --path=./services/processor
