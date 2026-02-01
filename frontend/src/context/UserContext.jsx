import React, { createContext, useContext, useState, useEffect } from 'react';

const UserContext = createContext();

export const useUser = () => useContext(UserContext);

export const UserProvider = ({ children }) => {
    // Current logged in user. Null means not logged in.
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check local storage for session simulation
        const storedUser = localStorage.getItem('stocksteward_user');
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }
        setLoading(false);
    }, []);

    const login = (userData) => {
        // userData should include { id, name, role: 'ADMIN' | 'USER', email }
        setUser(userData);
        localStorage.setItem('stocksteward_user', JSON.stringify(userData));
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem('stocksteward_user');
    };

    const isAdmin = user?.role === 'ADMIN';

    return (
        <UserContext.Provider value={{ user, login, logout, isAdmin, loading }}>
            {children}
        </UserContext.Provider>
    );
};
