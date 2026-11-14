
import { MeasurementPreview } from "../components/MeasurementPreview";

const metrics = [
  {
    label: "Resting Heart Rate",
    value: "62",
    unit: "bpm",
    icon: "♡",
    description: "Latest recorded measurement",
  },
  {
    label: "Sleep Duration",
    value: "7.2",
    unit: "hours",
    icon: "◷",
    description: "Last sleep period",
  },
  {
    label: "Body Temperature",
    value: "36.7",
    unit: "°C",
    icon: "♧",
    description: "Latest recorded measurement",
  },
  {
    label: "Blood Pressure",
    value: "118/76",
    unit: "mmHg",
    icon: "⌁",
    description: "Systolic / Diastolic",
  },
];

const navigation = [
  { label: "Overview", href: "#overview", icon: "◫" },
  { label: "Measurements", href: "#measurements", icon: "♡" },
  { label: "Health Trends", href: "#trends", icon: "⌁" },
  { label: "Health Notes", href: "#health-notes", icon: "▤" },
];

export default function Home() {
  return (
    <main
      id="overview"
      className="min-h-screen bg-slate-950 text-slate-100 lg:flex"
    >
      {/* SIDEBAR */}
      <aside className="border-b border-slate-800 bg-slate-900/80 p-5 lg:fixed lg:inset-y-0 lg:left-0 lg:w-64 lg:border-b-0 lg:border-r">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-400/10 text-xl text-cyan-300">
            ✦
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-wider">ASTRAVITAL</h1>
            <p className="text-xs text-slate-500">MISSION HEALTH SYSTEM</p>
          </div>
        </div>

        <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-slate-500">
          Workspace
        </p>

        <nav className="flex gap-2 overflow-x-auto lg:flex-col">
          {navigation.map((item, index) => (
            <a
              key={item.label}
              href={item.href}
              className={`flex shrink-0 items-center gap-3 rounded-xl px-4 py-3 text-sm transition ${
                index === 0
                  ? "bg-cyan-400/10 font-semibold text-cyan-300"
                  : "text-slate-400 hover:bg-slate-800 hover:text-white"
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              {item.label}
            </a>
          ))}
        </nav>

        <div className="mt-8 rounded-xl border border-cyan-900/60 bg-cyan-950/30 p-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-cyan-300">
            Mission status
          </p>
          <p className="mt-2 text-sm font-semibold text-white">
            Local simulation
          </p>
          <p className="mt-1 text-xs text-slate-400">
            Mission Day 42
          </p>
        </div>

        <div className="mt-8 hidden border-t border-slate-800 pt-5 lg:block">
          <p className="text-xs text-slate-500">ASTRAVITAL</p>
          <p className="mt-1 text-xs text-slate-600">
            NASA Space Apps Challenge 2026
          </p>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <div className="min-w-0 flex-1 p-5 sm:p-8 lg:ml-64 lg:p-10">
        {/* HEADER */}
        <header className="mb-9 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm font-medium uppercase tracking-widest text-cyan-400">
              Mission Control / Overview
            </p>
            <h2 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
              Health Dashboard
            </h2>
            <p className="mt-2 text-sm text-slate-400">
              Monitor your health throughout your space mission.
            </p>
          </div>

          <div className="flex items-center gap-3 rounded-xl border border-slate-800 bg-slate-900 px-4 py-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-cyan-400/10 font-bold text-cyan-300">
              A
            </div>
            <div>
              <p className="text-sm font-semibold">Synthetic Crew A</p>
              <p className="text-xs text-slate-400">Astronaut Profile</p>
            </div>
          </div>
        </header>

        {/* MISSION BANNER */}
        <section className="mb-8 overflow-hidden rounded-2xl border border-cyan-900/50 bg-gradient-to-r from-cyan-950/50 to-slate-900 p-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-cyan-300">
                Current mission
              </p>
              <h3 className="mt-2 text-2xl font-bold">
                Long Duration Space Mission
              </h3>
              <p className="mt-2 text-sm text-slate-400">
                Synthetic Crew A · Simulated Mission Day 42
              </p>
            </div>
            <div className="rounded-xl border border-cyan-800 bg-cyan-950/50 px-5 py-3">
              <p className="text-xs text-slate-400">MISSION DAY</p>
              <p className="text-3xl font-bold text-cyan-300">42</p>
            </div>
          </div>
        </section>

        {/* HEALTH METRICS */}
        <section id="measurements" className="mb-9">
          <div className="mb-5">
            <h3 className="text-xl font-bold">Health Overview</h3>
            <p className="mt-1 text-sm text-slate-400">
              Latest available synthetic measurements
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {metrics.map((metric) => (
              <article
                key={metric.label}
                className="rounded-2xl border border-slate-800 bg-slate-900 p-5 transition hover:border-cyan-800"
              >
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-slate-400">
                    {metric.label}
                  </p>
                  <span className="text-2xl text-cyan-300">
                    {metric.icon}
                  </span>
                </div>

                <div className="mt-5 flex items-baseline gap-2">
                  <span className="text-3xl font-bold tracking-tight">
                    {metric.value}
                  </span>
                  <span className="text-sm text-slate-400">
                    {metric.unit}
                  </span>
                </div>

                <p className="mt-3 text-xs text-slate-500">
                  {metric.description}
                </p>
              </article>
            ))}
          </div>
        </section>

        {/* CHART AND HEALTH NOTES */}
        <section className="grid gap-6 xl:grid-cols-[1.7fr_1fr]">
          <article
            id="trends"
            className="rounded-2xl border border-slate-800 bg-slate-900 p-5 sm:p-6"
          >
            <div className="mb-5">
              <h3 className="text-xl font-bold">Heart Rate Trends</h3>
              <p className="mt-1 text-sm text-slate-400">
                Resting heart rate · Synthetic preview
              </p>
            </div>

            <MeasurementPreview />
          </article>

          <article
            id="health-notes"
            className="rounded-2xl border border-amber-900/50 bg-amber-950/20 p-5 sm:p-6"
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl text-amber-300">ⓘ</span>
              <h3 className="text-xl font-bold text-amber-100">
                Health Notes
              </h3>
            </div>

            <p className="mt-5 text-sm leading-7 text-amber-50/80">
              Fatigue was not reported in the latest synthetic check-in.
              This information remains missing and is not interpreted as
              a normal result.
            </p>

            <div className="mt-5 border-t border-amber-900/50 pt-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-amber-300">
                Data completeness
              </p>
              <p className="mt-2 text-sm text-amber-100/70">
                One self-report field is missing.
              </p>
            </div>
          </article>
        </section>

        {/* DISCLAIMER */}
        <footer className="mt-9 border-t border-slate-800 pt-5">
          <p className="text-xs leading-6 text-slate-500">
            ASTRAVITAL is an offline-capable health monitoring and
            decision-support prototype. All displayed readings are
            synthetic. This application does not diagnose conditions
            or replace qualified medical judgment.
          </p>
        </footer>
      </div>
    </main>
  );
}
