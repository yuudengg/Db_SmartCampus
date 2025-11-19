import { ChevronLeft, UserRound } from "lucide-react";
import { NavLink } from "react-router";

export const EditUserPage = () => {
  return (
    <div className="flex flex-col h-full gap-6">
      <NavLink to="/user">
        <ChevronLeft className="m-2" size={30} />
      </NavLink>
      <div className="flex flex-col items-center justify-center">
        <div className="flex flex-col items-center mb-4">
          <UserRound size={80} color="oklch(37.9% 0.146 265.522)" />
          <p className="text-xl text-blue-900">ooo님</p>
        </div>
        <div className="flex flex-col items-center justify-center w-180 h-120 border border-blue-900 gap-4">
          <h1 className="text-5xl font-bold text-blue-900 mb-6">
            사용자 정보 수정
          </h1>
          <div className="flex gap-2 items-center">
            <p className="text-lg mr-10">이름</p>
            <input
              className="flex border w-60 h-13 p-4"
              placeholder="이름을 입력하세요."
            />
          </div>
          <div className="flex gap-2 items-center">
            <p className="text-lg mr-6">아이디</p>
            <input
              className="flex border w-60 h-13 p-4"
              placeholder="아이디를 입력하세요."
            />
          </div>
          <div className="flex gap-2 items-center">
            <p className="text-lg mr-2">비밀번호</p>
            <input
              className="flex border w-60 h-13 p-4"
              placeholder="비밀번호를 입력하세요."
            />
          </div>
          <button className="items-center border border-blue-900 text-blue-900 text-xl font-bold px-8 py-2 mt-4">
            수정
          </button>
        </div>
      </div>
    </div>
  );
};
