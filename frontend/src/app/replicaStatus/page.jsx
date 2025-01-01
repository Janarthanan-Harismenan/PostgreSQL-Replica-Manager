"use client";

import React, { useState, useEffect } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";

// Loading Spinner Component
const Loading = () => (
  <p className="text-center text-gray-500">Loading data, please wait...</p>
);

// Error Message Component
const ErrorMessage = ({ message }) => (
  <p className="text-center text-red-500">{message}</p>
);

// Replica Table Component
const ReplicaTable = ({ replicas, handlePauseResume }) => (
  <table className="table-auto w-full border-collapse border border-gray-200">
    <thead>
      <tr className="bg-blue-600 text-white text-center">
        <th className="border border-gray-200 px-4 py-2">Database Name</th>
        <th className="border border-gray-200 px-4 py-2">Status</th>
        <th className="border border-gray-200 px-4 py-2">Delay Time</th>
        <th className="border border-gray-200 px-4 py-2">Actions</th>
      </tr>
    </thead>
    <tbody>
      {replicas.map((replica) => (
        <tr key={replica.id || `replica-${Math.random()}`} className="hover:bg-blue-50 text-center">
          <td className="border text-gray-500 border-gray-200 px-4 py-2">{replica.name}</td>
          <td
            className={`border border-gray-200 px-4 py-2 font-semibold ${
              replica.status === "running"
                ? "text-green-600" // Green color for running
                : replica.status === "Paused"
                ? "text-yellow-500" // Yellow color for Paused
                : "text-gray-500" // Gray color for any other status
            }`}
          >
            {replica.status}
          </td>
          <td className="border text-gray-600 border-gray-200 px-4 py-2">{replica.delay}</td>
          <td className="border border-gray-200 px-4 py-2 space-x-2">
            {replica.status === "Active" ? (
              <button
                onClick={() => handlePauseResume(replica.id, "pause")}
                className="bg-red-500 text-white py-1 px-3 rounded hover:bg-red-600 w-20 text-center"
              >
                Pause
              </button>
            ) : (
              <button
                onClick={() => handlePauseResume(replica.id, "resume")}
                className="bg-green-500 text-white py-1 px-3 rounded hover:bg-green-600 w-20 text-center"
              >
                Resume
              </button>
            )}
          </td>
        </tr>
      ))}
    </tbody>
  </table>
);

const ReplicaStatus = () => {
  const router = useRouter();
  const [replicas, setReplicas] = useState([]); // Default to empty array
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch replicas data
  const fetchReplicas = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get("http://localhost:5000/api/replica-status");
      setReplicas(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      console.error("Error fetching replicas:", err);
      setError("Failed to fetch replica data. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReplicas(); // Fetch on component mount
  }, []); // Empty dependency array ensures this runs only once

  // Handle Pause/Resume actions
  const handlePauseResume = async (id, action) => {
    try {
      await axios.post("http://localhost:5000/api/replica/manage", { action });

      setReplicas((prevReplicas) =>
        prevReplicas.map((replica) =>
          replica.id === id
            ? { ...replica, status: action === "pause" ? "Paused" : "Active" }
            : replica
        )
      );
    } catch (err) {
      console.error(`Error ${action}ing replica:`, err);
      alert(`Failed to ${action} replica. Please try again.`);
    }
  };

  return (
    <div className=" bg-blue-50 flex flex-col items-center justify-center py-8">
      <div className="bg-white rounded-lg shadow-lg p-8 w-4/5 max-w-4xl">
        {/* Title */}
        <h1 className="text-3xl font-bold text-gray-700 mb-6 bg-blue-500 text-white text-center py-4 rounded">
          Replica Status
        </h1>

        {/* Loading and Error Handling */}
        {loading && <Loading />}
        {error && <ErrorMessage message={error} />}

        {/* Display Replica Data */}
        {!loading && !error && (
          <>
            {replicas.length > 0 ? (
              <ReplicaTable replicas={replicas} handlePauseResume={handlePauseResume} />
            ) : (
              <p className="text-center text-gray-500">No replica data available.</p>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default ReplicaStatus; 