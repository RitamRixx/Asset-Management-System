"use client";

import { useEffect, useRef, useState } from "react";
import { listNotifications, markNotificationRead } from "@/services/reference";
import type { Notification } from "@/types";

export default function NotificationBell() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  async function refresh() {
    try {
      setNotifications(await listNotifications());
    } catch {
      // Notifications are a convenience, not critical path — fail quietly.
    }
  }

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 30_000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  async function handleMarkRead(id: number) {
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
    try {
      await markNotificationRead(id);
    } catch {
      refresh();
    }
  }

  return (
    <div ref={containerRef} className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        aria-label={`Notifications${unreadCount > 0 ? `, ${unreadCount} unread` : ""}`}
        className="relative flex h-9 w-9 items-center justify-center rounded-md border border-border bg-card text-subtle hover:bg-surface hover:text-ink"
      >
        <BellIcon />
        {unreadCount > 0 && (
          <span className="absolute -right-1 -top-1 flex h-4 min-w-[1rem] items-center justify-center rounded-full bg-status-damaged px-1 font-mono text-[10px] font-semibold text-white">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 z-40 mt-2 w-80 rounded-lg border border-border bg-card shadow-lg">
          <div className="border-b border-border px-4 py-3">
            <h3 className="text-sm font-semibold text-ink">Notifications</h3>
          </div>
          {notifications.length === 0 ? (
            <p className="p-4 text-sm text-subtle">Nothing new.</p>
          ) : (
            <ul className="max-h-96 divide-y divide-border overflow-y-auto">
              {notifications.map((n) => (
                <li
                  key={n.id}
                  className={`px-4 py-3 text-sm ${n.is_read ? "" : "bg-primary-light/40"}`}
                >
                  <div className="mb-0.5 flex items-start justify-between gap-2">
                    <span className="font-medium text-ink">{n.title}</span>
                    {!n.is_read && (
                      <button
                        onClick={() => handleMarkRead(n.id)}
                        className="shrink-0 text-xs font-medium text-primary hover:text-primary-dark"
                      >
                        Mark read
                      </button>
                    )}
                  </div>
                  <p className="text-subtle">{n.message}</p>
                  <p className="mt-1 font-mono text-[11px] text-subtle">
                    {new Date(n.created_at).toLocaleString()}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

function BellIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" />
      <path d="M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
  );
}
