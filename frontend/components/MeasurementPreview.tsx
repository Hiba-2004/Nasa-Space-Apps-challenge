
"use client";

import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type Measurement = {
  measured_at: string;
  metric: string;
  value: number;
  unit: string;
};

type MeasurementPreviewProps = {
  measurements: Measurement[];
};

export function MeasurementPreview({
  measurements,
}: MeasurementPreviewProps) {
  const heartRateData = measurements
    .filter((item) => item.metric === "resting_heart_rate")
    .sort(
      (a, b) =>
        new Date(a.measured_at).getTime() -
        new Date(b.measured_at).getTime()
    )
    .map((item) => ({
      day: new Date(item.measured_at).toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "2-digit",
      }),
      value: item.value,
    }));

  return (
    <div
      aria-label="Resting heart rate measurements"
      className="h-56 w-full"
    >
      {heartRateData.length === 0 ? (
        <p className="flex h-full items-center justify-center text-sm text-slate-400">
          No heart rate measurements available.
        </p>
      ) : (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={heartRateData}
            margin={{ top: 10, right: 15, bottom: 5, left: 5 }}
          >
            <XAxis
              dataKey="day"
              stroke="#94a3b8"
              tick={{ fontSize: 12 }}
            />

            <YAxis
              domain={["auto", "auto"]}
              stroke="#94a3b8"
              width={55}
              tickFormatter={(value) => `${value}`}
              tick={{ fontSize: 12 }}
            />

            <Tooltip
              formatter={(value) => [`${value} bpm`, "Heart Rate"]}
              labelStyle={{ color: "#e2e8f0" }}
              contentStyle={{
                background: "#0f172a",
                borderColor: "#334155",
                borderRadius: "10px",
              }}
            />

            <Line
              type="monotone"
              dataKey="value"
              stroke="#67e8f9"
              strokeWidth={3}
              dot={{
                fill: "#67e8f9",
                stroke: "#0f172a",
                strokeWidth: 2,
                r: 4,
              }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

