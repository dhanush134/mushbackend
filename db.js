import pkg from "pg";
const { Pool } = pkg;

export const pool = new Pool({
  connectionString: process.env.postgres:uHCjCcuJLOqvwMePvQUhvRghhIAvmduY@postgres.railway.internal:5432/railway
});
