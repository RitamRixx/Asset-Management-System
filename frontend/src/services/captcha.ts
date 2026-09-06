// hCaptcha site key is public by design (it's embedded in every page
// load) — unlike the secret key, which never leaves the backend.
export const HCAPTCHA_SITE_KEY = process.env.NEXT_PUBLIC_HCAPTCHA_SITE_KEY ?? "";
export const HCAPTCHA_ENABLED = HCAPTCHA_SITE_KEY.length > 0;