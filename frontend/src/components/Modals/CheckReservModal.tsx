import { axiosInstance } from "../../apis/axiosInstance";

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
  if (!reservation) return null;

  // 사용 완료 처리 함수
  const handleComplete = async () => {
    try {
      const res = await axiosInstance.put(
        `/reservation/complete/${reservation.id}`
      );

      if (res.data.success) {
        alert("사용 완료로 처리되었습니다!");
        onClose(); // 모달 닫기
      } else {
        alert(res.data.message);
      }
    } catch (error) {
      console.error(error);
      alert("사용 완료 처리 중 오류가 발생했습니다.");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-black/40 opacity-60"
        onClick={onClose}
      />
      <div className="relative bg-white p-8 rounded-xl shadow-xl z-10 w-100">
        <h2 className="text-xl font-bold text-blue-900 mb-6">예약 상세 정보</h2>

        <div className="text-blue-900 text-lg mb-8">
          <p className="mb-2">예약 번호: {reservation.id}</p>
          <p className="mb-2">공간 이름: {reservation.spaceName}</p>
          <p className="mb-2">예약 날짜: {reservation.date}</p>
          <p className="mb-2">예약 시간: {reservation.time}</p>
        </div>

        <div className="flex justify-end gap-3">
          {/* 사용 완료 버튼 */}
          <button
            onClick={handleComplete}
            className="px-4 py-2 bg-green-600 text-white rounded-lg shadow hover:bg-green-700"
          >
            사용 완료
          </button>

          {/* 닫기 버튼 */}
          <button
            onClick={onClose}
            className="px-4 py-2 border rounded-lg hover:bg-gray-100"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  );
}
