// import { useMemo, useState } from "react";
// import type { FormEvent } from "react";

// type SectionTab = "dashboard" | "booking" | "repairs" | "announcements";
// type DeviceType = "ماشین لباس‌شویی" | "جاروبرقی";
// type SlotStatus = "available" | "booked_other" | "booked_mine";

// interface TimeSlot {
//   id: string;
//   timeRange: string;
//   location: string;
//   status: SlotStatus;
//   assignedBy: string;
// }

// interface DaySchedule {
//   id: string;
//   dayLabel: string;
//   dateLabel: string;
//   slotsByDevice: Record<DeviceType, TimeSlot[]>;
// }

// interface RepairItem {
//   id: number;
//   title: string;
//   category: string;
//   room: string;
//   date: string;
//   status: "در انتظار بررسی" | "در حال انجام" | "انجام‌شده" | "نامرتبط";
// }

// interface AnnouncementItem {
//   id: number;
//   title: string;
//   description: string;
//   date: string;
// }

// const INITIAL_SCHEDULE: DaySchedule[] = [
//   {
//     id: "day-1",
//     dayLabel: "یکشنبه",
//     dateLabel: "۲۴ آبان",
//     slotsByDevice: {
//       "ماشین لباس‌شویی": [
//         {
//           id: "w-1-1",
//           timeRange: "۰۹:۰۰ تا ۱۰:۰۰",
//           location: "رخت‌شوی‌خانه • دستگاه ۰۱",
//           status: "booked_other",
//           assignedBy: "مسئول نوبت‌دهی",
//         },
//         {
//           id: "w-1-2",
//           timeRange: "۱۰:۰۰ تا ۱۱:۰۰",
//           location: "رخت‌شوی‌خانه • دستگاه ۰۱",
//           status: "available",
//           assignedBy: "مسئول نوبت‌دهی",
//         },
//         {
//           id: "w-1-3",
//           timeRange: "۱۸:۰۰ تا ۱۹:۰۰",
//           location: "رخت‌شوی‌خانه • دستگاه ۰۲",
//           status: "booked_mine",
//           assignedBy: "مسئول نوبت‌دهی",
//         },
//         {
//           id: "w-1-4",
//           timeRange: "۲۰:۰۰ تا ۲۱:۰۰",
//           location: "رخت‌شوی‌خانه • دستگاه ۰۲",
//           status: "available",
//           assignedBy: "مسئول نوبت‌دهی",
//         },
//       ],
//       جاروبرقی: [
//         {
//           id: "v-1-1",
//           timeRange: "۱۵:۰۰ تا ۱۵:۳۰",
//           location: "بلوک ب • اتاق خدمات",
//           status: "available",
//           assignedBy: "مسئول نوبت‌دهی",
//         },
//         {
//           id: "v-1-2",
//           timeRange: "۱۶:۰۰ تا ۱۶:۳۰",
//           location: "بلوک ب • اتاق خدمات",
//           status: "booked_mine",
//           assignedBy: "مسئول نوبت‌دهی",
//         },
//         {
//           id: "v-1-3",
//           timeRange: "۱۷:۳۰ تا ۱۸:۰۰",
//           location: "بلوک ب • اتاق خدمات",
//           status: "booked_other",
//           assignedBy: "مسئول نوبت‌دهی",
//         },
//       ],
//     },
//   },
//   {
//     id: "day-2",
//     dayLabel: "دوشنبه",
//     dateLabel: "۲۵ آبان",
//     slotsByDevice: {
//       "ماشین لباس‌شویی": [
//         {
//           id: "w-2-1",
//           timeRange: "۱۱:۰۰ تا ۱۲:۰۰",
//           location: "رخت‌شوی‌خانه • دستگاه ۰۱",
//           status: "available",
//           assignedBy: "مسئول نوبت‌دهی",
//         },
//         {
//           id: "w-2-2",
//           timeRange: "۱۴:۰۰ تا ۱۵:۰۰",
//           location: "رخت‌شوی‌خانه • دستگاه ۰۲",
//           status: "available",
//           assignedBy: "مسئول نوبت‌دهی",
//         },
//         {
//           id: "w-2-3",
//           timeRange: "۱۹:۰۰ تا ۲۰:۰۰",
//           location: "رخت‌شوی‌خانه • دستگاه ۰۱",
//           status: "booked_other",
//           assignedBy: "مسئول نوبت‌دهی",
//         },
//       ],
//       جاروبرقی: [
//         {
//           id: "v-2-1",
//           timeRange: "۱۰:۳۰ تا ۱۱:۰۰",
//           location: "بلوک ب • اتاق خدمات",
//           status: "available",
//           assignedBy: "مسئول نوبت‌دهی",
//         },
//         {
//           id: "v-2-2",
//           timeRange: "۱۶:۳۰ تا ۱۷:۰۰",
//           location: "بلوک ب • اتاق خدمات",
//           status: "available",
//           assignedBy: "مسئول نوبت‌دهی",
//         },
//       ],
//     },
//   },
//   {
//     id: "day-3",
//     dayLabel: "سه‌شنبه",
//     dateLabel: "۲۶ آبان",
//     slotsByDevice: {
//       "ماشین لباس‌شویی": [
//         {
//           id: "w-3-1",
//           timeRange: "۰۹:۰۰ تا ۱۰:۰۰",
//           location: "رخت‌شوی‌خانه • دستگاه ۰۲",
//           status: "available",
//           assignedBy: "مسئول نوبت‌دهی",
//         },
//         {
//           id: "w-3-2",
//           timeRange: "۱۷:۰۰ تا ۱۸:۰۰",
//           location: "رخت‌شوی‌خانه • دستگاه ۰۱",
//           status: "available",
//           assignedBy: "مسئول نوبت‌دهی",
//         },
//       ],
//       جاروبرقی: [
//         {
//           id: "v-3-1",
//           timeRange: "۱۲:۰۰ تا ۱۲:۳۰",
//           location: "بلوک ب • اتاق خدمات",
//           status: "booked_other",
//           assignedBy: "مسئول نوبت‌دهی",
//         },
//         {
//           id: "v-3-2",
//           timeRange: "۱۸:۰۰ تا ۱۸:۳۰",
//           location: "بلوک ب • اتاق خدمات",
//           status: "available",
//           assignedBy: "مسئول نوبت‌دهی",
//         },
//       ],
//     },
//   },
// ];

// const INITIAL_REPAIRS: RepairItem[] = [
//   {
//     id: 1,
//     title: "چکه‌کردن شیر آب",
//     category: "تأسیسات",
//     room: "اتاق ۲۰۴",
//     date: "۲۲ آبان",
//     status: "در انتظار بررسی",
//   },
//   {
//     id: 2,
//     title: "خرابی چراغ اتاق",
//     category: "برق",
//     room: "اتاق ۲۰۴",
//     date: "۲۰ آبان",
//     status: "در حال انجام",
//   },
//   {
//     id: 3,
//     title: "تعمیر قفل کمد",
//     category: "تجهیزات",
//     room: "اتاق ۲۰۴",
//     date: "۱۸ آبان",
//     status: "انجام‌شده",
//   },
//   {
//     id: 4,
//     title: "قطعی اینترنت دانشگاه",
//     category: "سایر",
//     room: "اتاق ۲۰۴",
//     date: "۱۵ آبان",
//     status: "نامرتبط",
//   },
// ];

// const ANNOUNCEMENTS: AnnouncementItem[] = [
//   {
//     id: 1,
//     title: "سرویس دوره‌ای رخت‌شوی‌خانه",
//     description: "رخت‌شوی‌خانه شنبه از ساعت ۹ تا ۱۲ در دسترس نیست.",
//     date: "۲۱ آبان ۱۴۰۵",
//   },
//   {
//     id: 2,
//     title: "تغییر ساعت تحویل جاروبرقی",
//     description: "تحویل و دریافت جاروبرقی تا ساعت ۲۱ انجام می‌شود.",
//     date: "۲۰ آبان ۱۴۰۵",
//   },
// ];

// function getStatusBadgeStyle(status: RepairItem["status"]) {
//   switch (status) {
//     case "در انتظار بررسی":
//       return "bg-amber-900/6 text-amber-900 border-amber-900/15";
//     case "در حال انجام":
//       return "bg-zinc-900/8 text-zinc-900 border-zinc-900/15";
//     case "انجام‌شده":
//       return "bg-emerald-900/6 text-emerald-900 border-emerald-900/15";
//     case "نامرتبط":
//       return "bg-black/5 text-[#62625e] border-black/10";
//   }
// }

// export default function DashboardPage() {
//   const [activeTab, setActiveTab] = useState<SectionTab>("dashboard");
//   const [schedule, setSchedule] = useState<DaySchedule[]>(INITIAL_SCHEDULE);
//   const [selectedDevice, setSelectedDevice] =
//     useState<DeviceType>("ماشین لباس‌شویی");
//   const [selectedDayId, setSelectedDayId] = useState<string>(
//     INITIAL_SCHEDULE[0].id
//   );
//   const [selectedSlotId, setSelectedSlotId] = useState<string | null>(null);

//   const [repairs, setRepairs] = useState<RepairItem[]>(INITIAL_REPAIRS);
//   const [newTitle, setNewTitle] = useState("");
//   const [newCategory, setNewCategory] = useState("تأسیسات");

//   const currentDay = useMemo(
//     () => schedule.find((d) => d.id === selectedDayId) ?? schedule[0],
//     [schedule, selectedDayId]
//   );

//   const currentSlots = currentDay.slotsByDevice[selectedDevice];

//   const myBookings = useMemo(() => {
//     const list: Array<{
//       id: string;
//       device: DeviceType;
//       dayLabel: string;
//       dateLabel: string;
//       timeRange: string;
//       location: string;
//     }> = [];

//     for (const day of schedule) {
//       (["ماشین لباس‌شویی", "جاروبرقی"] as DeviceType[]).forEach((dev) => {
//         day.slotsByDevice[dev].forEach((slot) => {
//           if (slot.status === "booked_mine") {
//             list.push({
//               id: slot.id,
//               device: dev,
//               dayLabel: day.dayLabel,
//               dateLabel: day.dateLabel,
//               timeRange: slot.timeRange,
//               location: slot.location,
//             });
//           }
//         });
//       });
//     }
//     return list;
//   }, [schedule]);

//   const handleConfirmSlotBooking = () => {
//     if (!selectedSlotId) return;

//     setSchedule((prev) =>
//       prev.map((day) => {
//         if (day.id !== currentDay.id) return day;
//         return {
//           ...day,
//           slotsByDevice: {
//             ...day.slotsByDevice,
//             [selectedDevice]: day.slotsByDevice[selectedDevice].map((slot) =>
//               slot.id === selectedSlotId && slot.status === "available"
//                 ? { ...slot, status: "booked_mine" }
//                 : slot
//             ),
//           },
//         };
//       })
//     );
//     setSelectedSlotId(null);
//   };

//   const handleCancelMySlot = (slotIdToCancel: string) => {
//     setSchedule((prev) =>
//       prev.map((day) => ({
//         ...day,
//         slotsByDevice: {
//           "ماشین لباس‌شویی": day.slotsByDevice["ماشین لباس‌شویی"].map((s) =>
//             s.id === slotIdToCancel ? { ...s, status: "available" } : s
//           ),
//           جاروبرقی: day.slotsByDevice["جاروبرقی"].map((s) =>
//             s.id === slotIdToCancel ? { ...s, status: "available" } : s
//           ),
//         },
//       }))
//     );
//   };

//   const handleAddRepair = (e: FormEvent) => {
//     e.preventDefault();
//     if (!newTitle.trim()) return;

//     setRepairs((prev) => [
//       {
//         id: Date.now(),
//         title: newTitle.trim(),
//         category: newCategory,
//         room: "اتاق ۲۰۴",
//         date: "۲۲ آبان",
//         status: "در انتظار بررسی",
//       },
//       ...prev,
//     ]);
//     setNewTitle("");
//   };

//   const marqueeItems = [...ANNOUNCEMENTS, ...ANNOUNCEMENTS];

//   return (
//     <div dir="rtl" className="ud-shell">
//       <style>{`
//         .ud-shell {
//           box-sizing: border-box;
//           --text: #252525;
//           --muted: #8a8a86;
//           --subtext: #62625e;
//           --charcoal: #252525;
//           --charcoal-soft: #484844;
//           min-height: 100vh;
//           width: 100%;
//           color: var(--text);
//           font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
//           background: linear-gradient(135deg, #f1f0ed 0%, #e8e7e3 52%, #f7f6f3 100%);
//         }

//         .ud-glass {
//           border-radius: 22px;
//           background: rgba(255, 255, 255, 0.52);
//           border: 1px solid rgba(255, 255, 255, 0.9);
//           box-shadow: 0 16px 42px rgba(35, 35, 35, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.95);
//           backdrop-filter: blur(20px);
//           -webkit-backdrop-filter: blur(20px);
//         }

//         .ud-well {
//           border-radius: 16px;
//           background: linear-gradient(145deg, #ffffff, #efeeeb);
//           border: 1px solid rgba(255, 255, 255, 0.96);
//           box-shadow: inset 2px 2px 5px rgba(170, 168, 160, 0.24), inset -2px -2px 6px #ffffff, 0 6px 16px rgba(35, 35, 35, 0.04);
//         }

//         .ud-btn-primary {
//           border: 1px solid rgba(255, 255, 255, 0.65);
//           border-radius: 14px;
//           cursor: pointer;
//           color: #ffffff;
//           background: linear-gradient(110deg, var(--charcoal), var(--charcoal-soft));
//           box-shadow: 0 8px 20px rgba(25, 25, 25, 0.16), inset 0 1px 0 rgba(255, 255, 255, 0.22);
//           transition: transform 200ms ease, box-shadow 200ms ease, opacity 200ms ease;
//         }

//         .ud-btn-primary:hover:not(:disabled) {
//           transform: translateY(-1px);
//           box-shadow: 0 12px 24px rgba(25, 25, 25, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.26);
//         }

//         .ud-btn-primary:disabled {
//           opacity: 0.45;
//           cursor: not-allowed;
//         }

//         .ud-btn-secondary {
//           border-radius: 14px;
//           cursor: pointer;
//           color: var(--text);
//           background: linear-gradient(145deg, #ffffff, #efeeeb);
//           border: 1px solid rgba(255, 255, 255, 0.95);
//           box-shadow: 0 6px 16px rgba(35, 35, 35, 0.05), inset 0 1px 0 #ffffff;
//           transition: transform 200ms ease, box-shadow 200ms ease;
//         }

//         .ud-btn-secondary:hover {
//           transform: translateY(-1px);
//         }

//         .ud-input {
//           width: 100%;
//           border-radius: 15px;
//           padding: 12px 16px;
//           font-size: 14px;
//           color: var(--text);
//           background: linear-gradient(145deg, #ffffff, #efeeeb);
//           border: 1px solid rgba(255, 255, 255, 0.96);
//           box-shadow: inset 2px 2px 5px rgba(170, 168, 160, 0.28), inset -2px -2px 6px #ffffff;
//           outline: none;
//           transition: border-color 200ms ease, box-shadow 200ms ease;
//         }

//         .ud-input:focus {
//           border-color: rgba(55, 55, 55, 0.34);
//           box-shadow: inset 2px 2px 5px rgba(170, 168, 160, 0.2), 0 0 0 3px rgba(55, 55, 55, 0.07);
//         }

//         @keyframes udTickerMove {
//           0% {
//             transform: translateX(0%);
//           }
//           100% {
//             transform: translateX(50%);
//           }
//         }

//         .ud-ticker-track {
//           display: flex;
//           width: max-content;
//           animation: udTickerMove 28s linear infinite;
//         }

//         .ud-ticker-wrap:hover .ud-ticker-track {
//           animation-play-state: paused;
//         }
//       `}</style>

//       {/* نوار اطلاعیه‌های متحرک در بالاترین نقطه صفحه (جایگزین متن خوش‌آمدگویی) */}
//       <div
//         role="region"
//         aria-label="نوار اطلاعیه‌های خوابگاه"
//         className="ud-ticker-wrap w-full overflow-hidden border-b border-white/80 bg-white/60 backdrop-blur-md"
//       >
//         <div className="ud-ticker-track py-2.5">
//           {marqueeItems.map((item, idx) => (
//             <button
//               key={`${item.id}-${idx}`}
//               type="button"
//               onClick={() => setActiveTab("announcements")}
//               className="flex items-center gap-3 px-6 text-xs text-[#252525] hover:opacity-80 cursor-pointer shrink-0"
//             >
//               <span className="inline-block w-1.5 h-1.5 rounded-full bg-[#252525]" />
//               <span className="font-bold">{item.title}:</span>
//               <span className="text-[#62625e]">{item.description}</span>
//               <span className="text-[11px] text-[#8a8a86]">({item.date})</span>
//             </button>
//           ))}
//         </div>
//       </div>

//       {/* هدر بالایی مدرن و مینیمال + تب‌های مستقل هر بخش */}
//       <header className="sticky top-0 z-20 border-b border-white/75 bg-white/55 backdrop-blur-xl">
//         <div className="max-w-6xl mx-auto px-4 sm:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
//           <div className="flex items-center gap-6">
//             <button
//               type="button"
//               onClick={() => setActiveTab("dashboard")}
//               className="text-right cursor-pointer"
//             >
//               <span className="text-xl font-extrabold tracking-tight text-[#252525]">
//                 UniDorm
//               </span>
//               <span className="block text-[11px] text-[#8a8a86]">
//                 خوابگاه سرو • اتاق ۲۰۴
//               </span>
//             </button>

//             <nav className="flex items-center gap-1.5 p-1 rounded-2xl bg-black/[0.04] border border-white/80">
//               {(
//                 [
//                   { id: "dashboard", label: "داشبورد" },
//                   { id: "booking", label: "رزرو خدمات" },
//                   { id: "repairs", label: "درخواست خرابی" },
//                   { id: "announcements", label: "اطلاعیه‌ها" },
//                 ] as const
//               ).map((tab) => {
//                 const active = activeTab === tab.id;
//                 return (
//                   <button
//                     key={tab.id}
//                     type="button"
//                     onClick={() => setActiveTab(tab.id)}
//                     className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer ${
//                       active
//                         ? "bg-gradient-to-l from-[#252525] to-[#484844] text-white shadow-xs"
//                         : "text-[#62625e] hover:text-[#252525]"
//                     }`}
//                   >
//                     {tab.label}
//                   </button>
//                 );
//               })}
//             </nav>
//           </div>

//           <div className="flex items-center gap-3">
//             <div className="ud-well px-3 py-1.5 rounded-xl flex items-center gap-2">
//               <span className="w-6 h-6 rounded-full bg-[#252525] text-white text-[11px] font-bold flex items-center justify-center">
//                 ع م
//               </span>
//               <span className="text-xs font-semibold text-[#252525] hidden sm:inline">
//                 علی محمدی
//               </span>
//             </div>
//             <button
//               type="button"
//               onClick={() => console.log("Logout clicked")}
//               className="ud-btn-secondary px-3.5 py-2 text-xs font-semibold"
//             >
//               خروج
//             </button>
//           </div>
//         </div>
//       </header>

//       {/* محتوای اصلیِ متناسب با تب انتخاب‌شده (صفحه مستقل هر بخش) */}
//       <main className="max-w-6xl mx-auto px-4 sm:px-8 py-8">
//         {activeTab === "dashboard" && (
//           <div className="space-y-6">
//             {/* ردیف اول: خلاصه متوازن و هم‌وزن */}
//             <section className="grid grid-cols-1 md:grid-cols-3 gap-5">
//               <div className="ud-glass p-6 flex flex-col justify-between gap-4">
//                 <div>
//                   <div className="text-xs text-[#8a8a86]">رزروهای فعال من</div>
//                   <div className="text-2xl font-extrabold text-[#252525] mt-1">
//                     {myBookings.length} نوبت
//                   </div>
//                 </div>
//                 <button
//                   type="button"
//                   onClick={() => setActiveTab("booking")}
//                   className="ud-btn-primary w-full py-2.5 text-xs font-semibold"
//                 >
//                   رفتن به تقویم رزرو
//                 </button>
//               </div>

//               <div className="ud-glass p-6 flex flex-col justify-between gap-4">
//                 <div>
//                   <div className="text-xs text-[#8a8a86]">درخواست‌های خرابی</div>
//                   <div className="text-2xl font-extrabold text-[#252525] mt-1">
//                     {repairs.length} مورد
//                   </div>
//                 </div>
//                 <button
//                   type="button"
//                   onClick={() => setActiveTab("repairs")}
//                   className="ud-btn-secondary w-full py-2.5 text-xs font-semibold"
//                 >
//                   مدیریت و ثبت خرابی
//                 </button>
//               </div>

//               <div className="ud-glass p-6 flex flex-col justify-between gap-4">
//                 <div>
//                   <div className="text-xs text-[#8a8a86]">اطلاعیه‌های جدید</div>
//                   <div className="text-2xl font-extrabold text-[#252525] mt-1">
//                     {ANNOUNCEMENTS.length} اطلاعیه
//                   </div>
//                 </div>
//                 <button
//                   type="button"
//                   onClick={() => setActiveTab("announcements")}
//                   className="ud-btn-secondary w-full py-2.5 text-xs font-semibold"
//                 >
//                   مشاهده همه اطلاعیه‌ها
//                 </button>
//               </div>
//             </section>

//             {/* ردیف دوم: دو ستون کاملاً هم‌تراز (رزروهای من و آخرین خرابی‌ها) */}
//             <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
//               <div className="ud-glass p-6 flex flex-col justify-between gap-4">
//                 <div className="space-y-3">
//                   <div className="flex items-center justify-between">
//                     <h2 className="text-sm font-bold text-[#252525]">
//                       رزروهای ثبت‌شده من
//                     </h2>
//                     <button
//                       type="button"
//                       onClick={() => setActiveTab("booking")}
//                       className="text-xs text-[#62625e] hover:text-[#252525] cursor-pointer"
//                     >
//                       صفحه رزرو ←
//                     </button>
//                   </div>

//                   {myBookings.length === 0 ? (
//                     <div className="ud-well p-5 text-xs text-[#62625e] text-center">
//                       هنوز نوبتی رزرو نکرده‌اید.
//                     </div>
//                   ) : (
//                     myBookings.map((b) => (
//                       <div
//                         key={b.id}
//                         className="ud-well p-4 flex items-center justify-between gap-3"
//                       >
//                         <div>
//                           <div className="text-xs font-bold text-[#252525]">
//                             {b.device}
//                           </div>
//                           <div className="text-[11px] text-[#62625e] mt-0.5">
//                             {b.dayLabel}، {b.dateLabel} • {b.location}
//                           </div>
//                         </div>
//                         <span className="text-xs font-semibold text-[#252525] shrink-0">
//                           {b.timeRange}
//                         </span>
//                       </div>
//                     ))
//                   )}
//                 </div>
//               </div>

//               <div className="ud-glass p-6 flex flex-col justify-between gap-4">
//                 <div className="space-y-3">
//                   <div className="flex items-center justify-between">
//                     <h2 className="text-sm font-bold text-[#252525]">
//                       وضعیت آخرین درخواست‌های خرابی
//                     </h2>
//                     <button
//                       type="button"
//                       onClick={() => setActiveTab("repairs")}
//                       className="text-xs text-[#62625e] hover:text-[#252525] cursor-pointer"
//                     >
//                       صفحه خرابی‌ها ←
//                     </button>
//                   </div>

//                   {repairs.slice(0, 3).map((item) => (
//                     <div
//                       key={item.id}
//                       className="ud-well p-4 flex items-center justify-between gap-3"
//                     >
//                       <div>
//                         <div className="text-xs font-bold text-[#252525]">
//                           {item.title}
//                         </div>
//                         <div className="text-[11px] text-[#62625e] mt-0.5">
//                           {item.category} • {item.date}
//                         </div>
//                       </div>
//                       <span
//                         className={`text-[11px] font-medium px-2.5 py-1 rounded-full border shrink-0 ${getStatusBadgeStyle(
//                           item.status
//                         )}`}
//                       >
//                         {item.status}
//                       </span>
//                     </div>
//                   ))}
//                 </div>
//               </div>
//             </section>
//           </div>
//         )}

//         {activeTab === "booking" && (
//           <div className="space-y-6">
//             <div className="ud-glass p-6 space-y-6">
//               <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
//                 <div>
//                   <h1 className="text-xl font-extrabold text-[#252525]">
//                     رزرو خدمات خوابگاه
//                   </h1>
//                   <p className="text-xs text-[#62625e] mt-1">
//                     دستگاه را انتخاب کنید، روز را در تقویم برگزینید و یکی از بازه‌های تعریف‌شده توسط دانشجوی مسئول را رزرو کنید.
//                   </p>
//                 </div>

//                 {/* انتخاب نوع دستگاه */}
//                 <div className="flex items-center gap-2 p-1 rounded-2xl bg-black/[0.04] border border-white/80 self-start">
//                   {(["ماشین لباس‌شویی", "جاروبرقی"] as DeviceType[]).map(
//                     (dev) => (
//                       <button
//                         key={dev}
//                         type="button"
//                         onClick={() => {
//                           setSelectedDevice(dev);
//                           setSelectedSlotId(null);
//                         }}
//                         className={`px-4 py-2 rounded-xl text-xs font-semibold transition cursor-pointer ${
//                           selectedDevice === dev
//                             ? "bg-[#252525] text-white"
//                             : "text-[#62625e] hover:text-[#252525]"
//                         }`}
//                       >
//                         {dev}
//                       </button>
//                     )
//                   )}
//                 </div>
//               </div>

//               {/* تقویم انتخاب روز */}
//               <div className="grid grid-cols-3 gap-3">
//                 {schedule.map((day) => {
//                   const isSelected = day.id === currentDay.id;
//                   const availableCount = day.slotsByDevice[selectedDevice].filter(
//                     (s) => s.status === "available"
//                   ).length;

//                   return (
//                     <button
//                       key={day.id}
//                       type="button"
//                       onClick={() => {
//                         setSelectedDayId(day.id);
//                         setSelectedSlotId(null);
//                       }}
//                       className={`p-4 rounded-2xl text-right transition cursor-pointer ${
//                         isSelected
//                           ? "bg-gradient-to-l from-[#252525] to-[#484844] text-white shadow-md"
//                           : "ud-well text-[#252525] hover:opacity-95"
//                       }`}
//                     >
//                       <div className="text-xs font-bold">{day.dayLabel}</div>
//                       <div
//                         className={`text-sm font-extrabold mt-0.5 ${
//                           isSelected ? "text-white" : "text-[#252525]"
//                         }`}
//                       >
//                         {day.dateLabel}
//                       </div>
//                       <div
//                         className={`text-[11px] mt-1.5 ${
//                           isSelected ? "text-white/80" : "text-[#62625e]"
//                         }`}
//                       >
//                         {availableCount} بازه آزاد
//                       </div>
//                     </button>
//                   );
//                 })}
//               </div>

//               {/* لیست بازه‌های زمانیِ از پیش مشخص‌شده توسط دانشجوی مسئول برای روز انتخاب‌شده */}
//               <div className="space-y-3">
//                 <div className="flex items-center justify-between text-xs text-[#62625e]">
//                   <span>
//                     ساعات تعریف‌شده برای{" "}
//                     <strong className="text-[#252525]">{selectedDevice}</strong> در{" "}
//                     <strong className="text-[#252525]">
//                       {currentDay.dayLabel} {currentDay.dateLabel}
//                     </strong>
//                   </span>
//                   <span>تنظیم‌شده توسط دانشجوی مسئول</span>
//                 </div>

//                 <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
//                   {currentSlots.map((slot) => {
//                     const isAvailable = slot.status === "available";
//                     const isMine = slot.status === "booked_mine";
//                     const isPicked = selectedSlotId === slot.id;

//                     return (
//                       <div
//                         key={slot.id}
//                         onClick={() => {
//                           if (isAvailable) setSelectedSlotId(slot.id);
//                         }}
//                         className={`ud-well p-4 flex items-center justify-between gap-3 transition ${
//                           isAvailable
//                             ? "cursor-pointer hover:border-black/25"
//                             : "opacity-80"
//                         } ${
//                           isPicked
//                             ? "ring-2 ring-[#252525] bg-white"
//                             : ""
//                         }`}
//                       >
//                         <div>
//                           <div className="text-sm font-bold text-[#252525]">
//                             {slot.timeRange}
//                           </div>
//                           <div className="text-[11px] text-[#62625e] mt-0.5">
//                             {slot.location}
//                           </div>
//                         </div>

//                         {isMine ? (
//                           <button
//                             type="button"
//                             onClick={(e) => {
//                               e.stopPropagation();
//                               handleCancelMySlot(slot.id);
//                             }}
//                             className="px-3 py-1.5 rounded-xl text-[11px] font-semibold bg-black/5 text-[#252525] hover:bg-black/10 cursor-pointer"
//                           >
//                             لغو نوبت من
//                           </button>
//                         ) : isAvailable ? (
//                           <span className="px-3 py-1 rounded-full text-[11px] font-semibold bg-emerald-900/8 text-emerald-900 border border-emerald-900/15">
//                             {isPicked ? "انتخاب‌شده" : "آزاد"}
//                           </span>
//                         ) : (
//                           <span className="px-3 py-1 rounded-full text-[11px] font-medium bg-black/5 text-[#62625e]">
//                             رزرو شده
//                           </span>
//                         )}
//                       </div>
//                     );
//                   })}
//                 </div>
//               </div>

//               <div className="pt-2 flex justify-end">
//                 <button
//                   type="button"
//                   disabled={!selectedSlotId}
//                   onClick={handleConfirmSlotBooking}
//                   className="ud-btn-primary px-6 py-3 text-xs font-bold"
//                 >
//                   تأیید و ثبت بازه انتخابی
//                 </button>
//               </div>
//             </div>
//           </div>
//         )}

//         {activeTab === "repairs" && (
//           <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
//             <form
//               onSubmit={handleAddRepair}
//               className="lg:col-span-5 ud-glass p-6 space-y-4"
//             >
//               <h1 className="text-lg font-extrabold text-[#252525]">
//                 ثبت درخواست خرابی جدید
//               </h1>

//               <div>
//                 <label className="block text-xs font-semibold text-[#62625e] mb-1.5">
//                   عنوان خرابی
//                 </label>
//                 <input
//                   type="text"
//                   required
//                   value={newTitle}
//                   onChange={(e) => setNewTitle(e.target.value)}
//                   placeholder="مثلاً: خرابی شیر روشویی یا پریز"
//                   className="ud-input"
//                 />
//               </div>

//               <div>
//                 <label className="block text-xs font-semibold text-[#62625e] mb-1.5">
//                   دسته‌بندی
//                 </label>
//                 <select
//                   value={newCategory}
//                   onChange={(e) => setNewCategory(e.target.value)}
//                   className="ud-input"
//                 >
//                   <option value="تأسیسات">تأسیسات</option>
//                   <option value="برق">برق</option>
//                   <option value="تجهیزات">تجهیزات</option>
//                   <option value="سایر">سایر</option>
//                 </select>
//               </div>

//               <button
//                 type="submit"
//                 className="ud-btn-primary w-full py-3 text-xs font-bold"
//               >
//                 ارسال درخواست خرابی
//               </button>
//             </form>

//             <section className="lg:col-span-7 ud-glass p-6 space-y-3">
//               <h2 className="text-base font-extrabold text-[#252525]">
//                 لیست درخواست‌های ثبت‌شده
//               </h2>

//               {repairs.map((item) => (
//                 <div
//                   key={item.id}
//                   className="ud-well p-4 flex items-center justify-between gap-4"
//                 >
//                   <div>
//                     <div className="text-sm font-bold text-[#252525]">
//                       {item.title}
//                     </div>
//                     <div className="text-xs text-[#62625e] mt-0.5">
//                       {item.category} • {item.room} • {item.date}
//                     </div>
//                   </div>
//                   <span
//                     className={`text-xs font-medium px-3 py-1 rounded-full border shrink-0 ${getStatusBadgeStyle(
//                       item.status
//                     )}`}
//                   >
//                     {item.status}
//                   </span>
//                 </div>
//               ))}
//             </section>
//           </div>
//         )}

//         {activeTab === "announcements" && (
//           <section className="ud-glass p-6 space-y-4">
//             <h1 className="text-xl font-extrabold text-[#252525]">
//               اطلاعیه‌های خوابگاه
//             </h1>

//             <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//               {ANNOUNCEMENTS.map((ann) => (
//                 <article key={ann.id} className="ud-well p-5 space-y-2">
//                   <div className="flex items-center justify-between gap-2">
//                     <h2 className="text-sm font-bold text-[#252525]">
//                       {ann.title}
//                     </h2>
//                     <span className="text-[11px] text-[#8a8a86]">
//                       {ann.date}
//                     </span>
//                   </div>
//                   <p className="text-xs text-[#62625e] leading-relaxed">
//                     {ann.description}
//                   </p>
//                 </article>
//               ))}
//             </div>
//           </section>
//         )}
//       </main>
//     </div>
//   );
// }