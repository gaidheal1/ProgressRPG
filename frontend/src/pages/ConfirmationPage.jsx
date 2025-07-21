import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const BASE_URL = import.meta.env.VITE_API_BASE_URL;
const API_URL = `${BASE_URL}/api/v1`;
console.log("API_URL:", API_URL);

export default function ConfirmationPage() {
  const { key } = useParams();
  const navigate = useNavigate();
  const { login } = useAuth();

  const [status, setStatus] = useState("loading"); // loading | success | error
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!key) {
      setStatus("error");
      setMessage("Invalid confirmation link.");
      return;
    }

    const confirmedKey = sessionStorage.getItem("confirmedKey");
    if (confirmedKey === key) {
      setStatus("success");
      setMessage("Email already confirmed!");
      setTimeout(() => navigate("/onboarding"), 2000);
      return;
    }

    async function confirmEmail() {
      try {
        const res = await fetch(`${API_URL}/auth/confirm_email/${key}/`);
        const data = await res.json();

        if (res.ok) {
          setStatus("success");
          setMessage("Email confirmed! Logging you in...");

          // Optional: auto-login if you want
          if (data.access && data.refresh && login) {
            await login(data.access, data.refresh);
          }

          sessionStorage.setItem("confirmedKey", key);
          setTimeout(() => navigate("/onboarding"), 2000);
        } else {
          setStatus("error");
          setMessage(data?.message || "Confirmation failed.");
        }
      } catch (err) {
        setStatus("error");
        setMessage("Something went wrong.");
      }
    }

    confirmEmail();
  }, [key, navigate, login]);

  return (
    <div>
      {status === "loading" && <p>Just a moment...</p>}
      {status === "success" && <p style={{ color: "green" }}>{message}</p>}
      {status === "error" && <p style={{ color: "red" }}>{message}</p>}
    </div>
  );
}
