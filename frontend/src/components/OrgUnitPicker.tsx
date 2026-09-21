"use client";

import { useQuery } from "@tanstack/react-query";
import { listOrgUnits } from "@/services/org_units";
import { useMemo } from "react";
import type { OrgUnit } from "@/types";

interface OrgUnitPickerProps {
  value: number | undefined;
  onChange: (value: number | undefined) => void;
  required?: boolean;
  className?: string;
}

export default function OrgUnitPicker({ value, onChange, required, className }: OrgUnitPickerProps) {
  const { data: orgUnits = [], isLoading } = useQuery({
    queryKey: ["orgUnits"],
    queryFn: listOrgUnits,
  });

  const options = useMemo(() => {
    if (!orgUnits.length) return [];

    const map = new Map<number, OrgUnit>();
    orgUnits.forEach((u) => map.set(u.id, u));

    // Build paths
    const getPath = (id: number): string => {
      const u = map.get(id);
      if (!u) return "";
      if (u.parent_id) {
        return getPath(u.parent_id) + " > " + u.name;
      }
      return u.name;
    };

    const list = orgUnits.map((u) => ({
      id: u.id,
      path: getPath(u.id),
    }));

    list.sort((a, b) => a.path.localeCompare(b.path));
    return list;
  }, [orgUnits]);

  if (isLoading) {
    return (
      <select disabled className={className || "input"}>
        <option>Loading…</option>
      </select>
    );
  }

  return (
    <select
      required={required}
      value={value ?? ""}
      onChange={(e) => {
        const val = e.target.value;
        onChange(val ? Number(val) : undefined);
      }}
      className={className || "input"}
    >
      <option value="">— Select unit —</option>
      {options.map((opt) => (
        <option key={opt.id} value={opt.id}>
          {opt.path}
        </option>
      ))}
    </select>
  );
}
