"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation"; // Import useRouter

function ReplicaStatus() {
  const router = useRouter(); // Initialize router

  // Sample data for database replicas
  const [replicas, setReplicas] = useState([
    { id: 1, name: "Database1", status: "Active", delayTime: "5s" },
    { id: 2, name: "Database2", status: "Paused", delayTime: "10s" },
    { id: 3, name: "Database3", status: "Active", delayTime: "2s" },
  ]);

  const handlePauseResume = (id, action) => {
    setReplicas((prevReplicas) =>
      prevReplicas.map((replica) =>
        replica.id === id
          ? {
              ...replica,
              status: action === "pause" ? "Paused" : "Active",
            }
          : replica
      )
    );

    console.log(`Replica ${id} ${action}d`);
  };

  return (
    <div className="min-h-screen bg-blue-300 flex flex-col items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg p-8 w-4/5">
        <h1 className="text-3xl font-bold text-gray-700 mb-6 bg-blue-400 text-center py-4 rounded">
          Replica Status
        </h1>

        

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
        {/* Back Button */}
        <button
          onClick={() => router.push("/")}
          className="mb-6 bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600 font-semibold  mt-2 flex justify-center"
        >
          Back to Home
        </button>
      </div>
    </div>
  );
}

export default ReplicaStatus;
