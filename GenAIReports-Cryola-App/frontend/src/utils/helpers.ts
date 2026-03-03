import type { User } from "../api/model/MeResponse";

// Simple, practical validator (fast & readable)
export function isValidEmail(email: string): boolean {
  if (!email || typeof email !== "string") return false;
  // Basic, widely-used pattern: not perfect RFC5322 but solid in practice
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email.trim());
}

export const validatePassword = (password: string) => {
  const regex =
    /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;
  return regex.test(password);
};

export const logoutUser = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("loggedIn");
};

export const storeToken = (access_token: string, refresh_token: string) => {
  localStorage.setItem("access_token", access_token);
  localStorage.setItem("refresh_token", refresh_token);
};

export const storeUser = (user: User) => {
  localStorage.setItem("id", user.id);
  localStorage.setItem("name", user.name);
  localStorage.setItem("login_type", user.login_type);
};

export const isSSO = () => {
  return localStorage.getItem("login_type") == "SSO";
};

export const downloadImageFromUrl = (url: string): void => {
  const fileName = decodeURIComponent(
    url.split("/").pop()?.split("?")[0] || "file"
  );
  const a = document.createElement("a");
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  a.remove();
};
