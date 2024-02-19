/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./**/*.{html, js, css, py}"],  
  theme: {
    extend: {
      colors: {
        'primary': '#16171b',
        'secondary': 'linear-gradient(to right, #00C9A7, #00B4D8, #0096C7, #0057D9)',
      }
    },
  },
  corePlugins: {
  },
  plugins: [],
}

