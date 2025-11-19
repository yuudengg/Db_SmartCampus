import { ChevronLeft } from "lucide-react";
import { useState } from "react";
import { NavLink } from "react-router";
import { StopCheckingModal } from "../../components/StopCheckingModal";

export const ManageUserPage = () => {
  const [open, setOpen] = useState(false);
  const [isStop, setIsStop] = useState(false);

  const handleClick = () => {
    setOpen(true);
  };

  const handleConfirm = () => {
    setIsStop((prev) => !prev);
    setOpen(false);
  };

  const handleCancel = () => {
    setOpen(false);
  };

  return (
    <div className="flex flex-col h-full gap-6">
      <NavLink to="/admin">
        <ChevronLeft className="m-2" size={30} />
      </NavLink>
      <div className="flex flex-col items-center justify-center">
        <h1 className="flex text-5xl font-bold text-blue-900 my-8">
          사용자 관리
        </h1>
        <div className="flex flex-col w-200 h-100 border-2 border-blue-900 gap-2 p-6 overflow-auto">
          <div className="grid grid-cols-5 text-2xl text-blue-900 font-bold gap-4 pb-2">
            <div className="flex justify-center">유저 아이디</div>
            <div className="flex justify-center">이름</div>
            <div className="flex justify-center">역할</div>
            <div className="flex justify-center">노쇼 횟수</div>
            <div></div>
          </div>
          <div className="grid grid-cols-5 justify-center text-xl text-blue-900 gap-4 border-b py-2">
            <div className="flex justify-center">1</div>
            <div className="flex justify-center">2</div>
            <div className="flex justify-center">3</div>
            <div className="flex justify-center">4</div>
            <button
              className={`border ${
                isStop ? "text-red-500" : "text-blue-900 px-4"
              }`}
              onClick={handleClick}
            >
              {isStop ? "사용 중지 해제" : "사용 중지"}
            </button>
          </div>
        </div>
        <p className="text-blue-900 text-lg mt-2">
          * 노쇼로 인한 사용 중지의 경우 3일 정지
        </p>
      </div>
      <StopCheckingModal
        open={open}
        isStop={isStop}
        onConfirm={handleConfirm}
        onCancel={handleCancel}
      />
    </div>
  );
};
