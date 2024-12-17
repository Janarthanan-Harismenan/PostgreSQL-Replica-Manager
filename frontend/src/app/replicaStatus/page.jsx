"use client";

import React, { useState, useEffect } from "react";
import axios from "axios";

function ReplicaStatus() {
  // State for replica data, loading, and errors
  const [replicas, setReplicas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch replicas data from the backend
  const fetchReplicas = async () => {
    setLoading(true);
    setError(null); // Reset error before fetching
    try {
      const response = await axios.get("http://localhost:5000/api/replica-status");
      setReplicas(response.data); // Update replicas state with data from API
    } catch (err) {
      console.error("Error fetching replicas:", err);
      setError("Failed to fetch data. Please try again.");
    } finally {
      setLoading(false); // Stop loading once the fetch completes
    }
  };

  // Update replica status when the user pauses or resumes a replica
  const handlePauseResume = async (id, action) => {
    try {
      await axios.post("http://localhost:5000/api/replica/manage", {
        id,
        action,
      });

      // Optimistically update UI or refetch data
      setReplicas((prevReplicas) =>
        prevReplicas.map((replica) =>
          replica.id === id
            ? { ...replica, status: action === "pause" ? "Paused" : "Active" }
            : replica
        )
      );
    } catch (err) {
      console.error(`Error ${action}ing replica ${id}:`, err);
      alert(`Failed to ${action} replica.`);
    }
  };

  // Fetch data on mount and set up polling
  useEffect(() => {
    fetchReplicas(); // Initial data fetch

    const interval = setInterval(fetchReplicas, 10000); // Fetch every 10 seconds
    return () => clearInterval(interval); // Clean up on component unmount
  }, []);

  return (
    <div className="min-h-screen bg-blue-300 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg p-8 w-4/5">
        <h1 className="text-3xl font-bold text-gray-700 mb-6 bg-blue-400 text-center py-4 rounded">
          Replica Status
        </h1>

        {/* Show loading spinner or error message */}
        {loading && <p className="text-center text-gray-500">Loading...</p>}
        {error && <p className="text-center text-red-500">{error}</p>}

        {/* Display data only when not loading and no error */}
        {!loading && !error && (
          <table className="table-auto w-full border-collapse border border-gray-200">
            <thead>
              <tr className="bg-gray-100 text-center">
                <th className="border border-gray-200 px-4 py-2">Database Name</th>
                <th className="border border-gray-200 px-4 py-2">Status</th>
                <th className="border border-gray-200 px-4 py-2">Delay Time</th>
                <th className="border border-gray-200 px-4 py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {replicas.map((replica) => (
                <tr key={replica.id} className="hover:bg-gray-100 text-center">
                  <td className="border border-gray-200 px-4 py-2">{replica.name}</td>
                  <td
                    className={`border border-gray-200 px-4 py-2 font-semibold ${
                      replica.status === "Active" ? "text-green-500" : "text-red-500"
                    }`}
                  >
                    {replica.status}
                  </td>
                  <td className="border border-gray-200 px-4 py-2">{replica.delayTime}</td>
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
        )}
      </div>
    </div>
  );
}

export default ReplicaStatus;
