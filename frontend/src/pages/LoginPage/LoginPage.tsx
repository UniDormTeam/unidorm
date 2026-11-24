

import { useState } from "react";
import type { FormEvent } from "react";
import "./LoginPage.css";
import { login } from "../../services/auth";




function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  /*کاربر نتونه چندتا درخواست بفرسته.اون پایین بزنیم درحال ورود مثلا*/

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (isLoading) return;

    setError("");
    setIsLoading(true);

    try {
      const data = await login({ username, password });
      console.log("Login successful");

    } catch (error) {
        if (error instanceof TypeError) {
            setError("ارتباط با سرور برقرار نشد. لطفاً دوباره تلاش کنید.");
        } else if (error instanceof Error) {
            setError(error.message);
        } else {
            setError("خطای غیرمنتظره‌ای رخ داد.");
        }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main dir="rtl" className="login-page">
      
      <section className="login-card" aria-label="ورود به UniDorm">
        <div className="brand-side">
          <div className="logo-wrap">
            <img className="brand-logo" src="/home-unidorm-logo.png" alt="لوگوی UniDorm" />
          </div>
        </div>

        <div className="form-side">
          
          <p className="form-title">دانشگاه صنعتی نوشیروانی بابل</p>
          <p className="form-subtitle">برای ادامه، وارد حساب کاربری خود شوید.</p>

          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-step">
              <label className="sr-only" htmlFor="username">نام کاربری</label>
              <div className="input-shell">
                <input
                  id="username"
                  name="username"
                  type="text"
                  autoComplete="username"
                  placeholder="شماره دانشجویی/کارمندی"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-step">
              <label className="sr-only" htmlFor="password">رمز عبور</label>
              <div className="input-shell">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  placeholder="رمز عبور"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                />
                <button
                  className="password-toggle"
                  type="button"
                  aria-label={showPassword ? "مخفی کردن رمز عبور" : "نمایش رمز عبور"}
                  onClick={() => setShowPassword((current) => !current)}
                >
                  {showPassword ? (
                    <svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" strokeWidth="1.7">
                      <path d="M3 3l18 18M10.6 10.6a2 2 0 002.8 2.8" strokeLinecap="round" />
                      <path d="M9.9 5.2A10.8 10.8 0 0112 5c5.2 0 8.7 4.6 9.5 6-.3.6-1.2 1.9-2.8 3.2M6.2 6.2C3.9 7.8 2.7 10 2.5 11c.8 1.4 4.3 6 9.5 6 1 0 2-.2 2.8-.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  ) : (
                    <svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" strokeWidth="1.7">
                      <path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z" strokeLinejoin="round" />
                      <circle cx="12" cy="12" r="2.5" />
                    </svg>
                  )}
                </button>
              </div>
            </div>
            {error && (
                  <p className="login-error" role="alert">
                    {error}
                  </p>
                )}

            <div className="form-step">
              <button type="submit" className="login-button" disabled={isLoading}>
                <span>ورود به سامانه</span>
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M14 5l7 7m0 0l-7 7m7-7H3" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
            </div>
          </form>
        </div>
      </section>
    </main>
  );
}

export default LoginPage;
