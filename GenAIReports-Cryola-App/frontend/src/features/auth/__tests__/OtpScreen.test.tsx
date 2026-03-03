import React from "react";
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import { describe, it, vi, beforeEach, beforeAll, expect, afterEach } from "vitest";
import { MemoryRouter } from "react-router-dom";
import OTPScreen from "../Pages/OtpScreen";
import { verifyOtp, resendOtp } from "../../../api/auth";

// Mock API calls
vi.mock("../../../api/auth", () => ({
  verifyOtp: vi.fn(),
  resendOtp: vi.fn(),
}));

// Mock react-router-dom navigate
const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<any>("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock SSOLogin component
vi.mock("../Pages/SSOLogin", () => ({
  default: () => <div data-testid="sso-login">SSOLogin</div>,
}));

describe("OTPScreen Component", () => {
  const updateScreen = vi.fn();

  beforeAll(() => {
    localStorage.setItem("email", "test@example.com");
  });

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllTimers();
    vi.useRealTimers(); // ✅ always restore real timers
  });


  it("renders component correctly", () => {
    render(
      <MemoryRouter>
        <OTPScreen updateScreen={updateScreen} />
      </MemoryRouter>
    );

    expect(screen.getByText(/Reset Password/i)).toBeInTheDocument();
    expect(screen.getByTestId("otp-label")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Verify OTP/i })).toBeInTheDocument();
    expect(screen.getByTestId("sso-login")).toBeInTheDocument();
    expect(screen.getByText(/Sign Up/i)).toBeInTheDocument();
    expect(screen.getByTestId("resend-otp")).toBeInTheDocument();
  });

  it("shows error if OTP is incomplete", async () => {
    render(
      <MemoryRouter>
        <OTPScreen updateScreen={updateScreen} />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByRole("button", { name: /Verify OTP/i }));

    await waitFor(() => {
      expect(screen.getByTestId("otp-error")).toHaveTextContent("Please enter a 6-digit OTP");
    });
  });

  it("calls verifyOtp and updates screen on successful OTP", async () => {
    (verifyOtp as unknown as vi.Mock).mockResolvedValue({
      data: { data: { password_reset_token: "mockToken" } },
    });

    render(
      <MemoryRouter>
        <OTPScreen updateScreen={updateScreen} />
      </MemoryRouter>
    );

    const inputs = screen.getAllByRole("textbox");
    inputs.forEach((input, i) => {
      fireEvent.change(input, { target: { value: (i + 1).toString() } });
    });

    fireEvent.click(screen.getByRole("button", { name: /Verify OTP/i }));

    await waitFor(() => {
      expect(verifyOtp).toHaveBeenCalledWith("test@example.com", "123456");
      expect(updateScreen).toHaveBeenCalledWith("resetPassword");
      expect(localStorage.getItem("passwordResetToken")).toBe("mockToken");
    });
  });

  it("shows OTP error if verifyOtp fails", async () => {
    (verifyOtp as unknown as vi.Mock).mockRejectedValue({
      response: { data: { message: "Invalid OTP" } },
    });

    render(
      <MemoryRouter>
        <OTPScreen updateScreen={updateScreen} />
      </MemoryRouter>
    );

    const inputs = screen.getAllByRole("textbox");
    inputs.forEach((input, i) => {
      fireEvent.change(input, { target: { value: "1" } });
    });

    fireEvent.click(screen.getByRole("button", { name: /Verify OTP/i }));

    await waitFor(() => {
      expect(screen.getByTestId("otp-error")).toHaveTextContent("Invalid OTP");
    });
  });

//  it("resends OTP when Resend button clicked after timer", async () => {
//     (resendOtp as unknown as vi.Mock).mockResolvedValue({ data: {} });

//     // Use fake timers
//     vi.useFakeTimers();

//     render(
//       <MemoryRouter>
//         <OTPScreen updateScreen={updateScreen} />
//       </MemoryRouter>
//     );

//     const resendButton = screen.getByTestId("resend-otp");

//     // Fast-forward 30 seconds
//     vi.advanceTimersByTime(30000);

//     // Wait for React to update canResend -> true
//     await waitFor(() => expect(resendButton).toBeEnabled());

//     // Click resend
//     fireEvent.click(resendButton);

//     // Check API call
//     expect(resendOtp).toHaveBeenCalledWith("test@example.com");
//   }, 30000);

  it("navigates to signup on Sign Up link click", () => {
    render(
      <MemoryRouter>
        <OTPScreen updateScreen={updateScreen} />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByText(/Sign Up/i));
    expect(updateScreen).toHaveBeenCalledWith("signup");
  });
});
``