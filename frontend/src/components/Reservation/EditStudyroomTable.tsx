import { useState, useEffect, forwardRef, useImperativeHandle } from "react";
import { axiosInstance } from "../../apis/axiosInstance";
import type { SpaceInfo } from "../../types/space";
import { EditSpaceModal } from "../Modals/EditSpaceModal";

export interface EditSpaceHandle {
  getSelectedPeriods: () => Record<number, { start: string; end: string }>;
  clearSelectedPeriods: () => void;
  getUpdatedSpaces: () => SpaceInfo[];
}

export const EditStudyroomTable = forwardRef<EditSpaceHandle>((_, ref) => {
  const [selectedPeriods, setSelectedPeriods] = useState<
    Record<number, { start: string; end: string }>
  >({});

  useImperativeHandle(ref, () => ({
    getSelectedPeriods: () => selectedPeriods,
    clearSelectedPeriods: () => setSelectedPeriods({}),
    getUpdatedSpaces: () => studyrooms,
  }));
  const [studyrooms, setStudyrooms] = useState<SpaceInfo[]>([]);
  const [selectBuilding, setSelectBuilding] = useState("중앙도서관");
  const [activePicker, setActivePicker] = useState<number | null>(null);

  // ✅ 서버에서 스터디룸 목록 불러오기
  useEffect(() => {
    const fetchStudyrooms = async () => {
      try {
        const res = await axiosInstance.get("/spaces/studyroom");
        if (res.data.success) setStudyrooms(res.data.data);
        else alert("스터디룸 데이터를 불러오지 못했습니다.");
      } catch (err) {
        console.error(err);
        alert("서버 연결 오류 발생!");
      }
    };
    fetchStudyrooms();
  }, []);

  const updateSpaceInfo = async (
    space_id: number,
    space_name?: string,
    capacity?: number,
    disable_start?: string,
    disable_end?: string
  ) => {
    if (!space_id) return console.warn("🚫 space_id 누락");

    // 모든 필드가 비었으면 요청 안 함
    if (
      !space_name &&
      capacity === undefined &&
      !disable_start &&
      !disable_end
    ) {
      console.warn("🚫 수정할 데이터가 없습니다.");
      return;
    }

    try {
      const res = await axiosInstance.put("/admin/spaces/edit", {
        space_id,
        space_name,
        capacity,
        disable_start,
        disable_end,
      });

      if (res.data.success) {
        console.log("✅ DB 업데이트 성공:", res.data.data);
        setStudyrooms((prev) =>
          prev.map((room) =>
            room.space_id === space_id ? { ...room, ...res.data.data } : room
          )
        );
      } else {
        alert(res.data.message || "수정 실패");
      }
    } catch (err) {
      console.error("🚨 공간 수정 중 오류:", err);
      alert("서버 오류 발생!");
    }
  };

  const filteredRooms = studyrooms.filter(
    (room) => room.location === selectBuilding
  );

  const buildings = [
    { label: "종합관", value: "중앙도서관" },
    { label: "TIP", value: "TIP" },
  ];

  return (
    <div className="flex flex-col items-center relative">
      {/* 🔹 건물 선택 */}
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

      {/* 🔹 스터디룸 목록 */}
      <div className="flex flex-col w-200 h-100 border-2 border-blue-900 gap-2 p-6 overflow-auto">
        <div className="grid grid-cols-4 text-2xl text-blue-900 font-bold gap-4 pb-2">
          <div className="flex justify-center"></div>
          <div className="flex justify-center">스터디룸</div>
          <div className="flex justify-center">수용 인원</div>
          <div className="flex justify-center">사용 중지</div>
        </div>

        {filteredRooms.map((room, index) => (
          <div
            key={room.space_id}
            className="grid grid-cols-4 text-xl text-blue-900 border-b py-2 items-center"
          >
            <div className="text-center">{index + 1}</div>
            <input
              className="text-center w-40 border rounded-md px-2 ml-2"
              defaultValue={room.space_name}
              onBlur={(e) => {
                const newName = e.target.value.trim();
                if (newName && newName !== room.space_name)
                  updateSpaceInfo(room.space_id, newName, room.capacity);
              }}
            />
            <input
              type="number"
              className="text-center w-20 border rounded-md px-2 ml-14"
              defaultValue={room.capacity}
              onBlur={(e) => {
                const newCap = Number(e.target.value);
                if (newCap && newCap !== room.capacity)
                  updateSpaceInfo(room.space_id, room.space_name, newCap);
              }}
            />
            <div className="flex flex-col items-center justify-center">
              {selectedPeriods[room.space_id] && (
                <p className="text-blue-700 text-sm mb-1">
                  {selectedPeriods[room.space_id].start} ~{" "}
                  {selectedPeriods[room.space_id].end}
                </p>
              )}
              <button
                className="text-center w-35 border px-2 mx-4"
                onClick={() => setActivePicker(room.space_id)}
              >
                날짜 선택
              </button>
            </div>
          </div>
        ))}
      </div>

      <EditSpaceModal
        open={!!activePicker}
        onCancel={() => setActivePicker(null)}
        onConfirm={(start, end) => {
          setSelectedPeriods((prev) => ({
            ...prev,
            [activePicker!]: { start, end },
          }));
          setActivePicker(null);
        }}
      />
    </div>
  );
});
