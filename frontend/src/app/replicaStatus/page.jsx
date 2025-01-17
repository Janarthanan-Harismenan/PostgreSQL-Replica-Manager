"use client";

import React, { useState, useEffect } from "react";
import axios from "axios";
import Papa from "papaparse";

const Loading = () => (
  <p className="text-center text-gray-500">Loading data, please wait...</p>
);

const ErrorMessage = ({ message }) => (
  <p className="text-center text-red-500">{message}</p>
);

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
        <tr key={replica.delay_name} className="hover:bg-blue-50 text-center">
          <td className="border text-gray-500 border-gray-200 px-4 py-2">
            {replica.name} : {replica.delay_name}
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
            {replica.status || "Loading..."}
          </td>
          <td className="border text-gray-600 border-gray-200 px-4 py-2">
            {replica.delay || "N/A"}
          </td>
          <td className="border border-gray-200 px-4 py-2 space-x-2">
            {replica.status !== "loading" && replica.status === "paused" ? (
              <button
                onClick={() => handlePauseResume(replica.delay_name, "resume")}
                className={`${
                  replica.loading
                    ? "bg-gray-400 text-white cursor-not-allowed opacity-50"
                    : "bg-green-500 text-white hover:bg-green-600"
                } py-1 px-3 rounded`}
                disabled={replica.loading}
              >
                Resume
              </button>
            ) : replica.status !== "loading" && replica.status === "running" ? (
              <button
                onClick={() => handlePauseResume(replica.delay_name, "pause")}
                className={`${
                  replica.loading
                    ? "bg-gray-400 text-white cursor-not-allowed opacity-50"
                    : "bg-red-500 text-white hover:bg-red-600"
                } py-1 px-3 rounded`}
                disabled={replica.loading}
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

const Replica = () => {
  const [replicas, setReplicas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch delay data from CSV
  const fetchDelayTimes = async () => {
    try {
      const response = await axios.get(
        "http://localhost:5000/api/static/replica_status"
      );
      let parsedData = [];
      Papa.parse(response.data, {
        complete: (result) => {
          parsedData = result.data
            .slice(1) // Skip the header
            .filter(
              (row) => row.length > 1 && row.some((cell) => cell.trim() !== "")
            ); // Filter empty rows
        },
        header: false,
      });

      // const lastThreeRows = parsedData.slice(-3).map((row) => ({
      //   name: row[0], // Assuming the first column is the name
      //   delay_name: row[1], // Adjust column index if needed
      //   delay: row[2],
      // }));

      // return lastThreeRows;

      const seenDelayNames = new Set();
      const uniqueRows = [];

      // Traverse from the end to find rows with unique delay_name
      for (let i = parsedData.length - 1; i >= parsedData.length - 10; i--) {
        const row = parsedData[i];
        const delayName = row[1]; // Adjust column index if needed
        if (!seenDelayNames.has(delayName)) {
          seenDelayNames.add(delayName);
          uniqueRows.push({
            name: row[0], // Assuming the first column is the name
            delay_name: delayName,
            delay: row[2],
          });
        } else {
          break;
        }
      }

      return uniqueRows.reverse();
    } catch (err) {
      console.error("Error fetching delay times:", err);
      setError("Failed to fetch delay data.");
      return [];
    }
  };

  // Fetch status data
  const fetchStatuses = async () => {
    try {
      const response = await axios.get("http://localhost:5000/api/status");
      return response.data;
    } catch (err) {
      console.error("Error fetching status:", err);
      setError("Failed to fetch status data.");
      return [];
    }
  };

  // Fetch initial data
  const fetchInitialData = async () => {
    try {
      const delayData = await fetchDelayTimes();
      setReplicas(
        delayData.map((item) => ({
          ...item,
          status: null, // Initialize status as empty or loading
          loading: false, // Initialize loading state
        }))
      );
      setLoading(false); // Remove loading spinner

      const statusData = await fetchStatuses();
      setReplicas((prevReplicas) =>
        prevReplicas.map((replica) => ({
          ...replica,
          status:
            statusData.find(
              (statusItem) => statusItem.delay_name === replica.delay_name
            )?.status || "Unknown",
        }))
      );
    } catch (err) {
      console.error("Error fetching initial data:", err);
      setError("Failed to fetch initial data.");
    } finally {
      setLoading(false); // Ensure loading spinner is removed
    }
  };

  // Update delay times every 10 seconds
  const updateDelays = async () => {
    try {
      const delayData = await fetchDelayTimes();
      setReplicas((prevReplicas) =>
        prevReplicas.map((replica) => ({
          ...replica,
          delay:
            delayData.find(
              (delayItem) => delayItem.delay_name === replica.delay_name
            )?.delay || "N/A",
        }))
      );
    } catch (err) {
      console.error("Error updating delay times:", err);
      setError("Failed to update delay times.");
    }
  };

  // Handle pause/resume actions
  const handlePauseResume = async (delay_name, action) => {
    setReplicas((prevReplicas) =>
      prevReplicas.map((replica) =>
        replica.delay_name === delay_name
          ? { ...replica, loading: true }
          : replica
      )
    );

    try {
      const response = await axios.post(
        "http://localhost:5000/api/replica/manage",
        {
          action,
          delay_name,
        }
      );
      if (response.data.status) {
        setReplicas((prevReplicas) =>
          prevReplicas.map((replica) =>
            replica.delay_name === delay_name
              ? {
                  ...replica,
                  status: action === "pause" ? "paused" : "running",
                  loading: false,
                }
              : replica
          )
        );
      } else {
        console.error("Error updating status:", response.data.error);
        alert(response.data.error || "Action failed. Please try again.");
      }
    } catch (err) {
      console.error("Error performing action:", err);
      alert(`Failed to ${action} the replica.`);
      setReplicas((prevReplicas) =>
        prevReplicas.map((replica) =>
          replica.delay_name === delay_name
            ? { ...replica, loading: false }
            : replica
        )
      );
    }
  };

  useEffect(() => {
    fetchInitialData(); // Fetch initial delay and status data

    // Set interval to update delay times every 10 seconds
    const interval = setInterval(updateDelays, 10000);

    return () => clearInterval(interval); // Cleanup interval on unmount
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-center mb-4">Replica Status</h1>
      {loading && <Loading />}
      {error && <ErrorMessage message={error} />}
      {!loading && !error && (
        <ReplicaTable
          replicas={replicas}
          handlePauseResume={handlePauseResume}
        />
      )}
    </div>
  );
};

export default Replica;
