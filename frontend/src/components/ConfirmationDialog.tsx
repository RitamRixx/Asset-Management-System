"use client";

import Modal from "@/components/Modal";

export default function ConfirmationDialog({
  open,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = "Confirm",
  danger = false,
  loading = false,
}: {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmLabel?: string;
  danger?: boolean;
  loading?: boolean;
}) {
  return (
    <Modal open={open} onClose={onClose} title={title}>
      <p className="text-sm text-subtle">{message}</p>
      <div className="mt-6 flex justify-end gap-2">
        <button
          onClick={onClose}
          className="rounded-md border border-border px-4 py-2 text-sm font-medium text-ink hover:bg-surface"
        >
          Cancel
        </button>
        <button
          onClick={onConfirm}
          disabled={loading}
          className={`rounded-md px-4 py-2 text-sm font-medium text-white disabled:opacity-50 ${
            danger ? "bg-status-damaged hover:bg-status-damaged/90" : "bg-primary hover:bg-primary-dark"
          }`}
        >
          {loading ? "Working…" : confirmLabel}
        </button>
      </div>
    </Modal>
  );
}
