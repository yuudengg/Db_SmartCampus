import { ChevronLeft, UserRoundCog } from "lucide-react";
import { NavLink, useNavigate } from "react-router";
import { useAdmin } from "../../hooks/useAdmin";
import { useEffect, useState } from "react";
import { axiosInstance } from "../../apis/axiosInstance";

export const EditAdminPage = () => {
  const admin = useAdmin();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    admin_id: admin?.admin_id || "",
    name: admin?.name || "",
    department: admin?.department || "",
  });

  useEffect(() => {
    if (admin && admin.admin_id) {
      setFormData({
        admin_id: admin.admin_id,
        name: "",
        department: "",
      });
    }
  }, [admin]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    try {
      const res = await axiosInstance.put("/admin/edit", {
        name: formData.name,
        department: formData.department,
        admin_id: formData.admin_id,
      });

      if (res.data.success) {
        alert("정보가 성공적으로 수정되었습니다!");
        localStorage.setItem("admin", JSON.stringify(res.data.admin)); // ✅ 수정된 정보 다시 저장
        navigate("/admin");
      } else {
        alert(res.data.message || "수정에 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      alert("에러가 발생했습니다.");
    }
  };
  return (
    <div className="flex flex-col h-full gap-6">
      <NavLink to="/admin">
        <ChevronLeft className="m-2" size={30} />
      </NavLink>
      <div className="flex flex-col items-center justify-center">
        <div className="flex flex-col items-center mb-4">
          <UserRoundCog size={80} color="oklch(37.9% 0.146 265.522)" />
          <p className="text-xl text-blue-900">{admin?.name}님</p>
        </div>
        <div className="flex flex-col items-center justify-center w-180 h-120 border border-blue-900 gap-4">
          <h1 className="text-5xl font-bold text-blue-900 mb-6">
            관리자 정보 수정
          </h1>
          <div className="flex gap-2 items-center">
            <p className="text-lg mr-2">부서명</p>
            <input
              className="flex border w-60 h-13 p-4"
              name="department"
              placeholder={`${admin?.department}`}
              value={formData.department}
              onChange={handleChange}
            />
          </div>
          <div className="flex gap-2 items-center">
            <p className="text-lg mr-7">이름</p>
            <input
              className="flex border w-60 h-13 p-4"
              name="name"
              placeholder={`${admin?.name}`}
              value={formData.name}
              onChange={handleChange}
            />
          </div>
          <button
            onClick={handleSave}
            className="items-center border border-blue-900 text-blue-900 text-xl font-bold px-8 py-2 mt-4"
          >
            수정
          </button>
        </div>
      </div>
    </div>
  );
};
