import express, { json } from "express";
import cors from "cors";
import dotenv from "dotenv";

import optimiseRoute from "./routes/optimise.js";

dotenv.config();
const app = express();

app.use(
  cors({
    origin: process.env.FRONTEND_URL,
    credentials: true,
  }),
);

app.use(json());

app.use("/api", optimiseRoute);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Backend running on http://localhost:${PORT}`);
});
