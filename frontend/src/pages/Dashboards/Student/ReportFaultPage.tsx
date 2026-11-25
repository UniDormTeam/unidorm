import { useState } from "react";
import type { FormEvent, ChangeEvent } from "react";
import { useNavigate } from "react-router-dom";

import { getAuthSession, getDefaultOrganization } from "../../../services/authSession";
import { createMaintenanceRequest } from "../../../services/maintenanceService";

import type { FaultCategory } from "../../../types/maintenance";

import "./StudentFormPages.css";

const categoryOptions: {
  value: FaultCategory;
  label: string;
}[] = [
  { value: "repairs", label: "تعمیرات" },
  { value: "facilities", label: "تأسیسات" },
  { value: "internet", label: "اینترنت" },
  { value: "other", label: "متفرقه" },
];

function ReportFaultPage() {
  const navigate = useNavigate();

  const session = getAuthSession();
  const organization = getDefaultOrganization();

  const profile = session?.user.profile;

  const initialRoomNumber =
    profile && "room_number" in profile
      ? profile.room_number
      : organization?.room_number ?? "";

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState<FaultCategory>("facilities");
  const [roomNumber, setRoomNumber] = useState(initialRoomNumber);
  const [image, setImage] = useState<File | null>(null);

  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccessful, setIsSuccessful] = useState(false);

  function handleImageChange(event: ChangeEvent<HTMLInputElement>) {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) {
      setImage(null);
      return;
    }

    if (!selectedFile.type.startsWith("image/")) {
      setError("لطفاً یک فایل تصویری انتخاب کنید.");
      event.target.value = "";
      return;
    }

    if (selectedFile.size > 5 * 1024 * 1024) {
      setError("حجم تصویر نباید بیشتر از ۵ مگابایت باشد.");
      event.target.value = "";
      return;
    }

    setError("");
    setImage(selectedFile);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (isLoading) return;

    setError("");

    if (!session) {
      setError("نشست شما معتبر نیست. لطفاً دوباره وارد شوید.");
      return;
    }

    if (!organization) {
      setError("برای حساب شما سازمانی ثبت نشده است.");
      return;
    }

    if (!session.capabilities.can_report_faults) {
      setError("حساب شما اجازه ثبت درخواست خرابی ندارد.");
      return;
    }

    if (title.trim().length < 3) {
      setError("عنوان درخواست باید حداقل ۳ حرف داشته باشد.");
      return;
    }

    if (description.trim().length < 5) {
      setError("لطفاً توضیحات بیشتری وارد کنید.");
      return;
    }

    setIsLoading(true);

    try {
      await createMaintenanceRequest(organization.organization_id, {
        title,
        description,
        category,
        room_number: roomNumber,
        image,
      });

      setIsSuccessful(true);
    } catch (error) {
      if (error instanceof TypeError) {
        setError("ارتباط با سرور برقرار نشد. دوباره تلاش کنید.");
      } else if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("خطای غیرمنتظره‌ای رخ داد.");
      }
    } finally {
      setIsLoading(false);
    }
  }

  if (isSuccessful) {
    return (
      <main className="student-form-page" dir="rtl">
        <section className="form-success">
          <div className="success-icon">✓</div>

          <h1>درخواست شما ثبت شد</h1>

          <p>
            درخواست خرابی با موفقیت برای مسئول مربوطه ارسال شد.
          </p>

          <button
            type="button"
            className="primary-form-button"
            onClick={() => navigate("/dashboard", { replace: true })}
          >
            بازگشت به داشبورد
          </button>
        </section>
      </main>
    );
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
          <h1>ثبت درخواست خرابی</h1>
          <p>
            مشکل پیش‌آمده را توضیح دهید تا مسئول مربوطه آن را بررسی کند.
          </p>
        </header>

        <form className="student-form-card" onSubmit={handleSubmit}>
          <div className="form-field">
            <label htmlFor="fault-title">عنوان درخواست</label>
            <input
              id="fault-title"
              type="text"
              placeholder="مثلاً خرابی چراغ اتاق"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              maxLength={150}
              required
            />
          </div>

          <div className="form-field">
            <label htmlFor="fault-category">دسته‌بندی خرابی</label>
            <select
              id="fault-category"
              value={category}
              onChange={(event) =>
                setCategory(event.target.value as FaultCategory)
              }
              required
            >
              {categoryOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-field">
            <label htmlFor="fault-room">شماره اتاق</label>
            <input
              id="fault-room"
              type="text"
              placeholder="شماره اتاق"
              value={roomNumber}
              onChange={(event) => setRoomNumber(event.target.value)}
            />
            <span className="field-hint">
              در صورت خالی بودن، شماره اتاق از پروفایل شما دریافت می‌شود.
            </span>
          </div>

          <div className="form-field">
            <label htmlFor="fault-description">شرح مشکل</label>
            <textarea
              id="fault-description"
              placeholder="مشکل را با جزئیات توضیح دهید..."
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              rows={5}
              required
            />
          </div>

          <div className="form-field">
            <label htmlFor="fault-image">تصویر (اختیاری)</label>

            <label className="image-upload-box" htmlFor="fault-image">
              <span>＋</span>
              <strong>
                {image ? image.name : "انتخاب تصویر"}
              </strong>
              <small>حداکثر حجم: ۵ مگابایت</small>
            </label>

            <input
              id="fault-image"
              className="visually-hidden-input"
              type="file"
              accept="image/*"
              onChange={handleImageChange}
            />

            {image && (
              <button
                type="button"
                className="remove-image-button"
                onClick={() => setImage(null)}
              >
                حذف تصویر انتخاب‌شده
              </button>
            )}
          </div>

          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}

          <button
            type="submit"
            className="primary-form-button"
            disabled={isLoading}
          >
            {isLoading ? "در حال ارسال درخواست..." : "ثبت درخواست خرابی"}
          </button>
        </form>
      </div>
    </main>
  );
}

export default ReportFaultPage;