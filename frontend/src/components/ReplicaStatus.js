import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ReplicaStatus() {
    const [replicaStatus, setReplicaStatus] = useState([]);

    useEffect(() => {
        axios.get('http://localhost:5000/api/replica-status')
            .then(response => setReplicaStatus(response.data))
            .catch(error => console.error('Error fetching replica status:', error));
    }, []);

    const handlePause = (port) => {
        console.log(`Pause button clicked for port: ${port}`);
        // Add logic for pausing replication here
    };

    const handleReceive = (port) => {
        console.log(`Receive button clicked for port: ${port}`);
        // Add logic for receiving replication here
    };

    console.log("replicaStatus : ", replicaStatus)

    return (
        <div className="bg-gray-100 max-h-screen flex justify-center p-4">
            <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-4xl">
                <h2 className="text-center text-2xl font-bold text-gray-800 mb-6">Replica Status</h2>
                <table className="table-auto w-full border-collapse bg-white rounded-lg overflow-hidden shadow">
                    <thead>
                        <tr className="bg-green-500 text-white">
                            <th className="p-3 text-left font-bold">Database Name</th>
                            <th className="p-3 text-left font-bold">Status</th>
                            <th className="p-3 text-left font-bold">Delay Time</th>
                            <th className="p-3 text-left font-bold">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {replicaStatus.map((replica, index) => (
                            <tr 
                                key={index} 
                                className={`border-b ${index % 2 === 0 ? 'bg-gray-100' : 'bg-white'} hover:bg-gray-200`}
                            >
                                <td className="p-3">{replica.database || 'N/A'}</td>
                                <td className="p-3">{replica.status}</td>
                                <td className="p-3">{replica.delay || 'N/A'}</td>
                                <td className="p-3">
                                    <button 
                                        onClick={() => handlePause(replica.port)}
                                        className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded mr-2"
                                    >
                                        Pause
                                    </button>
                                    <button 
                                        onClick={() => handleReceive(replica.port)}
                                        className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded"
                                    >
                                        Receive
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default ReplicaStatus;
