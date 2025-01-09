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
        <tr
          key={replica.pg_host || `replica-${Math.random()}`}
          className="hover:bg-blue-50 text-center"
        >
          <td className="border text-gray-500 border-gray-200 px-4 py-2">
            {replica.name || replica.pg_host || "Unknown"}
          </td>
          <td
            className={`border border-gray-200 px-4 py-2 font-semibold ${
              replica.status === "running"
                ? "text-green-600"
                : replica.status === "paused"
                ? "text-yellow-500"
                : "text-gray-500"
            }`}
          >
            {replica.status}
          </td>
          <td className="border text-gray-600 border-gray-200 px-4 py-2">
            {replica.delay || "N/A"}
          </td>
          <td className="border border-gray-200 px-4 py-2 space-x-2">
            {replica.status === "paused" || replica.status === "Paused" ? (
              <button
                onClick={() =>
                  handlePauseResume(replica.pg_host, replica.name, "resume")
                }
                className="bg-green-500 text-white py-1 px-3 rounded hover:bg-green-600 w-20 text-center"
              >
                Resume
              </button>
            ) : replica.status === "running" || replica.status === "Running" ? (
              <button
                onClick={() =>
                  handlePauseResume(replica.pg_host, replica.name, "pause")
                }
                className="bg-red-500 text-white py-1 px-3 rounded hover:bg-red-600 w-20 text-center"
              >
                Pause
              </button>
            ) : null}
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
      const response = await axios.get(
        "http://localhost:5000/api/replica-status"
      );
      setReplicas(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      console.error("Error fetching replicas:", err);
      const errorMessage =
        err.response?.data?.error ||
        "Failed to fetch replica data. Please try again later.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReplicas(); // Fetch on component mount
  }, []); // Empty dependency array ensures this runs only once

  // Handle Pause/Resume actions
  const handlePauseResume = async (host, name, action) => {
    setLoading(true); // Show loading state during the operation
    try {
      const response = await axios.post(
        "http://localhost:5000/api/replica/manage",
        {
          action,
          name,
        }
      );

      // Update the status in the frontend
      if (response.data.status === "paused" || response.data.status === "resumed") {
        setReplicas((prevReplicas) =>
          prevReplicas.map((replica) =>
            replica.pg_host === host
              ? { ...replica, status: action === "pause" ? "paused" : "running" }
              : replica
          )
        );
      } else {
        console.error("Error managing replica:", response.data.error);
        alert(response.data.error || "An error occurred. Please try again.");
      }
    } catch (err) {
      console.error(`Error ${action}ing replica:`, err);
      alert(`Failed to ${action} the replica. Please try again.`);
    } finally {
      setLoading(false); // Hide loading state
    }
  };

  return (
    <div className="bg-blue-50 flex flex-col items-center justify-center py-8">
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
