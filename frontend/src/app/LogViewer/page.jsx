"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

function LogViewer() {
  const [logFiles, setLogFiles] = useState([]);
  const [selectedFileIndex, setSelectedFileIndex] = useState(0);
  const [keyword, setKeyword] = useState("");
  const [fileContent, setFileContent] = useState([]); // Store as a 2D array for before, matched, after content
  const [selectedLineIndex, setSelectedLineIndex] = useState(null); // Track selected matched line
  const [logFetchLoading, setLogFetchLoading] = useState(false); // Loading state for fetching log files
  const [searchLoading, setSearchLoading] = useState(false); // Separate loading state for search
  const [errorMessage, setErrorMessage] = useState("");
  const [noContentMessage, setNoContentMessage] = useState("");
  const router = useRouter();

  // Fetch the last 10 log files on component mount
  useEffect(() => {
    const fetchLogFiles = async () => {
      try {
        setLogFetchLoading(true);
        const response = await fetch("http://localhost:5000/api/fetch-last-10-logs");
        if (response.ok) {
          const data = await response.json();
          setLogFiles(data.log_files || []);
          setSelectedFileIndex(0); // Default to the first file
        } else {
          const error = await response.json();
          setErrorMessage(error.message || "Failed to fetch log files.");
        }
      } catch (error) {
        setErrorMessage(`Unexpected error: ${error.message}`);
      } finally {
        setLogFetchLoading(false);
      }
    };

    fetchLogFiles();
  }, []);

  // Fetch content of the selected file for the given keyword
  const fetchFileContent = async () => {
    if (!keyword.trim()) {
      setErrorMessage("Please enter a keyword.");
      return;
    }

    try {
      setSearchLoading(true);
      setErrorMessage("");
      setFileContent([]); // Reset content on new search
      setNoContentMessage(""); // Reset "no content" message
      setSelectedLineIndex(null); // Reset selected line

      const response = await fetch("http://localhost:5000/api/search-content-of-log-file", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          log_file_name: logFiles[selectedFileIndex],
          keyword,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const content = data.matched_lines || [];
        setFileContent(content);

        if (content.length === 0) {
          setNoContentMessage(`No relevant content found for the keyword: "${keyword}".`);
        }
      } else {
        const error = await response.json();
        setErrorMessage(error.message || "Failed to fetch file content.");
      }
    } catch (error) {
      setErrorMessage(`Unexpected error: ${error.message}`);
    } finally {
      setSearchLoading(false);
    }
  };

  // Handle "Next" button to navigate through files
  const handleNext = () => {
    if (selectedFileIndex < logFiles.length - 1) {
      setSelectedFileIndex(selectedFileIndex + 1);
      setFileContent([]); // Reset content when changing file
      setNoContentMessage(""); // Reset "no content" message
      setSelectedLineIndex(null); // Reset selected line
    }
  };

  // Reset file content when a new file is clicked
  const handleFileClick = (index) => {
    setSelectedFileIndex(index);
    setFileContent([]); // Clear content when a new file is selected
    setNoContentMessage(""); // Reset "no content" message
    setSelectedLineIndex(null); // Reset selected line
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-500 to-blue-700 flex flex-col items-center justify-center">
      <div className="bg-white rounded-lg shadow-2xl p-8 w-full max-w-4xl">
        <h1 className="text-4xl font-bold text-blue-600 text-center mb-6">Log Viewer</h1>

        {logFetchLoading && <p className="text-gray-600 text-center font-semibold">Loading...</p>}

        {errorMessage && <p className="text-red-500 font-semibold text-center">{errorMessage}</p>}

        {!logFetchLoading && logFiles.length > 0 && (
          <>
            <div className="mb-6">
              <h3 className="text-xl font-semibold text-gray-700 mb-2">Available Log Files:</h3>
              <ul className="list-disc pl-5 space-y-1">
                {logFiles.map((file, index) => (
                  <li
                    key={index}
                    className={`text-gray-600 cursor-pointer ${selectedFileIndex === index ? "text-blue-600 font-bold underline" : "hover:underline"}`}
                    onClick={() => handleFileClick(index)} // Handle file click to reset content
                  >
                    {file}
                  </li>
                ))}
              </ul>
            </div>

            <div className="space-y-4">
              <div>
                <label htmlFor="keyword" className="block text-gray-700 font-semibold mb-2">
                  Keyword:
                </label>
                <input
                  id="keyword"
                  type="text"
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg py-2 px-4 focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Enter keyword"
                />
              </div>

              <button
                onClick={fetchFileContent}
                className={`w-full text-white py-3 rounded-lg font-semibold transition duration-300 ${searchLoading ? "bg-blue-300 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"}`}
                disabled={searchLoading}
              >
                {searchLoading ? "Searching..." : "Search"}
              </button>
            </div>

            <div className="mt-6">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">
                Content from: <span className="text-blue-600">{logFiles[selectedFileIndex]}</span>
              </h3>
              <ul>
                {fileContent.map((item, index) => (
                  <li
                    key={index}
                    className="cursor-pointer text-blue-500 hover:underline"
                    onClick={() => setSelectedLineIndex(index)}
                  >
                    <span className="break-words">{item[0]}</span> {/* Matched line */}
                  </li>
                ))}
              </ul>

              {selectedLineIndex !== null && (
                <div className="mt-4 bg-gray-100 p-4 rounded">
                  <h4 className="text-lg font-semibold">Context:</h4>
                  <pre className="text-sm text-gray-800 whitespace-pre-wrap break-words">
                    {fileContent[selectedLineIndex][1].join("\n")} {/* Before context */}
                    {"\n"}
                    <strong>{fileContent[selectedLineIndex][0]}</strong> {/* Matched line */}
                    {"\n"}
                    {fileContent[selectedLineIndex][2].join("\n")} {/* After context */}
                  </pre>
                </div>
              )}
            </div>

            {noContentMessage && <p className="text-gray-700 mt-6 text-center">{noContentMessage}</p>}

            <button
              onClick={handleNext}
              className={`mt-6 w-full text-white py-3 rounded-lg font-semibold transition duration-300 ${selectedFileIndex >= logFiles.length - 1 ? "bg-gray-300 cursor-not-allowed" : "bg-gray-600 hover:bg-gray-700"}`}
              disabled={selectedFileIndex >= logFiles.length - 1}
            >
              Next File
            </button>

            <button
              onClick={() => router.push("/wal")}
              className="mt-6 w-full bg-gray-500 text-white py-3 rounded-lg font-semibold hover:bg-gray-600 transition duration-300"
            >
              Back to WAL Checker
            </button>
          </>
        )}

        {!logFetchLoading && logFiles.length === 0 && (
          <p className="text-red-500 font-semibold mt-4 text-center">No log files found. Please try again later.</p>
        )}
      </div>
    </div>
  );
}

export default LogViewer;