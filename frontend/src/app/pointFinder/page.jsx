"use client";

import React from "react";
import { useRouter } from "next/navigation";

function PointFinder() {
  const router = useRouter();

  const navigateToWal = () => {
    router.push("/wal");
  };

  const navigateToLogViewer = () => {
    router.push("/LogViewer");
  };

  const navigateToHome = () => {
    router.push("/");
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      {/* Main Content */}
      <div className="flex flex-col items-center justify-center flex-1 p-8">
        <section className="bg-white rounded-lg shadow-lg p-10 max-w-md w-full">
          <h1 className="text-4xl font-bold text-gray-800 mb-6 text-center">
            Where do you want to go?
          </h1>
          <p className="text-gray-600 text-center mb-8">
            Choose your destination below. You can navigate to WAL for logging management or view logs directly.
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
  );
}

export default PointFinder;