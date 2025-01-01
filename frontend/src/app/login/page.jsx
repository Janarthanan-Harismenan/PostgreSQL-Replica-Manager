"use client";
 
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  FaFacebookF,
  FaGoogle,
  FaLinkedinIn,
  FaRegEnvelope,
} from "react-icons/fa";
import { MdLockOutline } from "react-icons/md";
 
function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false); // Handle loading state
  const router = useRouter(); // Initialize useRouter
 
  const handleSignIn = async () => {
    if (!email || !password) {
      alert("Please enter both email and password!");
      return;
    }
 
    setLoading(true); // Start loading
 
    try {
      const response = await fetch("http://localhost:5000/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });
 
      if (response.ok) {
        const data = await response.json();
        alert(data.message); // Show success message
        router.push("/"); // Redirect to dashboard or home
      } else {
        const errorData = await response.json();
        alert(`Login failed: ${errorData.message}`);
      }
    } catch (error) {
      console.error("Error connecting to backend:", error);
      alert("An error occurred. Please try again.");
    } finally {
      setLoading(false); // Stop loading
    }
  };
 
  const handleSignup = () => {
    router.push("/signup"); // Navigate to the signup page
  };
 
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-2 bg-blue-100">
      <main className="flex flex-col items-center justify-center w-full flex-1 px-20 text-center">
        <div className="bg-white rounded-2xl shadow-2xl flex w-2/3 max-w-4xl">
          {/* Sign-In Section */}
          <div className="w-3/5 p-5">
            <div className="text-left font-bold">
              <span className="text-blue-300">GTN Technologies</span>
            </div>
            <div className="py-10">
              <h2 className="text-3xl font-bold text-blue-400 mb-2">
                Sign in to the Account
              </h2>
              <div className="border-2 w-10 border-blue-500 inline-block mb-2"></div>
              {/* Social Buttons */}
              <div className="flex justify-center my-2">
                <button
                  className="border-2 border-gray-200 rounded-full p-3 mx-1"
                  onClick={() => console.log("Facebook login clicked")}
                >
                  <FaFacebookF className="text-blue-500 text-sm" />
                </button>
                <button
                  className="border-2 border-gray-200 rounded-full p-3 mx-1"
                  onClick={() => console.log("Google login clicked")}
                >
                  <FaGoogle className="text-green-300 text-sm" />
                </button>
                <button
                  className="border-2 border-gray-200 rounded-full p-3 mx-1"
                  onClick={() => console.log("LinkedIn login clicked")}
                >
                  <FaLinkedinIn className="text-blue-500 text-sm" />
                </button>
              </div>
              <p className="text-gray-500 mt-2">or use your email account:</p>
              {/* Email Input */}
              <div className="flex flex-col items-center mb-3">
                <div className="bg-gray-100 w-64 p-2 flex items-center">
                  <FaRegEnvelope className="text-gray-400 m-2" />
                  <input
                    type="email"
                    name="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="bg-gray-100 outline-none text-sm flex-1"
                  />
                </div>
              </div>
              {/* Password Input */}
              <div className="flex flex-col items-center mb-3">
                <div className="bg-gray-100 w-64 p-2 flex items-center">
                  <MdLockOutline className="text-gray-400 m-2" />
                  <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="bg-gray-100 outline-none text-sm flex-1"
                  />
                </div>
                <div className="flex w-64 mb-5 mt-2 justify-between">
                  <label className="flex items-center text-xs">
                    <input type="checkbox" name="remember" />
                    Remember me
                  </label>
                  <a href="#" className="text-xs">
                    Forgot Password
                  </a>
                </div>
              </div>
              {/* Sign In Button */}
              <button
                className="border-2 border-blue-500 rounded-full px-12 py-2 font-semibold hover:bg-blue-500 hover:text-white disabled:opacity-50"
                onClick={handleSignIn}
                disabled={loading}
              >
                {loading ? "Signing in..." : "Sign in"}
              </button>
            </div>
          </div>
 
          {/* Signup Section */}
          <div className="w-2/5 bg-blue-700 text-white rounded-tr-2xl rounded-br-2xl py-36 px-12">
            <h2 className="text-3xl font-bold mb-2">New Here?</h2>
            <div className="border-2 w-10 border-white inline-block mb-2"></div>
            <p className="mb-10">Create an account to join us.</p>
            <button
              className="border-2 border-white rounded-full px-12 py-2 font-semibold hover:bg-white hover:text-black"
              onClick={handleSignup}
            >
              Signup
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
 
export default LoginPage;