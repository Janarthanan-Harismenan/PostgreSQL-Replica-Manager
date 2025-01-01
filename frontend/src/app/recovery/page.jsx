"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import ReplicaStatus from "../ReplicaStatus/page";

function Recovery() {
  const [recoveryMethod, setRecoveryMethod] = useState(""); // For recovery method dropdown
  const [recoveryOption, setRecoveryOption] = useState(""); // For database selection
  const [walFileName, setWalFileName] = useState(""); // WAL file input
  const [recoveryTime, setRecoveryTime] = useState(""); // Recovery time input
  const [isProcessing, setIsProcessing] = useState(false);
  const [recoveryMessage, setRecoveryMessage] = useState("");
  const [paths, setPaths] = useState([]); // For storing paths from PATH_CONFIG
  const [selectedPath, setSelectedPath] = useState(""); // For storing the selected path
  const router = useRouter();

  const recoveryOptions = ["Database 1", "Database 2", "Database 3"];
  const recoveryMethods = ["WAL", "Log"];

  // Fetch paths from the backend
  useEffect(() => {
    const fetchPaths = async () => {
      try {
        const response = await fetch("http://localhost:5000/api/get-path-config");
        if (response.ok) {
          const data = await response.json();
          setPaths(data.paths || []);
          setSelectedPath(data.paths?.[0] || ""); // Default to the first path
        } else {
          alert("Failed to fetch paths from the server.");
        }
      } catch (error) {
        alert(`Unexpected error: ${error.message}`);
      }
    };

    fetchPaths();
  }, []);

  const handleStartRecovery = async () => {
    if (!recoveryOption) {
      alert("Please select a recovery option.");
      return;
    }

    if (!recoveryMethod) {
      alert("Please select a recovery method.");
      return;
    }

    if (recoveryMethod === "WAL" && !walFileName.trim()) {
      alert("Please enter a valid WAL file name.");
      return;
    }

    if (recoveryMethod === "Log" && !recoveryTime.trim()) {
      alert("Please enter a valid recovery time.");
      return;
    }

    if (!selectedPath) {
      alert("Please select a recovery path.");
      return;
    }

    setIsProcessing(true);
    setRecoveryMessage("");

    // Simulate recovery process
    setTimeout(() => {
      const message = `Recovery initiated for "${recoveryOption}" using method "${recoveryMethod}"${
        recoveryMethod === "WAL"
          ? ` with WAL file "${walFileName}"`
          : ` with recovery time "${recoveryTime}"`
      } in path "${selectedPath}".`;
      setRecoveryMessage(message);
      alert("Recovery process started successfully!");
      setIsProcessing(false);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl p-8 w-full max-w-4xl">
        <h1 className="text-4xl font-extrabold text-gray-800 mb-6 text-center">
          Database Recovery
        </h1>

        <ReplicaStatus />

        {/* Recovery Options Dropdown */}
        <div className="mb-6">
          <label
            htmlFor="recoveryOption"
            className="block text-gray-700 font-semibold mb-2"
          >
            Select Database
          </label>
          <select
            id="recoveryOption"
            value={recoveryOption}
            onChange={(e) => setRecoveryOption(e.target.value)}
            className="w-full border border-gray-300 rounded-lg py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200"
          >
            <option value="">-- Select a Database --</option>
            {recoveryOptions.map((option, index) => (
              <option key={index} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

        {/* Recovery Method Dropdown */}
        <div className="mb-6">
          <label
            htmlFor="recoveryMethod"
            className="block text-gray-700 font-semibold mb-2"
          >
            Select Recovery Method
          </label>
          <select
            id="recoveryMethod"
            value={recoveryMethod}
            onChange={(e) => setRecoveryMethod(e.target.value)}
            className="w-full border border-gray-300 rounded-lg py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200"
          >
            <option value="">-- Select a Method --</option>
            {recoveryMethods.map((method, index) => (
              <option key={index} value={method}>
                {method}
              </option>
            ))}
          </select>
        </div>

        {/* Conditional Inputs */}
        {recoveryMethod === "WAL" && (
          <div className="mb-6">
            <label
              htmlFor="walFileName"
              className="block text-gray-700 font-semibold mb-2"
            >
              Enter WAL LSN Number
            </label>
            <input
              type="text"
              id="walFileName"
              placeholder="e.g., wal_file_123.log"
              value={walFileName}
              onChange={(e) => setWalFileName(e.target.value)}
              className="w-full border border-gray-300 rounded-lg py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200"
            />
          </div>
        )}

        {recoveryMethod === "Log" && (
          <div className="mb-6">
            <label
              htmlFor="recoveryTime"
              className="block text-gray-700 font-semibold mb-2"
            >
              Enter Recovery Time
            </label>
            <input
              type="datetime-local"
              id="recoveryTime"
              value={recoveryTime}
              onChange={(e) => setRecoveryTime(e.target.value)}
              className="w-full border border-gray-300 rounded-lg py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200"
            />
          </div>
        )}

        {/* Start Recovery Button */}
        <button
          onClick={handleStartRecovery}
          className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition duration-300"
          disabled={isProcessing}
        >
          {isProcessing ? "Processing..." : "Start Recovery"}
        </button>

        {/* Recovery Message */}
        {recoveryMessage && (
          <div className="mt-6 text-center">
            <p className="text-green-600 font-medium">{recoveryMessage}</p>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="border-t border-gray-300 mt-6 pt-4">
          <div className="flex justify-between">
            <button
              onClick={() => router.push("/")}
              className="flex-grow mx-2 bg-gray-500 text-white py-3 rounded-lg font-semibold hover:bg-gray-600 transition duration-300"
            >
              Back to Home
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Recovery;
