import { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  UserRound,
  CalendarDays,
  Wrench,
  WashingMachine,
  Wind,
  Megaphone,
  Home,
  ChevronLeft,
  ChevronRight,
  X,
} from "lucide-react";

import "./StudentDashboard.css";

import {
  mockAnnouncements,
  mockBookings,
  mockFaultRequests,
} from "./data/mockData";

import type {
  DashboardTab,
  ServiceBooking,
} from "./types";

import type { FaultRequest } from "../../../types/maintenance";
import { getAuthSession } from "../../../services/authSession";

// تاریخ اطلاعیه
function getAnnouncementDate(
  announcement: (typeof mockAnnouncements)[number]
) {
  // ممکن است تاریخ در داده‌های فعلی Mock هنوز تعریف نشده باشد.
  const item = announcement as typeof announcement & {
    created_at?: string;
  };

  if (!item.created_at) return null;

  const date = new Date(item.created_at);

  if (Number.isNaN(date.getTime())) return null;

  return date.toLocaleDateString("fa-IR");
}

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

// اسلایدشو اطلاعیه‌ها؛ فقط در صفحه خانه
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

  const announcementDate = getAnnouncementDate(announcement);

  return (
    <section className="announcement-card">
      <div className="announcement-content">
        <span className="section-eyebrow">
          اطلاعیه‌های خوابگاه
        </span>

        <h2>{announcement.title}</h2>

        <p>{announcement.description}</p>

        {announcementDate && (
          <span className="announcement-date">
            تاریخ انتشار: {announcementDate}
          </span>
        )}
      </div>

      {mockAnnouncements.length > 1 && (
        <>
          <button
            type="button"
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
                type="button"
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
            type="button"
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

// فهرست اطلاعیه‌ها با صفحه‌بندی
function AnnouncementsList() {
  const [currentPage, setCurrentPage] = useState(1);

  const itemsPerPage = 7;
  const totalPages = Math.ceil(
    mockAnnouncements.length / itemsPerPage
  );

  const startIndex = (currentPage - 1) * itemsPerPage;

  const visibleAnnouncements = mockAnnouncements.slice(
    startIndex,
    startIndex + itemsPerPage
  );

  function goToPreviousPage() {
    setCurrentPage((page) => Math.max(1, page - 1));
  }

  function goToNextPage() {
    setCurrentPage((page) =>
      Math.min(totalPages, page + 1)
    );
  }

  return (
    <section className="announcements-page">
      <div className="section-header">
        <h2>اطلاعیه‌های خوابگاه</h2>

        <span className="announcements-count">
          {mockAnnouncements.length} اطلاعیه
        </span>
      </div>

      {visibleAnnouncements.length > 0 ? (
        <div className="announcements-list">
          {visibleAnnouncements.map((announcement) => {
            const date = getAnnouncementDate(announcement);

            return (
              <article
                className="announcement-list-card"
                key={announcement.id}
              >
                <div className="announcement-list-icon">
                  <Megaphone size={20} />
                </div>

                <div className="announcement-list-content">
                  <h3>{announcement.title}</h3>

                  {date && (
                    <span className="announcement-date">
                      {date}
                    </span>
                  )}

                  <p>{announcement.description}</p>
                </div>
              </article>
            );
          })}
        </div>
      ) : (
        <div className="empty-state">
          هنوز اطلاعیه‌ای ثبت نشده است.
        </div>
      )}

      {totalPages > 1 && (
        <div className="pagination">
          <button
            type="button"
            onClick={goToPreviousPage}
            disabled={currentPage === 1}
            aria-label="صفحه قبلی"
          >
            <ChevronRight size={18} />
          </button>

          {Array.from(
            { length: totalPages },
            (_, index) => index + 1
          ).map((page) => (
            <button
              type="button"
              key={page}
              className={
                currentPage === page ? "active" : ""
              }
              onClick={() => setCurrentPage(page)}
              aria-current={
                currentPage === page ? "page" : undefined
              }
            >
              {page}
            </button>
          ))}

          <button
            type="button"
            onClick={goToNextPage}
            disabled={currentPage === totalPages}
            aria-label="صفحه بعدی"
          >
            <ChevronLeft size={18} />
          </button>
        </div>
      )}
    </section>
  );
}

// پنل پروفایل
function ProfilePanel({
  onClose,
}: {
  onClose: () => void;
}) {
  const session = getAuthSession();
  const user = session?.user;

  const profile = user?.profile;

  const studentProfile =
    profile && "student_number" in profile
      ? profile
      : null;

  return (
    <div className="profile-panel">
      <div className="profile-panel-header">
        <div className="profile-avatar">
          <UserRound size={22} />
        </div>

        <div className="profile-name">
          <strong>
            {user?.full_name || "کاربر"}
          </strong>
          <span>{user?.role_display || ""}</span>
        </div>

        <button
          type="button"
          className="profile-close-button"
          onClick={onClose}
          aria-label="بستن پروفایل"
        >
          <X size={18} />
        </button>
      </div>

      <div className="profile-details">
        <div>
          <span>شماره دانشجویی</span>
          <strong>
            {studentProfile?.student_number || "ثبت نشده"}
          </strong>
        </div>

        <div>
          <span>شماره تماس</span>
          <strong>
            {user?.phone_number || "ثبت نشده"}
          </strong>
        </div>

        <div>
          <span>خوابگاه</span>
          <strong>
            {studentProfile?.dormitory_name || "ثبت نشده"}
          </strong>
        </div>

        <div>
          <span>ساختمان</span>
          <strong>
            {studentProfile?.building || "ثبت نشده"}
          </strong>
        </div>

        <div>
          <span>شماره اتاق</span>
          <strong>
            {studentProfile?.room_number || "ثبت نشده"}
          </strong>
        </div>

        <div>
          <span>ایمیل</span>
          <strong>
            {user?.email || "ثبت نشده"}
          </strong>
        </div>
      </div>
    </div>
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
  // در محیط RTL اولین آیتم در سمت راست قرار می‌گیرد.
  const items = [
    {
      id: "home" as const,
      label: "خانه",
      icon: Home,
    },
    {
      id: "requests" as const,
      label: "درخواست‌ها",
      icon: Wrench,
    },
    {
      id: "bookings" as const,
      label: "رزروها",
      icon: CalendarDays,
    },
    {
      id: "announcements" as const,
      label: "اطلاعیه‌ها",
      icon: Megaphone,
    },
  ];

  return (
    <nav className="bottom-nav">
      {items.map((item) => {
        const Icon = item.icon;

        return (
          <button
            key={item.id}
            type="button"
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

  const [isProfileOpen, setIsProfileOpen] =
    useState(false);

  const navigate = useNavigate();

  const session = getAuthSession();
  const user = session?.user;

  const profile = user?.profile;

  const studentProfile =
    profile && "student_number" in profile
      ? profile
      : null;

  return (
    <div className="dashboard-page" dir="rtl">
      {/* هدر */}
      <header className="dashboard-header">
        <button
          type="button"
          className="profile-button"
          aria-label="پروفایل دانشجو"
          aria-expanded={isProfileOpen}
          onClick={() =>
            setIsProfileOpen((open) => !open)
          }
        >
          <UserRound size={20} />
        </button>

        {isProfileOpen && (
          <ProfilePanel
            onClose={() => setIsProfileOpen(false)}
          />
        )}
      </header>

      <main className="dashboard-main">
        {/* صفحه خانه */}
        {activeTab === "home" && (
          <>
            <AnnouncementSlider />

            {/* دسترسی سریع */}
            <section className="quick-actions">
              <button
                type="button"
                className="quick-action"
                onClick={() =>
                  navigate("/dashboard/report-fault")
                }
              >
                <Wrench size={27} />
                <span>ثبت خرابی</span>
              </button>

              <button
                type="button"
                className="quick-action"
                onClick={() =>
                  navigate("/dashboard/new-booking")
                }
              >
                <CalendarDays size={27} />
                <span>رزرو خدمات</span>
              </button>
            </section>

            {/* [CHANGE] کنار هم قرار گرفتن رزروهای پیش‌رو و آخرین درخواست‌های خرابی */}
            <div className="dashboard-two-col">
              {/* رزروهای پیش‌رو */}
              <section className="dashboard-section">
                <div className="section-header">
                  <h2>رزروهای پیش‌رو</h2>

                  <button
                    type="button"
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
                    type="button"
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
            </div>

            {/* اطلاعات خوابگاه از بک‌اند */}
            {studentProfile && (
              <div className="student-room-info">
                <span>{studentProfile.dormitory_name}</span>

                <span>
                  ساختمان {studentProfile.building}، اتاق{" "}
                  {studentProfile.room_number}
                </span>
              </div>
            )}
          </>
        )}

        {/* صفحه درخواست‌های خرابی */}
        {activeTab === "requests" && (
          <section className="dashboard-section">
            <button
              type="button"
              className="primary-form-button"
              onClick={() =>
                navigate("/dashboard/report-fault")
              }
            >
              ثبت خرابی جدید
            </button>

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
            <button
              type="button"
              className="primary-form-button"
              onClick={() =>
                navigate("/dashboard/new-booking")
              }
            >
              ثبت رزرو جدید
            </button>

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

        {/* صفحه اطلاعیه‌ها: فهرست صفحه‌بندی‌شده */}
        {activeTab === "announcements" && (
          <AnnouncementsList />
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