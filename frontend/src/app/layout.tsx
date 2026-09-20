// import type { Metadata } from "next";
// import { IBM_Plex_Sans, IBM_Plex_Mono } from "next/font/google";
// import "./globals.css";
// import { AuthProvider } from "@/contexts/AuthContext";

// const plexSans = IBM_Plex_Sans({
//   subsets: ["latin"],
//   weight: ["400", "500", "600", "700"],
//   variable: "--font-plex-sans",
//   display: "swap",
// });

// const plexMono = IBM_Plex_Mono({
//   subsets: ["latin"],
//   weight: ["400", "500", "600"],
//   variable: "--font-plex-mono",
//   display: "swap",
// });

// export const metadata: Metadata = {
//   title: "AMS Platform",
//   description: "Enterprise Asset Management System",
// };

// export default function RootLayout({
//   children,
// }: {
//   children: React.ReactNode;
// }) {
//   return (
//     <html lang="en" className={`${plexSans.variable} ${plexMono.variable}`}>
//       <body className="min-h-screen bg-surface font-sans text-ink antialiased">
//         <AuthProvider>{children}</AuthProvider>
//       </body>
//     </html>
//   );
// }


import type { Metadata } from "next";
import { IBM_Plex_Sans, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { BrandProvider } from "@/contexts/BrandContext";
import QueryProvider from "@/components/QueryProvider";

const plexSans = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-plex-sans",
  display: "swap",
});

const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-plex-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Logarhythm AMS",
  description: "Enterprise Asset Management System",
};

// Runs before React hydrates, so the correct theme class is on <html>
// before first paint — without this there's a flash of light mode for
// anyone who has dark mode saved.
const THEME_INIT_SCRIPT = `
(function () {
  try {
    var stored = localStorage.getItem("ams_theme");
    var theme = stored || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    if (theme === "dark") document.documentElement.classList.add("dark");
  } catch (e) {}
})();
`;

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${plexSans.variable} ${plexMono.variable}`}>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
      </head>
      <body className="min-h-screen bg-surface font-sans text-ink antialiased transition-colors duration-150">
        <ThemeProvider>
          <BrandProvider>
            <QueryProvider>
              <AuthProvider>{children}</AuthProvider>
            </QueryProvider>
          </BrandProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
