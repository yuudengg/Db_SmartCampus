export const StudentFields = () => {
  return (
    <>
      <div className="flex gap-2 items-center">
        <p className="text-lg mr-15.5">학번</p>
        <input className="border w-60 h-13 p-4" />
      </div>
      <div className="flex gap-2 items-center">
        <p className="text-lg mr-15.5">학년</p>
        <input className="border w-60 h-13 p-4" />
      </div>
      <div className="flex gap-2 items-center">
        <p className="text-lg mr-15.5">학과</p>
        <input className="border w-60 h-13 p-4" />
      </div>
    </>
  );
};
