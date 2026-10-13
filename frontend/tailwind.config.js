/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "#06b6d4", // Cyan-500
          foreground: "#ffffff",
        },
        secondary: {
          DEFAULT: "#a855f7", // Purple-500
          foreground: "#ffffff",
        },
        accent: {
          DEFAULT: "#f43f5e", // Rose-500
          foreground: "#ffffff",
        },
        muted: {
          DEFAULT: "#64748b", // Slate-400
          foreground: "#94a3b8",
        },
        card: {
          DEFAULT: "rgba(30, 41, 59, 0.7)", // slate-800 with opacity
          foreground: "#f8fafc",
        },
      },
      backgroundImage: {
        'glass-gradient': 'linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05))',
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'neon': '0 0 15px rgba(6, 182, 212, 0.4)',
      }
    },
  },
  plugins: [],
}
