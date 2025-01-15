"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import ReplicaStatus from "./ReplicaStatus/page"; // Import the ReplicaStatus component

function HomePage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState("replicaStatus");
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(null); // Set initial state to null
  const [isLoading, setIsLoading] = useState(true); // Add loading state

  // Check user authentication status
  useEffect(() => {
    const token = localStorage.getItem("authToken");
    setIsAuthenticated(!!token); // Set true if token exists
    setIsLoading(false); // Stop loading after check is done
  }, []);

  const handleLogin = () => {
    router.push("/login");
  };

  const handleSignup = () => {
    router.push("/signup");
  };

  const handleLogout = () => {
    // Clear authentication token and redirect to login
    localStorage.removeItem("authToken");
    setIsAuthenticated(false);
    router.push("/login");
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

  if (isLoading) {
    // Optionally, you can return a loading spinner or similar here.
    return <div>Loading...</div>;
  }

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      {/* Header Bar */}
      <header className="bg-blue-600 text-white p-4 flex justify-between items-center shadow-md">
        <button onClick={toggleSidebar} className="text-white text-2xl">
          &#9776; {/* Hamburger Menu Icon */}
        </button>
        <div className="text-lg font-bold">GTN Technologies</div>
        <div className="space-x-4">
          {/* {isAuthenticated ? (
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
          )} */}
          <button
            onClick={handleLogout}
            className="text-white font-semibold hover:bg-blue-700 py-2 px-4 rounded transition"
          >
            Logout
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
              { tab: "logFiles", label: "Log" },
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

      {/* Main content wrapper */}
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
        <ReplicaStatus />

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

// "use client";

// import React, { useState, useEffect } from "react";
// import axios from "axios";
// import Papa from "papaparse";

// const Loading = () => (
//   <p className="text-center text-gray-500">Loading data, please wait...</p>
// );

// const ErrorMessage = ({ message }) => (
//   <p className="text-center text-red-500">{message}</p>
// );

// const ReplicaTable = ({ replicas, handlePauseResume }) => (
//   <table className="table-auto w-full border-collapse border border-gray-200">
//     <thead>
//       <tr className="bg-blue-600 text-white text-center">
//         <th className="border border-gray-200 px-4 py-2">Database Name</th>
//         <th className="border border-gray-200 px-4 py-2">Status</th>
//         <th className="border border-gray-200 px-4 py-2">Delay Time</th>
//         <th className="border border-gray-200 px-4 py-2">Actions</th>
//       </tr>
//     </thead>
//     <tbody>
//       {replicas.map((replica) => (
//         <tr key={replica.delay_name} className="hover:bg-blue-50 text-center">
//           <td className="border text-gray-500 border-gray-200 px-4 py-2">
//             {replica.name} : {replica.delay_name}
//           </td>
//           <td
//             className={`border border-gray-200 px-4 py-2 font-semibold ${
//               replica.status === "running"
//                 ? "text-green-600"
//                 : replica.status === "paused"
//                 ? "text-yellow-500"
//                 : "text-gray-500"
//             }`}
//           >
//             {replica.status || "Loading..."}
//           </td>
//           <td className="border text-gray-600 border-gray-200 px-4 py-2">
//             {replica.delay || "N/A"}
//           </td>
//           <td className="border border-gray-200 px-4 py-2 space-x-2">
//             {replica.status !== "loading" && replica.status === "paused" ? (
//               <button
//                 onClick={() => handlePauseResume(replica.delay_name, "resume")}
//                 className={`${
//                   replica.loading
//                     ? "bg-gray-400 text-white cursor-not-allowed opacity-50"
//                     : "bg-green-500 text-white hover:bg-green-600"
//                 } py-1 px-3 rounded`}
//                 disabled={replica.loading}
//               >
//                 Resume
//               </button>
//             ) : replica.status !== "loading" && replica.status === "running" ? (
//               <button
//                 onClick={() => handlePauseResume(replica.delay_name, "pause")}
//                 className={`${
//                   replica.loading
//                     ? "bg-gray-400 text-white cursor-not-allowed opacity-50"
//                     : "bg-red-500 text-white hover:bg-red-600"
//                 } py-1 px-3 rounded`}
//                 disabled={replica.loading}
//               >
//                 Pause
//               </button>
//             ) : null}
//           </td>
//         </tr>
//       ))}
//     </tbody>
//   </table>
// );

// const HomePage = () => {
//   const [replicas, setReplicas] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);

//   // Fetch delay data from CSV
//   const fetchDelayTimes = async () => {
//     try {
//       const response = await axios.get(
//         "http://localhost:5000/api/static/replica_status"
//       );
//       let parsedData = [];
//       Papa.parse(response.data, {
//         complete: (result) => {
//           parsedData = result.data
//             .slice(1) // Skip the header
//             .filter(
//               (row) => row.length > 1 && row.some((cell) => cell.trim() !== "")
//             ); // Filter empty rows
//         },
//         header: false,
//       });

//       const lastThreeRows = parsedData.slice(-3).map((row) => ({
//         name: row[0], // Assuming the first column is the name
//         delay_name: row[1], // Adjust column index if needed
//         delay: row[2],
//       }));

//       return lastThreeRows;
//     } catch (err) {
//       console.error("Error fetching delay times:", err);
//       setError("Failed to fetch delay data.");
//       return [];
//     }
//   };

//   // Fetch status data
//   const fetchStatuses = async () => {
//     try {
//       const response = await axios.get("http://localhost:5000/api/status");
//       return response.data;
//     } catch (err) {
//       console.error("Error fetching status:", err);
//       setError("Failed to fetch status data.");
//       return [];
//     }
//   };

//   // Fetch initial data
//   const fetchInitialData = async () => {
//     try {
//       const delayData = await fetchDelayTimes();
//       setReplicas(
//         delayData.map((item) => ({
//           ...item,
//           status: null, // Initialize status as empty or loading
//           loading: false, // Initialize loading state
//         }))
//       );
//       setLoading(false); // Remove loading spinner

//       const statusData = await fetchStatuses();
//       setReplicas((prevReplicas) =>
//         prevReplicas.map((replica) => ({
//           ...replica,
//           status:
//             statusData.find(
//               (statusItem) => statusItem.delay_name === replica.delay_name
//             )?.status || "Unknown",
//         }))
//       );
//     } catch (err) {
//       console.error("Error fetching initial data:", err);
//       setError("Failed to fetch initial data.");
//     } finally {
//       setLoading(false); // Ensure loading spinner is removed
//     }
//   };

//   // Update delay times every 10 seconds
//   const updateDelays = async () => {
//     try {
//       const delayData = await fetchDelayTimes();
//       setReplicas((prevReplicas) =>
//         prevReplicas.map((replica) => ({
//           ...replica,
//           delay:
//             delayData.find(
//               (delayItem) => delayItem.delay_name === replica.delay_name
//             )?.delay || "N/A",
//         }))
//       );
//     } catch (err) {
//       console.error("Error updating delay times:", err);
//       setError("Failed to update delay times.");
//     }
//   };

//   // Handle pause/resume actions
//   const handlePauseResume = async (delay_name, action) => {
//     setReplicas((prevReplicas) =>
//       prevReplicas.map((replica) =>
//         replica.delay_name === delay_name
//           ? { ...replica, loading: true }
//           : replica
//       )
//     );

//     try {
//       const response = await axios.post(
//         "http://localhost:5000/api/replica/manage",
//         {
//           action,
//           delay_name,
//         }
//       );
//       if (response.data.status) {
//         setReplicas((prevReplicas) =>
//           prevReplicas.map((replica) =>
//             replica.delay_name === delay_name
//               ? {
//                   ...replica,
//                   status: action === "pause" ? "paused" : "running",
//                   loading: false,
//                 }
//               : replica
//           )
//         );
//       } else {
//         console.error("Error updating status:", response.data.error);
//         alert(response.data.error || "Action failed. Please try again.");
//       }
//     } catch (err) {
//       console.error("Error performing action:", err);
//       alert(`Failed to ${action} the replica.`);
//       setReplicas((prevReplicas) =>
//         prevReplicas.map((replica) =>
//           replica.delay_name === delay_name
//             ? { ...replica, loading: false }
//             : replica
//         )
//       );
//     }
//   };

//   useEffect(() => {
//     fetchInitialData(); // Fetch initial delay and status data

//     // Set interval to update delay times every 10 seconds
//     const interval = setInterval(updateDelays, 10000);

//     return () => clearInterval(interval); // Cleanup interval on unmount
//   }, []);

//   return (
//     <div className="p-8">
//       <h1 className="text-3xl font-bold text-center mb-4">Replica Status</h1>
//       {loading && <Loading />}
//       {error && <ErrorMessage message={error} />}
//       {!loading && !error && (
//         <ReplicaTable
//           replicas={replicas}
//           handlePauseResume={handlePauseResume}
//         />
//       )}
//     </div>
//   );
// };

// export default HomePage;
