interface CircleGraphProps {
  percentage: number; // 0~100
  size?: number;
}

export function CircleGraph({ percentage, size = 120 }: CircleGraphProps) {
  const radius = size / 2;
  const stroke = 12;
  const circumference = 2 * Math.PI * (radius - stroke);

  const offset = circumference - (percentage / 100) * circumference;

  return (
    <svg width={size} height={size}>
      {/* 배경 원 */}
      <circle
        cx={radius}
        cy={radius}
        r={radius - stroke}
        stroke="#e2e8f0"
        strokeWidth={stroke}
        fill="none"
      />

      {/* 퍼센트 원 */}
      <circle
        cx={radius}
        cy={radius}
        r={radius - stroke}
        stroke="#1e3a8a"
        strokeWidth={stroke}
        fill="none"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        transform={`rotate(-90 ${radius} ${radius})`}
      />

      {/* 퍼센트 글자 */}
      <text
        x="50%"
        y="50%"
        textAnchor="middle"
        dy=".3em"
        fontSize="22"
        fill="#1e3a8a"
        fontWeight="bold"
      >
        {percentage}%
      </text>
    </svg>
  );
}
