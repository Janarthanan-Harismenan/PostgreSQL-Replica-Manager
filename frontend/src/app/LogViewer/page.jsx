"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

function LogViewer() {
  const [logFiles, setLogFiles] = useState([]);
  const [selectedFileIndex, setSelectedFileIndex] = useState(0);
  const [keyword, setKeyword] = useState("");
  const [fileContent, setFileContent] = useState([]);
  const [selectedLineIndex, setSelectedLineIndex] = useState(null);
  const [logFetchLoading, setLogFetchLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [noContentMessage, setNoContentMessage] = useState("");
  const [numberOfFiles, setNumberOfFiles] = useState(10);
  const [findButtonPressed, setFindButtonPressed] = useState(false); // Track if "Find" has been pressed
  const router = useRouter();

  // Fetch the specified number of log files when the "Find" button is clicked
  const fetchLogFiles = async () => {
    try {
      setLogFetchLoading(true);
      setErrorMessage("");
      setFindButtonPressed(true); // Mark that "Find" has been pressed
      const response = await fetch("http://localhost:5000/api/fetch-last-logs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ number_of_files: numberOfFiles }),
      });
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

  // Fetch content of the selected file for the given keyword
  const fetchFileContent = async () => {
    if (!keyword.trim()) {
      setErrorMessage("Please enter a keyword.");
      return;
    }

    try {
      setSearchLoading(true);
      setErrorMessage("");
      setFileContent([]);
      setNoContentMessage("");
      setSelectedLineIndex(null);

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
      setFileContent([]);
      setNoContentMessage("");
      setSelectedLineIndex(null);
    }
  };

  // Reset file content when a new file is clicked
  const handleFileClick = (index) => {
    setSelectedFileIndex(index);
    setFileContent([]);
    setNoContentMessage("");
    setSelectedLineIndex(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-500 to-blue-700 flex flex-col items-center justify-center">
      <div className="bg-white rounded-lg shadow-2xl p-8 w-full max-w-4xl">
        <h1 className="text-4xl font-bold text-blue-600 text-center mb-6">Log Viewer</h1>

        {logFetchLoading && <p className="text-gray-600 text-center font-semibold">Loading...</p>}

        {errorMessage && <p className="text-red-500 font-semibold text-center">{errorMessage}</p>}

        <div className="mb-6 space-y-4">
          <div>
            <label htmlFor="numberOfFiles" className="block text-gray-700 font-semibold mb-2">
              Number of Files to Fetch:
            </label>
            <input
              id="numberOfFiles"
              type="number"
              value={numberOfFiles}
              onChange={(e) => setNumberOfFiles(Number(e.target.value))}
              className="w-full border border-gray-300 rounded-lg py-2 px-4 focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="Enter number of files"
            />
          </div>

          <button
            onClick={fetchLogFiles}
            className={`w-full text-white py-3 rounded-lg font-semibold transition duration-300 ${
              logFetchLoading ? "bg-blue-300 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
            }`}
            disabled={logFetchLoading}
          >
            {logFetchLoading ? "Finding..." : "Find"}
          </button>
        </div>

        {!logFetchLoading && logFiles.length > 0 && (
          <>
            <div className="mb-6">
              <h3 className="text-xl font-semibold text-gray-700 mb-2">Available Log Files:</h3>
              <ul className="list-disc pl-5 space-y-1">
                {logFiles.map((file, index) => (
                  <li
                    key={index}
                    className={`text-gray-600 cursor-pointer ${
                      selectedFileIndex === index ? "text-blue-600 font-bold underline" : "hover:underline"
                    }`}
                    onClick={() => handleFileClick(index)}
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
                className={`w-full text-white py-3 rounded-lg font-semibold transition duration-300 ${
                  searchLoading ? "bg-blue-300 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
                }`}
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
              className={`mt-6 w-full text-white py-3 rounded-lg font-semibold transition duration-300 ${
                selectedFileIndex >= logFiles.length - 1 ? "bg-gray-300 cursor-not-allowed" : "bg-gray-600 hover:bg-gray-700"
              }`}
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

            {/* <button
              onClick={() => router.push("/")}
              className="mt-6 w-full bg-gray-700 text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition duration-300"
            >
              Back to Home
            </button> */}
          </>
        )}

        {!logFetchLoading && findButtonPressed && logFiles.length === 0 && (
          <p className="text-red-500 font-semibold mt-4 text-center">No log files found. Please try again later.</p>
        )}

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

export default LogViewer;