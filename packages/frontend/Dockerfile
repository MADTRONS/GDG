# Stage 1: Dependencies and Build
FROM node:20.11.0-alpine AS builder

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@8.15.0

# Copy workspace configuration
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# Copy frontend package files
COPY packages/frontend/package.json ./packages/frontend/

# Install all dependencies
RUN pnpm install --frozen-lockfile

# Copy frontend application code
COPY packages/frontend ./packages/frontend

# Build the application
WORKDIR /app/packages/frontend
RUN pnpm build

# Stage 2: Production
FROM node:20.11.0-alpine AS runner

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@8.15.0

# Copy workspace configuration
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# Copy frontend package.json
COPY packages/frontend/package.json ./packages/frontend/

# Install production dependencies only
RUN pnpm install --frozen-lockfile --prod

# Copy built application from builder
COPY --from=builder /app/packages/frontend/.next ./packages/frontend/.next
COPY --from=builder /app/packages/frontend/public ./packages/frontend/public
COPY --from=builder /app/packages/frontend/next.config.mjs ./packages/frontend/

# Set working directory to frontend
WORKDIR /app/packages/frontend

# Expose port
EXPOSE 3000

# Set NODE_ENV
ENV NODE_ENV=production

# Run application
CMD ["pnpm", "start"]