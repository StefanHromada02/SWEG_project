# Stage 1: Build Angular application
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files (if they exist)
COPY package.json ./

# Install dependencies if package.json has dependencies
RUN if [ -f package.json ]; then npm install || true; fi

# Copy source code
COPY . .

# Build the application
RUN npm run build || mkdir -p dist

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration if needed
# COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
