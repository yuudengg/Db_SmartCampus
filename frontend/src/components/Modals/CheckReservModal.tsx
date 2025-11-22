interface CheckReservProps {
  reservation: {
    id: number;
    spaceName: string;
    date: string;
    time: string;
  } | null;
  onClose: () => void;
}

export function CheckReservModal({ reservation, onClose }: CheckReservProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-black/40 opacity-60"
        onClick={onClose}
      />
      <div className="relative bg-white p-8 rounded-xl shadow-xl z-10 w-100">
        <h2 className="text-xl font-bold text-blue-900 mb-6">예약 상세 정보</h2>
        <div className="text-blue-900 text-lg mb-8">
          <p className="mb-2">예약 번호: {reservation?.id}</p>
          <p className="mb-2">공간 이름: {reservation?.spaceName}</p>
          <p className="mb-2">예약 날짜: {reservation?.date}</p>
          <p className="mb-2">예약 시간: {reservation?.time}</p>
        </div>
        <div className="flex justify-end">
          <button onClick={onClose} className="px-4 py-2 border rounded-lg">
            닫기
          </button>
        </div>
      </div>
    </div>
  );
}
