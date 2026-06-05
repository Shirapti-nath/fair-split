import { useState } from "react";

const API_URL = import.meta.env.VITE_API_URL ?? "";

type PerPerson = {
  name: string;
  items: string[];
  subtotal: number;
  tax_share: number;
  service_share: number;
  discount_share: number;
  total: number;
};

type SettleUp = { from: string; to: string; amount: number };

type SplitResult = {
  per_person: PerPerson[];
  grand_total: number;
  reconciliation: { sum_of_person_totals: number; matches_bill: boolean };
  paid_by: string;
  settle_up: SettleUp[];
  assumptions: string[];
  flags: string[];
};

function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      const base64 = result.includes(",") ? result.split(",")[1] : result;
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

export default function App() {
  const [description, setDescription] = useState(
    "Three of us — Ravi, Neha, Sameer. Ravi had the cappuccino and the sandwich. Neha had the pasta and the lime soda. Sameer had the brownie. Sameer paid."
  );
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SplitResult | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const receipt_base64 = file ? await fileToBase64(file) : "";
      const base = API_URL.replace(/\/$/, "");
      const url = base ? `${base}/split` : "/split";
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ receipt_base64, description }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || res.statusText);
      }
      const data = (await res.json()) as SplitResult;
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  function loadFixture(id: string) {
    setDescription(`fixture:${id}`);
    setFile(null);
  }

  return (
    <main>
      <h1>Fair Split</h1>
      <p className="subtitle">
        Upload a receipt, describe who had what, get a fair per-person breakdown.
      </p>

      <form className="card" onSubmit={handleSubmit}>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="receipt">Receipt image</label>
          <input
            id="receipt"
            type="file"
            accept="image/*"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
          <p style={{ fontSize: "0.85rem", color: "#666", marginTop: "0.35rem" }}>
            Or test without OCR:{" "}
            {(["R1", "R2", "R3", "R4"] as const).map((id) => (
              <button
                key={id}
                type="button"
                style={{
                  marginRight: "0.35rem",
                  background: "#e5e7eb",
                  color: "#111",
                  padding: "0.2rem 0.5rem",
                  fontSize: "0.8rem",
                }}
                onClick={() => loadFixture(id)}
              >
                {id}
              </button>
            ))}
          </p>
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="desc">Who had what</label>
          <textarea
            id="desc"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Splitting…" : "Split bill"}
        </button>
      </form>

      {error && (
        <p className="error card" role="alert">
          {error}
        </p>
      )}

      {result && (
        <>
          <div className="card">
            <p>
              <strong>Grand total:</strong> ₹{result.grand_total}{" "}
              {result.paid_by && (
                <>
                  · <strong>Paid by:</strong> {result.paid_by}
                </>
              )}
            </p>
            <p>
              Reconciliation: ₹{result.reconciliation.sum_of_person_totals}{" "}
              {result.reconciliation.matches_bill ? "matches bill" : "does NOT match bill"}
            </p>
          </div>

          <div className="card" style={{ overflowX: "auto" }}>
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Items</th>
                  <th>Subtotal</th>
                  <th>Tax</th>
                  <th>Service</th>
                  <th>Discount</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {result.per_person.map((p) => (
                  <tr key={p.name}>
                    <td>{p.name}</td>
                    <td>{p.items.join(", ")}</td>
                    <td>₹{p.subtotal}</td>
                    <td>₹{p.tax_share}</td>
                    <td>₹{p.service_share}</td>
                    <td>₹{p.discount_share}</td>
                    <td>
                      <strong>₹{p.total}</strong>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {result.settle_up.length > 0 && (
            <div className="card">
              <h3>Settle up</h3>
              <ul className="settle">
                {result.settle_up.map((s, i) => (
                  <li key={i}>
                    <strong>{s.from}</strong> → <strong>{s.to}</strong>: ₹{s.amount}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.flags.length > 0 && (
            <div className="flags card">
              <h3>Flags</h3>
              <ul>
                {result.flags.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            </div>
          )}

          {result.assumptions.length > 0 && (
            <div className="card assumptions">
              <h3>Assumptions</h3>
              <ul>
                {result.assumptions.map((a, i) => (
                  <li key={i}>{a}</li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}
    </main>
  );
}
