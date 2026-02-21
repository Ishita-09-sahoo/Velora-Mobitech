// routes/optimise.js

import { Router } from "express";
import multer from "multer";

import sendToPython from "../utils/sendToPython.js";

const router = Router();

const upload =
multer({ dest: "uploads/" });


router.post(
"/optimise",
upload.single("file"),

async (req, res) => {

    try {

        const result =
        await sendToPython(
        req.file.path
        );

        res.json(result);

    }

    catch (err) {

        res.status(500).json({
        error: err.message
        });

    }

});


export default router;