import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  timeout: 60000,
});

export async function generateStudyMaterial(notes) {
  const response = await api.post("/generate", { notes });
  return response.data;
}

export async function sendEmail(email, studyMaterial) {
  const response = await api.post("/send-email", {
    email,
    study_material: studyMaterial,
  });
  return response.data;
}
