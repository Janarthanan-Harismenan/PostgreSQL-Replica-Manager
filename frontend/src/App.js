import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './components/LoginPage'; // Import the login page
import MainPage from './components/MainPage'; // Import the main page with tabs
import ReplicaStatus from './components/ReplicaStatus';
import CatalogCheck from './components/CatalogCheck';
import WalSearch from './components/WalSearch';
import Recovery from './components/Recovery';
import PrivateRoute from './components/PrivateRoute'; // Import PrivateRoute

function App() {
    return (
        <Router>
            <Routes>
                {/* Public Route for Login */}
                <Route path="/" element={<LoginPage />} />

                {/* Protected Routes after login */}
                <Route element={<PrivateRoute />}>
                    <Route path="/main" element={<MainPage />}>
                        {/* Nested Routes */}
                        <Route path="replica-status" element={<ReplicaStatus />} />
                        <Route path="catalog-check" element={<CatalogCheck />} />
                        <Route path="wal-search" element={<WalSearch />} />
                        <Route path="recovery" element={<Recovery />} />
                    </Route>
                </Route>
            </Routes>
        </Router>
    );
}

export default App;
