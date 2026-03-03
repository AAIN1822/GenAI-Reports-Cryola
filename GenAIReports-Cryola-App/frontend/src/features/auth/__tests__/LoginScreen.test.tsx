
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi, describe, it, beforeEach, afterEach, expect } from "vitest";
import { MemoryRouter } from "react-router-dom";
import LoginScreen from "../Pages/LoginScreen";
import { login, ssoLogin } from "../../../api/auth";

// ✅ Mock the API functions
vi.mock("../../../api/auth", () => ({
  login: vi.fn(),
  ssoLogin: vi.fn(),
}));

// ✅ Mock react-router-dom useNavigate
const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<any>("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe("LoginScreen Component", () => {
  let updateScreenMock: React.Dispatch<React.SetStateAction<"login" | "signup" | "forgotPassword" | "resetPassword" | "otp">>;

  beforeEach(() => {
    vi.clearAllMocks();
    updateScreenMock = vi.fn() as React.Dispatch<React.SetStateAction<"login" | "signup" | "forgotPassword" | "resetPassword" | "otp">>;
    
    // ✅ Mock successful login by default
    (login as unknown as vi.Mock).mockResolvedValue({ data: { message: "Success" } });
    (ssoLogin as unknown as vi.Mock).mockResolvedValue({ data: { message: "SSO Success" } });

    render(
      <MemoryRouter>
        <LoginScreen updateScreen={updateScreenMock} />
      </MemoryRouter>
    );
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders all main UI elements", () => {
    expect(screen.getByText("Login")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Email address")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Password (min. 8 characters)")).toBeInTheDocument();
    expect(screen.getByText("Sign in")).toBeInTheDocument();
    expect(screen.getByText("Forgot password?")).toBeInTheDocument();
    expect(screen.getByText("Sign Up")).toBeInTheDocument();
  });

  it("shows validation errors for empty fields", async () => {
    const button = screen.getByText("Sign in");
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText("Please enter your email.")).toBeInTheDocument();
      expect(screen.getByText("Please enter your password.")).toBeInTheDocument();
    });
  });

  it("calls login API and navigates on valid input", async () => {
    fireEvent.change(screen.getByPlaceholderText("Email address"), { target: { value: "user@example.com" } });
    fireEvent.change(screen.getByPlaceholderText("Password (min. 8 characters)"), { target: { value: "password123" } });

    fireEvent.click(screen.getByText("Sign in"));

    await waitFor(() => {
      expect(login).toHaveBeenCalledWith("user@example.com", "password123");
      expect(mockNavigate).toHaveBeenCalledWith("/campaign");
    });
  });

  it("calls updateScreen('forgotPassword') when clicking Forgot password?", async () => {
    fireEvent.click(screen.getByText("Forgot password?"));
    expect(updateScreenMock).toHaveBeenCalledWith("forgotPassword");
  });

  it("calls updateScreen('signup') when clicking Sign Up", async () => {
    fireEvent.click(screen.getByText("Sign Up"));
    expect(updateScreenMock).toHaveBeenCalledWith("signup");
  });
});
