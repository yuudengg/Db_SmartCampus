import { UserRound } from "lucide-react";
import { NavLink } from "react-router";

export const UserPage = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-6">
      <UserRound size={80} color="oklch(37.9% 0.146 265.522)" />
      <p className="text-xl text-blue-900">ooo님</p>
      <div className="flex justify-between w-80">
        <NavLink
          to="/user/edit"
          className="border-2 border-blue-900 rounded-full px-6 py-2 text-blue-900 font-bold"
        >
          정보 수정
        </NavLink>
        <NavLink
          to="/"
          className="border-2 border-red-500 rounded-full px-6 py-2 text-red-500 font-bold"
        >
          로그아웃
        </NavLink>
      </div>
      <NavLink
        to="/user/reservation"
        className="flex items-center justify-center border w-130 h-40 text-6xl text-blue-900 font-bold"
      >
        장소 예약
      </NavLink>
      <NavLink
        to="/user/reservation/check"
        className="flex items-center justify-center border w-130 h-40 text-6xl text-blue-900 font-bold"
      >
        예약 조회
      </NavLink>
    </div>
  );
};
