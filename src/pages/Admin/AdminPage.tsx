import { UserRoundCog } from "lucide-react";
import { NavLink } from "react-router";

export const AdminPage = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-6">
      <UserRoundCog size={80} color="oklch(37.9% 0.146 265.522)" />
      <p className="text-xl text-blue-900">ooo님</p>
      <div className="flex justify-between w-80">
        <NavLink
          to="/admin/edit"
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
      <div className="flex flex-col justify-center w-200 px-4 gap-4">
        <p className="bg-linear-to-r from-indigo-800 to-white text-3xl text-white p-2 w-60">
          관리
        </p>
        <div className="flex flex-row justify-between">
          <NavLink
            to="/admin/manage/user"
            className="text-4xl text-blue-900 font-bold border border-blue-900 p-4"
          >
            사용자 관리
          </NavLink>
          <NavLink
            to="/admin/manage/space"
            className="text-4xl text-blue-900 font-bold border border-blue-900 p-4"
          >
            장소 관리
          </NavLink>
          <NavLink
            to="/admin/manage/reservation"
            className="text-4xl text-blue-900 font-bold border border-blue-900 p-4"
          >
            예약 관리
          </NavLink>
        </div>
        <p className="bg-linear-to-r from-indigo-800 to-white text-3xl text-white p-2 w-60 mt-4">
          통계
        </p>
        <div className="flex flex-row justify-between">
          <NavLink
            to="/admin/static"
            className="text-4xl text-blue-900 font-bold border border-blue-900 p-4"
          >
            통계 대시보드
          </NavLink>
        </div>
      </div>
    </div>
  );
};
