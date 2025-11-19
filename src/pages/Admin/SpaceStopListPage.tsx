import { ChevronLeft } from "lucide-react";
import { NavLink } from "react-router";
import type { SpaceStop } from "../../types/space";
import { useState } from "react";
import { StopSpaceModal } from "../../components/Modals/StopSpaceModal";

export const SpaceStopListPage = () => {
  const [stopList, setStopList] = useState<SpaceStop[]>([
    {
      id: 1,
      spaceName: "A101",
      startDate: "2025-02-20",
      endDate: "2025-02-23",
    },
    {
      id: 2,
      spaceName: "B202",
      startDate: "2025-02-18",
      endDate: "2025-02-22",
    },
  ]);

  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [open, setOpen] = useState(false);

  const handleOpenModal = (id: number) => {
    setSelectedId(id);
    setOpen(true);
  };

  const handleConfirm = () => {
    setStopList((prev) => prev.filter((item) => item.id !== selectedId));
    setOpen(false);
    setSelectedId(null);
  };

  const handleCancel = () => {
    setOpen(false);
    setSelectedId(null);
  };

  return (
    <div className="flex flex-col h-full">
      <NavLink to="/admin">
        <ChevronLeft className="m-2" size={30} />
      </NavLink>
      <div className="flex flex-col items-center justify-center">
        <h1 className="flex text-5xl font-bold text-blue-900 my-8">
          사용중지 리스트
        </h1>
        <div className="flex flex-col w-200 mt-8">
          <div className="grid grid-cols-5 gap-4 mb-4 text-2xl text-blue-900 font-bold">
            <p className="flex items-center justify-center">공간중지번호</p>
            <p className="flex items-center justify-center">공간이름</p>
            <p className="flex items-center justify-center">중지시작일</p>
            <p className="flex items-center justify-center">중지종료일</p>
          </div>
          {stopList.map((item) => (
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
          ))}
        </div>
      </div>
      {open && (
        <StopSpaceModal onConfirm={handleConfirm} onCancel={handleCancel} />
      )}
    </div>
  );
};
