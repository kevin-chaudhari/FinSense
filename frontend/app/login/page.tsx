"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

export default function LoginPage() {
  const [userId, setUserId] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      const res = await fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include", // crucial for cookie
        body: JSON.stringify({ user_id: userId }),
      });

      const data = await res.json();

      if (res.ok) {
        toast.success("Login successful");
        setTimeout(() => router.push("/ask-question"), 1000);
      } else {
        setError(data.error || "Login failed");
      }
    } catch (err: any) {
      setError("Network error: Failed to connect to backend");
      console.error("Login error:", err);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6">
      <h1 className="text-2xl font-bold text-center mb-6 text-indigo-800 dark:text-indigo-200">
        Login to BrokeNoMore
      </h1>
      <form
        onSubmit={handleLogin}
        className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg space-y-4"
      >
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          User ID
        </label>
        <input
          type="text"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          className="input w-full"
          placeholder="e.g., user_123"
          required
        />
        {error && <p className="text-red-500 text-sm italic">{error}</p>}
        <button
          type="submit"
          className="btn bg-indigo-600 hover:bg-indigo-700 text-white w-full font-semibold py-2 px-4 rounded"
        >
          Log In
        </button>
      </form>
      <ToastContainer position="bottom-right" autoClose={3000} />
    </div>
  );
}
