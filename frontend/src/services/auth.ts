import type { LoginResponse } from "../types/user";
import { API_BASE_URL } from "./api";

type LoginCredentials = {
  username: string;
  password: string;
};

export async function login(credentials: LoginCredentials) {

  
  const response = await fetch(
    `${API_BASE_URL}/api/auth/login/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(credentials),
    }
  );

  const contentType = response.headers.get("content-type");
  const isJson = contentType?.includes("application/json");
  
  if (!response.ok) {
    let message = "ورود ناموفق بود";

    if (isJson) {
      const errorData = await response.json();

      message =
        errorData.detail ||
        errorData.username?.[0] ||
        errorData.password?.[0] ||
        message;
    } else {
      message = "پاسخ نامعتبر از سرور دریافت شد.";
    }

    throw new Error(message);
  }

  const data: LoginResponse = await response.json();
  return data;
  
}