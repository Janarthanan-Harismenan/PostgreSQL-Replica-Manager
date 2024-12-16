import React, { useState } from 'react';
import axios from 'axios';

function CatalogCheck() {
    const [report, setReport] = useState('');

    const handleRunCheck = () => {
        axios.get('http://localhost:5000/api/pg-catcheck')
            .then(response => setReport(response.data.report))
            .catch(error => console.error('Error running catalog check:', error));
    };

    return (
        <div>
            <h2>Catalog Check</h2>
            <button onClick={handleRunCheck}>Run pg_catcheck</button>
            <pre>{report}</pre>
        </div>
    );
}

export default CatalogCheck;
