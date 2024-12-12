"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

function HomePage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState("replicaStatus");
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const handleLogin = () => {
    router.push("/login");
  };

  const handleSignup = () => {
    router.push("/signup");
  };

  const handleTabClick = (tab) => {
    setActiveTab(tab);
    setIsSidebarOpen(false); // Close the sidebar after selecting a tab
    router.push(`/${tab}`); // Update the URL
  };

  const toggleSidebar = () => {
    setIsSidebarOpen((prev) => !prev);
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Header Bar */}
      <header className="bg-blue-600 text-white p-4 flex justify-between items-center">
        <button onClick={toggleSidebar} className="text-white text-2xl">
          &#9776; {/* Hamburger Menu Icon */}
        </button>
        <div className="text-lg font-bold">GTN Technologies</div>
        <div className="space-x-4">
          <button
            onClick={handleLogin}
            className="text-white font-semibold hover:bg-blue-700 py-2 px-4 rounded"
          >
            Login
          </button>
          <button
            onClick={handleSignup}
            className="text-white font-semibold hover:bg-blue-700 py-2 px-4 rounded"
          >
            Signup
          </button>
        </div>
      </header>

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-full bg-gray-800 text-white w-64 transform ${
          isSidebarOpen ? "translate-x-0" : "-translate-x-full"
        } transition-transform duration-300 ease-in-out z-50`}
      >
        <div className="p-4">
          <h2 className="text-xl font-bold mb-4">Menu</h2>
          <div className="space-y-4">
            <button
              onClick={() => handleTabClick("replicaStatus")}
              className={`w-full text-left py-2 px-4 rounded ${
                activeTab === "replicaStatus" ? "bg-blue-600" : "bg-blue-500"
              }`}
            >
              Replica Status
            </button>
            <button
              onClick={() => handleTabClick("catalogCheck")}
              className={`w-full text-left py-2 px-4 rounded ${
                activeTab === "catalogCheck" ? "bg-blue-600" : "bg-blue-500"
              }`}
            >
              Catalog Check
            </button>
            <button
              onClick={() => handleTabClick("wal")}
              className={`w-full text-left py-2 px-4 rounded ${
                activeTab === "wal" ? "bg-blue-600" : "bg-blue-500"
              }`}
            >
              WAL
            </button>
            <button
              onClick={() => handleTabClick("recovery")}
              className={`w-full text-left py-2 px-4 rounded ${
                activeTab === "recovery" ? "bg-blue-600" : "bg-blue-500"
              }`}
            >
              Recovery
            </button>
          </div>
        </div>
      </aside>

      {/* Backdrop */}
      {isSidebarOpen && (
        <div
          onClick={toggleSidebar}
          className="fixed inset-0 bg-black opacity-50 z-40"
        ></div>
      )}

      {/* Main content */}
      <main className="flex-1 p-8">
        <h1 className="text-3xl font-bold text-gray-700 mb-6">
          Welcome to GTN Technologies
        </h1>
        <p className="text-lg text-gray-600 mb-6">
          Here you can access various services like Replica Status, Catalog
          Check, WAL, and Recovery.
        </p>

        {/* Content for the active tab */}
        {activeTab === "replicaStatus" && (
          <div>
            <h2 className="text-xl font-semibold text-gray-700">
              Replica Status
            </h2>
            <p>Here you can check the status of the replica.</p>
          </div>
        )}

        {activeTab === "catalogCheck" && (
          <div>
            <h2 className="text-xl font-semibold text-gray-700">
              Catalog Check
            </h2>
            <p>Here you can perform a catalog check.</p>
          </div>
        )}

        {activeTab === "wal" && (
          <div>
            <h2 className="text-xl font-semibold text-gray-700">WAL</h2>
            <p>Here you can monitor Write-Ahead Logging (WAL).</p>
          </div>
        )}

        {activeTab === "recovery" && (
          <div>
            <h2 className="text-xl font-semibold text-gray-700">Recovery</h2>
            <p>Here you can manage system recovery processes.</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default HomePage;
