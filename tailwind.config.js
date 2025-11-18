/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        // Minimalist light mode palette from color-palette.md
        primary: {
          50: '#f9f8fc',
          100: '#f3f1f9',
          200: '#e8e4f4',
          300: '#d9cfed',
          400: '#b5a8d1',
          500: '#78597A', // Dusty Lavender
          600: '#6b4f6d',
          700: '#5e4560',
          800: '#514553',
          900: '#443a46',
          950: '#2d2530',
        },
        accent: {
          50: '#f0f7f5',
          100: '#e1f0ed',
          200: '#c3e1db',
          300: '#a5d1c9',
          400: '#6bafa1',
          500: '#2E8166', // Jungle Teal
          600: '#2a7059',
          700: '#265f4d',
          800: '#224e41',
          900: '#1e3d35',
          950: '#192f2a',
        },
        light: {
          bg: '#FCFCFC', // White
          surface: '#F8F7FA', // Very light lavender
          elevated: '#F3F1F9', // Slightly darker light lavender
          hover: '#EDE9F3', // Light hover state
          border: '#DDD6F0', // Light border
          text: '#2D2D2D', // Dark text for contrast
          muted: '#6B6B7A', // Muted text
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'glow': '0 0 20px rgba(120, 89, 122, 0.15)',
        'glow-accent': '0 0 20px rgba(46, 129, 102, 0.15)',
        'soft': '0 2px 8px rgba(120, 89, 122, 0.08)',
        'soft-lg': '0 4px 16px rgba(120, 89, 122, 0.12)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
      gridTemplateColumns: {
        '7': 'repeat(7, minmax(0, 1fr))',
      },
    },
  },
  plugins: [],
}
