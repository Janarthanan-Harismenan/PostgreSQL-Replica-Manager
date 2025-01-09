"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import ReplicaStatus from "../ReplicaStatus/page";

function Recovery() {
  const [recoveryMethod, setRecoveryMethod] = useState("");
  const [selectedHost, setSelectedHost] = useState("");
  const [selectedPort, setSelectedPort] = useState("");
  const [walFileName, setWalFileName] = useState("");
  const [recoveryTime, setRecoveryTime] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [recoveryMessage, setRecoveryMessage] = useState("");
  const [pgHosts, setPgHosts] = useState([]);
  const [responsePayload, setResponsePayload] = useState(null);
  const [isFetchingDatabases, setIsFetchingDatabases] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [databases, setDatabases] = useState([]);
  const [selectedDatabase, setSelectedDatabase] = useState("");
  const [primaryDatabase, setPrimaryDatabase] = useState(null); // New state for primary database
  const [secondaryDatabase, setSecondaryDatabase] = useState(null); // New state for secondary database

  const router = useRouter();

  const recoveryMethods = ["WAL", "Log"];

  useEffect(() => {
    const fetchPgHostsAndPorts = async () => {
      try {
        const response = await fetch(
          "http://localhost:5000/api/get-server-config"
        );
        if (response.ok) {
          const data = await response.json();
          const pgHostsAndPorts = data.pg_hosts_and_ports || [];
          setPgHosts(pgHostsAndPorts);
          if (pgHostsAndPorts.length > 0) {
            setSelectedHost(pgHostsAndPorts[0].pg_host || "");
            setSelectedPort(pgHostsAndPorts[0].port || "");
          }
        } else {
          alert("Failed to fetch server configurations.");
        }
      } catch (error) {
        alert(`Unexpected error: ${error.message}`);
      }
    };

    fetchPgHostsAndPorts();
  }, []);

  const handleStartRecovery = async () => {
    if (!selectedHost || !selectedPort || !recoveryMethod) {
      alert("Please ensure all required fields are selected.");
      return;
    }

    if (recoveryMethod === "WAL" && !walFileName.trim()) {
      alert("Please enter a valid WAL file name.");
      return;
    }

    if (recoveryMethod === "Log" && !recoveryTime.trim()) {
      alert(
        "Please enter a valid recovery time in the format: Thu Jan  2 04:31:31 UTC 2025."
      );
      return;
    }

    const payload = {
      recovery_host: selectedHost,
      recovery_method: recoveryMethod,
      wal_file_name: recoveryMethod === "WAL" ? walFileName : null,
      recovery_time: recoveryMethod === "Log" ? recoveryTime : null,
      recovery_database: selectedDatabase,
    };

    setIsProcessing(true);
    setRecoveryMessage("");
    setResponsePayload(null);

    try {
      const response = await fetch("http://localhost:5000/api/start-recovery", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      setResponsePayload(data);

      if (response.ok) {
        setRecoveryMessage(
          data.message?.message || "Recovery process completed successfully!"
        );
      } else {
        setRecoveryMessage(
          data.message?.message || "Failed to complete the recovery process."
        );
      }
    } catch (error) {
      setRecoveryMessage(`Unexpected error: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const fetchDatabases = async () => {
    if (!selectedHost || !selectedPort) {
      setErrorMessage("Please select a valid PostgreSQL host and port.");
      return;
    }

    setIsFetchingDatabases(true);
    setErrorMessage("");

    try {
      const response = await fetch("http://localhost:5000/api/get-databases", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ pg_host: selectedHost, port: selectedPort }),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.status === "success") {
          setDatabases(result.databases || []);
        } else {
          setErrorMessage(`Error fetching databases: ${result.message}`);
        }
      } else {
        const error = await response.json();
        setErrorMessage(`Error: ${error.message}`);
      }
    } catch (error) {
      setErrorMessage(`Unexpected error: ${error.message}`);
    } finally {
      setIsFetchingDatabases(false);
    }
  };

  const makeSecondaryPrimary = () => {
    setPrimaryDatabase(secondaryDatabase);
    setSecondaryDatabase(null); // Clear secondary database after promotion
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl p-8 w-full max-w-4xl">
        <h1 className="text-4xl font-extrabold text-gray-800 mb-6 text-center">
          Database Recovery
        </h1>

        <ReplicaStatus />

        {/* Recovery Host Dropdown */}
        <div className="my-6">
          <label className="block text-gray-700 font-semibold mb-2">
            Select Recovery Host
          </label>
          <select
            value={`${selectedHost}:${selectedPort}`}
            onChange={(e) => {
              const [host, port] = e.target.value.split(":");
              setSelectedHost(host);
              setSelectedPort(port);
            }}
            className="w-full border border-gray-300 rounded-lg py-2 px-4"
          >
            <option value="">-- Select a Host --</option>
            {pgHosts.map((host, index) => (
              <option key={index} value={`${host.pg_host}:${host.port}`}>
                {host.pg_host}
              </option>
            ))}
          </select>
        </div>

        {/* Fetch Databases Button */}
        <button
          onClick={fetchDatabases}
          className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition duration-300"
          disabled={isFetchingDatabases}
        >
          {isFetchingDatabases ? "Fetching Databases..." : "Fetch Databases"}
        </button>

        {/* Database Selection */}
        {databases.length > 0 && (
          <div className="mt-6">
            <label
              htmlFor="database"
              className="block text-gray-700 font-semibold mb-2"
            >
              Select Database:
            </label>
            <select
              id="database"
              value={selectedDatabase}
              onChange={(e) => setSelectedDatabase(e.target.value)}
              className="w-full border border-gray-300 rounded-lg py-2 px-4 focus:ring-2 focus:ring-blue-500 outline-none"
            >
              <option value="">-- Select a Database --</option>
              {databases.map((db, index) => (
                <option key={index} value={db}>
                  {db}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Button to make secondary database the primary */}
        {secondaryDatabase && (
          <div className="mt-6 text-center">
            <button
              onClick={makeSecondaryPrimary}
              className="bg-yellow-500 text-white py-2 px-6 rounded-lg font-semibold hover:bg-yellow-600"
            >
              Make Secondary Database Primary
            </button>
          </div>
        )}

        {/* Recovery Method Dropdown */}
        <div className="my-6">
          <label className="block text-gray-700 font-semibold mb-2">
            Select Recovery Method
          </label>
          <select
            value={recoveryMethod}
            onChange={(e) => setRecoveryMethod(e.target.value)}
            className="w-full border border-gray-300 rounded-lg py-2 px-4"
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
          <div className="my-6">
            <label className="block text-gray-700 font-semibold mb-2">
              Enter WAL LSN Number
            </label>
            <input
              type="text"
              placeholder="e.g., wal_file_123.log"
              value={walFileName}
              onChange={(e) => setWalFileName(e.target.value)}
              className="w-full border border-gray-300 rounded-lg py-2 px-4"
            />
          </div>
        )}

        {recoveryMethod === "Log" && (
          <div className="my-6">
            <label className="block text-gray-700 font-semibold mb-2">
              Enter Recovery Time
            </label>
            <input
              type="text"
              placeholder="e.g., Thu Jan  2 04:31:31 UTC 2025"
              value={recoveryTime}
              onChange={(e) => setRecoveryTime(e.target.value)}
              className="w-full border border-gray-300 rounded-lg py-2 px-4"
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
            <p
              className={`font-bold ${
                responsePayload?.status === "success"
                  ? "text-green-600"
                  : "text-red-600"
              }`}
            >
              {recoveryMessage}
            </p>
          </div>
        )}

        {/* Show Make Secondary Database Primary button after recovery completion */}
        {responsePayload?.status === "success" && secondaryDatabase && (
          <div className="mt-6 text-center">
            <button
              onClick={makeSecondaryPrimary}
              className="bg-yellow-500 text-white py-2 px-6 rounded-lg font-semibold hover:bg-yellow-600"
            >
              Make Secondary Database Primary
            </button>
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
