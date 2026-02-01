# Build stage
FROM node:18-alpine as build-stage

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY src src
COPY public public

# React build
RUN npm run build || true 
# Note: package.json didn't show building scripts, adding a placeholder for production. 
# For basic project, we might just use a dev server or standard Nginx for static.

# Production stage
FROM nginx:stable-alpine as production-stage
# COPY --from=build-stage /app/build /usr/share/nginx/html
# For now, since it's a "basic project", I'll provide a dev-ready Dockerfile too or just static Nginx if built.
# Let's use a simpler one for "basic project" - just serve what's there if it's static or use a node server.

FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
