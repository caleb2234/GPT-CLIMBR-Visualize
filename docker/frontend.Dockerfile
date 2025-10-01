  # Build stage
  FROM node:18-alpine AS builder

  WORKDIR /app

  # Copy package files
  COPY frontend/package*.json ./
  RUN npm ci

  # Copy source code and build
  COPY frontend/ .
  RUN npm run build

  # Production stage
  FROM nginx:alpine

  # Copy built files to nginx
  COPY --from=builder /app/build /usr/share/nginx/html

  # Copy nginx config
  COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

  EXPOSE 80

  CMD ["nginx", "-g", "daemon off;"]