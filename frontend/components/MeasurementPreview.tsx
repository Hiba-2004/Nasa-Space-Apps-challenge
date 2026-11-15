
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

type TimedPoint = {
  measured_at: string;
  value: number;
};

// Formatage des dates et distinction des mesures prises au même moment.
function formatMeasurementDates<T extends TimedPoint>(
  points: T[]
): (T & { day: string })[] {
  const dateCounts = new Map<string, number>();

  points.forEach((point) => {
    const date = new Date(point.measured_at).toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "2-digit",
    });

    dateCounts.set(date, (dateCounts.get(date) ?? 0) + 1);
  });

  const labelCounts = new Map<string, number>();

  return points.map((point) => {
    const measuredAt = new Date(point.measured_at);

    const date = measuredAt.toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "2-digit",
    });

    const baseLabel =
      (dateCounts.get(date) ?? 0) > 1
        ? `${date} ${measuredAt.toLocaleTimeString("en-GB", {
            hour: "2-digit",
            minute: "2-digit",
          })}`
        : date;

    const occurrence = (labelCounts.get(baseLabel) ?? 0) + 1;
    labelCounts.set(baseLabel, occurrence);

    const day =
      occurrence > 1 ? `${baseLabel} (${occurrence})` : baseLabel;

    return { ...point, day };
  });
}

const chartMargin = {
  top: 10,
  right: 15,
  bottom: 5,
  left: 5,
};

const tooltipStyle = {
  background: "#0f172a",
  borderColor: "#334155",
  borderRadius: "10px",
};

export function MeasurementPreview({
  measurements,
}: MeasurementPreviewProps) {

  // 1. HEART RATE
  const heartRatePoints = measurements
    .filter((item) => item.metric === "resting_heart_rate")
    .sort(
      (a, b) =>
        new Date(a.measured_at).getTime() -
        new Date(b.measured_at).getTime()
    )
    .map((item) => ({
      measured_at: item.measured_at,
      value: item.value,
    }));

  const heartRateData = formatMeasurementDates(heartRatePoints);

  // 2. SLEEP DURATION
  const sleepPoints = measurements
    .filter((item) => item.metric === "sleep_hours")
    .sort(
      (a, b) =>
        new Date(a.measured_at).getTime() -
        new Date(b.measured_at).getTime()
    )
    .map((item) => ({
      measured_at: item.measured_at,
      value: item.value,
    }));

  const sleepData = formatMeasurementDates(sleepPoints);

  // 3. BODY TEMPERATURE
  const temperaturePoints = measurements
    .filter((item) => item.metric === "body_temperature")
    .sort(
      (a, b) =>
        new Date(a.measured_at).getTime() -
        new Date(b.measured_at).getTime()
    )
    .map((item) => ({
      measured_at: item.measured_at,
      value: item.value,
    }));

  const temperatureData = formatMeasurementDates(temperaturePoints);

  // 4. BLOOD PRESSURE
  // Regrouper les valeurs systoliques et diastoliques
  // par horodatage, puis les associer dans leur ordre d'enregistrement.
  const bloodPressureGroups = new Map<
    string,
    {
      systolic: number[];
      diastolic: number[];
    }
  >();

  measurements
    .filter(
      (item) =>
        item.metric === "blood_pressure_systolic" ||
        item.metric === "blood_pressure_diastolic"
    )
    .forEach((item) => {
      const timestamp = item.measured_at;

      const current = bloodPressureGroups.get(timestamp) ?? {
        systolic: [],
        diastolic: [],
      };

      if (item.metric === "blood_pressure_systolic") {
        current.systolic.push(item.value);
      } else {
        current.diastolic.push(item.value);
      }

      bloodPressureGroups.set(timestamp, current);
    });

  const bloodPressurePoints = Array.from(
    bloodPressureGroups.entries()
  )
    .sort(
      (a, b) =>
        new Date(a[0]).getTime() - new Date(b[0]).getTime()
    )
    .flatMap(([measured_at, values]) => {
      const count = Math.max(
        values.systolic.length,
        values.diastolic.length
      );

      return Array.from({ length: count }, (_, index) => ({
        measured_at,
        value: 0,
        systolic: values.systolic[index],
        diastolic: values.diastolic[index],
      }));
    });

  const bloodPressureDatePoints = formatMeasurementDates(
    bloodPressurePoints
  );

  const bloodPressureData = bloodPressurePoints.map((item, index) => ({
    ...item,
    day: bloodPressureDatePoints[index].day,
  }));

  return (
    <div className="space-y-8">

      {/* HEART RATE CHART */}
      <div>
        <h4 className="mb-3 text-sm font-semibold text-cyan-300">
          Resting Heart Rate (bpm)
        </h4>

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
              <LineChart data={heartRateData} margin={chartMargin}>
                <XAxis
                  dataKey="day"
                  stroke="#94a3b8"
                  tick={{ fontSize: 12 }}
                />

                <YAxis
                  domain={["auto", "auto"]}
                  stroke="#94a3b8"
                  width={55}
                  tick={{ fontSize: 12 }}
                />

                <Tooltip
                  formatter={(value) => [`${value} bpm`, "Heart Rate"]}
                  labelStyle={{ color: "#e2e8f0" }}
                  contentStyle={tooltipStyle}
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
      </div>

      {/* SLEEP DURATION CHART */}
      <div className="border-t border-slate-700 pt-6">
        <h4 className="mb-3 text-sm font-semibold text-violet-300">
          Sleep Duration (hours)
        </h4>

        <div
          aria-label="Sleep duration measurements"
          className="h-56 w-full"
        >
          {sleepData.length === 0 ? (
            <p className="flex h-full items-center justify-center text-sm text-slate-400">
              No sleep measurements available.
            </p>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sleepData} margin={chartMargin}>
                <XAxis
                  dataKey="day"
                  stroke="#94a3b8"
                  tick={{ fontSize: 12 }}
                />

                <YAxis
                  domain={["auto", "auto"]}
                  stroke="#94a3b8"
                  width={55}
                  tick={{ fontSize: 12 }}
                />

                <Tooltip
                  formatter={(value) => [`${value} hours`, "Sleep Duration"]}
                  labelStyle={{ color: "#e2e8f0" }}
                  contentStyle={tooltipStyle}
                />

                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#c4b5fd"
                  strokeWidth={3}
                  dot={{
                    fill: "#c4b5fd",
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
      </div>

      {/* BODY TEMPERATURE CHART */}
      <div className="border-t border-slate-700 pt-6">
        <h4 className="mb-3 text-sm font-semibold text-amber-300">
          Body Temperature (°C)
        </h4>

        <div
          aria-label="Body temperature measurements"
          className="h-56 w-full"
        >
          {temperatureData.length === 0 ? (
            <p className="flex h-full items-center justify-center text-sm text-slate-400">
              No temperature measurements available.
            </p>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={temperatureData} margin={chartMargin}>
                <XAxis
                  dataKey="day"
                  stroke="#94a3b8"
                  tick={{ fontSize: 12 }}
                />

                <YAxis
                  domain={["auto", "auto"]}
                  stroke="#94a3b8"
                  width={55}
                  tick={{ fontSize: 12 }}
                />

                <Tooltip
                  formatter={(value) => [`${value} °C`, "Body Temperature"]}
                  labelStyle={{ color: "#e2e8f0" }}
                  contentStyle={tooltipStyle}
                />

                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#fbbf24"
                  strokeWidth={3}
                  dot={{
                    fill: "#fbbf24",
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
      </div>

      {/* BLOOD PRESSURE CHART */}
      <div className="border-t border-slate-700 pt-6">
        <h4 className="mb-3 text-sm font-semibold text-emerald-300">
          Blood Pressure (mmHg)
        </h4>

        <div
          aria-label="Blood pressure measurements"
          className="h-56 w-full"
        >
          {bloodPressureData.length === 0 ? (
            <p className="flex h-full items-center justify-center text-sm text-slate-400">
              No blood pressure measurements available.
            </p>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={bloodPressureData} margin={chartMargin}>
                <XAxis
                  dataKey="day"
                  stroke="#94a3b8"
                  tick={{ fontSize: 12 }}
                />

                <YAxis
                  domain={["auto", "auto"]}
                  stroke="#94a3b8"
                  width={55}
                  tick={{ fontSize: 12 }}
                />

                <Tooltip
                  formatter={(value, name) => [
                    value === undefined ? "Not available" : `${value} mmHg`,
                    name === "systolic" ? "Systolic" : "Diastolic",
                  ]}
                  labelStyle={{ color: "#e2e8f0" }}
                  contentStyle={tooltipStyle}
                />

                <Line
                  type="monotone"
                  dataKey="systolic"
                  name="systolic"
                  stroke="#34d399"
                  strokeWidth={3}
                  connectNulls
                  dot={{
                    fill: "#34d399",
                    stroke: "#0f172a",
                    strokeWidth: 2,
                    r: 4,
                  }}
                  activeDot={{ r: 6 }}
                />

                <Line
                  type="monotone"
                  dataKey="diastolic"
                  name="diastolic"
                  stroke="#fb7185"
                  strokeWidth={3}
                  connectNulls
                  dot={{
                    fill: "#fb7185",
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

        <div className="mt-3 flex flex-wrap gap-5 text-xs text-slate-400">
          <span className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            Systolic
          </span>

          <span className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-rose-400" />
            Diastolic
          </span>
        </div>
      </div>
    </div>
  );
}
