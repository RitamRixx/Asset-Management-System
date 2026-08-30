// "use client";

// import { useEffect } from "react";
// import { useRouter } from "next/navigation";
// import { useAuth } from "@/contexts/AuthContext";
// import Sidebar from "@/components/Sidebar";
// import NotificationBell from "@/components/NotificationBell";

// export default function AppLayout({ children }: { children: React.ReactNode }) {
//   const { user, loading } = useAuth();
//   const router = useRouter();

//   useEffect(() => {
//     if (!loading && !user) router.replace("/login");
//   }, [loading, user, router]);

//   if (loading) {
//     return (
//       <div className="flex h-screen items-center justify-center text-sm text-subtle">
//         Loading…
//       </div>
//     );
//   }

//   if (!user) return null;

//   return (
//     <div className="flex">
//       <Sidebar />
//       <div className="flex min-h-screen flex-1 flex-col">
//         <header className="flex items-center justify-end border-b border-border bg-card px-8 py-3">
//           <NotificationBell />
//         </header>
//         <main className="flex-1 overflow-y-auto bg-surface p-8">{children}</main>
//       </div>
//     </div>
//   );
// }


"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import Sidebar from "@/components/Sidebar";
import NotificationBell from "@/components/NotificationBell";
import ThemeToggle from "@/components/ThemeToggle";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center text-sm text-subtle">
        Loading…
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="flex">
      <Sidebar />
      <div className="flex min-h-screen flex-1 flex-col">
        <header className="flex items-center justify-end gap-2 border-b border-border bg-card px-8 py-3">
          <ThemeToggle />
          <NotificationBell />
        </header>
        <main className="flex-1 overflow-y-auto bg-surface p-8">{children}</main>
      </div>
    </div>
  );
}
