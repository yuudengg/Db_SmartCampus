import { ChevronLeft } from "lucide-react";
import { useState } from "react";
import { NavLink } from "react-router";
import { StopCheckingModal } from "../../components/Modals/StopCheckingModal";
import type { User } from "../../types/user";

export const ManageUserPage = () => {
  const [users, setUsers] = useState<User[]>([
    { id: 1, name: "김철수", role: "학생", noShow: 2, isStop: false },
    { id: 2, name: "이영희", role: "교수", noShow: 0, isStop: true },
    { id: 3, name: "박민수", role: "학생", noShow: 1, isStop: false },
  ]);

  const [open, setOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  const handleOpenModal = (user: User) => {
    setSelectedUser(user);
    setOpen(true);
  };

  const handleConfirm = () => {
    if (!selectedUser) return;

    setUsers((prev) =>
      prev.map((u) =>
        u.id === selectedUser.id ? { ...u, isStop: !u.isStop } : u
      )
    );

    setOpen(false);
    setSelectedUser(null);
  };

  const handleCancel = () => {
    setOpen(false);
    setSelectedUser(null);
  };

  return (
    <div className="flex flex-col h-full gap-6">
      <NavLink to="/admin">
        <ChevronLeft className="m-2" size={30} />
      </NavLink>

      <div className="flex flex-col items-center justify-center">
        <h1 className="flex text-5xl font-bold text-blue-900 my-8">
          사용자 관리
        </h1>
        <div className="flex flex-col w-200 h-100 border-2 border-blue-900 gap-2 p-6 overflow-auto">
          <div className="grid grid-cols-5 text-2xl text-blue-900 font-bold gap-4 pb-2">
            <div className="flex justify-center">유저 아이디</div>
            <div className="flex justify-center">이름</div>
            <div className="flex justify-center">역할</div>
            <div className="flex justify-center">노쇼 횟수</div>
            <div></div>
          </div>
          {users.map((user) => (
            <div
              key={user.id}
              className="grid grid-cols-5 justify-center text-xl text-blue-900 gap-4 border-b py-2"
            >
              <div className="flex justify-center">{user.id}</div>
              <div className="flex justify-center">{user.name}</div>
              <div className="flex justify-center">{user.role}</div>
              <div className="flex justify-center">{user.noShow}</div>
              <button
                className={`border ${
                  user.isStop ? "text-red-500" : "text-blue-900 px-4"
                }`}
                onClick={() => handleOpenModal(user)}
              >
                {user.isStop ? "사용 중지 해제" : "사용 중지"}
              </button>
            </div>
          ))}
        </div>
        <p className="text-blue-900 text-lg mt-2">
          * 노쇼로 인한 사용 중지의 경우 3일 정지
        </p>
      </div>
      {selectedUser && (
        <StopCheckingModal
          open={open}
          isStop={selectedUser.isStop}
          onConfirm={handleConfirm}
          onCancel={handleCancel}
        />
      )}
    </div>
  );
};
