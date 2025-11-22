import { ChevronLeft } from "lucide-react";
import { NavLink } from "react-router";
import type { ReservationManage } from "../../types/reservation";
import { useEffect, useState } from "react";
import { CancelSpaceModal } from "../../components/Modals/CancelReservModal";
import { EditReservModal } from "../../components/Modals/EditResevModal";
import { axiosInstance } from "../../apis/axiosInstance";

export const ManageReservPage = () => {
  const [reservations, setReservations] = useState<ReservationManage[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [modalType, setModalType] = useState<"edit" | "cancel" | null>(null);

  // ✅ 예약 목록 불러오기
  useEffect(() => {
    const fetchReservations = async () => {
      try {
        const res = await axiosInstance.get("/admin/reservations");
        if (res.data.success) {
          setReservations(res.data.data);
        } else {
          alert("예약 데이터를 불러오지 못했습니다.");
        }
      } catch (err) {
        console.error("🚨 예약 조회 오류:", err);
        alert("서버 연결 오류가 발생했습니다.");
      }
    };

    fetchReservations();
  }, []);

  // ✅ 모달 제어
  const openEditModal = (id: number) => {
    setSelectedId(id);
    setModalType("edit");
  };

  const openCancelModal = (id: number) => {
    setSelectedId(id);
    setModalType("cancel");
  };

  const handleCloseModal = () => {
    setModalType(null);
    setSelectedId(null);
  };

  // ✅ 예약 수정 저장
  const handleEditSave = async (updated: ReservationManage) => {
    try {
      const res = await axiosInstance.put("/admin/reservations/edit", updated);
      if (res.data.success) {
        setReservations((prev) =>
          prev.map((item) => (item.id === updated.id ? res.data.data : item))
        );
        alert("예약 정보가 수정되었습니다!");
      } else {
        alert(res.data.message || "예약 수정 실패");
      }
    } catch (err) {
      console.error("🚨 예약 수정 오류:", err);
      alert("서버 오류가 발생했습니다.");
    }
    handleCloseModal();
  };

  // ✅ 예약 취소
  const handleCancelConfirm = async () => {
    if (!selectedId) return;
    try {
      const res = await axiosInstance.put("/admin/reservations/cancel", {
        id: selectedId,
      });
      if (res.data.success) {
        alert("예약이 취소되었습니다!");
        // 상태만 "예약취소"로 바꿔서 표시
        setReservations((prev) =>
          prev.map((item) =>
            item.id === selectedId ? { ...item, status: "예약취소" } : item
          )
        );
      } else {
        alert(res.data.message || "예약 취소 실패");
      }
    } catch (err) {
      console.error("🚨 예약 취소 오류:", err);
      alert("서버 연결 오류가 발생했습니다.");
    }
    handleCloseModal();
  };

  return (
    <div className="flex flex-col h-full">
      <NavLink to="/admin">
        <ChevronLeft className="m-2" size={30} />
      </NavLink>

      <div className="flex flex-col items-center justify-center">
        <h1 className="flex text-5xl font-bold text-blue-900 mt-4 mb-12">
          예약 관리
        </h1>

        <div className="flex flex-col w-300">
          <div className="grid grid-cols-9 gap-4 mb-4 text-2xl text-blue-900 font-bold">
            <p className="flex items-center justify-center">예약번호</p>
            <p className="flex items-center justify-center">이름</p>
            <p className="flex items-center justify-center">공간이름</p>
            <p className="flex items-center justify-center">예약날짜</p>
            <p className="flex items-center justify-center">예약시간</p>
            <p className="flex items-center justify-center">사용목적</p>
            <p className="flex items-center justify-center">상태</p>
          </div>

          {reservations.map((item) => (
            <div
              key={item.id}
              className="grid grid-cols-9 justify-center text-lg text-blue-900 gap-4 border-b py-2"
            >
              <div className="flex justify-center">{item.id}</div>
              <div className="flex justify-center">{item.userName}</div>
              <div className="flex justify-center">{item.spaceName}</div>
              <div className="flex justify-center">{item.date}</div>
              <div className="flex justify-center">{item.time}</div>
              <div className="flex justify-center">{item.purpose}</div>
              <div
                className={`flex justify-center ${
                  item.status === "예약취소"
                    ? "text-red-500"
                    : item.status === "사용완료"
                    ? "text-gray-500"
                    : "text-blue-900"
                }`}
              >
                {item.status}
              </div>

              {/* 수정 버튼 */}
              <button
                className={`border w-20 ml-4 ${
                  item.status !== "예약됨"
                    ? "border-gray-400 text-gray-400"
                    : "border-blue-900 text-blue-900"
                }`}
                onClick={() => openEditModal(item.id)}
                disabled={item.status !== "예약됨"}
              >
                수정
              </button>

              {/* 취소 버튼 */}
              <button
                className={`border w-20 ml-4 ${
                  item.status !== "예약됨"
                    ? "border-gray-400 text-gray-400"
                    : "border-red-500 text-red-500"
                }`}
                onClick={() => openCancelModal(item.id)}
                disabled={item.status !== "예약됨"}
              >
                취소
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* ✅ 모달 영역 */}
      {modalType === "cancel" && (
        <CancelSpaceModal
          onConfirm={handleCancelConfirm}
          onCancel={handleCloseModal}
        />
      )}

      {modalType === "edit" && selectedId && (
        <EditReservModal
          reservation={reservations.find((r) => r.id === selectedId)!}
          onSave={handleEditSave}
          onCancel={handleCloseModal}
        />
      )}
    </div>
  );
};
