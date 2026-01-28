import { loadKeys } from "./helpers";

export default function handler(req, res) {
  if (req.method !== "GET") return res.status(405).json({ error: "Method not allowed" });
  const keys = loadKeys();
  res.status(200).json(keys);
}
