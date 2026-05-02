/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#FF6636',
          50:  '#FFF4F0',
          100: '#FFE8DF',
          200: '#FFD0BF',
          300: '#FFB09A',
          400: '#FF8F73',
          500: '#FF6636',
          600: '#E5481A',
          700: '#BF3410',
          800: '#99270C',
          900: '#731C08',
        },
        secondary: {
          DEFAULT: '#564FFD',
          50:  '#EEECFF',
          100: '#DDD9FF',
          200: '#BBB3FF',
          300: '#998DFF',
          400: '#7767FF',
          500: '#564FFD',
          600: '#3B33E0',
          700: '#2820B8',
          800: '#190F91',
          900: '#0D076B',
        },
        neutral: {
          DEFAULT: '#1D2026',
          50:  '#F5F7FA',
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
        success: '#23BD33',
        warning: '#FD8E1F',
        error:   '#E34444',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        card:       '0 1px 4px rgba(0,0,0,0.06)',
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
