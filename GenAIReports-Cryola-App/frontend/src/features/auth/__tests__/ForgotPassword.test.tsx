import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, beforeAll } from "vitest";
import { MemoryRouter } from "react-router-dom";
import ForgotPassword from "../Pages/ForgotPassword";
import { forgotPassword } from "../../../api/auth";

// ✅ Mock updateScreen function
const mockUpdateScreen = vi.fn();

// ✅ Mock API
vi.mock("../../../api/auth", () => ({
  forgotPassword: vi.fn(),
}));

describe("ForgotPassword Component", () => {
  beforeAll(() => {
    vi.clearAllMocks();
  });

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders all elements correctly", () => {
    render(
      <MemoryRouter>
        <ForgotPassword updateScreen={mockUpdateScreen} />
      </MemoryRouter>
    );

    expect(screen.getByPlaceholderText(/Enter your email address/i)).toBeInTheDocument();
    expect(screen.getByText(/Forgot Password/i)).toBeInTheDocument();
    expect(screen.getByText(/We got your back/i)).toBeInTheDocument();
    expect(screen.getByTestId("signup-link")).toBeInTheDocument();
  });

  it("shows error when email is empty", async () => {
    render(
      <MemoryRouter>
        <ForgotPassword updateScreen={mockUpdateScreen} />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByText(/Send Reset Link/i));

    expect(await screen.findByTestId("email-error")).toHaveTextContent("Email is required.");
  });

  it("shows error when email is invalid", async () => {
    render(
      <MemoryRouter>
        <ForgotPassword updateScreen={mockUpdateScreen} />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByPlaceholderText(/Enter your email address/i), {
      target: { value: "invalid-email" },
    });

    fireEvent.click(screen.getByText(/Send Reset Link/i));

    expect(await screen.findByTestId("email-error")).toHaveTextContent("Enter a valid email address.");
  });

  it("calls forgotPassword API and shows success message", async () => {
    (forgotPassword as unknown as vi.Mock).mockResolvedValue({
      data: { message: "Reset link sent successfully!" },
    });

    render(
      <MemoryRouter>
        <ForgotPassword updateScreen={mockUpdateScreen} />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByPlaceholderText(/Enter your email address/i), {
      target: { value: "test@example.com" },
    });

    fireEvent.click(screen.getByText(/Send Reset Link/i));

    await waitFor(() => {
      expect(forgotPassword).toHaveBeenCalledWith("test@example.com");
      expect(mockUpdateScreen).toHaveBeenCalledWith("otp");
      expect(screen.getByText("Reset link sent successfully!")).toBeInTheDocument();
    });
  });

  it("calls updateScreen to signup when 'Sign Up' link is clicked", async () => {
    render(
      <MemoryRouter>
        <ForgotPassword updateScreen={mockUpdateScreen} />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByTestId("signup-link"));

    expect(mockUpdateScreen).toHaveBeenCalledWith("signup");
  });
});
