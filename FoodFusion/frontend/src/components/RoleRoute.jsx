import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.js";

export function RoleRoute({ roles }) {
  const { user, loading } = useAuth();

  if (loading) return <div>Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (!roles.includes(user.active_role)) return <Navigate to="/unauthorized" replace />;
  return <Outlet />;
}
