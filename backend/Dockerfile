# docker-compose.yml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    container_name: ai_news_mongo
    restart: always
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_DATABASE: ai_news_aggregator
    volumes:
      - mongodb_data:/data/db

  backend:
    build: ./backend
    container_name: ai_news_backend
    restart: always
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongodb:27017/ai_news_aggregator
      - HUGGINGFACE_TOKEN=${HUGGINGFACE_TOKEN}
    depends_on:
      - mongodb
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    container_name: ai_news_frontend
    restart: always
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend

volumes:
  mongodb_data: