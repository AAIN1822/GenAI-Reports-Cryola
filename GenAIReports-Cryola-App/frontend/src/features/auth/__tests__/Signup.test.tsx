import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, beforeAll } from "vitest";
import { MemoryRouter } from "react-router-dom";
import Signup from "../Pages/Signup";
import { registerUser } from "../../../api/auth";

// Mock navigate
const mockNavigate = vi.fn();

// Mock the auth module
vi.mock("../../../api/auth", () => ({
  registerUser: vi.fn(),
}));

// Mock react-router-dom
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<any>("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe("Signup Component", () => {
  const updateScreen = vi.fn();

  beforeAll(() => {
    globalThis.alert = vi.fn();
  });

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should call updateScreen('login') when Sign In link is clicked", () => {
    render(
      <MemoryRouter>
        <Signup updateScreen={updateScreen} />
      </MemoryRouter>
    );

    const signInLink = screen.getByText(/sign in/i);
    fireEvent.click(signInLink);

    expect(updateScreen).toHaveBeenCalledWith("login");
  });

  it("should show validation errors when fields are empty", async () => {
    render(
      <MemoryRouter>
        <Signup updateScreen={updateScreen} />
      </MemoryRouter>
    );

    const signUpButton = screen.getByRole("button", { name: /sign up/i });
    fireEvent.click(signUpButton);

    expect(await screen.findByText("Please enter your full name.")).toBeInTheDocument();
    expect(await screen.findByText("Please enter your email.")).toBeInTheDocument();
    expect(await screen.findByText("Please enter a password.")).toBeInTheDocument();
    expect(await screen.findByText("Please confirm your password.")).toBeInTheDocument();
  });

  it("should call registerUser and navigate on successful signup", async () => {
    // Mock API response
    (registerUser as unknown as vi.Mock).mockResolvedValue({
      data: { message: "Signup successful!" },
    });

    render(
      <MemoryRouter>
        <Signup updateScreen={updateScreen} />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByPlaceholderText(/Full Name/i), {
      target: { value: "Test User" },
    });
    fireEvent.change(screen.getByPlaceholderText(/Email address/i), {
      target: { value: "test@example.com" },
    });
    fireEvent.change(screen.getByPlaceholderText("Password"), {
      target: { value: "Password@123" },
    });
    fireEvent.change(screen.getByPlaceholderText("Confirm Password"), {
      target: { value: "Password@123" },
    });

    const signUpButton = screen.getByRole("button", { name: /sign up/i });
    fireEvent.click(signUpButton);

    await waitFor(() => {
      // Ensure API was called with correct args
      expect(registerUser).toHaveBeenCalledWith(
        "Test User",
        "test@example.com",
        "Password@123",
        1
      );
      // Ensure navigation happened
      expect(mockNavigate).toHaveBeenCalledWith("/creative-studio");
    });
  });

  it("should show general error message if signup fails", async () => {
    (registerUser as unknown as vi.Mock).mockRejectedValue({
      response: { data: { message: "Email already exists" } },
    });

    render(
      <MemoryRouter>
        <Signup updateScreen={updateScreen} />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByPlaceholderText(/Full Name/i), {
      target: { value: "Test User" },
    });
    fireEvent.change(screen.getByPlaceholderText(/Email address/i), {
      target: { value: "test@example.com" },
    });
    fireEvent.change(screen.getByPlaceholderText("Password"), {
      target: { value: "Password@123" },
    });
    fireEvent.change(screen.getByPlaceholderText("Confirm Password"), {
      target: { value: "Password@123" },
    });

    const signUpButton = screen.getByRole("button", { name: /sign up/i });
    fireEvent.click(signUpButton);

    expect(await screen.findByText("Email already exists")).toBeInTheDocument();
  });
});
