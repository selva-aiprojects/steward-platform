import React, { createContext, useContext, useState, useEffect } from 'react';

const UserContext = createContext();

export const useUser = () => useContext(UserContext);

export const UserProvider = ({ children }) => {
    // Current logged in user. Null means not logged in.
    const [user, setUser] = useState(null);
    const [selectedUser, setSelectedUser] = useState(null); // null = Global Overview (for Admins)
    const [loading, setLoading] = useState(true);

    const normalizeRole = (role) => {
        if (!role) return 'TRADER';
        if (role === 'ADMIN') return 'SUPERADMIN';
        if (role === 'USER') return 'TRADER';
        return role;
    };

    useEffect(() => {
        // Check local storage for session simulation
        const storedUser = localStorage.getItem('stocksteward_user');
        if (storedUser) {
            const parsedUser = JSON.parse(storedUser);
            const normalized = { ...parsedUser, role: normalizeRole(parsedUser.role) };
            setUser(normalized);
            // Non-admins default to their own view; Admins default to global
            if (normalized.role !== 'SUPERADMIN' && normalized.role !== 'BUSINESS_OWNER') {
                setSelectedUser(normalized);
            } else {
                setSelectedUser(null);
            }
        }
        setLoading(false);
    }, []);

    const login = (userData) => {
        // userData should include { id, name, role, email }
        const normalized = { ...userData, role: normalizeRole(userData.role) };
        setUser(normalized);
        if (normalized.role !== 'SUPERADMIN' && normalized.role !== 'BUSINESS_OWNER') {
            setSelectedUser(normalized);
        } else {
            setSelectedUser(null);
        }
        localStorage.setItem('stocksteward_user', JSON.stringify(normalized));
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

    const isAdmin = user?.role === 'SUPERADMIN' || user?.role === 'BUSINESS_OWNER';
    const isSuperAdmin = user?.role === 'SUPERADMIN';
    const isBusinessOwner = user?.role === 'BUSINESS_OWNER';
    const isTrader = user?.role === 'TRADER';
    const isAuditor = user?.role === 'AUDITOR';

    return (
        <UserContext.Provider value={{ user, setUser: refreshUser, login, logout, isAdmin, isSuperAdmin, isBusinessOwner, isTrader, isAuditor, loading, selectedUser, setSelectedUser }}>
            {children}
        </UserContext.Provider>
    );
};
