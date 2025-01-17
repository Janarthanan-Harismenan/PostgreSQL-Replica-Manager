"use client";

// import React from "react";
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import useAuth from "../Hooks/useAuth"; // Adjust the path to where `useAuth` is located

function PointFinder() {
  const router = useRouter();
  const { isAuthChecked, isAuthenticated } = useAuth(); // Use the authentication hook

  // Redirect to login if not authenticated after auth check
  useEffect(() => {
    if (isAuthChecked && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthChecked, isAuthenticated, router]);

  const navigateToWal = () => {
    router.push("/wal");
  };

  const navigateToLogViewer = () => {
    router.push("/LogViewer");
  };

  const navigateToHome = () => {
    router.push("/");
  };

  if (!isAuthChecked) {
    return (
      <div className="min-h-screen bg-gradient-to-r from-blue-500 to-blue-700 flex items-center justify-center">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-white border-opacity-75"></div>
          <p className="text-white font-semibold mt-4 text-lg">
            Checking authentication...
          </p>
        </div>
      </div>
    );
  }

  return isAuthenticated ? (
    <div className="flex flex-col min-h-screen bg-gray-50">
      {/* Main Content */}
      <div className="flex flex-col items-center justify-center flex-1 p-8">
        <section className="bg-white rounded-lg shadow-lg p-10 max-w-md w-full">
          <h1 className="text-4xl font-bold text-gray-800 mb-6 text-center">
            Where do you want to go?
          </h1>
          <p className="text-gray-600 text-center mb-8">
            Choose your destination below. You can navigate to WAL for logging
            management or view logs directly.
          </p>
          <div className="space-y-4">
            <button
              onClick={navigateToWal}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg shadow-md hover:bg-blue-700 transition"
            >
              Go to WAL
            </button>
            <button
              onClick={navigateToLogViewer}
              className="w-full bg-green-600 text-white py-3 px-6 rounded-lg shadow-md hover:bg-green-700 transition"
            >
              Go to Log Viewer
            </button>
            <button
              onClick={navigateToHome}
              className="w-full bg-gray-600 text-white py-3 px-6 rounded-lg shadow-md hover:bg-gray-700 transition"
            >
              Back to Home
            </button>
          </div>
        </section>
      </div>
    </div>
  ) : null;
}

export default PointFinder;
