FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package.json ./
COPY frontend/next.config.js ./
COPY frontend/tailwind.config.js ./
COPY frontend/postcss.config.js ./
RUN npm install
COPY frontend .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=build /app .
EXPOSE 3000
CMD ["npm", "start"]
