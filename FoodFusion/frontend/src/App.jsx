import { BrowserRouter, Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "./components/ProtectedRoute.jsx";
import { RoleRoute } from "./components/RoleRoute.jsx";
import { AuthProvider } from "./context/AuthContext.jsx";
import { Dashboard } from "./pages/Dashboard.jsx";
import { Login } from "./pages/Login.jsx";
import { Register } from "./pages/Register.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Any authenticated user */}
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<Dashboard />} />
          </Route>

          {/* Role-gated */}
          <Route element={<RoleRoute roles={["Admin"]} />}>
            <Route path="/admin" element={<div><h1>Admin Panel</h1></div>} />
          </Route>

          <Route element={<RoleRoute roles={["RestaurantOwner"]} />}>
            <Route path="/restaurant" element={<div><h1>Restaurant Dashboard</h1></div>} />
          </Route>

          <Route element={<RoleRoute roles={["DeliveryPerson"]} />}>
            <Route path="/delivery" element={<div><h1>Delivery Dashboard</h1></div>} />
          </Route>

          <Route path="/unauthorized" element={<div><h1>403 — Unauthorized</h1></div>} />
          <Route path="*" element={<div><h1>404 — Not Found</h1></div>} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
