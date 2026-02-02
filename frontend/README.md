# Hospital Stress Early Warning System - Frontend

Next.js 15 frontend for the Hospital Stress Early Warning System.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

3. Set up Google OAuth:
- Create a project in Google Cloud Console
- Enable Google OAuth API
- Create OAuth 2.0 credentials
- Add authorized redirect URIs
- Copy client ID and secret to .env.local

## Running Locally

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Building for Production

```bash
npm run build
npm start
```

## Testing

```bash
npm test
```

## Project Structure

```
src/
├── app/              # Next.js 15 App Router pages
├── components/       # React components
│   └── ui/          # Shadcn/UI components
├── lib/             # Utility functions
└── types/           # TypeScript type definitions
```

## Features

- Server-side rendering with Next.js 15
- Google OAuth authentication with NextAuth
- Shadcn/UI components with Tailwind CSS
- Dark mode support
- Real-time dashboard updates
- Interactive what-if simulator
- Natural language chat interface
