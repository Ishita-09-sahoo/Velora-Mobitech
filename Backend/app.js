import express, { json } from "express";
import cors from "cors";
import dotenv from "dotenv";

import optimiseRoute from "./routes/optimise.js";

dotenv.config();
const app = express();

const allowedOrigins = [
  "http://localhost:5173",
  process.env.FRONTEND_URL
];

app.get("/", (req, res) => {
  res.send("Node backend running");
});

app.use(
  cors({
    origin: function (origin, callback) {
      if (!origin || allowedOrigins.includes(origin)) {
        callback(null, true);
      } else {
        callback(new Error("Not allowed by CORS"));
      }
    }
  })
);

app.use(json());

app.use("/api", optimiseRoute);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Backend running on http://localhost:${PORT}`);
});
