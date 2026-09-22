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

# Optional cube setting overrides, left empty so every cube size keeps its default
ARG VITE_ANIMATION_SPEED=
ARG VITE_MOVE_DELAY=
ARG VITE_DRAW_BLACK_FACES=
ARG VITE_SHOW_SUBTITLES=
ENV VITE_ANIMATION_SPEED=${VITE_ANIMATION_SPEED}
ENV VITE_MOVE_DELAY=${VITE_MOVE_DELAY}
ENV VITE_DRAW_BLACK_FACES=${VITE_DRAW_BLACK_FACES}
ENV VITE_SHOW_SUBTITLES=${VITE_SHOW_SUBTITLES}

RUN npm run build

# The built bundle is a static site, so it is served by nginx rather than a Node process
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
