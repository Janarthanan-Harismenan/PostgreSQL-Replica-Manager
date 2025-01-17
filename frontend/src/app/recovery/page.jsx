"use client";

import React, { useState, useEffect } from "react";
import useAuth from "../Hooks/useAuth";
import { useRouter } from "next/navigation";
import ReplicaStatus from "../ReplicaStatus/page";
import "react-datepicker/dist/react-datepicker.css";
import ReactDatePicker from "react-datepicker";

function Recovery() {
  const [recoveryMethod, setRecoveryMethod] = useState("");
  const { isAuthChecked, isAuthenticated } = useAuth(); // Use the authentication hook
  const [selectedHost, setSelectedHost] = useState("");
  // const [selectedPort, setSelectedPort] = useState("");
  const [selectedConfigKey, setSelectedConfigKey] = useState("");
  const [pgHost, setPgHost] = useState("");
  const [walFileName, setWalFileName] = useState("");
  const [recoveryTime, setRecoveryTime] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [recoveryMessage, setRecoveryMessage] = useState("");
  const [pgHosts, setPgHosts] = useState([]);
  const [responsePayload, setResponsePayload] = useState(null);
  // const [isFetchingDatabases, setIsFetchingDatabases] = useState(false);
  // const [errorMessage, setErrorMessage] = useState("");
  // const [databases, setDatabases] = useState([]);
  // const [selectedDatabase, setSelectedDatabase] = useState("");
  // const [primaryDatabase, setPrimaryDatabase] = useState(null); // New state for primary database
  // const [secondaryDatabase, setSecondaryDatabase] = useState(null); // New state for secondary database

  const router = useRouter();

  const recoveryMethods = ["WAL", "Log"];

  // Redirect to login if not authenticated after auth check
  useEffect(() => {
    if (isAuthChecked && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthChecked, isAuthenticated, router]);

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
            // setSelectedPort(pgHostsAndPorts[0].port || "");
            setSelectedConfigKey(pgHostsAndPorts[0].config_key || "");
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

  // const handleStartRecovery = async () => {
  //   if (!selectedHost || !selectedPort || !recoveryMethod) {
  //     alert("Please ensure all required fields are selected.");
  //     return;
  //   }

  //   if (recoveryMethod === "WAL" && !walFileName.trim()) {
  //     alert("Please enter a valid WAL file name.");
  //     return;
  //   }

  //   if (recoveryMethod === "Log" && !recoveryTime.trim()) {
  //     alert(
  //       "Please enter a valid recovery time in the format: Thu Jan  2 04:31:31 UTC 2025."
  //     );
  //     return;
  //   }

  //   const payload = {
  //     recovery_host: selectedHost,
  //     recovery_method: recoveryMethod,
  //     wal_file_name: recoveryMethod === "WAL" ? walFileName : null,
  //     recovery_time: recoveryMethod === "Log" ? recoveryTime : null,
  //     // recovery_database: selectedDatabase,
  //     recovery_port: selectedPort,
  //   };

  //   setIsProcessing(true);
  //   setRecoveryMessage("");
  //   setResponsePayload(null);

  //   try {
  //     const response = await fetch("http://localhost:5000/api/start-recovery", {
  //       method: "POST",
  //       headers: {
  //         "Content-Type": "application/json",
  //       },
  //       body: JSON.stringify(payload),
  //     });

  //     const data = await response.json();
  //     setResponsePayload(data);

  //     if (response.ok) {
  //       setRecoveryMessage(
  //         data.message?.message || "Recovery process completed successfully!"
  //       );
  //     } else {
  //       setRecoveryMessage(
  //         data.message?.message || "Failed to complete the recovery process."
  //       );
  //     }
  //   } catch (error) {
  //     setRecoveryMessage(`Unexpected error: ${error.message}`);
  //   } finally {
  //     setIsProcessing(false);
  //   }
  // };

  const handleStartRecovery = async () => {
    if (!selectedHost || !selectedConfigKey || !recoveryMethod) {
      alert("Please ensure all required fields are selected.");
      return;
    }

    if (recoveryMethod === "WAL") {
      const lsnFormat = /^0\/[A-Fa-f0-9]+$/; // Regular expression for LSN format
      if (!walFileName.trim() || !lsnFormat.test(walFileName)) {
        alert(
          "Invalid WAL LSN Number. Please ensure it is in the format 0/1D99F200."
        );
        return;
      }
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
      config_key: selectedConfigKey,
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

  const handleSwitchToPrimary = async () => {
    if (!selectedHost || !selectedConfigKey) {
      alert(
        "Please select a host, database and port before switching primary."
      );
      return;
    }

    const payload = {
      recovery_host: selectedHost,
      config_key: selectedConfigKey,
      // recovery_database: selectedDatabase,
    };

    try {
      const response = await fetch("http://localhost:5000/api/switch-primary", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok && data.status === "success") {
        alert("Successfully switched the secondary database to primary.");
        // setPrimaryDatabase(selectedDatabase);
        // setSecondaryDatabase(null); // Clear secondary database after promotion
      } else {
        alert(`Failed to switch primary: ${data.message}`);
      }
    } catch (error) {
      alert(`Unexpected error: ${error.message}`);
    }
  };

  if (!isAuthChecked) {
    return (
      <div className="min-h-screen bg-gradient-to-r from-blue-500 to-blue-700 flex items-center justify-center">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-white border-opacity-75"></div>
          <p className="text-white font-semibold mt-4 text-lg">
            Checking authentication...
          </p>
        </div>
      </div>
    );
  }

  return isAuthenticated ? (
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
            value={`${selectedHost}:${selectedConfigKey}`}
            onChange={(e) => {
              const [host, config_key] = e.target.value.split(":");
              setSelectedHost(host);
              setSelectedConfigKey(config_key);
            }}
            className="w-full border border-gray-300 rounded-lg py-2 px-4"
          >
            <option value="">-- Select a Host --</option>
            {pgHosts.map((host, index) => (
              <option key={index} value={`${host.pg_host}:${host.config_key}`}>
                {host.pg_host} : {host.config_key}
              </option>
            ))}
          </select>
        </div>
        {/* Fetch Databases Button */}
        {/* <button
          onClick={fetchDatabases}
          className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition duration-300"
          disabled={isFetchingDatabases}
        >
          {isFetchingDatabases ? "Fetching Databases..." : "Fetch Databases"}
        </button> */}
        {/* Database Selection */}
        {/* {databases.length > 0 && (
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
        )} */}
        {/* Button to make secondary database the primary
        {secondaryDatabase && (
          <div className="mt-6 text-center">
            <button
              onClick={makeSecondaryPrimary}
              className="bg-yellow-500 text-white py-2 px-6 rounded-lg font-semibold hover:bg-yellow-600"
            >
              Make Secondary Database Primary
            </button>
          </div>
        )} */}
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
              placeholder="e.g., 0/1D99F200"
              value={walFileName}
              onChange={(e) => setWalFileName(e.target.value)}
              className="w-full border border-gray-300 rounded-lg py-2 px-4"
            />
          </div>
        )}
        {/* {recoveryMethod === "WAL" && (
          <div className="my-6">
            <label className="block text-gray-700 font-semibold mb-2">
              Enter WAL LSN Number
            </label>
            <input
              type="text"
              placeholder="e.g., 0/1D99F200"
              value={walFileName}
              onChange={(e) => {
                const input = e.target.value;
                const lsnFormat = /^0\/[A-Fa-f0-9]+$/; // Regular expression for LSN format
                if (lsnFormat.test(input) || input === "") {
                  setWalFileName(input); // Update value if it matches the format or is empty
                } else {
                  alert("Invalid WAL LSN Number. Format must be 0/1D99F200.");
                }
              }}
              className="w-full border border-gray-300 rounded-lg py-2 px-4"
            />
          </div>
        )} */}

        {/* {recoveryMethod === "Log" && (
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
        )} */}

        {recoveryMethod === "Log" && (
          <div className="my-6">
            <label className="block text-gray-700 font-semibold mb-2">
              Select Recovery Time
            </label>
            <ReactDatePicker
              selected={recoveryTime ? new Date(recoveryTime) : null}
              onChange={(date) => {
                if (date) {
                  const formattedDate = date
                    .toUTCString()
                    .replace("GMT", "UTC"); // Format the date
                  setRecoveryTime(formattedDate);
                } else {
                  setRecoveryTime(""); // Clear the state if no date is selected
                }
              }}
              showTimeSelect
              timeFormat="HH:mm:ss"
              timeIntervals={1}
              dateFormat="EEE MMM d HH:mm:ss 'UTC' yyyy"
              placeholderText="Select a date and time"
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
        {/* Show Make Secondary Database Primary button after recovery completion
        {responsePayload?.status === "success" && secondaryDatabase && (
          <div className="mt-6 text-center">
            <button
              onClick={makeSecondaryPrimary}
              className="bg-yellow-500 text-white py-2 px-6 rounded-lg font-semibold hover:bg-yellow-600"
            >
              Make Secondary Database Primary
            </button>
          </div>
        )} */}
        {/* <div className="border-t border-gray-300 mt-6 pt-4"> */}
        {/* Switch Secondary to Primary Button */}
        {/* <button
          onClick={handleSwitchToPrimary}
          className="w-full bg-orange-600 text-white py-3 rounded-lg font-semibold hover:bg-orange-700 transition duration-300 mt-4"
        >
          Switch Secondary to Primary
        </button> */}
        {/* Show Make Secondary Database Primary button after recovery completion */}
        {responsePayload?.status === "success" && (
          <div className="mt-6 text-center">
            <button
              onClick={handleSwitchToPrimary}
              className="w-full bg-orange-600 text-white py-3 rounded-lg font-semibold hover:bg-orange-700 transition duration-300 mt-4"
            >
              Switch Secondary to Primary
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
  ) : null;
}

export default Recovery;
