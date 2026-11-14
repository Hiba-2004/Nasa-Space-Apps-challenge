
"use client";

import { useState } from "react";

export default function MeasurementsPage() {
  const [form, setForm] = useState({
    measuredAt: "",
    heartRate: "",
    sleepHours: "",
    temperature: "",
    systolic: "",
    diastolic: "",
  });

  const [message, setMessage] = useState("");

  function handleChange(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    setForm({
      ...form,
      [event.target.name]: event.target.value,
    });
    setMessage("");
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const draft = {
      measured_at: new Date(form.measuredAt).toISOString(),
      measurements: [
        {
          metric: "resting_heart_rate",
          value: Number(form.heartRate),
          unit: "bpm",
        },
        {
          metric: "sleep_hours",
          value: Number(form.sleepHours),
          unit: "h",
        },
        {
          metric: "body_temperature",
          value: Number(form.temperature),
          unit: "Cel",
        },
        {
          metric: "blood_pressure_systolic",
          value: Number(form.systolic),
          unit: "mmHg",
        },
        {
          metric: "blood_pressure_diastolic",
          value: Number(form.diastolic),
          unit: "mmHg",
        },
      ],
      source: "synthetic manual entry",
    };

    console.log("Measurement draft:", draft);

    setMessage(
      "Measurement draft created successfully. API integration is not connected yet."
    );
  }

  function Field({
    label,
    name,
    unit,
    placeholder,
    step = "any",
  }: {
    label: string;
    name: keyof typeof form;
    unit: string;
    placeholder: string;
    step?: string;
  }) {
    return (
      <div>
        <label
          htmlFor={name}
          className="mb-2 block text-sm font-medium text-slate-300"
        >
          {label}
        </label>

        <div className="flex items-center rounded-xl border border-slate-700 bg-slate-950 focus-within:border-cyan-400">
          <input
            id={name}
            name={name}
            type="number"
            step={step}
            min="0"
            required
            value={form[name]}
            onChange={handleChange}
            placeholder={placeholder}
            className="w-full bg-transparent px-4 py-3 text-white outline-none placeholder:text-slate-600"
          />
          <span className="px-4 text-sm text-slate-500">{unit}</span>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 px-5 py-10 text-slate-100 sm:px-8 lg:px-12">
      <div className="mx-auto max-w-4xl">

        <a
          href="/"
          className="text-sm text-cyan-400 hover:text-cyan-300"
        >
          ← Back to Dashboard
        </a>

        <header className="mb-8 mt-7">
          <p className="text-sm font-semibold uppercase tracking-widest text-cyan-400">
            Mission Control / Health Monitoring
          </p>

          <h1 className="mt-3 text-3xl font-bold sm:text-4xl">
            Health Measurements
          </h1>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Record your daily health indicators during the mission.
            All entries in this prototype are synthetic.
          </p>
        </header>

        <form
          onSubmit={handleSubmit}
          className="rounded-2xl border border-slate-800 bg-slate-900 p-5 sm:p-8"
        >
          <div className="mb-8">
            <h2 className="text-xl font-semibold">
              Measurement Details
            </h2>
            <p className="mt-2 text-sm text-slate-400">
              Enter the observation date and time.
            </p>

            <div className="mt-5">
              <label
                htmlFor="measuredAt"
                className="mb-2 block text-sm font-medium text-slate-300"
              >
                Measurement Date & Time
              </label>

              <input
                id="measuredAt"
                name="measuredAt"
                type="datetime-local"
                required
                value={form.measuredAt}
                onChange={handleChange}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-cyan-400"
              />
            </div>
          </div>

          <div className="mb-8">
            <h2 className="mb-5 text-xl font-semibold">
              Vital Signs
            </h2>

            <div className="grid gap-6 sm:grid-cols-2">
              <Field
                label="Resting Heart Rate"
                name="heartRate"
                unit="bpm"
                placeholder="Example: 62"
              />

              <Field
                label="Sleep Duration"
                name="sleepHours"
                unit="hours"
                placeholder="Example: 7.2"
              />

              <Field
                label="Body Temperature"
                name="temperature"
                unit="°C"
                placeholder="Example: 36.7"
              />

              <div className="rounded-xl border border-cyan-900/50 bg-cyan-950/20 p-4 sm:col-span-2">
                <h3 className="mb-4 font-semibold text-cyan-300">
                  Blood Pressure
                </h3>

                <div className="grid gap-5 sm:grid-cols-2">
                  <Field
                    label="Systolic Pressure"
                    name="systolic"
                    unit="mmHg"
                    placeholder="Example: 118"
                    step="1"
                  />

                  <Field
                    label="Diastolic Pressure"
                    name="diastolic"
                    unit="mmHg"
                    placeholder="Example: 76"
                    step="1"
                  />
                </div>
              </div>
            </div>
          </div>

          {message && (
            <div
              role="status"
              className="mb-5 rounded-xl border border-cyan-800 bg-cyan-950/40 p-4 text-sm text-cyan-200"
            >
              {message}
            </div>
          )}

          <div className="flex flex-wrap gap-3">
            <button
              type="submit"
              className="rounded-xl bg-cyan-400 px-6 py-3 font-semibold text-slate-950 transition hover:bg-cyan-300"
            >
              Review Measurements
            </button>

            <button
              type="reset"
              onClick={() => {
                setForm({
                  measuredAt: "",
                  heartRate: "",
                  sleepHours: "",
                  temperature: "",
                  systolic: "",
                  diastolic: "",
                });
                setMessage("");
              }}
              className="rounded-xl border border-slate-700 px-6 py-3 text-slate-300 transition hover:bg-slate-800"
            >
              Clear Form
            </button>
          </div>
        </form>

        <p className="mt-6 text-xs leading-6 text-slate-500">
          ASTRAVITAL is a health monitoring and decision-support prototype.
          Entries are currently local drafts and are not saved to the backend.
          This application does not diagnose medical conditions.
        </p>
      </div>
    </main>
  );
}
