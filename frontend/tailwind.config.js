/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Moodle brand blue — primary actions, links, focus rings
        primary: {
          DEFAULT: '#0066CC',
          50:  '#E5F2FF',
          100: '#CCE5FF',
          200: '#99CBFF',
          300: '#66B0FF',
          400: '#3396FF',
          500: '#0066CC',
          600: '#0052A3',
          700: '#003D7A',
          800: '#002952',
          900: '#001429',
        },
        // Moodle sidebar / navbar navy
        secondary: {
          DEFAULT: '#1B4180',
          50:  '#EEF2FB',
          100: '#D8E2F3',
          200: '#B0C5E7',
          300: '#89A8DB',
          400: '#618BCF',
          500: '#1B4180',
          600: '#163366',
          700: '#10264D',
          800: '#0B1A33',
          900: '#050D1A',
        },
        neutral: {
          DEFAULT: '#1D2026',
          50:  '#F4F6FA',
          100: '#E9EAF0',
          200: '#D6DAE5',
          300: '#8C94A3',
          400: '#6E7485',
          500: '#4E5566',
          600: '#363B47',
          700: '#2D3038',
          800: '#23262F',
          900: '#1D2026',
        },
        success: '#5CB85C',
        warning: '#F0AD4E',
        error:   '#D9534F',
        // Moodle accent orange (used sparingly for highlights)
        accent:  '#F98012',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        card:         '0 1px 4px rgba(0,0,0,0.06)',
        'card-hover': '0 4px 16px rgba(0,0,0,0.10)',
      },
      borderRadius: {
        '2xl': '16px',
        '3xl': '24px',
      },
    },
  },
  plugins: [],
}
