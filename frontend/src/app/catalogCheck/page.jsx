"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

function CatalogCheck() {
  const [selectedDatabase, setSelectedDatabase] = useState("");
  const [reportGenerated, setReportGenerated] = useState(false);
  const [reportUrl, setReportUrl] = useState("");
  const router = useRouter();

  const databases = ["Database1", "Database2", "Database3", "Database4"];

  const handleGenerateReport = () => {
    if (!selectedDatabase) {
      alert("Please select a database.");
      return;
    }

    // Simulate report generation
    setTimeout(() => {
      // Mock report URL (in a real scenario, this URL would be generated dynamically on the backend)
      const generatedReportUrl = `/reports/${selectedDatabase}_catalog_report.pdf`;
      setReportUrl(generatedReportUrl);
      setReportGenerated(true);
      alert("Report generated successfully!");
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-blue-500 flex flex-col items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg p-8 w-4/5 max-w-lg">
        <h1 className="text-3xl font-bold text-gray-700 mb-6 text-center">Catalog Check</h1>

        

        {/* Dropdown for Database Selection */}
        <div className="mb-4">
          <label htmlFor="database" className="block text-gray-700 font-semibold mb-2">
            Select Database:
          </label>
          <select
            id="database"
            value={selectedDatabase}
            onChange={(e) => setSelectedDatabase(e.target.value)}
            className="w-full border border-gray-300 rounded py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">-- Select a Database --</option>
            {databases.map((db, index) => (
              <option key={index} value={db}>
                {db}
              </option>
            ))}
          </select>
        </div>

        {/* Generate Report Button */}
        <button
          onClick={handleGenerateReport}
          className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 w-full font-semibold"
        >
          Generate Report
        </button>

        {/* Report Download Section */}
        {reportGenerated && (
          <div className="mt-6 text-center">
            <p className="text-green-500 font-semibold mb-2">
              Report generated for {selectedDatabase}!
            </p>
            <a
              href={reportUrl}
              download
              className="bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600 inline-block font-semibold"
            >
              Download Report
            </a>
          </div>
        )}
        {/* Back Button */}
        <button
          onClick={() => router.push("/")}
          className="mb-4 bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600 font-semibold mt-2 w-full"
        >
          Back to Home
        </button>
      </div>
    </div>
  );
}
export default CatalogCheck;
