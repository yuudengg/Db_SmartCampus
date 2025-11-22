import { useState, useEffect } from "react";
import { ReservInfoModal } from "../Modals/ReservInfoModal";
import { axiosInstance } from "../../apis/axiosInstance";
import { useUser } from "../../hooks/useUser";
import type { SpaceInfo } from "../../types/space";

export const StudyroomTable = () => {
  const [open, setOpen] = useState(false);
  const [studyrooms, setStudyrooms] = useState<SpaceInfo[]>([]);
  const [selectBuilding, setSelectBuilding] = useState("중앙도서관");
  const [selectedSpaceId, setSelectedSpaceId] = useState<number | null>(null);
  const user = useUser();

  // 서버에서 스터디룸 목록 불러오기
  useEffect(() => {
    const fetchStudyrooms = async () => {
      try {
        const res = await axiosInstance.get("/spaces/studyroom");
        if (res.data.success) {
          setStudyrooms(res.data.data);
        } else {
          alert("스터디룸 데이터를 불러오지 못했습니다.");
        }
      } catch (err) {
        console.error(err);
        alert("서버 연결 오류가 발생했습니다!");
      }
    };
    fetchStudyrooms();
  }, []);

  // 선택한 건물의 강의실만 필터링
  const filteredRooms = studyrooms.filter(
    (room) => room.location === selectBuilding
  );

  // 예약 버튼 클릭 시
  const handleClick = (spaceId: number) => {
    setSelectedSpaceId(spaceId); // 🔹 spaceId 저장
    setOpen(true); // 🔹 모달 열기
  };
  const handleConfirm = () => setOpen(false);
  const handleCancel = () => setOpen(false);

  const buildings = [
    { label: "종합관", value: "중앙도서관" },
    { label: "TIP", value: "TIP" },
  ];

  return (
    <div className="flex flex-col items-center">
      <div className="flex w-200">
        {buildings.map((b) => (
          <button
            key={b.value}
            onClick={() => setSelectBuilding(b.value)}
            className={`px-4 w-1/7 rounded-t-sm border-2 border-blue-900 text-2xl ${
              selectBuilding === b.value
                ? "bg-blue-900 text-white"
                : "bg-white text-blue-900"
            }`}
          >
            {b.label}
          </button>
        ))}
      </div>

      <div className="flex flex-col w-200 h-100 border-2 border-blue-900 gap-2 p-6 overflow-auto">
        <div className="grid grid-cols-4 text-2xl text-blue-900 font-bold gap-4 pb-2">
          <div className="flex justify-center">번호</div>
          <div className="flex justify-center">강의실</div>
          <div className="flex justify-center">수용 인원</div>
        </div>

        {filteredRooms.map((room, index) => (
          <div
            key={room.space_id}
            className="grid grid-cols-4 text-xl text-blue-900 border-b py-2"
          >
            <div className="text-center">{index + 1}</div>
            <div className="text-center">{room.space_name}</div>
            <div className="text-center">{room.capacity}</div>
            <button
              className="text-center w-35 border px-2 mx-4"
              onClick={() => handleClick(room.space_id)}
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
        spaceId={selectedSpaceId ?? 0}
      />
    </div>
  );
};
