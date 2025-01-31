# services/search_ui/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Install serve to run the build
RUN npm install -g serve

# Run the app
CMD ["serve", "-s", "build", "-l", "3000"]