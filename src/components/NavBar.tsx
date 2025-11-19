import { NavLink } from "react-router";

const NavBar = () => {
  return (
    <>
      <nav className="bg-white dark:bg-gray-900 fixed w-full z-20">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center gap-4">
            <NavLink
              to="/"
              className="text-gray-900 dark:text-white text-xl font-bold"
            >
              스마트 캠퍼스
            </NavLink>
          </div>
        </div>
      </nav>
    </>
  );
};

export default NavBar;
