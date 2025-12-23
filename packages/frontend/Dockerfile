# Stage 1: Dependencies and Build
FROM node:20.11.0-alpine AS builder

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@8.15.0

# Copy workspace config for pnpm
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
COPY packages/frontend/package.json ./packages/frontend/

# Install dependencies
RUN pnpm install --frozen-lockfile --filter frontend

# Copy frontend application code
COPY packages/frontend ./packages/frontend

# Build the application
WORKDIR /app/packages/frontend
ENV TURBO_BUILD=0
RUN npx next build

# Stage 2: Production
FROM node:20.11.0-alpine AS runner

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@8.15.0

# Copy workspace config
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
COPY packages/frontend/package.json ./packages/frontend/

# Install production dependencies only
RUN pnpm install --frozen-lockfile --prod --filter frontend

# Copy built application from builder
COPY --from=builder /app/packages/frontend/.next ./packages/frontend/.next
COPY --from=builder /app/packages/frontend/public ./packages/frontend/public
COPY --from=builder /app/packages/frontend/next.config.mjs ./packages/frontend/

WORKDIR /app/packages/frontend

# Expose port
EXPOSE 3000

# Set NODE_ENV
ENV NODE_ENV=production

# Run application
CMD ["pnpm", "start"]