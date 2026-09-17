import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          950: "#070b16",
          900: "#0b1220",
          800: "#111827",
          700: "#1e293b",
        },
        accent: {
          DEFAULT: "#6366f1",
          soft: "#818cf8",
        },
      },
      boxShadow: {
        card: "0 10px 30px -18px rgba(15, 23, 42, 0.35)",
      },
    },
  },
  plugins: [],
};

export default config;
