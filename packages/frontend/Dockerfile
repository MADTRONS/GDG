# Stage 1: Dependencies and Build
FROM node:20.11.0-alpine AS builder

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@8.15.0

# Copy package files
COPY packages/frontend/package.json ./

# Install dependencies
RUN pnpm install

# Copy frontend application code
COPY packages/frontend ./

# Build the application
RUN pnpm build

# Stage 2: Production
FROM node:20.11.0-alpine AS runner

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@8.15.0

# Copy package.json
COPY packages/frontend/package.json ./

# Install production dependencies only
RUN pnpm install --prod

# Copy built application from builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.mjs ./

# Expose port
EXPOSE 3000

# Set NODE_ENV
ENV NODE_ENV=production

# Run application
CMD ["pnpm", "start"]