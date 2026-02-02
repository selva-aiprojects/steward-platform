import React, { createContext, useContext, useState, useEffect } from 'react';

const UserContext = createContext();

export const useUser = () => useContext(UserContext);

export const UserProvider = ({ children }) => {
    // Current logged in user. Null means not logged in.
    const [user, setUser] = useState(null);
    const [selectedUser, setSelectedUser] = useState(null); // null = Global Overview (for Admins)
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check local storage for session simulation
        const storedUser = localStorage.getItem('stocksteward_user');
        if (storedUser) {
            const parsedUser = JSON.parse(storedUser);
            setUser(parsedUser);
            // Non-admins default to their own view; Admins default to global
            if (parsedUser.role !== 'ADMIN') {
                setSelectedUser(parsedUser);
            } else {
                setSelectedUser(null);
            }
        }
        setLoading(false);
    }, []);

    const login = (userData) => {
        // userData should include { id, name, role: 'ADMIN' | 'USER', email }
        setUser(userData);
        if (userData.role !== 'ADMIN') {
            setSelectedUser(userData);
        } else {
            setSelectedUser(null);
        }
        localStorage.setItem('stocksteward_user', JSON.stringify(userData));
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem('stocksteward_user');
    };

    const refreshUser = (updatedData) => {
        const newUser = { ...user, ...updatedData };
        setUser(newUser);
        localStorage.setItem('stocksteward_user', JSON.stringify(newUser));
        if (selectedUser?.id === user?.id) {
            setSelectedUser(newUser);
        }
    };

    const isAdmin = user?.role === 'ADMIN';

    return (
        <UserContext.Provider value={{ user, setUser: refreshUser, login, logout, isAdmin, loading, selectedUser, setSelectedUser }}>
            {children}
        </UserContext.Provider>
    );
};
