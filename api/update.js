import { loadKeys, saveKeys } from "./helpers";

export default function handler(req, res) {
  if (req.method !== "PUT") return res.status(405).json({ error: "Method not allowed" });

  const { key, days } = req.body || {};
  if (!key || !days) return res.status(400).json({ error: "Missing key or days" });

  const keys = loadKeys();
  const k = keys.find(k => k.key === key);
  if (!k) return res.status(404).json({ error: "Key not found" });

  const expiry = new Date();
  expiry.setDate(expiry.getDate() + days);
  k.expiry = expiry.toISOString();
  saveKeys(keys);

  res.status(200).json({ message: "Updated", key: k.key, expiry: k.expiry });
}
