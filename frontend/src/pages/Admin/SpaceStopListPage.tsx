import { ChevronLeft } from "lucide-react";
import { NavLink } from "react-router";
import { useState, useEffect } from "react";
import { axiosInstance } from "../../apis/axiosInstance";
import type { SpaceStop } from "../../types/space";
import { StopSpaceModal } from "../../components/Modals/StopSpaceModal";

export const SpaceStopListPage = () => {
  const [stopList, setStopList] = useState<SpaceStop[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [open, setOpen] = useState(false);

  // ✅ 서버에서 사용중지 리스트 불러오기
  const fetchStopList = async () => {
    try {
      const res = await axiosInstance.get("/spaces/stop-list");
      if (res.data.success) {
        setStopList(res.data.data);
      } else {
        alert("사용중지 목록을 불러오지 못했습니다.");
      }
    } catch (err) {
      console.error("🚨 목록 불러오기 오류:", err);
      alert("서버 연결 오류가 발생했습니다!");
    }
  };

  useEffect(() => {
    fetchStopList();
  }, []);

  // ✅ 사용중지 해제 버튼 클릭
  const handleOpenModal = (id: number) => {
    setSelectedId(id);
    setOpen(true);
  };

  // ✅ 사용중지 해제 확정
  const handleConfirm = async () => {
    if (!selectedId) return;
    try {
      const res = await axiosInstance.delete(`/spaces/stop/${selectedId}`);
      if (res.data.success) {
        alert("공간 사용중지가 해제되었습니다.");
        setStopList((prev) => prev.filter((item) => item.id !== selectedId));
      } else {
        alert(res.data.message || "해제 실패");
      }
    } catch (err) {
      console.error("🚨 해제 중 오류:", err);
      alert("서버 오류가 발생했습니다!");
    } finally {
      setOpen(false);
      setSelectedId(null);
    }
  };

  const handleCancel = () => {
    setOpen(false);
    setSelectedId(null);
  };

  return (
    <div className="flex flex-col h-full">
      <NavLink to="/admin/manage/space">
        <ChevronLeft className="m-2" size={30} />
      </NavLink>
      <div className="flex flex-col items-center justify-center">
        <h1 className="flex text-5xl font-bold text-blue-900 my-8">
          사용중지 리스트
        </h1>

        <div className="flex flex-col w-200 mt-8">
          <div className="grid grid-cols-5 gap-4 mb-4 text-2xl text-blue-900 font-bold">
            <p className="flex items-center justify-center">번호</p>
            <p className="flex items-center justify-center">공간 이름</p>
            <p className="flex items-center justify-center">중지 시작일</p>
            <p className="flex items-center justify-center">중지 종료일</p>
          </div>

          {stopList.length > 0 ? (
            stopList.map((item) => (
              <div
                key={item.id}
                className="grid grid-cols-5 justify-center text-xl text-blue-900 gap-4 border-b py-2"
              >
                <div className="flex justify-center">{item.id}</div>
                <div className="flex justify-center">{item.spaceName}</div>
                <div className="flex justify-center">{item.startDate}</div>
                <div className="flex justify-center">{item.endDate}</div>
                <button
                  onClick={() => handleOpenModal(item.id)}
                  className="border border-red-500 text-red-500 w-20 ml-6"
                >
                  취소
                </button>
              </div>
            ))
          ) : (
            <p className="text-blue-900 text-lg text-center mt-10">
              현재 사용중지된 공간이 없습니다.
            </p>
          )}
        </div>
      </div>

      {open && (
        <StopSpaceModal onConfirm={handleConfirm} onCancel={handleCancel} />
      )}
    </div>
  );
};
