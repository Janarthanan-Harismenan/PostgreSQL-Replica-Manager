import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";

const useAuth = () => {
  const [isAuthChecked, setIsAuthChecked] = useState(false); // To track if auth check is complete
  const [isAuthenticated, setIsAuthenticated] = useState(false); // To track auth status
  const router = useRouter();

  useEffect(() => {
    const verifyToken = async () => {
      const token = localStorage.getItem("token");
      console.log("Token:", token);

      if (!token) {
        setIsAuthenticated(false);
        setIsAuthChecked(true);
        router.push("/login");
        return;
      }

      try {
        await axios.get("http://localhost:5000/api/protected", {
          headers: { Authorization: token },
        });
        setIsAuthenticated(true);
      } catch (err) {
        console.error("Token validation failed:", err);
        setIsAuthenticated(false);
        router.push("/login");
      } finally {
        setIsAuthChecked(true);
      }
    };

    verifyToken();
  }, [router]);

  return { isAuthChecked, isAuthenticated };
};

export default useAuth;
