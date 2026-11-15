
"use client";

import { useEffect, useState } from "react";
import { MeasurementPreview } from "../components/MeasurementPreview";
import {
  getAstronautMeasurements,
  getAstronautAssessments,
  createAstronautAssessment,
  getAstronautCheckins,
} from "../services/api";

const ASTRONAUT_ID = "2ed59a65-3aee-59ca-bf36-2e51cde454a5";

type Measurement = {
  id: string;
  measured_at: string;
  metric: string;
  value: number;
  unit: string;
  source: string | null;
  astronaut_id: string;
};

type Finding = {
  code: string;
  title: string;
  detail: string;
  evidence: string[];
  data_status: string;
};

type GuidanceAction = {
  id: string;
  title: string;
  rationale: string;
  evidence_links: string[];
  urgency: string;
};

type Checkin = {
  id: string;
  astronaut_id: string;
  recorded_at: string;
  mood: string | number | null;
  fatigue: string | number | null;
  notes: string | null;
};

type Assessment = {
  id: string;
  astronaut_id: string;
  created_at: string;
  findings: Finding[];
  guidance_actions: GuidanceAction[];
  summary: string;
  disclaimer?: string;
};

const navigation = [
  { label: "Overview", href: "#overview", icon: "◫" },
  { label: "Measurements", href: "/measurements", icon: "♡" },
  { label: "Health Trends", href: "#trends", icon: "⌁" },
  { label: "Health Notes", href: "#health-notes", icon: "▤" },
  { label: "Health Assessment", href: "#assessment", icon: "✦" },
];

export default function Home() {
  const [measurements, setMeasurements] = useState<Measurement[]>([]);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [checkins, setCheckins] = useState<Checkin[]>([]);
  const [loading, setLoading] = useState(true);
  const [assessmentLoading, setAssessmentLoading] = useState(true);
  const [error, setError] = useState("");
  const [assessmentError, setAssessmentError] = useState("");
  const [checkinLoading, setCheckinLoading] = useState(true);
  const [checkinError, setCheckinError] = useState("");
  const [generating, setGenerating] = useState(false);
  const [generationMessage, setGenerationMessage] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        const data: Measurement[] =
          await getAstronautMeasurements(ASTRONAUT_ID);
        setMeasurements(data);
      } catch (err) {
        console.error("Error loading measurements:", err);
        setError("Unable to load measurements from the backend.");
      } finally {
        setLoading(false);
      }

      try {
        const data: Assessment[] =
          await getAstronautAssessments(ASTRONAUT_ID);
        setAssessments(data);
      } catch (err) {
        console.error("Error loading assessments:", err);
        setAssessmentError("Unable to load health assessments.");
      } finally {
        setAssessmentLoading(false);
      }

      try {
        const data: Checkin[] = await getAstronautCheckins(ASTRONAUT_ID);
        setCheckins(data);
      } catch (err) {
        console.error("Error loading check-ins:", err);
        setCheckinError("Unable to load health notes from the backend.");
      } finally {
        setCheckinLoading(false);
      }
    }

    loadDashboard();
  }, []);

  function getLatestValue(metricName: string): number | null {
    const matchingMeasurements = measurements
      .filter((item) => item.metric === metricName)
      .sort(
        (a, b) =>
          new Date(b.measured_at).getTime() -
          new Date(a.measured_at).getTime()
      );

    return matchingMeasurements.length > 0
      ? matchingMeasurements[0].value
      : null;
  }

  const heartRate = getLatestValue("resting_heart_rate");
  const sleep = getLatestValue("sleep_hours");
  const temperature = getLatestValue("body_temperature");
  const systolic = getLatestValue("blood_pressure_systolic");
  const diastolic = getLatestValue("blood_pressure_diastolic");

  const metrics = [
    {
      label: "Resting Heart Rate",
      value: heartRate !== null ? String(heartRate) : "--",
      unit: "bpm",
      icon: "♡",
      description: "Latest recorded measurement",
    },
    {
      label: "Sleep Duration",
      value: sleep !== null ? String(sleep) : "--",
      unit: "hours",
      icon: "◷",
      description: "Last sleep period",
    },
    {
      label: "Body Temperature",
      value: temperature !== null ? String(temperature) : "--",
      unit: "°C",
      icon: "♧",
      description: "Latest recorded measurement",
    },
    {
      label: "Blood Pressure",
      value:
        systolic !== null && diastolic !== null
          ? `${systolic}/${diastolic}`
          : "--/--",
      unit: "mmHg",
      icon: "⌁",
      description: "Systolic / Diastolic",
    },
  ];

  const latestAssessment = assessments.length > 0
    ? [...assessments].sort(
        (a, b) =>
          new Date(b.created_at).getTime() -
          new Date(a.created_at).getTime()
      )[0]
    : null;

  const latestCheckin = checkins.length > 0
    ? [...checkins].sort(
        (a, b) =>
          new Date(b.recorded_at).getTime() -
          new Date(a.recorded_at).getTime()
      )[0]
    : null;

  const missingCheckinFields = latestCheckin
    ? [latestCheckin.mood, latestCheckin.fatigue, latestCheckin.notes].filter(
        (value) => value === null || value === undefined || value === ""
      ).length
    : null;

  async function handleGenerateAssessment() {
    try {
      setGenerating(true);
      setGenerationMessage("");
      setAssessmentError("");

      const newAssessment: Assessment =
        await createAstronautAssessment(ASTRONAUT_ID);

      setAssessments((current) => [newAssessment, ...current]);
      setGenerationMessage("New health assessment generated successfully.");
    } catch (err) {
      console.error("Error generating assessment:", err);
      setGenerationMessage(
        "Unable to generate a new assessment. Please try again."
      );
    } finally {
      setGenerating(false);
    }
  }

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
          <p className="mt-1 text-xs text-slate-400">Mission Day 42</p>
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

          {loading && (
            <p className="mb-4 text-sm text-cyan-300">
              Loading measurements...
            </p>
          )}

          {error && (
            <p className="mb-4 rounded-xl border border-red-800 bg-red-950/40 p-4 text-sm text-red-200">
              {error}
            </p>
          )}

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
                Resting heart rate · Backend measurements
              </p>
            </div>

            <MeasurementPreview measurements={measurements} />
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

            {checkinLoading && (
              <p className="mt-5 text-sm text-amber-100/70">
                Loading health check-ins...
              </p>
            )}

            {checkinError && (
              <p className="mt-5 rounded-xl border border-red-800 bg-red-950/40 p-3 text-sm text-red-200">
                {checkinError}
              </p>
            )}

            {!checkinLoading && !checkinError && !latestCheckin && (
              <p className="mt-5 text-sm leading-7 text-amber-50/80">
                No health check-in has been recorded yet.
              </p>
            )}

            {!checkinLoading && !checkinError && latestCheckin && (
              <div className="mt-5 space-y-3 text-sm text-amber-50/80">
                <p className="text-xs text-amber-200/60">
                  Latest check-in: {new Date(latestCheckin.recorded_at).toLocaleString()}
                </p>
                <p>
                  <span className="font-semibold text-amber-100">Mood: </span>
                  {latestCheckin.mood ?? "Not reported"}
                </p>
                <p>
                  <span className="font-semibold text-amber-100">Fatigue: </span>
                  {latestCheckin.fatigue ?? "Not reported"}
                </p>
                <div>
                  <p className="font-semibold text-amber-100">Notes:</p>
                  <p className="mt-1 whitespace-pre-wrap">
                    {latestCheckin.notes || "No notes provided."}
                  </p>
                </div>
              </div>
            )}

            <div className="mt-5 border-t border-amber-900/50 pt-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-amber-300">
                Data completeness
              </p>
              <p className="mt-2 text-sm text-amber-100/70">
                {checkinLoading
                  ? "Checking available self-report fields..."
                  : checkinError
                    ? "Completeness information is unavailable."
                    : !latestCheckin
                      ? "No self-report data is available."
                      : missingCheckinFields === 0
                        ? "All displayed self-report fields are provided."
                        : `${missingCheckinFields} of 3 self-report fields are missing.`}
              </p>
            </div>
          </article>
        </section>

        {/* HEALTH ASSESSMENT */}
        <section
          id="assessment"
          className="mt-9 rounded-2xl border border-cyan-900/50 bg-slate-900 p-5 sm:p-6"
        >
          <div className="mb-6">
            <p className="text-xs font-semibold uppercase tracking-widest text-cyan-400">
              Analytics & Health Assistant
            </p>
            <h3 className="mt-2 text-2xl font-bold">
              Health Assessment
            </h3>
            <p className="mt-2 text-sm text-slate-400">
              Descriptive findings and guidance generated by the backend.
            </p>
          </div>

          <div className="mb-6 flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={handleGenerateAssessment}
              disabled={generating}
              className="rounded-xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {generating ? "Generating..." : "Generate New Assessment"}
            </button>

            {generationMessage && (
              <p
                role="status"
                className={`text-sm ${
                  generationMessage.startsWith("Unable")
                    ? "text-red-300"
                    : "text-emerald-300"
                }`}
              >
                {generationMessage}
              </p>
            )}
          </div>

          {assessmentLoading && (
            <p className="text-sm text-cyan-300">
              Loading health assessment...
            </p>
          )}

          {assessmentError && (
            <p className="rounded-xl border border-red-800 bg-red-950/40 p-4 text-sm text-red-200">
              {assessmentError}
            </p>
          )}

          {!assessmentLoading && !assessmentError && !latestAssessment && (
            <p className="rounded-xl border border-slate-700 bg-slate-950 p-4 text-sm text-slate-400">
              No assessment is available yet. Generate an assessment through
              the backend first.
            </p>
          )}

          {latestAssessment && (
            <div className="space-y-6">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Latest assessment
                </p>
                <p className="mt-2 text-sm text-slate-300">
                  {new Date(latestAssessment.created_at).toLocaleString()}
                </p>
                <p className="mt-3 text-sm leading-6 text-slate-300">
                  {latestAssessment.summary}
                </p>
              </div>

              <div>
                <h4 className="mb-3 font-semibold text-cyan-300">
                  Analytics Findings
                </h4>

                <div className="space-y-3">
                  {latestAssessment.findings.map((finding) => (
                    <article
                      key={finding.code}
                      className="rounded-xl border border-slate-700 bg-slate-950 p-4"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <h5 className="font-semibold text-white">
                          {finding.title}
                        </h5>
                        <span className="rounded-full bg-cyan-400/10 px-3 py-1 text-xs text-cyan-300">
                          {finding.data_status}
                        </span>
                      </div>

                      <p className="mt-2 text-sm leading-6 text-slate-400">
                        {finding.detail}
                      </p>

                      {finding.evidence.length > 0 && (
                        <ul className="mt-3 space-y-1">
                          {finding.evidence.map((item, index) => (
                            <li
                              key={index}
                              className="text-xs text-slate-500"
                            >
                              • {item}
                            </li>
                          ))}
                        </ul>
                      )}
                    </article>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="mb-3 font-semibold text-emerald-300">
                  Health Assistant Guidance
                </h4>

                <div className="space-y-3">
                  {latestAssessment.guidance_actions.map((action) => (
                    <article
                      key={action.id}
                      className="rounded-xl border border-emerald-900/50 bg-emerald-950/20 p-4"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <h5 className="font-semibold text-emerald-100">
                          {action.title}
                        </h5>
                        <span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs text-emerald-300">
                          {action.urgency}
                        </span>
                      </div>

                      <p className="mt-2 text-sm leading-6 text-emerald-50/70">
                        {action.rationale}
                      </p>

                      {action.evidence_links.length > 0 && (
                        <p className="mt-3 text-xs text-emerald-200/50">
                          Evidence: {action.evidence_links.join(", ")}
                        </p>
                      )}
                    </article>
                  ))}
                </div>
              </div>

              {latestAssessment.disclaimer && (
                <div className="rounded-xl border border-amber-900/50 bg-amber-950/20 p-4">
                  <p className="text-xs leading-6 text-amber-200/80">
                    {latestAssessment.disclaimer}
                  </p>
                </div>
              )}
            </div>
          )}
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
