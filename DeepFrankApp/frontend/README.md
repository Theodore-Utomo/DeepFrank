# DeepFrank Frontend

Next.js + TypeScript frontend for DeepFrank Cat Emotional Analysis.

## Features

- Image upload and preview
- Real-time analysis of cat images
- Displays detections, body part analysis, and emotional state

## Getting Started

### Option 1: Run with Docker (Recommended for Development)

```bash
# From the repository root
docker-compose up frontend

# Or to build and start both backend and frontend
docker-compose up --build
```

The frontend will be available at http://localhost:3000

### Option 2: Run Locally

#### Install Dependencies

```bash
npm install
# or
yarn install
# or
pnpm install
```

#### Run Development Server

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Environment Variables

Create a `.env.local` file in the frontend directory (optional):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

This should point to your backend API URL. Defaults to `http://localhost:8000` if not set.

## Docker Development

The Docker setup includes:
- Hot reload - code changes automatically restart the server
- Volume mounting - your code is mounted for live editing
- Automatic dependency installation
- Development mode enabled

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx          # Main page with upload and analysis
│   ├── layout.tsx        # Root layout
│   └── globals.css       # Global styles (Tailwind CSS)
├── lib/
│   └── api.ts            # API client functions
├── types/
│   └── api.ts            # TypeScript type definitions
├── Dockerfile            # Development Docker configuration
└── package.json
```

## Usage

1. Start the backend API (if not already running):
   ```bash
   docker-compose up api
   ```

2. Start the frontend:
   ```bash
   docker-compose up frontend
   ```

3. Open http://localhost:3000 in your browser

4. Click "Select Cat Image" and choose an image file

5. Preview will show the selected image

6. Click "Analyze Image" to send to backend

7. Results will display below with:
   - Detected body parts (eyes, mouth, tail)
   - Analysis of each body part
   - Overall emotional state

## Troubleshooting

- **Port already in use**: Make sure port 3000 is not being used by another application
- **API connection errors**: Ensure the backend API is running on port 8000
- **Hot reload not working**: Check that volumes are properly mounted in docker-compose.yml
