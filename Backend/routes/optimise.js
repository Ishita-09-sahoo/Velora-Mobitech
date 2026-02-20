import { Router } from 'express';
import multer, { memoryStorage } from 'multer';
// FIX: Add .js extension
import runCppOptimizer from '../controllers/optimise.controller.js';

const router = Router();
const upload = multer({ storage: memoryStorage() });

router.post('/optimize', upload.fields([
  { name: 'demandFile', maxCount: 1 },
  { name: 'supplyFile', maxCount: 1 }
]), async (req, res) => {
  try {
    // Safety check to ensure files exist before accessing buffer
    if (!req.files || !req.files.demandFile || !req.files.supplyFile) {
        return res.status(400).json({ error: "Both demandFile and supplyFile are required." });
    }

    const result = await runCppOptimizer(
      req.files.demandFile[0].buffer,
      req.files.supplyFile[0].buffer
    );
    res.json(result);
  } catch (error) {
    console.error("Backend Error:", error); // Log error to console so you can see it
    res.status(500).json({ error: error.message });
  }
});

export default router;