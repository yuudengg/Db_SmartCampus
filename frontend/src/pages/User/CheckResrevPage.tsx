import { ChevronLeft } from "lucide-react";
import { useState, useEffect } from "react";
import { NavLink } from "react-router";
import { DeleteReservModal } from "../../components/Modals/DeleteReservModal";
import { CheckReservModal } from "../../components/Modals/CheckReservModal";
import { axiosInstance } from "../../apis/axiosInstance";
import { useUser } from "../../hooks/useUser";
import type { Reservation } from "../../types/reservation";

export const CheckResrevPage = () => {
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [selectedReservation, setSelectedReservation] =
    useState<Reservation | null>(null);
  const [modalType, setModalType] = useState<"cancel" | "check" | null>(null);
  const user = useUser();

  // ✅ 예약 데이터 불러오기
  useEffect(() => {
    const fetchReservations = async () => {
      if (!user) return;
      try {
        const res = await axiosInstance.get(`/reservations/${user.user_id}`);
        if (res.data.success) {
          setReservations(res.data.data);
        } else {
          alert("예약 내역을 불러올 수 없습니다.");
        }
      } catch (err) {
        console.error(err);
        alert("서버 연결 오류가 발생했습니다!");
      }
    };
    fetchReservations();
  }, [user]);

  const handleCancelReservation = async (id: number) => {
    if (!window.confirm("정말 이 예약을 취소하시겠습니까?")) return;
    try {
      const res = await axiosInstance.put(`/reservation/cancel/${id}`);
      if (res.data.success) {
        alert("예약이 취소되었습니다!");
        // 화면에서도 즉시 제거
        setReservations((prev) => prev.filter((r) => r.id !== id));
      } else {
        alert(res.data.message || "예약 취소에 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      alert("서버 오류가 발생했습니다.");
    }
  };

  const closeModal = () => {
    setModalType(null);
    setSelectedReservation(null);
  };

  return (
    <div className="flex flex-col h-full gap-6">
      <NavLink to="/user">
        <ChevronLeft className="m-2" size={30} />
      </NavLink>

      <div className="flex flex-col items-center justify-center">
        <h1 className="flex text-5xl font-bold text-blue-900 my-8">
          예약 조회
        </h1>

        <div className="flex flex-col w-200 h-100 border-2 border-blue-900 gap-2 p-6 overflow-auto">
          <div className="grid grid-cols-[1fr_2fr_2fr_2fr_2fr_2fr] text-2xl text-blue-900 font-bold gap-4 pb-2">
            <div className="flex justify-center">번호</div>
            <div className="flex justify-center">공간이름</div>
            <div className="flex justify-center">예약날짜</div>
            <div className="flex justify-center">예약시간</div>
          </div>

          {reservations.filter(
            (r) => r.status !== "예약취소" && r.status !== "취소됨"
          ).length === 0 ? (
            <p className="text-center text-gray-600 py-8">
              예약 내역이 없습니다.
            </p>
          ) : (
            reservations.map((item) => (
              <div
                key={item.id}
                className="grid grid-cols-[1fr_2fr_2fr_2fr_2fr_2fr] justify-center text-xl text-blue-900 gap-4 border-b py-2"
              >
                <div className="flex justify-center">{item.id}</div>
                <div className="flex justify-center">{item.spaceName}</div>
                <div className="flex justify-center">{item.date}</div>
                <div className="flex justify-center w-32">{item.time}</div>

                <div className="flex col-span-2 justify-center gap-2">
                  <button
                    className="text-lg border px-2"
                    onClick={() => handleCancelReservation(item.id)}
                  >
                    예약 취소
                  </button>

                  <button
                    className="text-lg border px-2"
                    onClick={() => {
                      setSelectedReservation(item);
                      setModalType("check");
                    }}
                  >
                    예약 확인
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* 취소 모달 */}
      {modalType === "cancel" && (
        <DeleteReservModal
          reservation={selectedReservation}
          onConfirm={closeModal}
          onCancel={closeModal}
        />
      )}

      {/* 확인 모달 */}
      {modalType === "check" && (
        <CheckReservModal
          reservation={selectedReservation}
          onClose={closeModal}
        />
      )}
    </div>
  );
};
