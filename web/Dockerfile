FROM node:20-bookworm-slim

WORKDIR /app

COPY web/package*.json ./
RUN npm ci --no-audit --no-fund

COPY web ./

EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0", "--port", "3000"]
