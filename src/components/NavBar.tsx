import { useNavigate } from "react-router";

const NavBar = () => {
  const navigate = useNavigate();
  const role = localStorage.getItem("role");

  const handleLogoClick = () => {
    if (!role) {
      navigate("/");
    } else if (role === "관리자") {
      navigate("/admin");
    } else {
      navigate("/user");
    }
  };
  return (
    <>
      <nav className="bg-white dark:bg-gray-900 fixed w-full z-20">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center gap-4">
            <button
              onClick={handleLogoClick}
              className="text-gray-900 dark:text-white text-xl font-bold"
            >
              스마트 캠퍼스
            </button>
          </div>
        </div>
      </nav>
    </>
  );
};

export default NavBar;
