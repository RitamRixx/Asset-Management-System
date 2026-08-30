"use client";

import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";
import { useBrand } from "@/contexts/BrandContext";

export default function SettingsPage() {
  const { user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const { brand, updateBrand, resetBrand } = useBrand();

  const [companyName, setCompanyName] = useState(brand.companyName);
  const [tagline, setTagline] = useState(brand.tagline);
  const [logoUrl, setLogoUrl] = useState(brand.logoUrl ?? "");
  const [saved, setSaved] = useState(false);

  const [emailNotifs, setEmailNotifs] = useState(
    typeof window !== "undefined" ? localStorage.getItem("ams_pref_email_notifs") !== "false" : true
  );

  function handleSaveBranding(e: React.FormEvent) {
    e.preventDefault();
    updateBrand({
      companyName: companyName.trim() || "AMS Platform",
      tagline: tagline.trim(),
      logoUrl: logoUrl.trim() || null,
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  function handleResetBranding() {
    resetBrand();
    setCompanyName("Logarhythm");
    setTagline("We make it work for you");
    setLogoUrl("");
  }

  function toggleEmailPref() {
    const next = !emailNotifs;
    setEmailNotifs(next);
    localStorage.setItem("ams_pref_email_notifs", String(next));
  }

  return (
    <div className="max-w-3xl space-y-8">
      <div>
        <h1 className="text-xl font-semibold text-ink">Settings</h1>
        <p className="text-sm text-subtle">Personalize how the AMS Platform looks and behaves for you.</p>
      </div>

      <section className="rounded-lg border border-border bg-card p-6">
        <h2 className="mb-1 text-sm font-semibold text-ink">Appearance</h2>
        <p className="mb-4 text-xs text-subtle">
          Switch between light and dark mode. This applies across every page, not just this one.
        </p>
        <div className="flex items-center justify-between rounded-md border border-border px-4 py-3">
          <div>
            <p className="text-sm font-medium text-ink">Theme</p>
            <p className="text-xs text-subtle">Currently {theme === "dark" ? "Dark" : "Light"} mode</p>
          </div>
          <button
            onClick={toggleTheme}
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary-dark"
          >
            Switch to {theme === "dark" ? "Light" : "Dark"}
          </button>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-card p-6">
        <h2 className="mb-1 text-sm font-semibold text-ink">Organization branding</h2>
        <p className="mb-4 text-xs text-subtle">
          Shown in the sidebar and browser tab. This is stored on this device only — making it a
          true shared, company-wide setting needs a backend field and endpoint, which doesn't
          exist yet (see note in BrandContext.tsx).
        </p>
        <form onSubmit={handleSaveBranding} className="space-y-4">
          <Field label="Company name">
            <input value={companyName} onChange={(e) => setCompanyName(e.target.value)} className="input" />
          </Field>
          <Field label="Tagline">
            <input value={tagline} onChange={(e) => setTagline(e.target.value)} className="input" />
          </Field>
          <Field label="Logo URL">
            <input
              value={logoUrl}
              onChange={(e) => setLogoUrl(e.target.value)}
              className="input"
              placeholder="/logo.png or https://…/logo.png (leave blank to use initials)"
            />
          </Field>
          <div className="flex items-center gap-3 pt-2">
            <button
              type="submit"
              className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary-dark"
            >
              Save
            </button>
            <button
              type="button"
              onClick={handleResetBranding}
              className="rounded-md border border-border px-4 py-2 text-sm font-medium text-ink hover:bg-surface"
            >
              Reset to default
            </button>
            {saved && <span className="text-xs text-status-available">Saved</span>}
          </div>
        </form>
      </section>

      <section className="rounded-lg border border-border bg-card p-6">
        <h2 className="mb-1 text-sm font-semibold text-ink">Notifications</h2>
        <p className="mb-4 text-xs text-subtle">
          In-app notifications are always on. Email delivery also depends on the server's
          EMAIL_ENABLED configuration — this toggle only records your personal preference on this
          device; it doesn't call any API yet.
        </p>
        <div className="flex items-center justify-between rounded-md border border-border px-4 py-3">
          <p className="text-sm font-medium text-ink">Email me about updates</p>
          <button
            onClick={toggleEmailPref}
            aria-pressed={emailNotifs}
            className={`h-6 w-11 rounded-full transition-colors ${emailNotifs ? "bg-primary" : "bg-border"}`}
          >
            <span
              className={`block h-5 w-5 translate-y-0.5 rounded-full bg-white transition-transform ${
                emailNotifs ? "translate-x-5" : "translate-x-0.5"
              }`}
            />
          </button>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-card p-6">
        <h2 className="mb-1 text-sm font-semibold text-ink">Account</h2>
        <p className="mb-4 text-xs text-subtle">
          Your login details. Password changes and profile edits aren't wired up on the backend
          yet — ask an Admin if you need those changed.
        </p>
        <dl className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <dt className="text-xs uppercase tracking-wide text-subtle">Email</dt>
            <dd className="mt-0.5 text-ink">{user?.email}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wide text-subtle">Role</dt>
            <dd className="mt-0.5 text-ink">{user?.role.replace("_", " ")}</dd>
          </div>
        </dl>
      </section>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-medium text-ink">{label}</span>
      {children}
    </label>
  );
}
