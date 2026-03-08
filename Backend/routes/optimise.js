import { Router } from "express";
import multer from "multer";

import sendToPython from "../utils/sendToPython.js";

const router = Router();

const upload = multer({ dest: "uploads/" });
let isProcessing = false;

router.post(
  "/optimise",
  upload.single("file"),

  async (req, res) => {
    if (isProcessing) {
      return res.status(429).json({ error: "Optimization already running" });
    }

    isProcessing = true;
    try {
      const result = await sendToPython(req.file.path);

      res.json(result);
    } catch (err) {
      res.status(500).json({
        error: err.message,
      });
    } finally {
      isProcessing = false;
    }
  },
);

export default router;
