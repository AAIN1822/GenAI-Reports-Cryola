# 1️⃣ Build stage: use Node to build the React + TypeScript app
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of your app
COPY . .

# Build the app (this runs: tsc -b && vite build)
RUN npm run build

# 2️⃣ Serve stage: use Nginx to serve the built static files
FROM nginx:alpine

# Copy build output to Nginx html folder
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80 (for browser access)
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]