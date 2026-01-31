import express from "express";
import { pool } from "../db.js";
const router = express.Router();

router.post("/", async (req, res) => {
  const { substrate_type, substrate_moisture_percent, spawn_rate_percent, start_date } = req.body;
  const result = await pool.query(
    `INSERT INTO batches(user_id, substrate_type, substrate_moisture_percent, spawn_rate_percent, start_date)
     VALUES($1,$2,$3,$4,$5) RETURNING *`,
    [req.userId, substrate_type, substrate_moisture_percent, spawn_rate_percent, start_date]
  );
  res.json(result.rows[0]);
});

router.get("/", async (req, res) => {
  const result = await pool.query(
    "SELECT * FROM batches WHERE user_id=$1 ORDER BY start_date DESC",
    [req.userId]
  );
  res.json(result.rows);
});

export default router;
