import { useEffect, useState } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table" // Assuming shadcn-like components exist or I'll stub basic HTML table
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

export function Users() {
    const [users, setUsers] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Mock fetch for now until we have full connection, or actually fetch if dev server running
        // Consuming valid API response structure
        const mockUsers = [
            { id: 1, email: "admin@stocksteward.ai", full_name: "Admin User", role: "ADMIN", risk_tolerance: "HIGH" },
            { id: 2, email: "trader@stocksteward.ai", full_name: "John Trader", role: "USER", risk_tolerance: "MODERATE" },
        ];
        setUsers(mockUsers);
        setIsLoading(false);
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">User Management</h2>
                    <p className="text-muted-foreground">Manage access and risk profiles.</p>
                </div>
                <Button>Add User</Button>
            </div>

            <div className="rounded-md border bg-card">
                <div className="p-4">
                    <table className="w-full text-sm text-left">
                        <thead className="text-muted-foreground font-medium border-b">
                            <tr>
                                <th className="h-12 px-4 align-middle">Name</th>
                                <th className="h-12 px-4 align-middle">Email</th>
                                <th className="h-12 px-4 align-middle">Role</th>
                                <th className="h-12 px-4 align-middle">Risk Profile</th>
                                <th className="h-12 px-4 align-middle text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map((user) => (
                                <tr key={user.id} className="border-b transition-colors hover:bg-muted/50">
                                    <td className="p-4 font-medium">{user.full_name}</td>
                                    <td className="p-4">{user.email}</td>
                                    <td className="p-4">
                                        <span className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-primary text-primary-foreground hover:bg-primary/80">
                                            {user.role}
                                        </span>
                                    </td>
                                    <td className="p-4">
                                        <span className={`inline-flex items-center rounded-md border px-2 py-1 text-xs font-medium ring-1 ring-inset ${user.risk_tolerance === 'HIGH' ? 'bg-red-50 text-red-700 ring-red-600/10 dark:bg-red-900/20 dark:text-red-400' :
                                                'bg-green-50 text-green-700 ring-green-600/20 dark:bg-green-900/20 dark:text-green-400'
                                            }`}>
                                            {user.risk_tolerance}
                                        </span>
                                    </td>
                                    <td className="p-4 text-right">
                                        <Button variant="ghost" size="sm">Edit</Button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}
