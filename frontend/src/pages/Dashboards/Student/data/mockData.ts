import type { StudentProfile } from "../../../../types/user";
import type { FaultRequest } from "../../../../types/maintenance";
import type { Announcement, ServiceBooking } from "../types";

export const mockStudentProfile: StudentProfile = {
  student_number: "40112345",
  is_dorm_resident: true,
  dormitory_name: "خوابگاه شهید چمران",
  building: "B",
  room_number: "204",
  phone_number: "09123456789",
};

export const mockAnnouncements: Announcement[] = [
  {
    id: 1,
    title: "سرویس دوره‌ای سیستم‌های خوابگاه",
    description: "رفت‌وشوی راهروهای خوابگاه شنبه از ساعت ۹ تا ۱۲ در دسترس نیست.",
    created_at: "2026-11-23T10:00:00",
    is_important: true,
  },
  {
    id: 2,
    title: "اطلاعیه رزرو خدمات",
    description: "دانشجویان می‌توانند برای استفاده از خدمات خوابگاه از بخش رزرو اقدام کنند.",
    created_at: "2026-11-22T09:00:00",
  },
];

export const mockBookings: ServiceBooking[] = [
  {
    id: 1,
    service_type: "washing_machine",
    service_title: "ماشین لباس‌شویی",
    device_label: "ماشین لباس‌شویی شماره ۲",
    date_display: "امروز، ۲۲ آبان",
    time_slot: "۱۸:۰۰ تا ۱۹:۰۰",
    status: "confirmed",
    status_display: "تأییدشده",
  },
  {
    id: 2,
    service_type: "vacuum_cleaner",
    service_title: "جاروبرقی",
    device_label: "جاروبرقی شماره ۱",
    date_display: "فردا، ۲۳ آبان",
    time_slot: "۱۶:۰۰ تا ۱۶:۳۰",
    status: "confirmed",
    status_display: "تأییدشده",
  },
];

export const mockFaultRequests: FaultRequest[] = [
  {
    id: 101,
    title: "چکه کردن شیر آب",
    description: "شیر آب روشویی سرویس بهداشتی چکه می‌کند.",
    category: "facilities",
    room_number: "204",
    created_at: "2026-11-22T14:30:00",
    status: "submitted",
    status_display: "در انتظار بررسی",
  },
  {
    id: 102,
    title: "خرابی چراغ اتاق",
    description: "چراغ اصلی اتاق نیاز به بررسی دارد.",
    category: "repairs",
    room_number: "204",
    created_at: "2026-11-20T10:00:00",
    status: "in_progress",
    status_display: "در حال انجام",
  },
];