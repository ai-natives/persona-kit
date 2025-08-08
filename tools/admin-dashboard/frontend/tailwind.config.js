/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'pk-bg': '#0e1011',
        'pk-surface': '#1a1d21',
        'pk-border': '#2d3239',
        'pk-text': '#e1e8ed',
        'pk-muted': '#9ca3af',
        'pk-success': '#10b981',
        'pk-warning': '#f59e0b',
        'pk-error': '#ef4444',
        'pk-info': '#3b82f6',
        'pk-purple': '#8b5cf6',
      },
      fontFamily: {
        mono: ['Monaco', 'Courier New', 'monospace']
      }
    },
  },
  plugins: [],
}