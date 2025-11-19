import { UserRound } from "lucide-react";
import { NavLink } from "react-router";

export const UserLoginPage = () => {
  return (
    <div className="flex flex-col">
      <div className="flex flex-col items-center justify-center w-fit">
        <UserRound
          className="flex mx-4 mt-4"
          size={80}
          color="oklch(37.9% 0.146 265.522)"
        />
        <p className="font-bold text-blue-900">사용자</p>
      </div>
      <div className="flex flex-col items-center justify-center">
        <h1 className="flex text-5xl font-bold text-blue-900 my-8">
          장소 예약 시스템
        </h1>
        <div className="flex flex-col items-center justify-center border w-150 h-100 gap-4">
          <input
            className="flex border w-120 h-13 p-4"
            placeholder="아이디를 입력하세요."
          />
          <input
            className="flex border w-120 h-13 p-4"
            placeholder="비밀번호를 입력하세요."
          />
          <button className="text-3xl font-bold text-blue-900">로그인</button>
          <div className="flex flex-row mt-8 text-xl">
            <p>계정이 없다면?</p>
            <NavLink to="/signup" className="text-blue-900 font-bold mx-2">
              회원가입
            </NavLink>
          </div>
        </div>
      </div>
    </div>
  );
};
