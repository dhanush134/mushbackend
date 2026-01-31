import express from "express";
import { pool } from "../db.js";

const router = express.Router();

router.get("/:batchId", async (req, res) => {
  const { batchId } = req.params;

  const obs = await pool.query(
    `SELECT * FROM daily_observations WHERE batch_id=$1 ORDER BY date`,
    [batchId]
  );

  const harvests = await pool.query(
    `SELECT * FROM harvests WHERE batch_id=$1`,
    [batchId]
  );

  const insights = [];

  if (harvests.rows.length > 0) {
    const avgYield =
      harvests.rows.reduce((s, h) => s + Number(h.flush_yield_kg), 0) /
      harvests.rows.length;

    if (avgYield < 0.7) {
      insights.push(
        "Yield is trending below historical norms for this batch. Early-stage optimization may improve final output."
      );
    }
  }

  const humidityVariance =
    obs.rows.reduce((s, o) => s + Math.abs(o.relative_humidity_percent - 85), 0) /
    obs.rows.length;

  if (humidityVariance > 10) {
    insights.push(
      "Humidity fluctuations are higher than normal and may be contributing to yield inconsistency."
    );
  }

  res.json({
    summary: insights.join(" "),
    signals: insights
  });
});

export default router;
