// "use client";

// import { useState } from "react";
// import { useAuth } from "@/contexts/AuthContext";
// import { ApiError } from "@/services/api";
// import { getSsoLoginUrl } from "@/services/auth";

// export default function LoginPage() {
//   const { login } = useAuth();
//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");
//   const [error, setError] = useState<string | null>(null);
//   const [submitting, setSubmitting] = useState(false);
//   const [ssoError, setSsoError] = useState<string | null>(null);

// async function handleMicrosoftLogin() {
//   setSsoError(null);
//   try {
//     const { authorization_url } = await getSsoLoginUrl();
//     window.location.href = authorization_url;
//   } catch {
//     setSsoError("Microsoft sign-in isn't available right now.");
//   }
// }

//   async function handleSubmit(e: React.FormEvent) {
//     e.preventDefault();
//     setError(null);
//     setSubmitting(true);
//     try {
//       await login(email, password);
//     } catch (err) {
//       setError(
//         err instanceof ApiError && err.status === 401
//           ? "Incorrect email or password."
//           : "Something went wrong. Please try again."
//       );
//     } finally {
//       setSubmitting(false);
//     }
//   }

//   return (
//     <div className="flex min-h-screen items-center justify-center bg-surface px-4">
//       <div className="w-full max-w-sm">
//         <div className="mb-8 flex flex-col items-center">
//           <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-primary font-mono text-sm font-bold text-white">
//             AM
//           </div>
//           <h1 className="text-lg font-semibold text-ink">AMS Platform</h1>
//           <p className="text-sm text-subtle">Sign in to manage assets</p>
//         </div>

//         <form
//           onSubmit={handleSubmit}
//           className="rounded-xl border border-border bg-card p-6 shadow-sm"
//         >
//           <div className="mb-4">
//             <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-ink">
//               Email
//             </label>
//             <input
//               id="email"
//               type="email"
//               required
//               autoComplete="username"
//               value={email}
//               onChange={(e) => setEmail(e.target.value)}
//               className="w-full rounded-md border border-border px-3 py-2 text-sm text-ink outline-none focus:border-primary"
//               placeholder="you@company.com"
//             />
//           </div>

//           <div className="mb-5">
//             <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-ink">
//               Password
//             </label>
//             <input
//               id="password"
//               type="password"
//               required
//               autoComplete="current-password"
//               value={password}
//               onChange={(e) => setPassword(e.target.value)}
//               className="w-full rounded-md border border-border px-3 py-2 text-sm text-ink outline-none focus:border-primary"
//               placeholder="••••••••"
//             />
//           </div>
          

//           {error && (
//             <p className="mb-4 rounded-md bg-status-damaged/10 px-3 py-2 text-sm text-status-damaged">
//               {error}
//             </p>
//           )}

//           <button
//             type="submit"
//             disabled={submitting}
//             className="w-full rounded-md bg-primary py-2 text-sm font-medium text-white transition-colors hover:bg-primary-dark disabled:opacity-60"
//           >
//             {submitting ? "Signing in…" : "Sign in"}
//           </button>
//         </form>

//         <p className="mt-6 text-center text-xs text-subtle">
//           Accounts are created by an administrator — there&apos;s no self-signup.
//         </p>
//       </div>
//     </div>
//   );
// }

"use client";

import { useEffect, useRef, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { ApiError } from "@/services/api";
import { getSsoLoginUrl } from "@/services/auth";
import { HCAPTCHA_ENABLED, HCAPTCHA_SITE_KEY } from "@/services/captcha";

declare global {
  interface Window {
    hcaptcha?: {
      render: (container: string | HTMLElement, opts: Record<string, unknown>) => string;
      reset: (widgetId?: string) => void;
      getResponse: (widgetId?: string) => string;
    };
  }
}

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [ssoError, setSsoError] = useState<string | null>(null);
  const [captchaToken, setCaptchaToken] = useState("");
  const captchaContainerRef = useRef<HTMLDivElement>(null);
  const widgetIdRef = useRef<string | undefined>(undefined);

  useEffect(() => {
    if (!HCAPTCHA_ENABLED) return;

    function renderWidget() {
      if (!window.hcaptcha || !captchaContainerRef.current) return;
     widgetIdRef.current = window.hcaptcha.render(captchaContainerRef.current, {
        sitekey: HCAPTCHA_SITE_KEY,
        callback: (token: string) => setCaptchaToken(token),
        "expired-callback": () => setCaptchaToken(""),
      });
    }

    if (window.hcaptcha) {
      renderWidget();
      return;
    }

    const script = document.createElement("script");
    script.src = "https://js.hcaptcha.com/1/api.js";
    script.async = true;
    script.defer = true;
    script.onload = renderWidget;
    document.head.appendChild(script);

    return () => {
      // Leave the script in place across re-mounts (hCaptcha's own docs
      // recommend against removing/re-adding it) — only the widget
      // itself, if any, needs no explicit cleanup here since the whole
      // container unmounts with the page.
    };
  }, []);

   async function handleSubmit(e: React.FormEvent) {
     e.preventDefault();
     setError(null);

    if (HCAPTCHA_ENABLED && !captchaToken) {
      setError("Please complete the CAPTCHA.");
      return;
    }

    setSubmitting(true);
    try {
      await login(email, password, captchaToken);
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 401
          ? "Incorrect email or password."
          : "Something went wrong. Please try again."
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function handleMicrosoftLogin() {
    setSsoError(null);
    try {
      const { authorization_url } = await getSsoLoginUrl();
      window.location.href = authorization_url;
    } catch {
      setSsoError("Microsoft sign-in isn't available right now.");
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center">
          <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-primary font-mono text-sm font-bold text-white">
            AM
          </div>
          <h1 className="text-lg font-semibold text-ink">AMS Platform</h1>
          <p className="text-sm text-subtle">Sign in to manage assets</p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="rounded-xl border border-border bg-card p-6 shadow-sm"
        >
          <div className="mb-4">
            <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-ink">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              autoComplete="username"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-md border border-border px-3 py-2 text-sm text-ink outline-none focus:border-primary"
              placeholder="you@company.com"
            />
          </div>

          <div className="mb-5">
            <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-ink">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md border border-border px-3 py-2 text-sm text-ink outline-none focus:border-primary"
              placeholder="••••••••"
            />
          </div>

          {HCAPTCHA_ENABLED && (
            <div className="mb-5" ref={captchaContainerRef} />
          )}

          {error && (
            <p className="mb-4 rounded-md bg-status-damaged/10 px-3 py-2 text-sm text-status-damaged">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-md bg-primary py-2 text-sm font-medium text-white transition-colors hover:bg-primary-dark disabled:opacity-60"
          >
            {submitting ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <div className="my-4 flex items-center gap-3">
          <div className="h-px flex-1 bg-border" />
          <span className="text-xs text-subtle">or</span>
          <div className="h-px flex-1 bg-border" />
        </div>

        <button
          onClick={handleMicrosoftLogin}
          className="flex w-full items-center justify-center gap-2 rounded-md border border-border bg-card py-2 text-sm font-medium text-ink hover:bg-surface"
        >
          <MicrosoftLogo />
          Sign in with Microsoft
        </button>

        {ssoError && <p className="mt-3 text-center text-sm text-status-damaged">{ssoError}</p>}

        <p className="mt-6 text-center text-xs text-subtle">
          Accounts are created by an administrator — there&apos;s no self-signup.
        </p>
      </div>
    </div>
  );
}

function MicrosoftLogo() {
  return (
    <svg width="16" height="16" viewBox="0 0 21 21">
      <rect x="1" y="1" width="9" height="9" fill="#f25022" />
      <rect x="11" y="1" width="9" height="9" fill="#7fba00" />
      <rect x="1" y="11" width="9" height="9" fill="#00a4ef" />
      <rect x="11" y="11" width="9" height="9" fill="#ffb900" />
    </svg>
  );
}