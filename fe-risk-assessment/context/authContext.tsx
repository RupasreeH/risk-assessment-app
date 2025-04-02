import { AuthContextType, UserType } from "@/types";
import { useRouter } from "expo-router";
import { createContext, useContext, useEffect, useState } from "react";

const AuthContext = createContext<AuthContextType | null>(null);

const url = "http://192.168.1.69:5757";

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<UserType>(null);
  const [results, setResults] = useState<any>();

  const router = useRouter();

  useEffect(() => {
    if (user) {
      router.replace("/(tabs)");
    } else {
      router.replace("/(auth)/welcome");
    }
  }, [user]);

  const login = async (email: string, password: string) => {
    try {
      const rawResponse = await fetch(`${url}/users/login`, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email: email, password: password }),
      });
      const content = await rawResponse.json();
      return { success: true, msg: content, status_code: rawResponse.status };
    } catch (error: any) {
      let msg = error.message;
      return { success: false, msg };
    }
  };

  const register = async (
    firstName: string,
    lastName: string,
    email: string,
    password: string
  ) => {
    try {
      const response = await fetch(`${url}/users/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          firstName: firstName,
          lastName: lastName,
          email: email,
          password: password,
        }),
      });
      const content = await response.json();
      return { success: true, msg: content, status_code: response.status };
    } catch (error: any) {
      let msg = error.message;
      return { success: false, msg };
    }
  };

  const search = async (search: string) => {
    try {
      const rawResponse = await fetch(
        `${url}/risksearch/?searchName=${search}`,
        {
          method: "GET",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
        }
      );
      const content = await rawResponse.json();
      return { success: true, msg: content, status_code: rawResponse.status };
    } catch (error: any) {
      let msg = error.message;
      return { success: false, msg };
    }
  };

  const extract = async (searchName: string, selectedUrls: string[]) => {
    try {
      const response = await fetch(`${url}/risksearch/extract`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          searchName: searchName,
          selectedUrls: selectedUrls,
        }),
      });
      const content = await response.json();
      return { success: true, msg: content, status_code: response.status };
    } catch (error: any) {
      let msg = error.message;
      return { success: false, msg };
    }
  };

  const userDetails = async (email: string) => {
    try {
      const rawResponse = await fetch(`${url}/users/details?email=${email}`, {
        method: "GET",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
      });
      const content = await rawResponse.json();
      return { success: true, msg: content, status_code: rawResponse.status };
    } catch (error: any) {
      let msg = error.message;
      return { success: false, msg };
    }
  };

  const updateUser = async (
    firstName: string,
    lastName: string,
    email: string,
    oldPassword: string,
    newPassword: string
  ) => {
    try {
      const response = await fetch(`${url}/users/update-user`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          firstName: firstName,
          lastName: lastName,
          email: email,
          oldPassword: oldPassword,
          newPassword: newPassword,
        }),
      });
      const content = await response.json();
      return { success: true, msg: content, status_code: response.status };
    } catch (error: any) {
      let msg = error.message;
      return { success: false, msg };
    }
  };

  const forgotPassword = async (email: string) => {
    try {
      const response = await fetch(`${url}/users/forgot-password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email,
        }),
      });
      const content = await response.json();
      return { success: true, msg: content, status_code: response.status };
    } catch (error: any) {
      let msg = error.message;
      return { success: false, msg };
    }
  };

  const contextValue: AuthContextType = {
    user,
    setUser,
    login,
    register,
    search,
    results,
    setResults,
    userDetails,
    updateUser,
    forgotPassword,
    extract,
  };

  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be wrapped inside AuthProvider");
  }
  return context;
};
