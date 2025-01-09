"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

function WALChecker() {
  const [searchWord, setSearchWord] = useState("");
  const [numFiles, setNumFiles] = useState("");
  const [resultFiles, setResultFiles] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [selectedFileDetails, setSelectedFileDetails] = useState(null);
  const [paths, setPaths] = useState([]); // For storing paths from PATH_CONFIG
  const [selectedPath, setSelectedPath] = useState(""); // For storing the selected path
  const [hasSearched, setHasSearched] = useState(false); // To track if search has been initiated
  const router = useRouter();

  // Fetch paths from the backend
  useEffect(() => {
    const fetchPaths = async () => {
      try {
        const response = await fetch(
          "http://localhost:5000/api/get-path-config"
        );
        if (response.ok) {
          const data = await response.json();
          setPaths(data.paths || []);
          setSelectedPath(data.paths?.[0] || ""); // Default to the first path
        } else {
          setErrorMessage("Failed to fetch paths from the server.");
        }
      } catch (error) {
        setErrorMessage(`Unexpected error: ${error.message}`);
      }
    };

    fetchPaths();
  }, []);

  const handleSearch = async () => {
    if (!searchWord || !numFiles || !selectedPath) {
      alert("Please fill in all fields.");
      return;
    }

    setIsSearching(true);
    setResultFiles([]);
    setErrorMessage("");
    setSelectedFileDetails(null);
    setHasSearched(true); // Mark that the user has initiated a search

    try {
      const response = await fetch("http://localhost:5000/api/run-wal-check", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          keyword: searchWord,
          number_of_files: numFiles,
          selected_path: selectedPath, // Include the selected path
        }),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.status === "success") {
          // Filter out files with empty content
          const nonEmptyFiles = result.matched_files?.filter(
            (file) => Array.isArray(file.content) && file.content.length > 0 // Check for non-empty arrays
          );
          setResultFiles(nonEmptyFiles || []);
        } else {
          setErrorMessage(result.message || "An unknown error occurred.");
        }
      } else {
        const error = await response.json();
        setErrorMessage(error.message || "Failed to fetch results.");
      }
    } catch (error) {
      setErrorMessage(`Unexpected error: ${error.message}`);
    } finally {
      setIsSearching(false);
    }
  };

  const handleFileClick = (file) => {
    setSelectedFileDetails(file);
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-500 to-blue-700 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl p-8 w-full max-w-4xl">
        <h1 className="text-4xl font-bold text-blue-600 text-center mb-6">
          WAL Checker
        </h1>

        {/* Select Path */}
        <div>
          <label
            htmlFor="pathSelector"
            className="block text-gray-700 font-semibold mb-2"
          >
            Select Path:
          </label>
          <select
            id="pathSelector"
            value={selectedPath}
            onChange={(e) => setSelectedPath(e.target.value)}
            className="w-full border border-gray-300 rounded-lg py-2 px-4 focus:ring-2 focus:ring-blue-500 outline-none"
          >
            {paths.map((path, index) => (
              <option key={index} value={path}>
                {path}
              </option>
            ))}
          </select>
        </div>

        {/* Search Inputs */}
        <div className="space-y-6 mt-4">
          <div>
            <label
              htmlFor="searchWord"
              className="block text-gray-700 font-semibold mb-2"
            >
              Word to Search:
            </label>
            <input
              id="searchWord"
              type="text"
              value={searchWord}
              onChange={(e) => setSearchWord(e.target.value)}
              className="w-full border border-gray-300 rounded-lg py-2 px-4 focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="Enter the word to search"
            />
          </div>

          <div>
            <label
              htmlFor="numFiles"
              className="block text-gray-700 font-semibold mb-2"
            >
              Number of Files to Search:
            </label>
            <input
              id="numFiles"
              type="number"
              value={numFiles}
              onChange={(e) => setNumFiles(e.target.value)}
              className="w-full border border-gray-300 rounded-lg py-2 px-4 focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="Enter the number of files"
            />
          </div>

          {/* Search Button */}
          <button
            onClick={handleSearch}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition duration-300"
            disabled={isSearching}
          >
            {isSearching ? "Searching..." : "Search Logs"}
          </button>
        </div>

        {/* Error Message */}
        {errorMessage && (
          <p className="text-red-500 font-semibold mt-4 text-center">
            {errorMessage}
          </p>
        )}

        {/* Results Section */}
        {!isSearching && resultFiles.length > 0 && (
          <div className="mt-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Files Contain "{searchWord}" :
            </h2>
            <ul className="space-y-2">
              {resultFiles.map((file, index) => (
                <li
                  key={index}
                  className="text-blue-600 cursor-pointer hover:underline"
                  onClick={() => handleFileClick(file)}
                >
                  {file.wal_file}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* No Results Message */}
        {!isSearching && hasSearched && resultFiles.length === 0 && (
          <p className="text-red-500 font-semibold mt-4 text-center">
            No files with content found for the word "{searchWord}".
          </p>
        )}

        {selectedFileDetails && (
          <div className="mt-6">
            <h3 className="text-xl font-semibold mb-2 text-gray-700">
              File:{" "}
              <span className="text-blue-600">
                {selectedFileDetails.wal_file}
              </span>
            </h3>
            <div
              className="border border-gray-300 rounded-lg bg-gray-50 p-4 overflow-auto"
              style={{ maxHeight: "300px" }}
            >
              {selectedFileDetails.content?.length > 0 && (
                <>
                  {/* Display Errors */}
                  {selectedFileDetails.content.some((line) =>
                    line.includes("error")
                  ) && (
                    <>
                      <h4 className="font-semibold text-red-600">Error:</h4>
                      <pre className="whitespace-pre-wrap text-sm font-mono overflow-x-auto">
                        {selectedFileDetails.content
                          .filter((line) => line.includes("error"))
                          .map((line) => `${line}\n`)
                          .join("\n")}
                      </pre>
                    </>
                  )}

                  {/* Display Non-Error Lines */}
                  <h4 className="font-semibold text-gray-600 mt-4">
                    Lines With "{searchWord}":
                  </h4>
                  <pre className="whitespace-pre-wrap text-sm font-mono overflow-x-auto">
                    {selectedFileDetails.content
                      .filter((line) => !line.includes("error"))
                      .map((line) => `${line}\n`)
                      .join("\n")}
                  </pre>
                </>
              )}

              <h4 className="font-semibold text-gray-600 mt-4">
                Database Info:
              </h4>
              <pre className="whitespace-pre-wrap text-sm font-mono overflow-x-auto">
                {selectedFileDetails.db_info?.database_name
                  ? `Name: ${selectedFileDetails.db_info.database_name}\nDir: ${selectedFileDetails.db_info.database_dir}`
                  : `Dir: ${selectedFileDetails.db_info.unmatched_directories}`}
              </pre>
            </div>
          </div>
        )}

        {/* Back to Home Button */}
        <div className="my-6">
          <button
            onClick={() => router.push("/")}
            className="w-full bg-gray-700 text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition duration-300"
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}

export default WALChecker;
