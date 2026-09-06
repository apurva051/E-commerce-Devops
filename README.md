# ShopSphere Microservices Application Code

This package intentionally contains only the application source code. Dockerfiles, Docker Compose, Jenkins, and Kubernetes configuration will be created separately during the DevOps practical.

## Included components

- `frontend` - HTML, CSS, JavaScript and Nginx configuration
- `api-gateway` - FastAPI gateway
- `product-service` - FastAPI service using MongoDB
- `order-service` - FastAPI service using PostgreSQL
- `user-service` - FastAPI service using Redis

## Push to GitHub

```bash
git init
git add .
git commit -m "Add initial microservices application code"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/production-microservices-devops-platform.git
git push -u origin main
```

## Next practical

We will write and understand each Dockerfile individually, build the images, connect the services manually, and finally create Docker Compose.
