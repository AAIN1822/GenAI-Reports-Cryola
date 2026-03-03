const CLIENT_ID = import.meta.env.VITE_CLIENT_ID;
const TENANT_ID = import.meta.env.VITE_TENANT_ID;
const REDIRECT_URI = import.meta.env.VITE_REDIRECT_URI;
export const msalConfig = {
  auth: {
    clientId: CLIENT_ID,
    authority: `https://login.microsoftonline.com/${TENANT_ID}`,
    redirectUri: REDIRECT_URI
  },
};