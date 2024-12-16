import React from 'react';
import { Link, Outlet } from 'react-router-dom'; // Link for navigation, Outlet for nested routes
import { Tabs, Tab, Box } from '@mui/material'; // MUI components

const MainPage = () => {
    // Define the active tab state
    const [activeTab, setActiveTab] = React.useState(0);

    // Handle tab change
    const handleTabChange = (event, newValue) => {
        setActiveTab(newValue);
    };

    return (
        <div className="p-6">
            <h2 className="flex justify-center text-3xl font-bold mb-6 justify-center">PostgreSQL Replica Manager</h2>

            {/* Material-UI Tabs for Navigation */}
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }} className="mb-4">
                <Tabs
                    value={activeTab}
                    onChange={handleTabChange}
                    aria-label="main-tabs"
                    variant="fullWidth"
                    centered
                >
                    <Tab
                        label="Replica Status"
                        component={Link}
                        to="replica-status"
                        className="text-lg font-medium text-gray-700"
                    />
                    <Tab
                        label="Catalog Check"
                        component={Link}
                        to="catalog-check"
                        className="text-lg font-medium text-gray-700"
                    />
                    <Tab
                        label="Wal Search"
                        component={Link}
                        to="wal-search"
                        className="text-lg font-medium text-gray-700"
                    />
                    <Tab
                        label="Recovery"
                        component={Link}
                        to="recovery"
                        className="text-lg font-medium text-gray-700"
                    />
                </Tabs>
            </Box>

            {/* This is where the nested routes will be displayed */}
            <div>
                <Outlet /> {/* This will render the current active sub-route */}
            </div>
        </div>
    );
};

export default MainPage;
