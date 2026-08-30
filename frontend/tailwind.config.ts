// import type { Config } from "tailwindcss";

// const config: Config = {
//   content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
//   theme: {
//     extend: {
//       colors: {
//         ink: "#14161A",
//         subtle: "#5B6472",
//         surface: "#F6F7F9",
//         card: "#FFFFFF",
//         border: "#E3E6EB",
//         primary: {
//           DEFAULT: "#3B4B8C",
//           dark: "#2F3C70",
//           light: "#EEF0F9",
//         },
//         // Central place for status-badge colors (section 44 of the spec:
//         // asset statuses must be visually distinguishable). Reused as the
//         // app's one signature device — a left-edge "state stripe" on every
//         // row/card that carries a lifecycle status, since state tracking
//         // is the entire point of this app.
//         status: {
//           available: "#16a34a",
//           assigned: "#2563eb",
//           reserved: "#7c3aed",
//           repair: "#d97706",
//           damaged: "#dc2626",
//           lost: "#7f1d1d",
//           retired: "#6b7280",
//           disposed: "#3f3f46",
//         },
//       },
//       fontFamily: {
//         sans: ["var(--font-plex-sans)", "system-ui", "sans-serif"],
//         mono: ["var(--font-plex-mono)", "ui-monospace", "monospace"],
//       },
//     },
//   },
//   plugins: [],
// };

// export default config;


import type { Config } from "tailwindcss";

const config: Config = {
  // Dark mode is toggled by adding/removing `.dark` on <html> (see
  // ThemeContext.tsx) rather than following the OS preference live —
  // gives users an explicit, persisted choice via the Settings page.
  darkMode: "class",
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        // These all resolve to CSS custom properties (see globals.css)
        // that flip value under `.dark` — every component already using
        // text-ink / bg-card / bg-surface / border-border / bg-primary
        // gets dark mode for free, with zero changes to those files.
        ink: "rgb(var(--color-ink) / <alpha-value>)",
        subtle: "rgb(var(--color-subtle) / <alpha-value>)",
        surface: "rgb(var(--color-surface) / <alpha-value>)",
        card: "rgb(var(--color-card) / <alpha-value>)",
        border: "rgb(var(--color-border) / <alpha-value>)",
        primary: {
          DEFAULT: "rgb(var(--color-primary) / <alpha-value>)",
          dark: "rgb(var(--color-primary-dark) / <alpha-value>)",
          light: "rgb(var(--color-primary-light) / <alpha-value>)",
        },
        // Logarhythm's gold accent (seen on the hero icons) — used
        // sparingly for highlights. Not theme-dependent; reads fine on
        // both light and dark surfaces.
        accent: "#F0A93B",
        // Status-badge colors (section 44 of the spec). Left as fixed
        // saturated colors — they're already used at low opacity (/10)
        // for backgrounds, which reads fine against both light and dark
        // cards without needing separate dark variants.
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