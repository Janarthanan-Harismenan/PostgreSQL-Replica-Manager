"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

function Recovery() {
  const [recoveryOption, setRecoveryOption] = useState("");
  const [recoveryMessage, setRecoveryMessage] = useState("");
  const [walFileName, setWalFileName] = useState("");
  const router = useRouter();

  const recoveryOptions = ["Database 1", "Database 2", "Database 3"];

  const handleStartRecovery = () => {
    if (!recoveryOption) {
      alert("Please select a recovery option.");
      return;
    }

    if (!walFileName) {
      alert("Please enter a WAL file name.");
      return;
    }

    // Simulate recovery process
    setTimeout(() => {
      setRecoveryMessage(
        `${recoveryOption} recovery process initiated using WAL file "${walFileName}".`
      );
      alert("Recovery process started successfully!");
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-blue-500 flex flex-col items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg p-8 w-4/5 max-w-lg">
        <h1 className="text-3xl font-bold text-gray-700 mb-6 text-center">Recovery</h1>

        {/* Dropdown for Recovery Options */}
        <div className="mb-4">
          <label htmlFor="recoveryOption" className="block text-gray-700 font-semibold mb-2">
            Select Recovery Option:
          </label>
          <select
            id="recoveryOption"
            value={recoveryOption}
            onChange={(e) => setRecoveryOption(e.target.value)}
            className="w-full border border-gray-300 rounded py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">-- Select a Recovery Option --</option>
            {recoveryOptions.map((option, index) => (
              <option key={index} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

        {/* Input for WAL File Name */}
        <div className="mb-4">
          <label htmlFor="walFileName" className="block text-gray-700 font-semibold mb-2">
            Enter WAL File Name:
          </label>
          <input
            type="text"
            id="walFileName"
            placeholder="Enter WAL file name"
            value={walFileName}
            onChange={(e) => setWalFileName(e.target.value)}
            className="w-full border border-gray-300 rounded py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Start Recovery Button */}
        <button
          onClick={handleStartRecovery}
          className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 w-full font-semibold"
        >
          Start Recovery
        </button>

        {/* Recovery Message Section */}
        {recoveryMessage && (
          <div className="mt-6 text-center">
            <p className="text-green-500 font-semibold">{recoveryMessage}</p>
          </div>
        )}

        {/* Back Button */}
        <button
          onClick={() => router.push("/")}
          className="mb-4 bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600 font-semibold mt-4 w-full"
        >
          Back to Home
        </button>
      </div>
    </div>
  );
}

export default Recovery;
