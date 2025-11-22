import { ChevronLeft } from "lucide-react";
import { useState, useRef } from "react";
import { NavLink } from "react-router";
import {
  EditClassroomTable,
  type EditSpaceHandle,
} from "../../components/Reservation/EditClassroomTable";
import { EditStudyroomTable } from "../../components/Reservation/EditStudyroomTable";
import { axiosInstance } from "../../apis/axiosInstance";

export const ManageSpacePage = () => {
  const [select, setSelect] = useState<"classroom" | "studyroom">("classroom");

  const classroomRef = useRef<EditSpaceHandle>(null);
  const studyroomRef = useRef<EditSpaceHandle>(null);

  const handleSave = async () => {
    const currentRef =
      select === "classroom" ? classroomRef.current : studyroomRef.current;

    const periods = currentRef?.getSelectedPeriods?.() || {};
    const stops = Object.entries(periods).map(([space_id, value]) => ({
      space_id: Number(space_id),
      start_date: value.start,
      end_date: value.end,
    }));

    try {
      // ✅ 사용 중지 기간 저장이 있을 때만 요청
      if (stops.length > 0) {
        const res = await axiosInstance.post("/spaces/stop", { stops });
        if (res.data.success) {
          alert("공간 정보가 성공적으로 저장되었습니다!");
        } else {
          alert(res.data.message || "저장 중 문제가 발생했습니다.");
        }
        currentRef?.clearSelectedPeriods?.();
      } else {
        // ✅ 기간이 비어 있어도 오류 아님 (이름/인원은 이미 저장됨)
        alert("공간 정보가 성공적으로 저장되었습니다!");
      }
    } catch (err) {
      console.error("🚨 저장 중 오류:", err);
      alert("서버 연결 오류가 발생했습니다!");
    }
  };

  return (
    <div className="flex flex-col h-full">
      <NavLink to="/admin">
        <ChevronLeft className="m-2" size={30} />
      </NavLink>
      <div className="flex flex-col items-center justify-center">
        <h1 className="flex text-5xl font-bold text-blue-900 my-8">
          장소 관리
        </h1>

        {/* 🔹 탭 전환 */}
        <div className="flex w-200 gap-4 mb-6">
          <button
            className={`border-2 border-blue-900 text-2xl font-bold w-35 py-1 ${
              select === "classroom"
                ? "text-white bg-blue-900"
                : "text-blue-900 bg-white"
            }`}
            onClick={() => setSelect("classroom")}
          >
            강의실
          </button>
          <button
            className={`border-2 border-blue-900 text-2xl font-bold w-35 py-1 ${
              select === "studyroom"
                ? "text-white bg-blue-900"
                : "text-blue-900 bg-white"
            }`}
            onClick={() => setSelect("studyroom")}
          >
            스터디룸
          </button>
        </div>

        {/* 🔹 테이블 */}
        {select === "classroom" ? (
          <EditClassroomTable ref={classroomRef} />
        ) : (
          <EditStudyroomTable ref={studyroomRef} />
        )}

        {/* 🔹 하단 버튼 */}
        <div className="flex w-200 justify-end my-2 gap-2">
          <NavLink
            to="/admin/manage/space/stop"
            className="flex border-2 border-blue-900 px-2 text-blue-900"
          >
            사용중지 리스트
          </NavLink>
          <button
            onClick={handleSave}
            className="flex border-2 border-blue-900 px-2 text-blue-900"
          >
            수정 완료
          </button>
        </div>
      </div>
    </div>
  );
};
