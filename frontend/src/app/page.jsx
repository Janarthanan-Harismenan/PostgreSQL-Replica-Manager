"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Replica from "./replicaStatus/page";

function HomePage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState("replicaStatus");
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check authentication status on initial render
    const checkAuthStatus = () => {
      const authToken = localStorage.getItem("token");
      setIsAuthenticated(!!authToken); // Set to true if authToken exists

      console.log("authToken :", authToken);
    };

    checkAuthStatus();

    // Listen to storage changes (e.g., logout/login from another tab)
    window.addEventListener("storage", checkAuthStatus);

    // Cleanup listener on component unmount
    return () => {
      window.removeEventListener("storage", checkAuthStatus);
    };
  }, []);

  const handleLogin = () => {
    router.push("/login");
  };

  const handleSignup = () => {
    router.push("/signup");
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsAuthenticated(false);
    // router.push("/login");
  };

  const handleTabClick = (tab) => {
    setActiveTab(tab);
    setIsSidebarOpen(false); // Close the sidebar after selecting a tab
    router.push(`/${tab}`);
  };

  const toggleSidebar = () => {
    setIsSidebarOpen((prev) => !prev);
  };

  const closeSidebar = () => {
    setIsSidebarOpen(false); // Close the sidebar when clicking the close button
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      {/* Header Bar */}
      <header className="bg-blue-600 text-white p-4 flex justify-between items-center shadow-md">
        <button onClick={toggleSidebar} className="text-white text-2xl">
          &#9776; {/* Hamburger Menu Icon */}
        </button>
        <div className="text-lg font-bold">GTN Technologies</div>
        <div className="space-x-4">
          {isAuthenticated ? (
            <button
              onClick={handleLogout}
              className="text-white font-semibold hover:bg-blue-700 py-2 px-4 rounded transition"
            >
              Logout
            </button>
          ) : (
            <>
              <button
                onClick={handleLogin}
                className="text-white font-semibold hover:bg-blue-700 py-2 px-4 rounded transition"
              >
                Login
              </button>
              <button
                onClick={handleSignup}
                className="text-white font-semibold hover:bg-blue-700 py-2 px-4 rounded transition"
              >
                Signup
              </button>
            </>
          )}
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
          <button
            onClick={closeSidebar}
            className="text-white absolute top-4 right-4 text-2xl"
          >
            &#10005; {/* Close Icon */}
          </button>
          <div className="space-y-4">
            {[
              { tab: "catalogCheck", label: "Catalog Check" },
              { tab: "wal", label: "WAL" },
              { tab: "logFiles", label: "Log Files" },
              { tab: "recovery", label: "Recovery" },
            ].map(({ tab, label }) => (
              <button
                key={tab}
                onClick={() => handleTabClick(tab)}
                className={`w-full text-left py-2 px-4 rounded ${
                  activeTab === tab ? "bg-blue-600" : "bg-blue-500"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div
        className={`flex-1 p-8 transition-transform duration-300 ease-in-out ${
          isSidebarOpen ? "ml-64" : ""
        }`}
      >
        {/* Hero Section */}
        <section className="bg-blue-600 text-white rounded-lg p-8 mb-6 shadow-lg">
          <h1 className="text-4xl font-bold mb-4">
            Welcome to GTN Technologies
          </h1>
          <p className="text-lg mb-4">
            Innovative solutions for data management and performance
            optimization. Explore our services and take your systems to the next
            level.
          </p>
          <div className="space-x-4">
            {!isAuthenticated && (
              <>
                <button
                  onClick={handleLogin}
                  className="bg-white text-blue-600 font-semibold py-2 px-4 rounded transition hover:bg-blue-100"
                >
                  Get Started
                </button>
                <button
                  onClick={handleSignup}
                  className="bg-transparent border-2 border-white text-white font-semibold py-2 px-4 rounded transition hover:bg-white hover:text-blue-600"
                >
                  Sign Up
                </button>
              </>
            )}
          </div>
        </section>

        {/* Replica Status Component */}
        <Replica />

        {/* Services Section */}
        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            {
              tab: "catalogCheck",
              title: "Catalog Check",
              description:
                "Ensure the integrity and synchronization of your catalogs.",
              buttonText: "Perform Catalog Check",
            },
            {
              tab: "pointFinder",
              title: "Point Finder",
              description:
                "Where do you want to go? Choose between WAL and Login.",
              buttonText: "Explore Options",
            },
            {
              tab: "recovery",
              title: "Recovery",
              description:
                "Manage system recovery processes to ensure business continuity.",
              buttonText: "Manage Recovery",
            },
          ].map(({ tab, title, description, buttonText }) => (
            <div
              key={tab}
              className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition duration-300"
            >
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                {title}
              </h2>
              <p className="text-gray-600 mb-4">{description}</p>
              <button
                onClick={() => handleTabClick(tab)}
                className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition"
              >
                {buttonText}
              </button>
            </div>
          ))}
        </section>
      </div>
    </div>
  );
}

export default HomePage;
