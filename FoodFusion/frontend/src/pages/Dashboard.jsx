import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.js";

export function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <div>
      <h1>Welcome, {user?.full_name}</h1>
      <p>Email: {user?.email}</p>
      <p>Role: {user?.active_role}</p>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}
