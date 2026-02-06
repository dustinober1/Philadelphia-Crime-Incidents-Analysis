"use client";

import { FormEvent, useState } from "react";

export function QuestionForm() {
  const [status, setStatus] = useState<string>("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const payload = {
      name: String(formData.get("name") || ""),
      email: String(formData.get("email") || "") || null,
      question_text: String(formData.get("question") || ""),
      honeypot: String(formData.get("company") || ""),
    };

    const response = await fetch("/api/v1/questions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      setStatus("Thanks! Your question has been submitted and we'll answer it soon.");
      event.currentTarget.reset();
    } else {
      const data = await response.json().catch(() => ({}));
      setStatus(data.detail ?? "Submission failed.");
    }
  }

  return (
    <form onSubmit={onSubmit} className="card grid gap-3">
      <label className="text-sm">Name<input required name="name" className="mt-1 w-full rounded border px-3 py-2" /></label>
      <label className="text-sm">Email (optional)<input name="email" type="email" className="mt-1 w-full rounded border px-3 py-2" /></label>
      <label className="text-sm">Question<textarea required name="question" maxLength={1000} rows={5} className="mt-1 w-full rounded border px-3 py-2" /></label>
      <input name="company" className="hidden" tabIndex={-1} autoComplete="off" />
      <button className="w-fit rounded bg-slate-900 px-4 py-2 text-white">Submit Question</button>
      {status && <p className="text-sm text-slate-600">{status}</p>}
    </form>
  );
}
