"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

function CatalogCheck() {
  const [pgHost, setPgHost] = useState("");
  const [port, setPort] = useState("5432"); // Default port
  const [databases, setDatabases] = useState([]);
  // const [selectedDatabase, setSelectedDatabase] = useState("");
  const [reportGenerated, setReportGenerated] = useState(false);
  const [reportUrl, setReportUrl] = useState("");
  const [selectedHost, setSelectedHost] = useState("");
  const [selectedConfigKey, setSelectedConfigKey] = useState("");
  const [pgHosts, setPgHosts] = useState([]);
  const [reportSummary, setReportSummary] = useState({
    errors: 0,
    inconsistencies: 0,
    warnings: 0,
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const router = useRouter();

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

  const handleGenerateReport = async () => {
    setIsGenerating(true);
    setErrorMessage("");
    setReportGenerated(false);

    try {
      const response = await fetch(
        "http://localhost:5000/api/run-pg-catcheck",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            pg_host: selectedHost,
            config_key: selectedConfigKey,
          }),
        }
      );

      if (response.ok) {
        const result = await response.json();
        if (result.status === "success") {
          setReportSummary({
            errors: result.errors || 0,
            inconsistencies: result.inconsistencies || 0,
            warnings: result.warnings || 0,
          });

          const pdfResponse = await fetch(
            "http://localhost:5000/api/generate-pdf"
          );
          if (pdfResponse.ok) {
            const blob = await pdfResponse.blob();
            const pdfUrl = URL.createObjectURL(blob);
            setReportUrl(pdfUrl);
            setReportGenerated(true);
          } else {
            setErrorMessage("Failed to generate PDF.");
          }
        } else {
          setErrorMessage(result.message);
        }
      } else {
        const error = await response.json();
        setErrorMessage(error.message);
      }
    } catch (error) {
      setErrorMessage(`Unexpected error: ${error.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-500 to-blue-700 flex items-center justify-center p-6">
      <div className="bg-white rounded-lg shadow-2xl p-8 w-full max-w-4xl">
        <h1 className="text-4xl font-bold text-blue-600 text-center mb-8">
          Catalog Check
        </h1>

        {/* Error Message */}
        {errorMessage && (
          <p className="text-red-500 text-center mb-4" aria-live="assertive">
            {errorMessage}
          </p>
        )}

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

        {/* Generate Report Button */}
        {/* {databases.length > 0 && ( */}
        <button
          onClick={handleGenerateReport}
          className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition duration-300 mt-6"
          disabled={isGenerating}
        >
          {isGenerating ? "Generating Report..." : "Generate Report"}
        </button>
        {/* )} */}

        {/* Report Summary */}
        {reportGenerated && (
          <div className="mt-6 text-center">
            <p className="text-green-500 font-semibold mb-4">Report Summary:</p>
            <div className="text-left bg-gray-100 p-4 rounded">
              <p>
                <strong>Errors:</strong> {reportSummary.errors}
              </p>
              <p>
                <strong>Inconsistencies:</strong>{" "}
                {reportSummary.inconsistencies}
              </p>
              <p>
                <strong>Warnings:</strong> {reportSummary.warnings}
              </p>
            </div>

            <a
              href={reportUrl}
              download
              className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition duration-300 mt-6 inline-block"
            >
              Download Report
            </a>
          </div>
        )}

        {/* Back to Home Button */}
        <div className="mt-6">
          <button
            onClick={() => router.push("/")}
            className="w-full bg-gray-500 text-white py-3 rounded-lg font-semibold hover:bg-gray-600 transition duration-300"
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}

export default CatalogCheck;
