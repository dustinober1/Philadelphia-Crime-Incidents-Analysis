"use client";

import { FormEvent, useState } from "react";
import useSWR from "swr";

import type { QuestionItem } from "@/lib/api";

async function adminFetcher([path, token]: [string, string]) {
  const response = await fetch(path, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.message ?? "Admin request failed");
  }
  return response.json();
}

export default function AdminPage() {
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  const [authError, setAuthError] = useState("");
  const [answerById, setAnswerById] = useState<Record<string, string>>({});
  const { data: pending = [], mutate } = useSWR<QuestionItem[]>(
    token ? ["/api/v1/questions?status=pending", token] : null,
    adminFetcher,
  );

  async function onLogin(event: FormEvent) {
    event.preventDefault();
    setAuthError("");
    const response = await fetch("/api/v1/questions/admin/session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      setAuthError(payload.message ?? "Invalid credentials");
      return;
    }
    const payload = (await response.json()) as { token: string };
    setToken(payload.token);
    setPassword("");
  }

  async function publish(id: string) {
    const answerText = answerById[id] || "";
    const response = await fetch(`/api/v1/questions/${id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ answer_text: answerText, status: "answered" }),
    });
    if (response.ok) {
      mutate();
    }
  }

  async function remove(id: string) {
    const response = await fetch(`/api/v1/questions/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (response.ok) {
      mutate();
    }
  }

  if (!token) {
    return (
      <form onSubmit={onLogin} className="card mx-auto max-w-md space-y-3">
        <h1 className="text-xl font-semibold">Admin Login</h1>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full rounded border px-3 py-2"
          required
        />
        {authError && <p className="text-sm text-red-700">{authError}</p>}
        <button className="rounded bg-slate-900 px-4 py-2 text-white">Enter</button>
      </form>
    );
  }

  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Admin Questions</h1>
      {pending.map((q) => (
        <article key={q.id} className="card space-y-2">
          <p className="font-medium">{q.question_text}</p>
          <textarea
            rows={4}
            value={answerById[q.id] ?? ""}
            onChange={(e) => setAnswerById((prev) => ({ ...prev, [q.id]: e.target.value }))}
            className="w-full rounded border px-3 py-2"
            placeholder="Write answer..."
          />
          <div className="flex gap-2">
            <button onClick={() => publish(q.id)} className="rounded bg-blue-700 px-3 py-2 text-white">
              Publish Answer
            </button>
            <button onClick={() => remove(q.id)} className="rounded bg-red-700 px-3 py-2 text-white">
              Delete
            </button>
          </div>
        </article>
      ))}
    </div>
  );
}
