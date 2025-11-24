FROM nginx:alpine

# Copy nginx configuration files
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Copy SSL certificates (if they exist)
COPY nginx/ssl/ /etc/nginx/ssl/

# Create certbot directory
RUN mkdir -p /var/www/certbot

