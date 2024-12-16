import React, { useState } from 'react';
import axios from 'axios';

function Recovery() {
    const [walFile, setWalFile] = useState('');
    const [replicaDataPath, setReplicaDataPath] = useState('');
    const [message, setMessage] = useState('');

    const handleRecovery = async () => {
        try {
            const response = await axios.post('http://localhost:5000/api/recover-replica', {
                wal_file: walFile,
                replica_data_path: replicaDataPath
            });
            setMessage(response.data.message);
        } catch (err) {
            setMessage('Error during recovery');
        }
    };

    return (
        <div>
            <h2>Recovery</h2>
            <input
                type="text"
                placeholder="WAL File"
                value={walFile}
                onChange={(e) => setWalFile(e.target.value)}
            />
            <input
                type="text"
                placeholder="Replica Data Path"
                value={replicaDataPath}
                onChange={(e) => setReplicaDataPath(e.target.value)}
            />
            <button onClick={handleRecovery}>Recover</button>
            <p>{message}</p>
        </div>
    );
}

export default Recovery;
