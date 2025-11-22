import { UserRoundCog } from "lucide-react";
import { useNavigate } from "react-router";
import { axiosInstance } from "../../apis/axiosInstance";
import { useState } from "react";

export const AdminLoginPage = () => {
  const [adminId, setAdminId] = useState("");
  const navigate = useNavigate();

  const handleLogin = async () => {
    if (!adminId.trim()) {
      alert("관리자 번호를 입력하세요!");
      return;
    }

    try {
      const res = await axiosInstance.post("/login/admin", {
        admin_id: adminId,
      });

      if (res.data.success) {
        alert(`${res.data.name} 관리자님 환영합니다!`);
        localStorage.setItem("admin", JSON.stringify(res.data));
        localStorage.setItem("role", res.data.role);
        navigate("/admin"); // 관리자 메인 페이지로 이동
      } else {
        alert(res.data.message || "로그인에 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      alert("서버 연결 오류가 발생했습니다!");
    }
  };

  return (
    <div className="flex flex-col">
      <div className="flex flex-col items-center justify-center w-fit">
        <UserRoundCog
          className="flex mx-4 mt-4"
          size={80}
          color="oklch(37.9% 0.146 265.522)"
        />
        <p className="font-bold text-blue-900">관리자</p>
      </div>
      <div className="flex flex-col items-center justify-center">
        <h1 className="flex text-5xl font-bold text-blue-900 my-8">
          장소 예약 시스템
        </h1>
        <div className="flex flex-col items-center justify-center border w-150 h-100 gap-4">
          <p className="self-start text-2xl font-bold text-blue-900 px-16">
            관리자 번호
          </p>
          <input
            value={adminId}
            onChange={(e) => setAdminId(e.target.value)}
            className="flex border w-120 h-13 p-4"
            placeholder="관리자번호를 입력하세요."
          />
          <button
            onClick={handleLogin}
            className="text-3xl font-bold text-blue-900"
          >
            로그인
          </button>
        </div>
      </div>
    </div>
  );
};
