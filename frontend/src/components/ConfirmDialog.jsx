import { X } from "lucide-react";

export default function ConfirmDialog({
  open,
  title,
  description,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  destructive = false,
  onConfirm,
  onCancel,
}) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4 py-8">
      <div
        className="absolute inset-0 bg-black/60"
        onClick={onCancel}
        aria-hidden
      />

      <div className="relative w-full max-w-md text-white pointer-events-auto">
        <div className="bg-[#121212] border border-[#3D3D3D] rounded-2xl p-8 shadow-xl">
          <button
            onClick={onCancel}
            className="absolute right-6 top-6 text-sm text-gray-300 hover:text-white"
            aria-label="Close"
          >
            <X size={20} color="white" />
          </button>

          <h2 className="text-2xl font-extrabold leading-tight mb-3">
            {title}
          </h2>

          {description && (
            <p className="text-gray-300 text-sm mb-8">{description}</p>
          )}

          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={onCancel}
              className="px-5 py-2.5 rounded-xl bg-transparent border border-gray-700 hover:border-gray-500 text-white text-sm font-semibold transition-colors"
            >
              {cancelLabel}
            </button>
            <button
              type="button"
              onClick={onConfirm}
              className={`px-5 py-2.5 rounded-xl text-white text-sm font-semibold transition-colors ${
                destructive
                  ? "bg-red-600 hover:bg-red-700"
                  : "bg-white/10 hover:bg-white/20 border border-gray-700"
              }`}
            >
              {confirmLabel}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
