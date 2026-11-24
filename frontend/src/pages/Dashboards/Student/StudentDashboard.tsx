
import { useState } from "react";
import {
  Bell,
  UserRound,
  CalendarDays,
  Wrench,
  WashingMachine,
  Wind,
  Megaphone,
  Home,
  ChevronLeft,
} from "lucide-react";

import "./StudentDashboard.css";

import {
  mockStudentProfile,
  mockAnnouncements,
  mockBookings,
  mockFaultRequests,
} from "./data/mockData";

import type {
  DashboardTab,
  ServiceBooking,
} from "./types";

import type { FaultRequest } from "../../../types/maintenance";

// وضعیت رزرو
function BookingStatusLabel({
  booking,
}: {
  booking: ServiceBooking;
}) {
  return (
    <span className="status-label">
      {booking.status_display}
    </span>
  );
}

// کارت رزرو
function BookingCard({
  booking,
}: {
  booking: ServiceBooking;
}) {
  const isWashingMachine =
    booking.service_type === "washing_machine";

  return (
    <div className="booking-card">
      <div className="item-icon">
        {isWashingMachine ? (
          <WashingMachine size={25} />
        ) : (
          <Wind size={25} />
        )}
      </div>

      <div className="booking-info">
        <h3>{booking.service_title}</h3>
        <p>{booking.date_display}</p>
      </div>

      <div className="booking-time">
        <BookingStatusLabel booking={booking} />
        <p>{booking.time_slot}</p>
      </div>
    </div>
  );
}

// کارت درخواست خرابی
function FaultCard({
  fault,
}: {
  fault: FaultRequest;
}) {
  return (
    <div className="fault-card">
      <div className="fault-info">
        <h3>{fault.title}</h3>
        <p>
          {new Date(fault.created_at).toLocaleDateString("fa-IR")}
        </p>
      </div>

      <span className="status-label">
        {fault.status_display}
      </span>
    </div>
  );
}

// اسلایدر اطلاعیه‌ها
function AnnouncementSlider() {
  const [currentIndex, setCurrentIndex] = useState(0);

  const announcement = mockAnnouncements[currentIndex];

  function showPrevious() {
    setCurrentIndex((current) =>
      current === 0
        ? mockAnnouncements.length - 1
        : current - 1
    );
  }

  function showNext() {
    setCurrentIndex((current) =>
      current === mockAnnouncements.length - 1
        ? 0
        : current + 1
    );
  }

  if (!announcement) return null;

  return (
    <section className="announcement-card">
      <div className="announcement-content">
        <span className="section-eyebrow">
          اطلاعیه‌های خوابگاه
        </span>

        <h2>{announcement.title}</h2>

        <p>{announcement.description}</p>
      </div>

      {mockAnnouncements.length > 1 && (
        <>
          <button
            className="slider-button slider-next"
            onClick={showNext}
            aria-label="اطلاعیه بعدی"
          >
            بعدی
          </button>

          <div className="slider-dots">
            {mockAnnouncements.map((item, index) => (
              <button
                key={item.id}
                className={`slider-dot ${
                  index === currentIndex ? "active" : ""
                }`}
                onClick={() => setCurrentIndex(index)}
                aria-label={`رفتن به اطلاعیه ${index + 1}`}
                aria-current={
                  index === currentIndex ? "true" : undefined
                }
              />
            ))}
          </div>

          <button
            className="slider-button slider-previous"
            onClick={showPrevious}
            aria-label="اطلاعیه قبلی"
          >
            قبلی
          </button>
        </>
      )}
    </section>
  );
}

// نوار پایین صفحه
function BottomNav({
  activeTab,
  onChange,
}: {
  activeTab: DashboardTab;
  onChange: (tab: DashboardTab) => void;
}) {
  const items = [
    {
      id: "announcements" as const,
      label: "اطلاعیه‌ها",
      icon: Megaphone,
    },
    {
      id: "bookings" as const,
      label: "رزروها",
      icon: CalendarDays,
    },
    {
      id: "requests" as const,
      label: "درخواست‌ها",
      icon: Wrench,
    },
    {
      id: "home" as const,
      label: "خانه",
      icon: Home,
    },
  ];

  return (
    <nav className="bottom-nav">
      {items.map((item) => {
        const Icon = item.icon;

        return (
          <button
            key={item.id}
            className={`nav-item ${
              activeTab === item.id ? "active" : ""
            }`}
            onClick={() => onChange(item.id)}
            aria-current={
              activeTab === item.id ? "page" : undefined
            }
          >
            <Icon size={21} strokeWidth={1.7} />
            <span>{item.label}</span>
          </button>
        );
      })}
    </nav>
  );
}

// صفحه داشبورد دانشجو
function StudentDashboard() {
  const [activeTab, setActiveTab] =
    useState<DashboardTab>("home");

  const student = mockStudentProfile;

  return (
    <div className="dashboard-page" dir="rtl">

      {/* هدر */}
      <header className="dashboard-header">
        <button
          className="header-icon-button"
          aria-label="اعلان‌ها"
          onClick={() => setActiveTab("announcements")}
        >
          <Bell size={21} />
        </button>

        <div
          className="profile-button"
          aria-label="پروفایل دانشجو"
        >
          <UserRound size={19} />
        </div>
      </header>

      <main className="dashboard-main">

        {/* صفحه خانه */}
        {activeTab === "home" && (
          <>
            <AnnouncementSlider />

            {/* دسترسی سریع */}
            <section className="quick-actions">
              <button
                className="quick-action"
                onClick={() => setActiveTab("requests")}
              >
                <Wrench size={27} />
                <span>ثبت خرابی</span>
              </button>

              <button
                className="quick-action"
                onClick={() => setActiveTab("bookings")}
              >
                <CalendarDays size={27} />
                <span>رزرو خدمات</span>
              </button>
            </section>

            {/* رزروهای پیش‌رو */}
            <section className="dashboard-section">
              <div className="section-header">
                <h2>رزروهای پیش‌رو</h2>

                <button
                  onClick={() => setActiveTab("bookings")}
                >
                  مشاهده همه
                  <ChevronLeft size={15} />
                </button>
              </div>

              <div className="section-list">
                {mockBookings.length > 0 ? (
                  mockBookings.map((booking) => (
                    <BookingCard
                      key={booking.id}
                      booking={booking}
                    />
                  ))
                ) : (
                  <p>هنوز رزروی ثبت نکرده‌اید.</p>
                )}
              </div>
            </section>

            {/* آخرین درخواست‌های خرابی */}
            <section className="dashboard-section">
              <div className="section-header">
                <h2>آخرین درخواست‌های خرابی</h2>

                <button
                  onClick={() => setActiveTab("requests")}
                >
                  مشاهده همه
                  <ChevronLeft size={15} />
                </button>
              </div>

              <div className="fault-list">
                {mockFaultRequests.length > 0 ? (
                  mockFaultRequests.map((fault) => (
                    <FaultCard
                      key={fault.id}
                      fault={fault}
                    />
                  ))
                ) : (
                  <p>هنوز درخواستی ثبت نکرده‌اید.</p>
                )}
              </div>
            </section>

            {/* اطلاعات خوابگاه */}
            <div className="student-room-info">
              <span>{student.dormitory_name}</span>

              <span>
                ساختمان {student.building}، اتاق{" "}
                {student.room_number}
              </span>
            </div>
          </>
        )}

        {/* صفحه درخواست‌های خرابی */}
        {activeTab === "requests" && (
          <section className="dashboard-section">
            <div className="section-header">
              <h2>درخواست‌های خرابی من</h2>
            </div>

            <div className="fault-list">
              {mockFaultRequests.length > 0 ? (
                mockFaultRequests.map((fault) => (
                  <FaultCard
                    key={fault.id}
                    fault={fault}
                  />
                ))
              ) : (
                <p>هنوز درخواستی ثبت نکرده‌اید.</p>
              )}
            </div>
          </section>
        )}

        {/* صفحه رزروها */}
        {activeTab === "bookings" && (
          <section className="dashboard-section">
            <div className="section-header">
              <h2>رزروهای من</h2>
            </div>

            <div className="section-list">
              {mockBookings.length > 0 ? (
                mockBookings.map((booking) => (
                  <BookingCard
                    key={booking.id}
                    booking={booking}
                  />
                ))
              ) : (
                <p>هنوز رزروی ثبت نکرده‌اید.</p>
              )}
            </div>
          </section>
        )}

        {/* صفحه اطلاعیه‌ها */}
        {activeTab === "announcements" && (
          <section>
            <div className="section-header">
              <h2>اطلاعیه‌های خوابگاه</h2>
            </div>

            <AnnouncementSlider />
          </section>
        )}

      </main>

      <BottomNav
        activeTab={activeTab}
        onChange={setActiveTab}
      />
    </div>
  );
}

export default StudentDashboard;
