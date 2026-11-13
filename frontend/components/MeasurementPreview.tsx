"use client";

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const syntheticPreview = [
  { day: "D40", value: 61 },
  { day: "D41", value: 63 },
  { day: "D42", value: 62 }
];

export function MeasurementPreview() {
  return (
    <div aria-label="Synthetic resting heart rate preview" className="h-56 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={syntheticPreview} margin={{ top: 10, right: 15, bottom: 5, left: 0 }}>
          <XAxis dataKey="day" stroke="#94a3b8" />
          <YAxis domain={[55, 70]} stroke="#94a3b8" unit=" bpm" width={70} />
          <Tooltip contentStyle={{ background: "#0f172a", borderColor: "#334155" }} />
          <Line type="monotone" dataKey="value" stroke="#67e8f9" strokeWidth={3} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

