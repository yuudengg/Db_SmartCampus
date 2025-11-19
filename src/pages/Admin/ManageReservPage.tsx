import { ChevronLeft } from "lucide-react";
import { NavLink } from "react-router";
import type { ReservationManage } from "../../types/Reservation";
import { useState } from "react";
import { CancelSpaceModal } from "../../components/Modals/CancelReservModal";
import { EditReservModal } from "../../components/Modals/EditResevModal";

export const ManageReservPage = () => {
  const [reservations, setReservations] = useState<ReservationManage[]>([
    {
      id: 1,
      userName: "김철수",
      spaceName: "A101",
      date: "2025-03-01",
      time: "10:00 ~ 12:00",
      purpose: "스터디",
      status: "예약됨",
    },
    {
      id: 2,
      userName: "이영희",
      spaceName: "B202",
      date: "2025-03-03",
      time: "14:00 ~ 16:00",
      purpose: "회의",
      status: "사용완료",
    },
    {
      id: 3,
      userName: "홍길동",
      spaceName: "B202",
      date: "2025-03-04",
      time: "15:00 ~ 16:00",
      purpose: "공부",
      status: "예약취소",
    },
  ]);

  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [modalType, setModalType] = useState<"edit" | "cancel" | null>(null);

  const openEditModal = (id: number) => {
    setSelectedId(id);
    setModalType("edit");
  };

  const openCancelModal = (id: number) => {
    setSelectedId(id);
    setModalType("cancel");
  };

  const handleCancelConfirm = () => {
    setReservations((prev) => prev.filter((item) => item.id !== selectedId));
    setModalType(null);
    setSelectedId(null);
  };

  const handleCloseModal = () => {
    setModalType(null);
    setSelectedId(null);
  };

  const handleEditSave = (updated: ReservationManage) => {
    setReservations((prev) =>
      prev.map((item) => (item.id === updated.id ? updated : item))
    );
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
            <p className="flex items-center justify-center">사용상태</p>
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
              <div className="flex justify-center">{item.status}</div>
              <button
                className={`border w-20 ml-4 ${
                  item.status != "예약됨"
                    ? "border-gray-500 text-gray-500"
                    : "border-blue-900"
                }`}
                onClick={() => openEditModal(item.id)}
                disabled={item.status != "예약됨"}
              >
                수정
              </button>
              <button
                className={`border w-20 ml-4 ${
                  item.status != "예약됨"
                    ? "border-gray-500 text-gray-500"
                    : "border-red-500 text-red-500"
                }`}
                onClick={() => openCancelModal(item.id)}
                disabled={item.status != "예약됨"}
              >
                취소
              </button>
            </div>
          ))}
        </div>
      </div>
      {modalType === "cancel" && (
        <CancelSpaceModal
          onConfirm={handleCancelConfirm}
          onCancel={handleCloseModal}
        />
      )}
      {modalType === "edit" && (
        <EditReservModal
          reservation={reservations.find((r) => r.id === selectedId)!}
          onSave={handleEditSave}
          onCancel={handleCloseModal}
        />
      )}
    </div>
  );
};
