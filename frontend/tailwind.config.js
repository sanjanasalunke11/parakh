/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      colors: {
        base: {
          950: "#05060a",
          900: "#0b0d14",
          850: "#0f1220",
          800: "#141826",
          700: "#1c2233",
          600: "#2a3145",
          500: "#3c4560",
        },
        brand: {
          400: "#7c9dff",
          500: "#5b7cfa",
          600: "#4361ee",
          glow: "#8b5cf6",
        },
        verdict: {
          verified: "#2dd4a7",
          false: "#fb6f92",
          misleading: "#f6c453",
          unverified: "#94a3b8",
        },
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(124,157,255,0.15), 0 8px 30px -8px rgba(91,124,250,0.35)",
        card: "0 1px 0 rgba(255,255,255,0.04) inset, 0 20px 40px -20px rgba(0,0,0,0.6)",
      },
      backgroundImage: {
        "grid-glow":
          "radial-gradient(circle at 20% -10%, rgba(91,124,250,0.25), transparent 45%), radial-gradient(circle at 90% 10%, rgba(139,92,246,0.18), transparent 40%)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "fade-in": "fadeIn 0.4s ease-out",
        "rise": "rise 0.5s cubic-bezier(0.16,1,0.3,1)",
      },
      keyframes: {
        fadeIn: { "0%": { opacity: 0 }, "100%": { opacity: 1 } },
        rise: {
          "0%": { opacity: 0, transform: "translateY(12px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};
