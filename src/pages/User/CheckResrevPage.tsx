import { ChevronLeft } from "lucide-react";
import { useState } from "react";
import { NavLink } from "react-router";
import { DeleteReservModal } from "../../components/DeleteReservModal";

export const CheckResrevPage = () => {
  const [open, setOpen] = useState(false);

  const handleClick = () => {
    setOpen(true);
  };

  const handleConfirm = () => {
    setOpen(false);
  };

  const handleCancel = () => {
    setOpen(false);
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
          <div className="grid grid-cols-6 text-2xl text-blue-900 font-bold gap-4 pb-2">
            <div className="flex justify-center">번호</div>
            <div className="flex justify-center">공간이름</div>
            <div className="flex justify-center">예약날짜</div>
            <div className="flex justify-center">예약시간</div>
          </div>
          <div className="grid grid-cols-6 justify-center text-xl text-blue-900 gap-4 border-b py-2">
            <div className="flex justify-center">1</div>
            <div className="flex justify-center">2</div>
            <div className="flex justify-center">3</div>
            <div className="flex justify-center">4</div>
            <div className="flex col-span-2 justify-center gap-2">
              <button className="text-lg border px-2" onClick={handleClick}>
                예약 취소
              </button>
              <button className="text-lg border px-2">예약 확인</button>
            </div>
          </div>
        </div>
      </div>
      <DeleteReservModal
        open={open}
        onConfirm={handleConfirm}
        onCancel={handleCancel}
      />
    </div>
  );
};
