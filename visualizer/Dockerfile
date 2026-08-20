# The Node version the visualizer is built with in CI
FROM node:24-alpine AS build

WORKDIR /app

# package-lock.json is not tracked in the repository, so the image installs the same way CI does
COPY package.json ./
RUN npm install

COPY . .

# Vite inlines VITE_* values into the bundle at build time, so they are build arguments rather than
# runtime environment variables — changing any of them means rebuilding the image
ARG VITE_SERVER_URL=http://localhost:8080
ARG VITE_API_KEY=visualizer
ARG VITE_CONNECT_TO_SERVER=true
ENV VITE_SERVER_URL=${VITE_SERVER_URL}
ENV VITE_API_KEY=${VITE_API_KEY}
ENV VITE_CONNECT_TO_SERVER=${VITE_CONNECT_TO_SERVER}

RUN npm run build

# The built bundle is a static site, so it is served by nginx rather than a Node process
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
