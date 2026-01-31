import express from "express";
import cors from "cors";
import { pool } from "./db.js";
import batchRoutes from "./routes/batches.js";
import insightRoutes from "./routes/insights.js";

const app = express();
app.use(cors({ origin: "*" }));
app.use(express.json());

app.use(async (req, res, next) => {
  const username = req.headers["x-username"];
  if (!username) return res.status(400).json({ error: "Username required" });

  const result = await pool.query(
    "INSERT INTO users(username) VALUES($1) ON CONFLICT(username) DO UPDATE SET username=EXCLUDED.username RETURNING id",
    [username]
  );
  req.userId = result.rows[0].id;
  next();
});

app.use("/batches", batchRoutes);
app.use("/insights", insightRoutes);

app.listen(process.env.PORT || 3000);
