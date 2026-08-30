// "use client";

// import Link from "next/link";
// import { usePathname } from "next/navigation";
// import { useAuth } from "@/contexts/AuthContext";
// import type { Role } from "@/types";

// interface NavItem {
//   href: string;
//   label: string;
//   roles: Role[];
// }

// const NAV_ITEMS: NavItem[] = [
//   { href: "/dashboard", label: "Dashboard", roles: ["ADMIN", "HR", "IT_SUPPORT", "EMPLOYEE"] },
//   { href: "/employees", label: "Employees", roles: ["ADMIN", "HR", "IT_SUPPORT"] },
//   { href: "/assets", label: "Assets", roles: ["ADMIN", "HR", "IT_SUPPORT"] },
//   { href: "/assignments/new", label: "New assignment", roles: ["ADMIN", "IT_SUPPORT"] },
//   { href: "/software", label: "Software", roles: ["ADMIN", "IT_SUPPORT"] },
//   { href: "/repairs", label: "Repairs", roles: ["ADMIN", "HR", "IT_SUPPORT"] },
//   { href: "/reports", label: "Reports", roles: ["ADMIN", "HR", "IT_SUPPORT"] },
//   { href: "/audit-logs", label: "Audit log", roles: ["ADMIN"] },
// ];

// export default function Sidebar() {
//   const pathname = usePathname();
//   const { user, logout } = useAuth();

//   const items = NAV_ITEMS.filter((item) => user && item.roles.includes(user.role));

//   return (
//     <aside className="flex h-screen w-60 flex-col border-r border-border bg-card">
//       <div className="flex items-center gap-2 border-b border-border px-5 py-4">
//         <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary font-mono text-xs font-bold text-white">
//           AM
//         </div>
//         <span className="font-semibold tracking-tight text-ink">AMS Platform</span>
//       </div>

//       <nav className="flex-1 space-y-0.5 px-3 py-4">
//         {items.map((item) => {
//           const active = pathname === item.href || pathname.startsWith(item.href + "/");
//           return (
//             <Link
//               key={item.href}
//               href={item.href}
//               className={`block rounded-md px-3 py-2 text-sm font-medium transition-colors ${
//                 active
//                   ? "bg-primary-light text-primary-dark"
//                   : "text-subtle hover:bg-surface hover:text-ink"
//               }`}
//             >
//               {item.label}
//             </Link>
//           );
//         })}
//       </nav>

//       <div className="border-t border-border px-3 py-3">
//         <div className="mb-2 px-2">
//           <p className="truncate text-sm font-medium text-ink">{user?.email}</p>
//           <p className="text-xs text-subtle">{user?.role.replace("_", " ")}</p>
//         </div>
//         <button
//           onClick={logout}
//           className="w-full rounded-md px-3 py-2 text-left text-sm font-medium text-subtle hover:bg-surface hover:text-ink"
//         >
//           Sign out
//         </button>
//       </div>
//     </aside>
//   );
// }


"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useBrand } from "@/contexts/BrandContext";
import type { Role } from "@/types";

interface NavItem {
  href: string;
  label: string;
  roles: Role[];
}

const NAV_ITEMS: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", roles: ["ADMIN", "HR", "IT_SUPPORT", "EMPLOYEE"] },
  { href: "/employees", label: "Employees", roles: ["ADMIN", "HR", "IT_SUPPORT"] },
  { href: "/assets", label: "Assets", roles: ["ADMIN", "HR", "IT_SUPPORT"] },
  { href: "/assignments/new", label: "New assignment", roles: ["ADMIN", "IT_SUPPORT"] },
  { href: "/software", label: "Software", roles: ["ADMIN", "IT_SUPPORT"] },
  { href: "/repairs", label: "Repairs", roles: ["ADMIN", "HR", "IT_SUPPORT"] },
  { href: "/reports", label: "Reports", roles: ["ADMIN", "HR", "IT_SUPPORT"] },
  { href: "/audit-logs", label: "Audit log", roles: ["ADMIN"] },
  { href: "/settings", label: "Settings", roles: ["ADMIN", "HR", "IT_SUPPORT", "EMPLOYEE"] },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const { brand } = useBrand();

  const items = NAV_ITEMS.filter((item) => user && item.roles.includes(user.role));

  return (
    <aside className="flex h-screen w-60 flex-col border-r border-border bg-card">
      <div className="flex items-center gap-2 border-b border-border px-5 py-4">
        {brand.logoUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={brand.logoUrl} alt={brand.companyName} className="h-7 w-auto" />
        ) : (
          <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary font-mono text-xs font-bold text-white">
            {brand.companyName.slice(0, 2).toUpperCase()}
          </div>
        )}
        <div className="min-w-0 leading-tight">
          <span className="block truncate font-semibold tracking-tight text-ink">
            {brand.companyName}
          </span>
          <span className="block truncate text-[10px] uppercase tracking-wide text-subtle">
            {brand.tagline}
          </span>
        </div>
      </div>

      <nav className="flex-1 space-y-0.5 px-3 py-4">
        {items.map((item) => {
          const active = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`block rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                active
                  ? "bg-primary-light text-primary-dark"
                  : "text-subtle hover:bg-surface hover:text-ink"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-border px-3 py-3">
        <div className="mb-2 px-2">
          <p className="truncate text-sm font-medium text-ink">{user?.email}</p>
          <p className="text-xs text-subtle">{user?.role.replace("_", " ")}</p>
        </div>
        <button
          onClick={logout}
          className="w-full rounded-md px-3 py-2 text-left text-sm font-medium text-subtle hover:bg-surface hover:text-ink"
        >
          Sign out
        </button>
      </div>
    </aside>
  );
}
