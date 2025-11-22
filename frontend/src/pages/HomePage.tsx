import { NavLink } from "react-router";

export const HomePage = () => {
  return (
    <div className="flex flex-col items-center justify-center">
      <h1 className="flex text-5xl text-blue-900 font-black p-8">
        장소 예약 시스템
      </h1>
      <section className="flex bg-black w-300 h-150">
        <NavLink
          to="/login/user"
          className="flex items-center justify-center text-3xl text-white font-black bg-yellow-500 w-100"
        >
          <p>사용자 로그인</p>
        </NavLink>
        <NavLink
          to="/signup"
          className="flex items-center justify-center text-3xl text-white font-black bg-blue-500 w-100"
        >
          <p>회원가입</p>
        </NavLink>
        <NavLink
          to="/login/admin"
          className="flex items-center justify-center text-3xl text-white font-black bg-green-500 w-100"
        >
          <p>관리자 로그인</p>
        </NavLink>
      </section>
    </div>
  );
};
