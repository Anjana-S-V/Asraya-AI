
"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

const API_URL = "http://127.0.0.1:8000";

type RiskData = {
  district: string;
  date: string;
  risk_category: string;
  risk_score: number;
  rainfall: {
    "1_day_mm": number;
    "3_day_mm": number;
    "7_day_mm": number;
    "30_day_mm": number;
  };
  explanation?: string;
  disclaimer?: string;
};

const suggestedQuestions = [
  "What should I do before a flood?",
  "What should I do during flooding?",
  "How should I prepare my family?",
];

function getRiskStyle(category: string) {
  switch (category) {
    case "VERY HIGH":
      return {
        badge: "bg-red-100 text-red-700 border-red-200",
        bar: "bg-red-500",
      };
    case "HIGH":
      return {
        badge: "bg-orange-100 text-orange-700 border-orange-200",
        bar: "bg-orange-500",
      };
    case "MODERATE":
      return {
        badge: "bg-yellow-100 text-yellow-700 border-yellow-200",
        bar: "bg-yellow-500",
      };
    default:
      return {
        badge: "bg-green-100 text-green-700 border-green-200",
        bar: "bg-green-500",
      };
  }
}

function RainfallCard({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-bold text-slate-900">
        {value.toFixed(1)}
        <span className="ml-1 text-sm font-medium text-slate-500">mm</span>
      </p>
    </div>
  );
}

function ProcessStep({
  number,
  title,
  description,
}: {
  number: string;
  title: string;
  description: string;
}) {
  return (
    <div className="relative">
      <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-full bg-slate-900 text-sm font-bold text-white">
        {number}
      </div>

      <h3 className="text-lg font-bold text-slate-900">{title}</h3>

      <p className="mt-2 text-sm leading-6 text-slate-600">
        {description}
      </p>
    </div>
  );
}

export default function Home() {
  const [districts, setDistricts] = useState<string[]>([]);
  const [district, setDistrict] = useState("");
  const [date, setDate] = useState("");

  const [risk, setRisk] = useState<RiskData | null>(null);
  const [question, setQuestion] = useState("");
  const [guidance, setGuidance] = useState("");

  const [loadingRisk, setLoadingRisk] = useState(false);
  const [loadingGuidance, setLoadingGuidance] = useState(false);

  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDistricts() {
      try {
        const response = await fetch(`${API_URL}/districts`);

        if (!response.ok) {
          throw new Error("Failed to load districts");
        }

        const data = await response.json();

        setDistricts(data.districts || []);

        if (data.districts?.length > 0) {
          setDistrict(data.districts[0]);
        }
      } catch {
        setError(
          "Unable to connect to Āśraya AI. Make sure the backend server is running."
        );
      }
    }

    loadDistricts();
  }, []);

  async function assessRisk() {
    if (!district || !date) {
      setError("Please select a district and date.");
      return;
    }

    setLoadingRisk(true);
    setError("");
    setRisk(null);
    setGuidance("");

    try {
      const response = await fetch(
        `${API_URL}/risk?district=${encodeURIComponent(
          district
        )}&date=${encodeURIComponent(date)}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to assess flood risk.");
      }

      setRisk(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to assess flood risk."
      );
    } finally {
      setLoadingRisk(false);
    }
  }

  async function getGuidance(customQuestion?: string) {
    const finalQuestion = customQuestion || question;

    if (!finalQuestion.trim()) {
      setError("Please enter a question.");
      return;
    }

    setLoadingGuidance(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/guidance`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: finalQuestion,
          district: district || null,
          date: date || null,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to generate guidance.");
      }

      setGuidance(data.answer || data.guidance || "");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to generate AI guidance."
      );
    } finally {
      setLoadingGuidance(false);
    }
  }

  const riskStyle = risk
    ? getRiskStyle(risk.risk_category)
    : getRiskStyle("LOW");

  const riskPercentage = risk
    ? Math.min(Math.max(risk.risk_score * 100, 0), 100)
    : 0;

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
          <div>
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-lg font-bold text-white">
                Ā
              </div>

              <div>
                <h1 className="text-xl font-bold tracking-tight">
                  Āśraya AI
                </h1>

                <p className="text-xs text-slate-500">
                  Community Disaster Resilience Platform
                </p>
              </div>
            </div>
          </div>

          <div className="hidden text-right sm:block">
            <p className="text-sm font-semibold text-slate-700">
              Prepare. Protect. Recover.
            </p>

            <p className="text-xs text-slate-500">
              Flood risk assessment & preparedness
            </p>
          </div>
        </div>
      </header>

      {/* Main */}
      <div className="mx-auto max-w-6xl px-6 py-10">
        {/* Hero */}
        <section className="mb-10">
          <div className="max-w-3xl">
            <p className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-500">
              Flood Risk Assessment
            </p>

            <h2 className="text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
              Understand flood risk.
              <br />
              Prepare with confidence.
            </h2>

            <p className="mt-4 max-w-2xl text-base leading-7 text-slate-600">
              Select a Kerala district and date to view a model-derived
              historical flood-risk assessment based on rainfall patterns.
            </p>
          </div>
        </section>

        {/* Assessment Input */}
        <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <div className="grid gap-6 md:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">
                District
              </label>

              <select
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
              >
                {districts.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">
                Date
              </label>

              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
              />
            </div>
          </div>

          <button
            onClick={assessRisk}
            disabled={loadingRisk}
            className="mt-6 w-full rounded-xl bg-slate-900 px-5 py-3.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60 md:w-auto"
          >
            {loadingRisk ? "Assessing..." : "Assess Flood Risk"}
          </button>
        </section>

        {/* Error */}
        {error && (
          <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Risk Assessment */}
        {risk && (
          <section className="mt-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
            <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">
                  Assessment
                </p>

                <h2 className="mt-1 text-2xl font-bold text-slate-950">
                  {risk.district}
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  {new Date(`${risk.date}T00:00:00`).toLocaleDateString(
                    "en-IN",
                    {
                      day: "numeric",
                      month: "long",
                      year: "numeric",
                    }
                  )}
                </p>
              </div>

              <div
                className={`rounded-full border px-4 py-2 text-sm font-bold ${riskStyle.badge}`}
              >
                {risk.risk_category}
              </div>
            </div>

            {/* Risk Score */}
            <div className="mt-8 rounded-2xl bg-slate-50 p-6">
              <div className="flex items-end justify-between gap-4">
                <div>
                  <p className="text-sm font-medium text-slate-500">
                    Model Risk Score
                  </p>

                  <p className="mt-1 text-4xl font-bold tracking-tight text-slate-950">
                    {riskPercentage.toFixed(1)}%
                  </p>
                </div>

                <p className="max-w-xs text-right text-xs leading-5 text-slate-500">
                  Model-derived score based on historical rainfall patterns.
                </p>
              </div>

              <div className="mt-5 h-2 overflow-hidden rounded-full bg-slate-200">
                <div
                  className={`h-full rounded-full transition-all ${riskStyle.bar}`}
                  style={{ width: `${riskPercentage}%` }}
                />
              </div>

              <p className="mt-3 text-xs leading-5 text-slate-500">
                This score is not a calibrated probability and should not be
                interpreted as the exact chance of flooding.
              </p>
            </div>

            {/* Rainfall */}
            <div className="mt-8">
              <div className="mb-4">
                <h3 className="text-lg font-bold text-slate-900">
                  Rainfall indicators
                </h3>

                <p className="mt-1 text-sm text-slate-500">
                  Rainfall accumulated through the selected date.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                <RainfallCard
                  label="1 Day"
                  value={risk.rainfall["1_day_mm"]}
                />

                <RainfallCard
                  label="3 Days"
                  value={risk.rainfall["3_day_mm"]}
                />

                <RainfallCard
                  label="7 Days"
                  value={risk.rainfall["7_day_mm"]}
                />

                <RainfallCard
                  label="30 Days"
                  value={risk.rainfall["30_day_mm"]}
                />
              </div>
            </div>

            {/* Disclaimer */}
            <div className="mt-8 border-t border-slate-200 pt-6">
              <p className="text-xs leading-5 text-slate-500">
                This is a model-derived historical risk assessment and should
                not be interpreted as an official government warning or
                evacuation order. For emergencies, follow instructions from
                local authorities and official emergency services.
              </p>
            </div>
          </section>
        )}

        {/* AI Assistant */}
        {risk && (
          <section className="mt-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
            <div className="max-w-2xl">
              <p className="text-sm font-semibold uppercase tracking-wider text-slate-500">
                AI Preparedness Assistant
              </p>

              <h2 className="mt-2 text-2xl font-bold text-slate-950">
                What should I do?
              </h2>

              <p className="mt-2 text-sm leading-6 text-slate-600">
                Ask Āśraya AI about flood preparedness, safety, or recovery.
                Your selected district and risk assessment are included as
                context when available.
              </p>
            </div>

            {/* Suggested questions */}
            <div className="mt-6 flex flex-wrap gap-2">
              {suggestedQuestions.map((item) => (
                <button
                  key={item}
                  onClick={() => {
                    setQuestion(item);
                    getGuidance(item);
                  }}
                  className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm text-slate-700 transition hover:border-slate-500 hover:bg-slate-50"
                >
                  {item}
                </button>
              ))}
            </div>

            {/* Question */}
            <div className="mt-5">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask Āśraya AI about flood preparedness..."
                rows={4}
                className="w-full resize-none rounded-2xl border border-slate-300 px-4 py-4 text-sm outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
              />

              <button
                onClick={() => getGuidance()}
                disabled={loadingGuidance}
                className="mt-3 rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loadingGuidance ? "Generating guidance..." : "Get AI Guidance"}
              </button>
            </div>

            {/* AI response */}
            {guidance && (
              <div className="mt-8 rounded-2xl border border-slate-200 bg-slate-50 p-6">
                <div className="mb-5 border-b border-slate-200 pb-4">
                  <p className="text-sm font-semibold text-slate-500">
                    Āśraya AI Response
                  </p>
                </div>

                <article className="prose prose-slate max-w-none text-sm leading-7">
                  <ReactMarkdown
                    components={{
                      h1: ({ children }) => (
                        <h1 className="mb-4 mt-6 text-2xl font-bold text-slate-950 first:mt-0">
                          {children}
                        </h1>
                      ),

                      h2: ({ children }) => (
                        <h2 className="mb-3 mt-6 text-xl font-bold text-slate-950">
                          {children}
                        </h2>
                      ),

                      h3: ({ children }) => (
                        <h3 className="mb-2 mt-5 text-lg font-bold text-slate-950">
                          {children}
                        </h3>
                      ),

                      p: ({ children }) => (
                        <p className="mb-4 leading-7 text-slate-700">
                          {children}
                        </p>
                      ),

                      strong: ({ children }) => (
                        <strong className="font-semibold text-slate-950">
                          {children}
                        </strong>
                      ),

                      ul: ({ children }) => (
                        <ul className="mb-5 list-disc space-y-2 pl-6 text-slate-700">
                          {children}
                        </ul>
                      ),

                      ol: ({ children }) => (
                        <ol className="mb-5 list-decimal space-y-2 pl-6 text-slate-700">
                          {children}
                        </ol>
                      ),

                      li: ({ children }) => (
                        <li className="leading-7">{children}</li>
                      ),

                      hr: () => (
                        <hr className="my-6 border-slate-200" />
                      ),
                    }}
                  >
                    {guidance}
                  </ReactMarkdown>
                </article>
              </div>
            )}
          </section>
        )}

        {/* How it works */}
        <section className="mt-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <div className="max-w-2xl">
            <p className="text-sm font-semibold uppercase tracking-wider text-slate-500">
              How Āśraya works
            </p>

            <h2 className="mt-2 text-2xl font-bold text-slate-950">
              From historical data to practical guidance
            </h2>
          </div>

          <div className="mt-8 grid gap-8 md:grid-cols-3">
            <ProcessStep
              number="01"
              title="Assess"
              description="Historical rainfall data is analyzed to estimate the likelihood of a recorded flood onset on the following day."
            />

            <ProcessStep
              number="02"
              title="Understand"
              description="Rainfall indicators and historical patterns provide context for the model-derived risk assessment."
            />

            <ProcessStep
              number="03"
              title="Prepare"
              description="A retrieval-augmented AI assistant provides practical flood preparedness and safety guidance."
            />
          </div>
        </section>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-6">
          <div className="flex flex-col gap-3 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between">
            <p>
              Āśraya AI — AI-Driven Community Disaster Resilience Platform
            </p>

            <p>
              For emergencies, follow instructions from local authorities and
              official emergency services.
            </p>
          </div>
        </div>
      </footer>
    </main>
  );
}

