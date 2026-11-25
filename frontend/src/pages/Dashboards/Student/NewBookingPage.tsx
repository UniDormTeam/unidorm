import { useState } from "react";
import { useNavigate } from "react-router-dom";

import type { ServiceType } from "./types";

import "./StudentFormPages.css";

const services: {
  value: ServiceType;
  label: string;
  description: string;
}[] = [
  {
    value: "washing_machine",
    label: "ماشین لباس‌شویی",
    description: "رزرو زمان استفاده از ماشین لباس‌شویی",
  },
  {
    value: "vacuum_cleaner",
    label: "جاروبرقی",
    description: "رزرو جاروبرقی خوابگاه",
  },
];

const devices: Record<ServiceType, string[]> = {
  washing_machine: [
    "ماشین لباس‌شویی شماره ۱",
    "ماشین لباس‌شویی شماره ۲",
    "ماشین لباس‌شویی شماره ۳",
  ],
  vacuum_cleaner: [
    "جاروبرقی شماره ۱",
    "جاروبرقی شماره ۲",
  ],
};

const timeSlots = [
  "۰۸:۰۰ تا ۰۹:۰۰",
  "۱۰:۰۰ تا ۱۱:۰۰",
  "۱۲:۰۰ تا ۱۳:۰۰",
  "۱۴:۰۰ تا ۱۵:۰۰",
  "۱۶:۰۰ تا ۱۷:۰۰",
  "۱۸:۰۰ تا ۱۹:۰۰",
];

function NewBookingPage() {
  const navigate = useNavigate();

  const [service, setService] = useState<ServiceType | "">("");
  const [device, setDevice] = useState("");
  const [date, setDate] = useState("");
  const [timeSlot, setTimeSlot] = useState("");
  const [showReview, setShowReview] = useState(false);
  const [showNotice, setShowNotice] = useState(false);

  const today = new Date().toISOString().split("T")[0];

  function handleServiceChange(value: ServiceType) {
    setService(value);
    setDevice("");
    setShowReview(false);
  }

  function handleContinue() {
    if (!service || !device || !date || !timeSlot) return;

    setShowReview(true);
  }

  function handleConfirm() {
    // [MOCK] هنوز API رزرو در بک‌اند وجود ندارد.
    // پس این مرحله نباید به کاربر اعلام کند رزرو واقعاً ثبت شده است.
    setShowNotice(true);
  }

  return (
    <main className="student-form-page" dir="rtl">
      <div className="student-form-container">
        <button
          type="button"
          className="form-back-button"
          onClick={() => navigate("/dashboard")}
        >
          <span>←</span>
          بازگشت به داشبورد
        </button>

        <header className="student-form-header">
          <span className="form-eyebrow">خدمات خوابگاه</span>
          <h1>رزرو امکانات</h1>
          <p>
            خدمت موردنظر و زمان استفاده را انتخاب کنید.
          </p>
        </header>

        <section className="student-form-card">
          <div className="booking-step">
            <span className="step-number">۱</span>
            <div>
              <h2>انتخاب خدمت</h2>
              <p>کدام خدمت را می‌خواهید رزرو کنید؟</p>
            </div>
          </div>

          <div className="service-options">
            {services.map((item) => (
              <button
                key={item.value}
                type="button"
                className={`service-option ${
                  service === item.value ? "selected" : ""
                }`}
                onClick={() => handleServiceChange(item.value)}
              >
                <strong>{item.label}</strong>
                <span>{item.description}</span>
              </button>
            ))}
          </div>

          {service && (
            <>
              <div className="booking-step">
                <span className="step-number">۲</span>
                <div>
                  <h2>انتخاب دستگاه</h2>
                  <p>دستگاه موردنظر خود را انتخاب کنید.</p>
                </div>
              </div>

              <div className="form-field">
                <label htmlFor="booking-device">دستگاه</label>
                <select
                  id="booking-device"
                  value={device}
                  onChange={(event) => {
                    setDevice(event.target.value);
                    setShowReview(false);
                  }}
                >
                  <option value="">انتخاب دستگاه</option>
                  {devices[service].map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </div>
            </>
          )}

          {device && (
            <>
              <div className="booking-step">
                <span className="step-number">۳</span>
                <div>
                  <h2>انتخاب زمان</h2>
                  <p>روز و ساعت موردنظر را مشخص کنید.</p>
                </div>
              </div>

              <div className="form-field">
                <label htmlFor="booking-date">تاریخ</label>
                <input
                  id="booking-date"
                  type="date"
                  min={today}
                  value={date}
                  onChange={(event) => {
                    setDate(event.target.value);
                    setShowReview(false);
                  }}
                />
              </div>

              <div className="form-field">
                <label htmlFor="booking-time">ساعت</label>
                <select
                  id="booking-time"
                  value={timeSlot}
                  onChange={(event) => {
                    setTimeSlot(event.target.value);
                    setShowReview(false);
                  }}
                >
                  <option value="">انتخاب بازه زمانی</option>
                  {timeSlots.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </div>
            </>
          )}

          {!showReview && (
            <button
              type="button"
              className="primary-form-button"
              disabled={!service || !device || !date || !timeSlot}
              onClick={handleContinue}
            >
              بررسی اطلاعات رزرو
            </button>
          )}

          {showReview && (
            <div className="booking-review">
              <div className="booking-step">
                <span className="step-number">۴</span>
                <div>
                  <h2>بررسی اطلاعات</h2>
                  <p>اطلاعات انتخاب‌شده را بررسی کنید.</p>
                </div>
              </div>

              <div className="review-row">
                <span>خدمت</span>
                <strong>
                  {services.find((item) => item.value === service)?.label}
                </strong>
              </div>

              <div className="review-row">
                <span>دستگاه</span>
                <strong>{device}</strong>
              </div>

              <div className="review-row">
                <span>تاریخ</span>
                <strong>{date}</strong>
              </div>

              <div className="review-row">
                <span>ساعت</span>
                <strong>{timeSlot}</strong>
              </div>

              <p className="booking-mock-warning">
                امکان ثبت نهایی رزرو هنوز در بک‌اند فعال نشده است.
                این اطلاعات فعلاً فقط برای نمایش و بررسی هستند.
              </p>

              <button
                type="button"
                className="primary-form-button"
                onClick={handleConfirm}
              >
                تأیید و ادامه
              </button>

              <button
                type="button"
                className="secondary-form-button"
                onClick={() => setShowReview(false)}
              >
                ویرایش اطلاعات
              </button>
            </div>
          )}

          {showNotice && (
            <div className="booking-mock-notice" role="status">
              <strong>رزرو هنوز ثبت نشده است.</strong>
              <p>
                پس از پیاده‌سازی API رزرو در بک‌اند، این مرحله به ثبت واقعی
                درخواست متصل خواهد شد.
              </p>

              <button
                type="button"
                className="secondary-form-button"
                onClick={() => navigate("/dashboard")}
              >
                بازگشت به داشبورد
              </button>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}

export default NewBookingPage;