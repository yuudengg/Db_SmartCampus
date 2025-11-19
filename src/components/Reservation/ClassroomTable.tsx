import { useState } from "react";
import { ReservInfoModal } from "../Modals/ReservInfoModal";
import type { SpaceInfo } from "../../types/space";

export const ClassroomTable = () => {
  const [open, setOpen] = useState(false);

  const handleClick = () => {
    setOpen(true);
  };

  const handleConfirm = () => {
    setOpen(false);
  };

  const handleCancel = () => {
    setOpen(false);
  };

  const buildings = ["A동", "B동", "C동", "D동", "E동", "G동", "P동", "산융"];
  const [selectBuilding, SetSelectBuilding] = useState("A동");

  const classroomData: Record<string, SpaceInfo[]> = {
    A동: [
      { no: 1, room: "A101", capacity: 40 },
      { no: 2, room: "A102", capacity: 35 },
    ],
    B동: [
      { no: 1, room: "B101", capacity: 40 },
      { no: 2, room: "B102", capacity: 35 },
    ],
    C동: [
      { no: 1, room: "C101", capacity: 40 },
      { no: 2, room: "C102", capacity: 35 },
    ],
    D동: [
      { no: 1, room: "D101", capacity: 40 },
      { no: 2, room: "D102", capacity: 35 },
    ],
    E동: [
      { no: 1, room: "E101", capacity: 40 },
      { no: 2, room: "E102", capacity: 35 },
    ],
    G동: [
      { no: 1, room: "G101", capacity: 40 },
      { no: 2, room: "G102", capacity: 35 },
    ],
    P동: [
      { no: 1, room: "P101", capacity: 40 },
      { no: 2, room: "P102", capacity: 35 },
    ],
    산융: [
      { no: 1, room: "산융201", capacity: 40 },
      { no: 2, room: "산융202", capacity: 35 },
    ],
  };
  const data = classroomData[selectBuilding];

  return (
    <div className="flex flex-col items-center">
      <div className="flex w-200">
        {buildings.map((b) => (
          <button
            key={b}
            onClick={() => SetSelectBuilding(b)}
            className={`px-4 w-1/7 rounded-t-sm border-2 border-blue-900 text-2xl ${
              selectBuilding === b
                ? "bg-blue-900 text-white"
                : "bg-white text-blue-900"
            }`}
          >
            {b}
          </button>
        ))}
      </div>
      <div className="flex flex-col w-200 h-100 border-2 border-blue-900 gap-2 p-6 overflow-auto">
        <div className="grid grid-cols-4 text-2xl text-blue-900 font-bold gap-4 pb-2">
          <div className="flex justify-center">번호</div>
          <div className="flex justify-center">강의실 번호</div>
          <div className="flex justify-center">수용 가능 인원</div>
        </div>

        {data.map((item) => (
          <div
            key={item.no}
            className="grid grid-cols-4 text-xl text-blue-900 border-b py-2"
          >
            <div className="text-center">{item.no}</div>
            <div className="text-center">{item.room}</div>
            <div className="text-center">{item.capacity}</div>
            <button
              className="text-center w-35 border px-2 mx-4"
              onClick={handleClick}
            >
              예약 신청
            </button>
          </div>
        ))}
      </div>
      <ReservInfoModal
        open={open}
        onConfirm={handleConfirm}
        onCancel={handleCancel}
      />
    </div>
  );
};
