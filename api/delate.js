import { loadKeys, saveKeys } from "./helpers";

export default function handler(req, res) {
  if (req.method !== "DELETE") return res.status(405).json({ error: "Method not allowed" });

  const { key } = req.body || {};
  if (!key) return res.status(400).json({ error: "Missing key" });

  let keys = loadKeys();
  const exists = keys.find(k => k.key === key);
  if (!exists) return res.status(404).json({ error: "Key not found" });

  keys = keys.filter(k => k.key !== key);
  saveKeys(keys);

  res.status(200).json({ message: "Deleted", key });
}
