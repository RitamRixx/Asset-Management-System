import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#14161A",
        subtle: "#5B6472",
        surface: "#F6F7F9",
        card: "#FFFFFF",
        border: "#E3E6EB",
        primary: {
          DEFAULT: "#3B4B8C",
          dark: "#2F3C70",
          light: "#EEF0F9",
        },
        // Central place for status-badge colors (section 44 of the spec:
        // asset statuses must be visually distinguishable). Reused as the
        // app's one signature device — a left-edge "state stripe" on every
        // row/card that carries a lifecycle status, since state tracking
        // is the entire point of this app.
        status: {
          available: "#16a34a",
          assigned: "#2563eb",
          reserved: "#7c3aed",
          repair: "#d97706",
          damaged: "#dc2626",
          lost: "#7f1d1d",
          retired: "#6b7280",
          disposed: "#3f3f46",
        },
      },
      fontFamily: {
        sans: ["var(--font-plex-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-plex-mono)", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
