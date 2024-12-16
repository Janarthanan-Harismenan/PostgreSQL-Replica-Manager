import React, { useState } from 'react';
import axios from 'axios';

function WalSearch() {
    const [keyword, setKeyword] = useState('');
    const [previousFiles, setPreviousFiles] = useState(10);
    const [searchResults, setSearchResults] = useState([]);
    const [error, setError] = useState(null);

    const handleSearch = async () => {
        try {
            const response = await axios.post('http://localhost:5000/api/search-wal', {
                keyword,
                previous_files: previousFiles
            });
            setSearchResults(response.data.results);
            setError(null);
        } catch (err) {
            setError('Error searching WAL files');
        }
    };

    return (
        <div>
            <h2>WAL Search</h2>
            <input
                type="text"
                placeholder="Search keyword"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
            />
            <input
                type="number"
                placeholder="Number of previous files"
                value={previousFiles}
                onChange={(e) => setPreviousFiles(Number(e.target.value))}
            />
            <button onClick={handleSearch}>Search WAL</button>

            {error && <p style={{ color: 'red' }}>{error}</p>}

            <ul>
                {searchResults.map((result, index) => (
                    <li key={index}>{result}</li>
                ))}
            </ul>
        </div>
    );
}

export default WalSearch;
