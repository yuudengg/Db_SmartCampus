interface ConfirmModalProps {
  open: boolean;
  isStop: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function StopCheckingModal({
  open,
  isStop,
  onConfirm,
  onCancel,
}: ConfirmModalProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-black/40 opacity-60"
        onClick={onCancel}
      />
      <div className="relative bg-white p-8 rounded-xl shadow-xl z-10 w-100">
        <h2 className="text-xl font-bold text-blue-900 mb-4">
          {isStop
            ? "정말 사용 중지를 해제하시겠습니까?"
            : "정말 사용을 중지하시겠습니까?"}
        </h2>
        <div className="flex justify-end gap-4">
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-blue-900 text-white rounded-lg"
          >
            네
          </button>
          <button onClick={onCancel} className="px-4 py-2 border rounded-lg">
            아니요
          </button>
        </div>
      </div>
    </div>
  );
}
