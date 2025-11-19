import { UserRoundCog } from "lucide-react";

export const AdminLoginPage = () => {
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
            className="flex border w-120 h-13 p-4"
            placeholder="관리자번호를 입력하세요."
          />
          <button className="text-3xl font-bold text-blue-900">로그인</button>
        </div>
      </div>
    </div>
  );
};
