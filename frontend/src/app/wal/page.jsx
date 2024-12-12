"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

function WALChecker() {
  const [searchWord, setSearchWord] = useState("");
  const [numFiles, setNumFiles] = useState("");
  const [resultFiles, setResultFiles] = useState([]);
  const router = useRouter();

  const handleSearch = () => {
    if (!searchWord || !numFiles) {
      alert("Please fill in both the word to search and the number of files.");
      return;
    }

    // Simulate backend search logic
    const mockFiles = [
      "file1.log",
      "file2.log",
      "file3.log",
      "file4.log",
      "file5.log",
    ];

    // Mock: Simulate search in first 'numFiles'
    const filesContainingWord = mockFiles
      .slice(0, parseInt(numFiles, 10))
      .filter((file) => file.includes(searchWord));

    setResultFiles(filesContainingWord);
  };

  return (
    <div className="min-h-screen bg-blue-500 flex flex-col items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg p-8 w-4/5 max-w-lg">
        <h1 className="text-3xl font-bold text-gray-700 mb-6 text-center">WAL Checker</h1>

        {/* Back Button */}
        

        {/* Input for Word to Search */}
        <div className="mb-4">
          <label htmlFor="searchWord" className="block text-gray-700 font-semibold mb-2">
            Word to Search:
          </label>
          <input
            id="searchWord"
            type="text"
            value={searchWord}
            onChange={(e) => setSearchWord(e.target.value)}
            className="w-full border border-gray-300 rounded py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter the word to search"
          />
        </div>

        {/* Input for Number of Files */}
        <div className="mb-4">
          <label htmlFor="numFiles" className="block text-gray-700 font-semibold mb-2">
            Number of Files to Search:
          </label>
          <input
            id="numFiles"
            type="number"
            value={numFiles}
            onChange={(e) => setNumFiles(e.target.value)}
            className="w-full border border-gray-300 rounded py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter the number of files"
          />
        </div>

        {/* Search Button */}
        <button
          onClick={handleSearch}
          className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 w-full font-semibold"
        >
          Search
        </button>

        {/* Result Section */}
        {resultFiles.length > 0 && (
          <div className="mt-6">
            <h2 className="text-xl font-semibold text-gray-700 mb-4">Files Containing "{searchWord}":</h2>
            <ul className="list-disc pl-5">
              {resultFiles.map((file, index) => (
                <li key={index} className="text-gray-600">
                  {file}
                </li>
              ))}
            </ul>
          </div>
        )}

        {resultFiles.length === 0 && searchWord && (
          <p className="text-red-500 font-semibold mt-4">No files contain the word "{searchWord}".</p>
        )}
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

export default WALChecker;
