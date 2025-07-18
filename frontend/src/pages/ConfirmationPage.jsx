import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const API_URL = import.meta.env.VITE_API_BASE_URL;

export default function ConfirmationPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();

  const [status, setStatus] = useState("loading"); // loading | success | error
  const [message, setMessage] = useState("");

  useEffect(() => {
    const key = searchParams.get("key");

    if (!key) {
      setStatus("error");
      setMessage("Invalid confirmation link.");
      return;
    }

    async function confirmEmail() {
      try {
        const res = await fetch(`${API_URL}/auth/confirm-email/${key}/`);
        const data = await res.json();

        if (res.ok) {
          setStatus("success");
          setMessage("Email confirmed! Logging you in...");

          // Optional: auto-login if you want
          if (data.access && data.refresh && login) {
            await login(data.access, data.refresh);
          }

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
  }, [searchParams, navigate, login]);

  return (
    <div>
      {status === "loading" && <p>Confirming your email...</p>}
      {status === "success" && <p style={{ color: "green" }}>{message}</p>}
      {status === "error" && <p style={{ color: "red" }}>{message}</p>}
    </div>
  );
}
