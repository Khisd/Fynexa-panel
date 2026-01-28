import { v4 as uuidv4 } from "uuid";
import { loadKeys, saveKeys } from "./helpers";

export default function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  const { days = 30 } = req.body || {};
  const key = uuidv4();
  const expiry = new Date();
  expiry.setDate(expiry.getDate() + days);

  const keys = loadKeys();
  keys.push({ key, expiry: expiry.toISOString() });
  saveKeys(keys);

  res.status(200).json({ key, expiry: expiry.toISOString() });
}
