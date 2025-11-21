/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        // Premium Black & Gold palette
        primary: {
          50: '#faf8f5',
          100: '#f5f3f0',
          200: '#efe9e2',
          300: '#e8dfd5',
          400: '#d9cdb5',
          500: '#d4af37', // Gold
          600: '#c9a961',
          700: '#b8964a',
          800: '#9f8239',
          900: '#8b7236',
          950: '#6b5924',
        },
        accent: {
          50: '#faf9f8',
          100: '#f5f3f1',
          200: '#e8e5e1',
          300: '#ddd9d3',
          400: '#c9c2b8',
          500: '#1a1a1a', // Dark Black
          600: '#121212',
          700: '#0a0a0a',
          800: '#050505',
          900: '#000000',
          950: '#000000',
        },
        light: {
          bg: '#faf8f5', // Cream/Off-white
          surface: '#f5f3f0', // Slightly darker cream
          elevated: '#efe9e2', // Light cream
          hover: '#e8dfd5', // Hover cream
          border: '#ddd9d3', // Border color
          text: '#1a1a1a', // Dark black text
          muted: '#8b8b8b', // Muted gray text
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'glow': '0 0 25px rgba(212, 175, 55, 0.2)',
        'glow-accent': '0 0 25px rgba(212, 175, 55, 0.15)',
        'soft': '0 2px 8px rgba(26, 26, 26, 0.08)',
        'soft-lg': '0 4px 16px rgba(26, 26, 26, 0.12)',
        'gold-glow': '0 0 30px rgba(212, 175, 55, 0.3)',
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
