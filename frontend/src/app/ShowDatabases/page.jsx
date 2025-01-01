"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

function ShowDatabases() {
  const [databases, setDatabases] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const router = useRouter();

  // Fetch stored databases from the backend
  useEffect(() => {
    const fetchDatabases = async () => {
      try {
        const response = await fetch("http://localhost:5000/api/databases");
        if (response.ok) {
          const data = await response.json();
          setDatabases(data.databases || []);
        } else {
          const error = await response.json();
          setErrorMessage(error.message || "Failed to fetch database details.");
        }
      } catch (error) {
        setErrorMessage(`Unexpected error: ${error.message}`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDatabases();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-500 to-blue-700 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl p-8 w-full max-w-4xl">
        <h1 className="text-4xl font-bold text-blue-600 text-center mb-6">Stored Databases</h1>

        {/* Loading Indicator */}
        {isLoading && <p className="text-center text-gray-700 font-semibold animate-pulse">Loading databases...</p>}

        {/* Error Message */}
        {errorMessage && <p className="text-center text-red-500 font-semibold">{errorMessage}</p>}

        {/* Database List */}
        {!isLoading && !errorMessage && databases.length > 0 && (
          <ul className="space-y-4 mt-4">
            {databases.map((db, index) => (
              <li key={index} className="border border-gray-300 rounded-lg p-4 bg-gray-50 shadow-md">
                <h3 className="text-lg font-semibold text-gray-700">
                  Database Name: <span className="text-blue-600">{db.name}</span>
                </h3>
                <p className="text-sm text-gray-600">Directory: {db.dir}</p>
              </li>
            ))}
          </ul>
        )}

        {/* No Databases Message */}
        {!isLoading && !errorMessage && databases.length === 0 && (
          <p className="text-center text-gray-500 font-semibold">No databases found.</p>
        )}

        {/* Action Buttons */}
        <div className="border-t border-gray-300 mt-6 pt-4">
          <button
            onClick={() => router.push("/AddDatabase")}
            className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition duration-300 mb-4"
          >
            Add Database Details
          </button>
          <button
            onClick={() => router.push("/wal")}
            className="w-full bg-gray-500 text-white py-3 rounded-lg font-semibold hover:bg-gray-600 transition duration-300"
          >
            Back to WAL Checker
          </button>
        </div>
      </div>
    </div>
  );
}

export default ShowDatabases;
