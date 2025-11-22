import { UserRound } from "lucide-react";
import { useState } from "react";
import { NavLink, useNavigate } from "react-router";
import { axiosInstance } from "../../apis/axiosInstance";

export const UserLoginPage = () => {
  const [loginId, setLoginId] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async () => {
    if (!loginId || !password) {
      alert("아이디와 비밀번호를 모두 입력하세요!");
      return;
    }
    try {
      const res = await axiosInstance.post("/login/user", {
        login_id: loginId,
        password: password,
      });
      if (res.data.success) {
        alert(`${res.data.name}님 환영합니다!`);
        localStorage.setItem("user", JSON.stringify(res.data));
        localStorage.setItem("role", res.data.role);
        navigate("/user");
      } else {
        alert(res.data.message || "로그인에 실패했습니다.");
      }
    } catch (error) {
      console.error(error);
      alert("에러가 발생했습니다.");
    }
  };

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
            value={loginId}
            onChange={(e) => setLoginId(e.target.value)}
          />
          <input
            type="password"
            className="flex border w-120 h-13 p-4"
            placeholder="비밀번호를 입력하세요."
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button
            onClick={handleLogin}
            className="text-3xl font-bold text-blue-900"
          >
            로그인
          </button>
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
