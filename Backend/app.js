import express, { json } from "express";
import cors from "cors";

import optimiseRoute from "./routes/optimise.js";

const app = express();

app.use(
  cors({
    origin: "http://localhost:5173",
    credentials: true,
  }),
);

app.use(json());

app.use("/api", optimiseRoute);

const PORT = 5000;
app.listen(PORT, () => {
  console.log(`Backend running on http://localhost:${PORT}`);
});
