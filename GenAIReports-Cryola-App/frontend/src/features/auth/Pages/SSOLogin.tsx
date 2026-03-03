import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMsal } from "@azure/msal-react";
import MDButton from "../../../components/common/MDButton";
import { ssoLogin } from "../../../api/auth";
import MDErrorMessage from "../../../components/common/MDErrorMessage";
import { storeToken, storeUser } from "../../../utils/helpers";
import { getMe } from "../../../api/User";

const SSOLogin: React.FC<{ disabled?: boolean }> = ({ disabled }) => {
  const { instance } = useMsal();
  const navigate = useNavigate();

  const [loading, setLoading] = useState<boolean>(false);
  const [ssoLoginError, setSsoLoginError] = useState<string>("");

  const handleSSOLogin = async () => {
    setLoading(true);
    setSsoLoginError("");
    try {
      const loginResponse = await instance.loginPopup({
        scopes: ["user.read", "email", "openid", "profile"],
      });
      console.log("SSO Login successful:", loginResponse);
      const idToken = loginResponse.idToken; // Microsoft ID Token
      try {
        const ssoLoginres = await ssoLogin(idToken, "designer");
        console.log("SSO Login Response:", ssoLoginres.data);
        storeToken(
          ssoLoginres.data.data.access_token,
          ssoLoginres.data.data.refresh_token
        );
        const meResponse = await getMe();
        console.log("Me Response:", meResponse.data);
        storeUser(meResponse.data.data);
        navigate("/ProjectHistory");
      } catch (error: any) {
        console.error("SSO Login error:", error.response?.data || error);
        if (error.response?.data?.message) {
          setSsoLoginError(error.response.data.message);
        } else {
          setSsoLoginError("SSO Login failed, please try again.");
        }
      } finally {
        setLoading(false);
      }
    } catch (error) {
      console.error("SSO Login failed:", error);
    }
  };

    return (
        <div style={{ width: "100%" }}>
            <MDButton
                text="SSO Login"
                data-testid="sso-login-button"
                onClick={handleSSOLogin}
                disabled={disabled || loading}
                variant="nopad"
                leftIcon={
                <img
                    src="https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg"
                    alt="MS Logo"
                    style={{ width: "18px", height: "18px" }}
                />
                }
            />
            {ssoLoginError && (
                <MDErrorMessage message={ssoLoginError} />
            )}
        </div>
    );
}

export default SSOLogin;
