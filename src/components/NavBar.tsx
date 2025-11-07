import { NavLink } from "react-router";

const NavBar = () => {
  return (
    <>
      <nav className="bg-white dark:bg-gray-900 fixed w-full z-20">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center gap-4">
            <img src="/로고_학교.png" className="w-33 h-10" />
            <NavLink
              to="/"
              className="text-gray-900 dark:text-white text-xl font-bold"
            >
              스마트 캠퍼스
            </NavLink>
          </div>
          <div className="flex space-x-6">
            <NavLink
              to="/reservation"
              className="text-gray-900 dark:text-white text-xl font-bold hover:text-blue-500"
            >
              장소 예약
            </NavLink>
            <NavLink
              to="/login"
              className="text-gray-900 dark:text-white text-xl font-bold hover:text-blue-500"
            >
              로그인
            </NavLink>
          </div>
        </div>
      </nav>
    </>
  );
};

export default NavBar;
