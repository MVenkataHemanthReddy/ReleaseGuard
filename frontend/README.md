# ReleaseGuard Frontend

A polished, Apple-quality React frontend for ReleaseGuard built with modern best practices.

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **TanStack Query** for server state management
- **React Router v7** for routing
- **Motion (Framer Motion)** for animations
- **Tailwind CSS** for styling
- **Zod** for validation
- **React Hook Form** for forms
- **Lucide React** for icons

## Design Principles

Following the "Apple way" design principles:

1. **Purposeful Design** - Every element serves a clear function
2. **Refined Typography** - Inter font with careful hierarchy
3. **Meaningful Motion** - Animations guide attention and communicate state
4. **Accessibility First** - WCAG 2.2 AA compliant
5. **Design System** - Consistent tokens for colors, spacing, typography
6. **Polish in Details** - Concentric radius, optical alignment, proper shadows

## Project Structure

```
frontend/
├── public/
│   └── favicon.svg
├── src/
│   ├── components/
│   │   ├── layout/          # Layout components (Sidebar, Header, Layout)
│   │   └── ui/              # Reusable UI components
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       ├── Badge.tsx
│   │       ├── Input.tsx
│   │       ├── Table.tsx
│   │       ├── Modal.tsx
│   │       ├── LoadingScreen.tsx
│   │       ├── Toast.tsx
│   │       ├── Dropdown.tsx
│   │       ├── Tabs.tsx
│   │       └── Icons.tsx
│   ├── context/
│   │   └── ProjectContext.tsx
│   ├── hooks/
│   │   └── use-reduced-motion.ts
│   ├── lib/
│   │   ├── api.ts           # API client with TypeScript types
│   │   ├── utils.ts         # Utility functions
│   │   ├── motion-tokens.ts # Motion design tokens
│   │   └── query-client.ts  # TanStack Query configuration
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Releases.tsx
│   │   ├── ReleaseDetail.tsx
│   │   ├── ApiChecks.tsx
│   │   ├── Issues.tsx
│   │   └── Settings.tsx
│   ├── App.tsx
│   ├── main.tsx
│   ├── index.css
│   └── vite-env.d.ts
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── tailwind.config.ts
├── postcss.config.js
└── eslint.config.js
```

## Features

### Pages

1. **Dashboard** - Overview of release health, stats, recent releases, issues, API health, test trends
2. **Releases** - List, create, and manage releases with search, filters, pagination
3. **Release Detail** - Detailed view with overview, test results, and release comparison
4. **API Checks** - Configure and monitor API health checks
5. **Issues** - Track and manage error groups with event details
6. **Settings** - Project configuration, environments, API tokens, integrations

### UI Components

- **Button** - Primary, secondary, ghost, danger variants with loading states
- **Card** - Consistent card layouts with header, content, footer
- **Badge** - Status indicators with variants and dot indicators
- **Input/Textarea/Select** - Form inputs with validation, error states
- **Table** - Sortable, paginated tables with loading/empty states
- **Modal** - Accessible modals with animations
- **Toast** - Notification system with success/error/warning/info
- **Dropdown** - Action menus and select dropdowns
- **Tabs** - Animated tab navigation with indicator

### Design System

- **Colors** - Brand, surface, semantic (success/warning/error) palettes
- **Typography** - Display, heading, body, caption scales with Inter font
- **Spacing** - 4px base unit scale (0-24)
- **Border Radius** - Consistent radius scale (xs-3xl)
- **Shadows** - Layered shadow system (xs-xl)
- **Motion** - Duration, easing, spring presets with reduced motion support

## Getting Started

### Prerequisites

- Node.js 18+
- npm or pnpm
- ReleaseGuard backend running on `http://127.0.0.1:8000`

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

This starts the Vite dev server on `http://localhost:3000` with API proxy to `http://127.0.0.1:8000/api`.

### Build

```bash
npm run build
```

Outputs to `dist/` directory.

### Lint

```bash
npm run lint
```

### Preview Production Build

```bash
npm run preview
```

## API Integration

The frontend connects to the ReleaseGuard Django REST API at `/api/v1/`. The API client in `src/lib/api.ts` provides typed methods for all endpoints.

### Authentication

Currently uses project-scoped tokens passed via headers. The `ProjectContext` manages the current project selection.

## Motion & Animation

Built on `motion/react` with design tokens from `src/lib/motion-tokens.ts`:

- **Durations**: instant (80ms), fast (180ms), normal (350ms), slow (600ms), crawl (1000ms)
- **Easings**: smooth, sharp, bounce, linear
- **Springs**: snappy, gentle, bouncy, instant, release
- **Reduced Motion**: Respects `prefers-reduced-motion` media query
- **Low-end Devices**: Automatically reduces non-essential animations

## Accessibility

- Semantic HTML elements
- ARIA labels and roles
- Focus visible states
- Keyboard navigation
- Color contrast (WCAG AA)
- Reduced motion support
- Screen reader announcements

## Code Quality

- **TypeScript Strict Mode** - No `any`, explicit types for public APIs
- **ESLint** - TypeScript-aware rules with react-hooks
- **React Patterns** - Derived state, proper hooks usage, composition over inheritance
- **Performance** - Memoization only when proven necessary, virtualized lists ready

## Customization

### Theme Colors

Edit `tailwind.config.ts` to customize the color palette:

```ts
colors: {
  brand: { /* your brand colors */ },
  surface: { /* your surface colors */ },
  semantic: { /* success, warning, error */ },
}
```

### Motion Tokens

Edit `src/lib/motion-tokens.ts` to adjust animation feel:

```ts
export const motionTokens = {
  duration: { /* your durations */ },
  easing: { /* your easings */ },
  // ...
}
```

## Deployment

The frontend can be deployed as static files to any hosting service:

```bash
npm run build
# Deploy dist/ folder
```

Configure your web server to:
1. Serve static files from `dist/`
2. Proxy `/api/*` to your ReleaseGuard backend
3. Fallback to `index.html` for SPA routing

## License

Part of ReleaseGuard project.