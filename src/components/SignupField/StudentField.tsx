export const StudentFields = ({
  formData,
  handleChange,
}: {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  formData: any;
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}) => (
  <>
    <div className="flex gap-2 items-center">
      <p className="text-lg mr-15.5">학번</p>
      <input
        name="student_id"
        value={formData.student_id}
        onChange={handleChange}
        className="border w-60 h-13 p-4"
      />
    </div>
    <div className="flex gap-2 items-center">
      <p className="text-lg mr-15.5">학년</p>
      <input
        name="grade"
        value={formData.grade}
        onChange={handleChange}
        className="border w-60 h-13 p-4"
      />
    </div>
    <div className="flex gap-2 items-center">
      <p className="text-lg mr-15.5">학과</p>
      <input
        name="major"
        value={formData.major}
        onChange={handleChange}
        className="border w-60 h-13 p-4"
      />
    </div>
  </>
);
