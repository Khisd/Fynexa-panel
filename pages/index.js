import { useState, useEffect } from "react";

export default function Home() {
  const [keys, setKeys] = useState([]);
  const [days, setDays] = useState(30);
  const [newKey, setNewKey] = useState(null);

  async function fetchKeys() {
    const res = await fetch("/api/keys");
    const data = await res.json();
    setKeys(data);
  }

  async function generateKey() {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ days: Number(days) }),
    });
    const data = await res.json();
    setNewKey(data);
    fetchKeys();
  }

  async function deleteKey(key) {
    await fetch("/api/delete", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key }),
    });
    fetchKeys();
  }

  useEffect(() => {
    fetchKeys();
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6 font-mono">
      <h1 className="text-3xl mb-4">Key Generator</h1>

      <div className="mb-4 flex items-center gap-2">
        <input
          type="number"
          value={days}
          onChange={(e) => setDays(e.target.value)}
          className="bg-gray-800 text-white p-2 rounded w-20"
        />
        <button
          onClick={generateKey}
          className="bg-blue-600 hover:bg-blue-700 p-2 rounded"
        >
          Generate Key
        </button>
      </div>

      {newKey && (
        <div className="mb-4 p-2 bg-gray-800 rounded">
          <strong>New Key:</strong> {newKey.key} <br />
          <strong>Expires:</strong> {newKey.expiry}
        </div>
      )}

      <h2 className="text-2xl mb-2">All Keys</h2>
      <div className="space-y-2">
        {keys.map((k) => (
          <div
            key={k.key}
            className="flex justify-between items-center p-2 bg-gray-800 rounded"
          >
            <div>
              <div>{k.key}</div>
              <div className="text-gray-400 text-sm">{k.expiry}</div>
            </div>
            <button
              onClick={() => deleteKey(k.key)}
              className="bg-red-600 hover:bg-red-700 p-1 rounded"
            >
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
