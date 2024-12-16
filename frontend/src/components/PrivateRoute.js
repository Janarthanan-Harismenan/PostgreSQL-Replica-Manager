import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

// Check if user is authenticated (e.g., based on localStorage)
const isAuthenticated = () => {
    return localStorage.getItem('authenticated') === 'true'; // or any other check for authentication
};

const PrivateRoute = () => {
    return isAuthenticated() ? <Outlet /> : <Navigate to="/" />; // If authenticated, render nested routes (Outlet), else redirect to login
};

export default PrivateRoute;
