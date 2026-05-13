export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 p-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight text-white">Monarqhs Analytics</h1>
        <p className="mt-3 text-lg text-slate-400">
          Personal investor/trader dashboard — IDX &amp; US markets
        </p>
      </div>

      <div className="mt-4 flex gap-3">
        <span className="rounded-full bg-emerald-900/50 px-3 py-1 text-xs font-medium text-emerald-400 ring-1 ring-emerald-800">
          Phase 1 — Foundation
        </span>
        <span className="rounded-full bg-slate-800 px-3 py-1 text-xs font-medium text-slate-400 ring-1 ring-slate-700">
          Dashboard coming soon
        </span>
      </div>

      <ApiStatus />
    </main>
  );
}

async function ApiStatus() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  let status = "unreachable";
  try {
    const res = await fetch(`${apiUrl}/health`, {
      next: { revalidate: 30 },
    });
    if (res.ok) {
      const data = await res.json();
      status = data.status ?? "unknown";
    }
  } catch {
    // API cold start or not yet deployed
  }

  return (
    <div className="mt-2 flex items-center gap-2 text-sm text-slate-500">
      <span
        className={`h-2 w-2 rounded-full ${status === "ok" ? "bg-emerald-500" : "bg-red-500"}`}
      />
      <span>API: {status}</span>
    </div>
  );
}
