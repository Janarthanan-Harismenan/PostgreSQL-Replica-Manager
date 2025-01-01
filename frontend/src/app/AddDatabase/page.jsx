"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

function AddDatabase() {
  const [databaseName, setDatabaseName] = useState("");
  const [databaseDir, setDatabaseDir] = useState("");
  const [message, setMessage] = useState("");
  const router = useRouter();

  const handleSubmit = async () => {
    if (!databaseName || !databaseDir) {
      alert("Please fill in both the database name and directory.");
      return;
    }

    try {
      const response = await fetch("http://localhost:5000/api/dbadder", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: databaseName,
          dir: databaseDir,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setMessage(result.message || "Database details added successfully!");
      } else {
        const error = await response.json();
        setMessage(error.message || "Failed to add database details.");
      }
    } catch (error) {
      setMessage(`Unexpected error: ${error.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-blue-500 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-4xl">
        <h1 className="text-4xl font-bold text-blue-600 text-center mb-6">
          Add Database Details
        </h1>

        <div className="space-y-6">
          <div>
            <label htmlFor="databaseName" className="block text-gray-700 font-semibold mb-2">
              Database Name:
            </label>
            <input
              id="databaseName"
              type="text"
              value={databaseName}
              onChange={(e) => setDatabaseName(e.target.value)}
              className="w-full border border-gray-300 rounded-lg py-2 px-4 focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="Enter the database name"
            />
          </div>

          <div>
            <label htmlFor="databaseDir" className="block text-gray-700 font-semibold mb-2">
              Database Directory:
            </label>
            <input
              id="databaseDir"
              type="text"
              value={databaseDir}
              onChange={(e) => setDatabaseDir(e.target.value)}
              className="w-full border border-gray-300 rounded-lg py-2 px-4 focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="Enter the database directory"
            />
          </div>

          <button
            onClick={handleSubmit}
            className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition duration-300"
          >
            Submit
          </button>
        </div>

        {message && <p className="text-center mt-4 font-semibold">{message}</p>}

        <button
          onClick={() => router.push("/ShowDatabases")}
          className="w-full bg-blue-900 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition duration-300 mt-4"
        >
          Show Database Details
        </button>

        <button
          onClick={() => router.push("/wal")}
          className="mt-6 w-full bg-gray-500 text-white py-3 rounded-lg font-semibold hover:bg-gray-600 transition duration-300"
        >
          Back to WAL Checker
        </button>
      </div>
    </div>
  );
}

export default AddDatabase;
