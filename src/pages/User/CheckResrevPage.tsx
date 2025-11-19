import { ChevronLeft } from "lucide-react";
import { useState } from "react";
import { NavLink } from "react-router";
import { DeleteReservModal } from "../../components/Modals/DeleteReservModal";
import { CheckReservModal } from "../../components/Modals/CheckReservModal";
import type { Reservation } from "../../types/Reservation";

export const CheckResrevPage = () => {
  const reservations: Reservation[] = [
    {
      id: 1,
      spaceName: "A101",
      date: "2025-02-20",
      time: "09:00 - 10:00",
      userId: 1,
    },
    {
      id: 2,
      spaceName: "B202",
      date: "2025-02-21",
      time: "14:00 - 15:00",
      userId: 2,
    },
  ];

  const [selectedReservation, setSelectedReservation] =
    useState<Reservation | null>(null);
  const [modalType, setModalType] = useState<"cancel" | "check" | null>(null);

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

          {reservations.map((item) => (
            <div
              key={item.id}
              className="grid grid-cols-[1fr_2fr_2fr_2fr_2fr_2fr] justify-center text-xl text-blue-900 gap-4 border-b py-2"
            >
              <div className="flex justify-center">{item.id}</div>
              <div className="flex justify-center">{item.spaceName}</div>
              <div className="flex justify-center">{item.date}</div>
              <div className="flex justify-center">{item.time}</div>

              <div className="flex col-span-2 justify-center gap-2">
                <button
                  className="text-lg border px-2"
                  onClick={() => {
                    setSelectedReservation(item);
                    setModalType("cancel");
                  }}
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
          ))}
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
