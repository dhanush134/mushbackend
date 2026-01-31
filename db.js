import pkg from "pg";
import 'dotenv/config'; // <-- auto-loads .env file

const { Pool } = pkg;

export const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});
