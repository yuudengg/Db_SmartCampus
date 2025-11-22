import React, { useState } from "react";

interface EditSpaceModalProps {
  open: boolean; // 모달 열림 여부
  onConfirm: (start: string, end: string) => void; // 확인 시 부모로 날짜 전달
  onCancel: () => void; // 취소 버튼 클릭 시
  initialStart?: string; // 이미 선택된 시작일
  initialEnd?: string; // 이미 선택된 종료일
}

export const EditSpaceModal: React.FC<EditSpaceModalProps> = ({
  open,
  onConfirm,
  onCancel,
  initialStart = "",
  initialEnd = "",
}) => {
  const [start, setStart] = useState(initialStart);
  const [end, setEnd] = useState(initialEnd);

  if (!open) return null;

  const handleConfirm = () => {
    if (!start || !end) {
      alert("시작일과 종료일을 모두 선택해주세요!");
      return;
    }
    if (end < start) {
      alert("종료일은 시작일보다 이후여야 합니다!");
      return;
    }
    onConfirm(start, end);
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl p-8 flex flex-col items-center w-96">
        <h2 className="text-2xl text-blue-900 font-bold mb-6">
          사용 중지 기간 설정
        </h2>

        <div className="flex flex-col gap-4 mb-6">
          <label className="flex flex-col text-blue-900">
            시작일
            <input
              type="date"
              value={start}
              onChange={(e) => setStart(e.target.value)}
              className="border p-2 mt-1"
            />
          </label>
          <label className="flex flex-col text-blue-900">
            종료일
            <input
              type="date"
              value={end}
              min={start}
              onChange={(e) => setEnd(e.target.value)}
              className="border p-2 mt-1"
            />
          </label>
        </div>

        <div className="flex gap-4">
          <button
            onClick={handleConfirm}
            className="bg-blue-900 text-white px-6 py-2 rounded-lg"
          >
            확인
          </button>
          <button
            onClick={onCancel}
            className="border border-blue-900 text-blue-900 px-6 py-2 rounded-lg"
          >
            취소
          </button>
        </div>
      </div>
    </div>
  );
};
