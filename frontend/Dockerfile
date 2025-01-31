# Build stage
FROM node:20-slim as builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM nginx:stable-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

# Create a non-root user
RUN adduser -D -H -u 1001 -s /sbin/nologin www-data

# Set proper permissions
RUN chown -R www-data:www-data /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html && \
    chown -R www-data:www-data /var/cache/nginx && \
    chown -R www-data:www-data /var/log/nginx && \
    chown -R www-data:www-data /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R www-data:www-data /var/run/nginx.pid

USER www-data

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
