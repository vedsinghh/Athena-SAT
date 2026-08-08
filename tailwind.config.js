/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        athena: {
          blue: '#2F62D6',
          navy: '#12346F',
          gold: '#E8A93E',
          purple: '#7A4AC8',
          green: '#18A05E',
          soft: '#F6F9FF'
        }
      },
      boxShadow: {
        card: '0 16px 45px rgba(31, 61, 125, .08), 0 2px 10px rgba(31, 61, 125, .04)'
      }
    }
  },
  plugins: []
}