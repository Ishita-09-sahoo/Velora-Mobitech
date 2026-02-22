import axios from "axios";
import FormData from "form-data";
import { createReadStream } from "fs";

const sendToPython = async (filePath) => {

    const formData = new FormData();

    formData.append(
        "file",
        createReadStream(filePath)
    );

    const response = await axios.post(

        "http://127.0.0.1:8000/optimise",

        formData,

        {
            headers: formData.getHeaders()
        }

    );

    return response.data;
};

export default sendToPython;