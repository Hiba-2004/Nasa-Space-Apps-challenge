import { MeasurementPreview } from "../components/MeasurementPreview";

const cards = [
  ["Resting heart rate", "62 bpm"],
  ["Sleep", "7.2 h"],
  ["Temperature", "36.7 Cel"],
  ["Blood pressure", "118 / 76 mmHg"]
];

export default function Home() {
  return (
    <main className="mx-auto max-w-6xl px-5 py-10 sm:px-8">
      <header className="mb-10 border-b border-slate-800 pb-7">
        <p className="mb-2 text-sm font-semibold uppercase tracking-[0.24em] text-cyan-300">
          Mission health overview
        </p>
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">ASTRAVITAL</h1>
        <p className="mt-4 max-w-3xl text-slate-300">
          An offline-first, explainable decision-support prototype. Synthetic preview data only;
          not a diagnosis or validated risk prediction.
        </p>
      </header>

      <section aria-labelledby="snapshot-heading">
        <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 id="snapshot-heading" className="text-2xl font-semibold">Crew snapshot</h2>
            <p className="text-slate-400">Synthetic Crew A · simulated mission day 42</p>
          </div>
          <span className="rounded-full border border-cyan-900 bg-cyan-950 px-3 py-1 text-sm text-cyan-200">
            Local mode
          </span>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {cards.map(([label, value]) => (
            <article key={label} className="rounded-xl border border-slate-800 bg-slate-900 p-5">
              <h3 className="text-sm font-medium text-slate-400">{label}</h3>
              <p className="mt-2 text-2xl font-semibold">{value}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="mt-8 grid gap-6 lg:grid-cols-[2fr_1fr]">
        <article className="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <h2 className="text-xl font-semibold">Recent observations</h2>
          <p className="mb-3 text-sm text-slate-400">Synthetic chart · descriptive only</p>
          <MeasurementPreview />
        </article>
        <aside className="rounded-xl border border-amber-900/70 bg-amber-950/30 p-5">
          <h2 className="text-xl font-semibold text-amber-100">Data completeness</h2>
          <p className="mt-3 text-amber-50/80">
            Fatigue was not reported in the latest synthetic check-in. It remains absent and is
            not interpreted as a normal result.
          </p>
        </aside>
      </section>
    </main>
  );
}

