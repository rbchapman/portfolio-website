/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 'custom-dark': '#181818',
        'custom-grey': '#232323',
        'custom-text': 'rgba(235, 235, 235, 0.64)',
        'text-primary': 'rgba(245, 245, 245, 0.9)'
      },
      fontFamily: {
        sans: ['Montserrat', 'sans-serif'],
        serif: ['Didot', 'serif']
      },
    },
  },
  plugins: [],
}

