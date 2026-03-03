import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import ResetPassword from "../Pages/ResetPassword";
import { resetPassword } from "../../../api/auth"; // adjust path

vi.mock("../../../api/auth", () => ({
  resetPassword: vi.fn(),
}));


describe("ResetPassword Component", () => {
  let updateScreenMock: React.Dispatch<
    React.SetStateAction<"login" | "signup" | "forgotPassword" | "resetPassword" | "otp">
  >;
  let alertMock: (message?: any) => void;

  beforeEach(() => {
    // ✅ Properly typed mocks
    updateScreenMock = vi.fn() as React.Dispatch<
      React.SetStateAction<"login" | "signup" | "forgotPassword" | "resetPassword" | "otp">
    >;
    alertMock = vi.fn();

    // ✅ Assign to globalThis.alert
    (globalThis as any).alert = alertMock;

    render(
      <MemoryRouter>
        <ResetPassword updateScreen={updateScreenMock} />
      </MemoryRouter>
    );
  });

  it("renders all inputs and buttons", () => {
    expect(screen.getByPlaceholderText("Enter new password")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Confirm new password")).toBeInTheDocument();
    expect(screen.getByText("Reset Password")).toBeInTheDocument();
    expect(screen.getByText("Back to Login")).toBeInTheDocument();
  });

  it("shows error if fields are empty", () => {
    fireEvent.click(screen.getByText("Reset Password"));
    expect(screen.getByText("Please fill out both fields.")).toBeInTheDocument();
  });

  it("shows error if password length < 8", () => {
    fireEvent.change(screen.getByPlaceholderText("Enter new password"), { target: { value: "123" } });
    fireEvent.change(screen.getByPlaceholderText("Confirm new password"), { target: { value: "123" } });
    fireEvent.click(screen.getByText("Reset Password"));

    expect(screen.getByText("Password must be at least 8 characters.")).toBeInTheDocument();
  });

  it("shows error if passwords do not match", () => {
    fireEvent.change(screen.getByPlaceholderText("Enter new password"), { target: { value: "12345678" } });
    fireEvent.change(screen.getByPlaceholderText("Confirm new password"), { target: { value: "87654321" } });
    fireEvent.click(screen.getByText("Reset Password"));

    expect(screen.getByText("Passwords do not match.")).toBeInTheDocument();
  });

  it("resets password successfully", async() => {
    fireEvent.change(screen.getByPlaceholderText("Enter new password"), { target: { value: "12345678" } });
    fireEvent.change(screen.getByPlaceholderText("Confirm new password"), { target: { value: "12345678" } });
    fireEvent.click(screen.getByText("Reset Password"));
    (resetPassword as unknown as vi.Mock).mockResolvedValue({ data: { message: "Success" } });
     // ✅ wait for alert to be called after async code completes
    await waitFor(() =>
      expect(alertMock).toHaveBeenCalledWith("Password reset successfully!")
    );
  });

  it("calls updateScreen when Back to Login is clicked", () => {
    fireEvent.click(screen.getByText("Back to Login"));
    expect(updateScreenMock).toHaveBeenCalledWith("login");
  });
});
