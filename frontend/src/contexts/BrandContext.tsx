"use client";

import { createContext, useContext, useEffect, useState } from "react";

export interface BrandSettings {
  companyName: string;
  tagline: string;
  /** null falls back to a generated initials badge instead of an <img>. */
  logoUrl: string | null;
}

const DEFAULT_BRAND: BrandSettings = {
  companyName: "Logarhythm",
  tagline: "We make it work for you",
  logoUrl: null,
};

const STORAGE_KEY = "ams_brand_settings";

interface BrandContextValue {
  brand: BrandSettings;
  updateBrand: (patch: Partial<BrandSettings>) => void;
  resetBrand: () => void;
}

const BrandContext = createContext<BrandContextValue | undefined>(undefined);

export function BrandProvider({ children }: { children: React.ReactNode }) {
  const [brand, setBrand] = useState<BrandSettings>(DEFAULT_BRAND);

  // This is device-local (localStorage), not a shared org-wide setting —
  // there's no backend field for it yet. See the note on the Settings
  // page. Wiring this to a real `/organization` endpoint later is a
  // drop-in replacement for the two functions below.
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) setBrand({ ...DEFAULT_BRAND, ...JSON.parse(stored) });
    } catch {
      // Malformed localStorage — fall back to defaults silently.
    }
  }, []);

  function updateBrand(patch: Partial<BrandSettings>) {
    setBrand((prev) => {
      const next = { ...prev, ...patch };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  }

  function resetBrand() {
    localStorage.removeItem(STORAGE_KEY);
    setBrand(DEFAULT_BRAND);
  }

  return (
    <BrandContext.Provider value={{ brand, updateBrand, resetBrand }}>
      {children}
    </BrandContext.Provider>
  );
}

export function useBrand(): BrandContextValue {
  const ctx = useContext(BrandContext);
  if (!ctx) throw new Error("useBrand must be used within BrandProvider");
  return ctx;
}
