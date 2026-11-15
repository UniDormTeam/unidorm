# مستند قرارداد API سامانه UniDorm

این مستند قرارداد ارتباطی میان فرانت‌اند و بک‌اند UniDorm را مشخص می‌کند.
برای هر عملیات، مسیر درخواست، روش HTTP، داده‌های ورودی، پاسخ مورد انتظار
و خطاهای احتمالی تعریف شده است.

-   **سبک ارتباط:** REST API
-   **فرمت تبادل داده:** JSON (`application/json`)؛ برای آپلود فایل از
    `multipart/form-data` استفاده می‌شود.
-   **احراز هویت:** JWT شامل Access Token و Refresh Token
-   **دامنه پوشش:** عملیات موردنیاز MVP شامل احراز هویت، مدیریت سازمان‌ها
    و اعضا، اطلاعیه‌ها، گزارش خرابی‌ها و نوبت‌دهی.

> این فایل قرارداد طراحی‌شده API است؛ جزئیات آن باید هنگام پیاده‌سازی با
> رفتار واقعی بک‌اند هماهنگ و در صورت تغییر، به‌روزرسانی شود. انتخاب
> تکنولوژی‌ها و برنامه میزبانی در فایل `Technology_and_Hosting_Plan` توضیح داده
> شده‌اند.

------------------------------------------------------------------------

## ساختار مستند

این مستند به‌ترتیب شامل قوانین عمومی درخواست‌ها و پاسخ‌ها، احراز هویت و
پروفایل، مدیریت سازمان‌ها و اعضا، اطلاعیه‌ها، گزارش خرابی‌ها و سیستم
نوبت‌دهی است.

## قوانین عمومی و استانداردهای API

### ۱. هدرهای مورد نیاز (Headers)

برای تمامی درخواست‌هایی که نیاز به احراز هویت دارند، فرانت‌اند باید هدر
زیر را ارسال کند:

``` http
Authorization: Bearer <access_token>
Content-Type: application/json
```

### ۲. سازوکار ماندگاری لاگین (Persistent Login)

-   هنگام لاگین، بک‌اند یک `access` توکن (با عمر کوتاه، مثلاً ۶۰ دقیقه) و
    یک `refresh` توکن (با عمر طولانی، مثلاً ۳۰ روز) برمی‌گرداند.
-   تا زمانی که کاربر Logout نکند، فرانت‌اند در صورت منقضی شدن `access`
    توکن، به‌صورت خودکار با اندپوینت `/api/auth/token/refresh/` توکن جدید
    می‌گیرد.
-   هنگام **Logout**، `refresh` توکن به بک‌اند فرستاده شده و در لیست سیاه
    (Blacklist) قرار می‌گیرد.

### ۳. ساختار استاندارد خطاها (Error Responses)

``` json
{
  "status": "error",
  "code": 400,
  "message": "خطا در اعتبارسنجی داده‌ها",
  "errors": {
    "field_name": ["توضیح خطای مربوط به این فیلد"]
  }
}
```

------------------------------------------------------------------------

## بخش ۱: احراز هویت و حساب کاربری (Authentication & Profile)

### ۱.۱. ثبت‌نام مدیر (Manager Registration)

ایجاد حساب کاربری جدید برای مدیر سیستم. \* **Endpoint:**
`POST /api/auth/register/manager/` \* **دسترسی:** عمومی (Public)

**Request Body (JSON):**

``` json
{
  "username": "ali_rezaei",
  "password": "StrongPassword123!",
  "first_name": "علی",
  "last_name": "رضایی",
  "email": "ali@example.com",
  "phone_number": "09123456789",
  "job_title": "سرپرست خوابگاه"
}
```

**Response `201 Created` (JSON):**

``` json
{
  "message": "ثبت‌نام مدیر با موفقیت انجام شد.",
  "user": {
    "id": 1,
    "username": "ali_rezaei",
    "first_name": "علی",
    "last_name": "رضایی",
    "role": "MANAGER"
  }
}
```

### ۱.۲. ورود به سامانه (Login)

دریافت توکن‌ها به همراه اطلاعات کامل کاربر، سازمان‌های عضو و مسئولیت‌های
ویژه (مورد نیاز React برای هدایت کاربر به داشبورد اختصاصی نقش خود: مدیر،
دانشجو، تأسیسات یا اینترنت). \* **Endpoint:** `POST /api/auth/login/` \*
**دسترسی:** عمومی (Public)

**Request Body (JSON):**

``` json
{
  "username": "400123456",
  "password": "UserPassword123!"
}
```

**Response `200 OK` (JSON) - نمونه برای دانشجو (دارای مسئولیت
لباسشویی):**

``` json
{
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "user": {
    "id": 12,
    "username": "400123456",
    "first_name": "سارا",
    "last_name": "محمدی",
    "email": "sara@uni.ac.ir",
    "role": "STUDENT",
    "profile": {
      "student_number": "400123456",
      "phone_number": "09351112233",
      "room_number": "204",
      "building": "بلوک A"
    }
  },
  "organizations": [
    {
      "organization_id": 1,
      "organization_name": "خوابگاه کوی دانشگاه - ساختمان ۱",
      "membership_role": "STUDENT",
      "is_default": true
    }
  ],
  "special_assignments": [
    {
      "resource_type_id": 1,
      "resource_name": "ماشین لباس‌شویی",
      "organization_id": 1
    }
  ]
}
```

**Response `200 OK` (JSON) - نمونه برای مسئول تأسیسات / اینترنت:**

``` json
{
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "user": {
    "id": 5,
    "username": "tech_karimi",
    "first_name": "رضا",
    "last_name": "کریمی",
    "email": "karimi@uni.ac.ir",
    "role": "INTERNET",
    "profile": {
      "phone_number": "09120001122"
    }
  },
  "organizations": [
    {
      "organization_id": 1,
      "organization_name": "خوابگاه کوی دانشگاه - ساختمان ۱",
      "membership_role": "INTERNET",
      "is_default": true
    },
    {
      "organization_id": 2,
      "organization_name": "خوابگاه شهید چمران - بلوک ۲",
      "membership_role": "INTERNET",
      "is_default": false
    }
  ],
  "special_assignments": []
}
```

> **راهنمای پنل‌های کاربری در React:** \* `role === "MANAGER"`: هدایت به
> پنل مدیریت خوابگاه. \* `role === "STUDENT"`: هدایت به پنل دانشجو (اگر
> `special_assignments` خالی نباشد، دکمه سوییچ به «پنل مدیریت نوبت‌دهی»
> نمایش داده می‌شود). \* `role === "FACILITIES"`: هدایت به پنل اختصاصی
> مسئول تأسیسات (فقط بخش گزارش خرابی‌های تأسیسات). \*
> `role === "INTERNET"`: هدایت به پنل اختصاصی مسئول اینترنت (فقط بخش
> گزارش خرابی‌های اینترنت).

### ۱.۳. تمدید توکن (Refresh Token)

-   **Endpoint:** `POST /api/auth/token/refresh/`
-   **دسترسی:** عمومی (با داشتن Refresh Token معتبر)

**Request Body (JSON):**

``` json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response `200 OK` (JSON):**

``` json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.new_token..."
}
```

### ۱.۴. خروج از سامانه (Logout)

-   **Endpoint:** `POST /api/auth/logout/`
-   **دسترسی:** کاربران لاگین‌شده

**Request Body (JSON):**

``` json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response `205 Reset Content` (JSON):**

``` json
{
  "message": "خروج از حساب کاربری با موفقیت انجام شد."
}
```

### ۱.۵. مشاهده و ویرایش پروفایل من (Get / Update Me)

-   **Endpoint:** `GET /api/auth/me/` و `PATCH /api/auth/me/`
-   **دسترسی:** کاربران لاگین‌شده

**Request Body برای `PATCH` (JSON):**

``` json
{
  "first_name": "علی",
  "last_name": "رضایی‌فر",
  "email": "new_ali@example.com",
  "phone_number": "09129998877"
}
```

**Response `200 OK` (JSON):**

``` json
{
  "id": 1,
  "username": "ali_rezaei",
  "first_name": "علی",
  "last_name": "رضایی‌فر",
  "email": "new_ali@example.com",
  "role": "MANAGER",
  "profile": {
    "job_title": "سرپرست خوابگاه",
    "phone_number": "09129998877"
  }
}
```

------------------------------------------------------------------------

## بخش ۲: مدیریت سازمان‌ها و اعضا (Organizations & Memberships)

### ۲.۱. لیست سازمان‌های من / ایجاد سازمان جدید

-   **Endpoint:** `GET /api/organizations/` و `POST /api/organizations/`
-   **دسترسی:** مدیر (Manager)

**Request Body برای `POST` (JSON):**

``` json
{
  "name": "خوابگاه شهید چمران - بلوک ۲",
  "description": "ساختمان شماره ۲ ویژه دانشجویان کارشناسی"
}
```

**Response `201 Created` (JSON):**

``` json
{
  "id": 2,
  "name": "خوابگاه شهید چمران - بلوک ۲",
  "description": "ساختمان شماره ۲ ویژه دانشجویان کارشناسی",
  "is_active": true,
  "created_at": "2026-11-13T10:00:00Z"
}
```

### ۲.۲. مشاهده و ویرایش اطلاعات سازمان (و امکانات خوابگاه برای دانشجو)

-   **Endpoint:** `GET /api/organizations/{org_id}/` و
    `PATCH /api/organizations/{org_id}/`
-   **دسترسی:** `GET` برای همه اعضای سازمان (از جمله دانشجو)، `PATCH`
    فقط برای مدیر.

**Response `200 OK` (JSON):**

``` json
{
  "id": 1,
  "name": "خوابگاه کوی دانشگاه - ساختمان ۱",
  "description": "دارای ۵ طبقه، سالن مطالعه، ۲ دستگاه لباسشویی صنعتی و اینترنت وای‌فای مرکزی.",
  "is_active": true,
  "stats": {
    "total_students": 120,
    "active_devices": 3
  }
}
```

### ۲.۳. افزودن تکی عضو (دانشجو، مدیر، مسئول تأسیسات یا اینترنت) به سازمان

**منطق بک‌اند (طبق معیار پذیرش):** 1. سیستم ابتدا `username` (مثلاً شماره
دانشجویی یا کد پرسنلی) را در جدول `User` جستجو می‌کند. 2. **اگر حساب
کاربری وجود نداشت:** ابتدا حساب کاربری و پروفایل متناسب با نقش
(`StudentProfile` / `FacilitiesOfficer` / `InternetOfficer` /
`ManagerProfile`) ساخته می‌شود (با رمز عبور پیش‌فرض مثلاً کد ملی یا شماره
دانشجویی) و سپس به سازمان متصل می‌گردد. 3. **اگر حساب کاربری از قبل وجود
داشت:** بدون ساخت کاربر تکراری، مستقیماً یک رکورد در
`OrganizationMembership` برای اتصال او به این سازمان ایجاد می‌شود.

-   **Endpoint:** `POST /api/organizations/{org_id}/members/`
-   **دسترسی:** مدیر سازمان

**Request Body (JSON):**

``` json
{
  "username": "401223344",
  "first_name": "امیر",
  "last_name": "حسینی",
  "membership_role": "STUDENT",
  "room_number": "305",
  "phone_number": "09191234567"
}
```

> مقادیر مجاز `membership_role`: `STUDENT`, `MANAGER`, `FACILITIES`,
> `INTERNET`

**Response `201 Created` (JSON):**

``` json
{
  "membership_id": 45,
  "account_status": "CREATED_AND_ATTACHED", 
  "user": {
    "id": 88,
    "username": "401223344",
    "full_name": "امیر حسینی"
  },
  "membership_role": "STUDENT",
  "room_number": "305"
}
```

> مقدار `account_status` یکی از دو حالت `CREATED_AND_ATTACHED` (اکانت
> جدید ساخته و عضو شد) یا `EXISTING_ATTACHED` (اکانت از قبل بود و
> مستقیماً عضو شد) است.

### ۲.۴. افزودن گروهی دانشجویان به سازمان (Bulk Add)

امکان افزودن هم‌زمان ده‌ها دانشجو (از طریق لیست JSON در فرانت‌اند یا آپلود
فایل اکسل/CSV) با همان منطق «ساخت خودکار اکانت در صورت نبودن، و عضویت
مستقیم در صورت وجود داشتن». \* **Endpoint:**
`POST /api/organizations/{org_id}/members/bulk/` \* **دسترسی:** مدیر
سازمان

**Request Body (JSON):**

``` json
{
  "members": [
    {
      "username": "401223344",
      "first_name": "امیر",
      "last_name": "حسینی",
      "room_number": "305",
      "phone_number": "09191234567"
    },
    {
      "username": "400112233",
      "first_name": "مهدی",
      "last_name": "کریمی",
      "room_number": "306",
      "phone_number": "09123334455"
    }
  ]
}
```

*(نکته: در صورت ارسال فایل اکسل/CSV، درخواست با
`Content-Type: multipart/form-data` و فیلد `file` ارسال می‌شود).*

**Response `200 OK` (JSON):**

``` json
{
  "summary": {
    "total_processed": 2,
    "new_accounts_created": 1,
    "existing_accounts_attached": 1,
    "failed_count": 0
  },
  "results": [
    {
      "username": "401223344",
      "full_name": "امیر حسینی",
      "status": "CREATED_AND_ATTACHED",
      "membership_id": 45
    },
    {
      "username": "400112233",
      "full_name": "مهدی کریمی",
      "status": "EXISTING_ATTACHED",
      "membership_id": 46
    }
  ],
  "errors": []
}
```

### ۲.۵. مشاهده لیست اعضای سازمان / حذف عضو

-   **Endpoint مشاهده:**
    `GET /api/organizations/{org_id}/members/?role=STUDENT` (فیلتر
    اختیاری بر اساس نقش: `STUDENT`, `FACILITIES`, `INTERNET`, `MANAGER`)
-   **Endpoint حذف:**
    `DELETE /api/organizations/{org_id}/members/{membership_id}/`
-   **دسترسی:** مدیر سازمان

**Response `200 OK` برای `GET` (JSON):**

``` json
[
  {
    "membership_id": 45,
    "user_id": 88,
    "username": "401223344",
    "full_name": "امیر حسینی",
    "membership_role": "STUDENT",
    "room_number": "305",
    "phone_number": "09191234567",
    "is_active": true
  }
]
```

------------------------------------------------------------------------

## بخش ۳: اطلاعیه‌ها (Announcements)

### ۳.۱. لیست اطلاعیه‌های سازمان

-   **Endpoint:** `GET /api/organizations/{org_id}/announcements/`
-   **دسترسی:** تمام اعضای سازمان (مدیر و دانشجو)

**Response `200 OK` (JSON):**

``` json
[
  {
    "id": 10,
    "title": "قطعی آب جهت تعمیرات تاسیسات",
    "content": "به اطلاع دانشجویان عزیز می‌رساند فردا از ساعت ۹ تا ۱۲ آب قطع خواهد بود.",
    "image": "https://api.dorm.ir/media/announcements/water_fix.jpg",
    "published_at": "2026-11-13T08:00:00Z",
    "expired_at": "2026-11-15T23:59:59Z",
    "created_by_name": "علی رضایی"
  }
]
```

### ۳.۲. ایجاد اطلاعیه جدید (با قابلیت آپلود تصویر)

-   **Endpoint:** `POST /api/organizations/{org_id}/announcements/`
-   **Content-Type:** `multipart/form-data`
-   **دسترسی:** مدیر سازمان

**Request Form-Data:** \* `title`: "برنامه جدید سالن مطالعه" (String) \*
`content`: "متن کامل اطلاعیه..." (String) \* `expired_at`:
"2026-12-01T23:59:59Z" (DateTime - اختیاری) \* `image`: `[Binary File]`
(Image - اختیاری)

**Response `201 Created` (JSON):**

``` json
{
  "id": 11,
  "title": "برنامه جدید سالن مطالعه",
  "content": "متن کامل اطلاعیه...",
  "image": "https://api.dorm.ir/media/announcements/study_room.png",
  "published_at": "2026-11-13T11:15:00Z",
  "expired_at": "2026-12-01T23:59:59Z"
}
```

### ۳.۳. مشاهده جزئیات، ویرایش و حذف اطلاعیه

-   **Endpoint:**
    `GET / PATCH / DELETE /api/organizations/{org_id}/announcements/{announcement_id}/`
-   **دسترسی:** `GET` برای همه، `PATCH` و `DELETE` فقط برای مدیر.

------------------------------------------------------------------------

## بخش ۴: گزارش خرابی‌ها و تعمیرات (Maintenance Requests)

### ۴.۱. لیست گزارش‌های خرابی (متناسب با پنل هر نقش)

-   **Endpoint:**
    `GET /api/organizations/{org_id}/maintenance-requests/`
-   **Query Params:**
    -   `?category=INTERNET` (`REPAIRS`, `FACILITIES`, `INTERNET`,
        `OTHER`)
    -   `?status=PENDING` (`PENDING`, `APPROVED`, `IN_PROGRESS`,
        `RESOLVED`, `REJECTED`, `IRRELEVANT`)
    -   `?ordering=-created_at` یا `?ordering=room_number`
-   **محدوده دسترسی خودکار در بک‌اند (Permissions):**
    -   **دانشجو:** فقط درخواست‌هایی که خودش ثبت کرده را می‌بیند.
    -   **مدیر:** همه درخواست‌های سازمان را در هر ۴ دسته می‌بیند.
    -   **مسئول تأسیسات (`FACILITIES`):** در پنل خود به صورت خودکار فقط
        گزارش‌های دسته `FACILITIES` (و گزارش‌های ارجاع‌شده به او) را
        می‌بیند.
    -   **مسئول اینترنت (`INTERNET`):** در پنل خود به صورت خودکار فقط
        گزارش‌های دسته `INTERNET` (و گزارش‌های ارجاع‌شده به او) را می‌بیند.

**Response `200 OK` (JSON):**

``` json
[
  {
    "id": 102,
    "title": "قطعی پریز شبکه اتاق",
    "description": "پریز اینترنت سمت راست اتاق کار نمی‌کند.",
    "category": "INTERNET",
    "category_display": "اینترنت",
    "room_number": "204",
    "status": "IN_PROGRESS",
    "status_display": "در حال پیگیری",
    "created_by": {
      "id": 12,
      "full_name": "سارا محمدی"
    },
    "assigned_to": {
      "id": 5,
      "full_name": "رضا کریمی (مسئول اینترنت)"
    },
    "created_at": "2026-11-12T14:30:00Z",
    "resolved_at": null,
    "has_rating": false
  }
]
```

### ۴.۲. ثبت گزارش خرابی جدید توسط دانشجو

-   **Endpoint:**
    `POST /api/organizations/{org_id}/maintenance-requests/`
-   **دسترسی:** دانشجو

**Request Body (JSON):**

``` json
{
  "title": "نشتی شیر آب روشویی",
  "description": "شیر آب سرد چکه می‌کند و بسته نمی‌شود.",
  "category": "FACILITIES",
  "room_number": "204"
}
```

> **نکته بک‌اند:** اگر `category` برابر `FACILITIES` یا `INTERNET` باشد،
> گزارش علاوه بر مدیر، بلافاصله در لیست پنل مسئول مربوطه نیز قابل مشاهده
> خواهد بود.

**Response `201 Created` (JSON):**

``` json
{
  "id": 103,
  "title": "نشتی شیر آب روشویی",
  "description": "شیر آب سرد چکه می‌کند و بسته نمی‌شود.",
  "category": "FACILITIES",
  "room_number": "204",
  "status": "PENDING",
  "created_at": "2026-11-13T11:20:00Z"
}
```

### ۴.۳. رسیدگی، تغییر وضعیت و ارجاع گزارش (پنل مدیر، تأسیسات و اینترنت)

-   **Endpoint:**
    `POST /api/organizations/{org_id}/maintenance-requests/{request_id}/updates/`
-   **دسترسی و مجوزها:**
    -   **مدیر:** می‌تواند درخواست را تایید (`APPROVED`)، رد
        (`REJECTED`)، در حال پیگیری (`IN_PROGRESS`) یا انجام‌شده
        (`RESOLVED`) کند؛ همچنین می‌تواند دسته‌بندی گزارش‌های «متفرقه»
        (`OTHER`) را تغییر داده و به مسئول مربوطه ارجاع دهد.
    -   **مسئول تأسیسات / اینترنت:** می‌تواند وضعیت گزارش‌های مربوط به خود
        را به «انجام‌شده» (`RESOLVED`) یا «نامرتبط» (`IRRELEVANT`) تغییر
        دهد و توضیح ثبت کند.

**Request Body - نمونه ارجاع توسط مدیر (JSON):**

``` json
{
  "new_status": "IN_PROGRESS",
  "category": "FACILITIES",
  "assigned_to_id": 4,
  "comment": "درخواست بررسی شد و به مسئول تاسیسات ارجاع داده شد."
}
```

**Request Body - نمونه بستن گزارش توسط مسئول تأسیسات یا اینترنت
(JSON):**

``` json
{
  "new_status": "RESOLVED",
  "comment": "مغزی شیر آب تعویض و تست شد."
}
```

*(یا برای گزارش نامرتبط: `"new_status": "IRRELEVANT"` با توضیح مربوطه).*

**Response `201 Created` (JSON):**

``` json
{
  "update_id": 55,
  "request_id": 103,
  "old_status": "PENDING",
  "new_status": "IN_PROGRESS",
  "comment": "درخواست بررسی شد و به مسئول تاسیسات ارجاع داده شد.",
  "updated_by": "علی رضایی",
  "created_at": "2026-11-13T11:25:00Z"
}
```

### ۴.۴. مشاهده جزئیات گزارش به همراه تاریخچه به‌روزرسانی‌ها

-   **Endpoint:**
    `GET /api/organizations/{org_id}/maintenance-requests/{request_id}/`
-   **دسترسی:** دانشجوی ثبت‌کننده، مدیر و مسئول مربوطه

**Response `200 OK` (JSON):**

``` json
{
  "id": 103,
  "title": "نشتی شیر آب روشویی",
  "description": "شیر آب سرد چکه می‌کند و بسته نمی‌شود.",
  "category": "FACILITIES",
  "room_number": "204",
  "status": "RESOLVED",
  "created_at": "2026-11-13T11:20:00Z",
  "resolved_at": "2026-11-14T10:30:00Z",
  "updates": [
    {
      "id": 55,
      "old_status": "PENDING",
      "new_status": "IN_PROGRESS",
      "comment": "به مسئول تاسیسات ارجاع داده شد.",
      "updated_by": "علی رضایی",
      "created_at": "2026-11-13T11:25:00Z"
    },
    {
      "id": 56,
      "old_status": "IN_PROGRESS",
      "new_status": "RESOLVED",
      "comment": "مغزی شیر تعویض شد.",
      "updated_by": "حسن پورمند (تاسیسات)",
      "created_at": "2026-11-14T10:30:00Z"
    }
  ],
  "rating": null
}
```

### ۴.۵. ثبت امتیاز و نظر برای گزارش انجام‌شده (توسط دانشجو)

-   **Endpoint:**
    `POST /api/organizations/{org_id}/maintenance-requests/{request_id}/rate/`
-   **دسترسی:** دانشجوی ثبت‌کننده درخواست (فقط زمانی که وضعیت `RESOLVED`
    باشد)

**Request Body (JSON):**

``` json
{
  "score": 5,
  "comment": "خیلی سریع و تمیز مشکل برطرف شد. ممنون."
}
```

**Response `201 Created` (JSON):**

``` json
{
  "id": 18,
  "request_id": 103,
  "score": 5,
  "comment": "خیلی سریع و تمیز مشکل برطرف شد. ممنون.",
  "created_at": "2026-11-14T12:00:00Z"
}
```

------------------------------------------------------------------------

## بخش ۵: سیستم نوبت‌دهی (Booking & Reservations)

### ۵.۱. دریافت انواع امکانات قابل رزرو و دستگاه‌های فعال سازمان

-   **Endpoint:** `GET /api/organizations/{org_id}/resources/`
-   **دسترسی:** تمام اعضای سازمان

**Response `200 OK` (JSON):**

``` json
[
  {
    "resource_type_id": 1,
    "name": "ماشین لباس‌شویی",
    "description": "لباسشویی‌های مستقر در طبقه همکف",
    "policy": {
      "slot_duration_minutes": 90,
      "max_daily_reservations": 1
    },
    "devices": [
      {
        "id": 10,
        "name": "ماشین لباس‌شویی شماره ۱ (سامسونگ)",
        "is_active": true
      },
      {
        "id": 11,
        "name": "ماشین لباس‌شویی شماره ۲ (ال‌جی)",
        "is_active": true
      }
    ]
  },
  {
    "resource_type_id": 2,
    "name": "جاروبرقی",
    "description": "تحویل از اتاق نگهبانی",
    "policy": {
      "slot_duration_minutes": 60,
      "max_daily_reservations": 1
    },
    "devices": [
      {
        "id": 12,
        "name": "جاروبرقی شماره ۱",
        "is_active": true
      }
    ]
  }
]
```

### ۵.۲. تنظیمات نوبت‌دهی و تعیین دانشجوی مسئول (توسط مدیر)

-   **Endpoint ویرایش قوانین:**
    `PATCH /api/organizations/{org_id}/booking-policies/{resource_type_id}/`
-   **Endpoint تعیین مسئول:**
    `POST /api/organizations/{org_id}/device-staff/`
-   **دسترسی:** مدیر سازمان

**Request Body برای تعیین مسئول (JSON):**

``` json
{
  "membership_id": 45,
  "resource_type_id": 1
}
```

**Response `201 Created` (JSON):**

``` json
{
  "id": 7,
  "student_name": "امیر حسینی",
  "student_number": "401223344",
  "resource_type": "ماشین لباس‌شویی",
  "is_active": true
}
```

### ۵.۳. مشاهده سانس‌های آزاد و رزروشده یک دستگاه در تاریخ مشخص

-   **Endpoint:**
    `GET /api/organizations/{org_id}/devices/{device_id}/slots/?date=2026-11-15`
-   **دسترسی:** دانشجو و مدیر

**Response `200 OK` (JSON):**

``` json
{
  "device_id": 10,
  "device_name": "ماشین لباس‌شویی شماره ۱ (سامسونگ)",
  "date": "2026-11-15",
  "slots": [
    {
      "slot_id": 501,
      "start_datetime": "2026-11-15T08:00:00Z",
      "end_datetime": "2026-11-15T09:30:00Z",
      "is_available": false,
      "is_reserved_by_me": false
    },
    {
      "slot_id": 502,
      "start_datetime": "2026-11-15T09:30:00Z",
      "end_datetime": "2026-11-15T11:00:00Z",
      "is_available": true,
      "is_reserved_by_me": false
    }
  ]
}
```

### ۵.۴. ثبت رزرو توسط دانشجو

در بک‌اند جنگو باید با استفاده از `transaction.atomic()` و
`select_for_update()` از رزرو هم‌زمان یک سانس و همچنین عبور از سقف مجاز
روزانه جلوگیری شود. \* **Endpoint:**
`POST /api/organizations/{org_id}/reservations/` \* **دسترسی:** دانشجو

**Request Body (JSON):**

``` json
{
  "slot_id": 502
}
```

**Response `201 Created` (JSON):**

``` json
{
  "reservation_id": 890,
  "device_name": "ماشین لباس‌شویی شماره ۱ (سامسونگ)",
  "start_datetime": "2026-11-15T09:30:00Z",
  "end_datetime": "2026-11-15T11:00:00Z",
  "status": "ACTIVE",
  "created_at": "2026-11-13T11:40:00Z"
}
```

### ۵.۵. مشاهده رزروهای من (دانشجو)

-   **Endpoint:** `GET /api/organizations/{org_id}/reservations/my/`
-   **دسترسی:** دانشجو

**Response `200 OK` (JSON):**

``` json
[
  {
    "reservation_id": 890,
    "resource_type": "ماشین لباس‌شویی",
    "device_name": "ماشین لباس‌شویی شماره ۱ (سامسونگ)",
    "start_datetime": "2026-11-15T09:30:00Z",
    "end_datetime": "2026-11-15T11:00:00Z",
    "status": "ACTIVE",
    "can_cancel": true
  }
]
```

### ۵.۶. لغو رزرو (توسط دانشجو، دانشجوی مسئول یا مدیر)

-   **Endpoint:**
    `POST /api/organizations/{org_id}/reservations/{reservation_id}/cancel/`
-   **دسترسی:**
    -   **دانشجو:** فقط در بازه زمانی مجاز قبل از شروع سانس.
    -   **دانشجوی مسئول:** در صورت دیر رسیدن فرد یا عدم حضور.
    -   **مدیر:** بدون محدودیت.

**Request Body (JSON):**

``` json
{
  "reason": "عدم حضور دانشجو در زمان مقرر"
}
```

**Response `200 OK` (JSON):**

``` json
{
  "reservation_id": 890,
  "status": "CANCELLED",
  "cancelled_at": "2026-11-15T09:45:00Z",
  "message": "رزرو با موفقیت لغو شد و سانس آزاد گردید."
}
```

### ۵.۷. پنل دانشجوی مسئول و مدیر: مشاهده لیست رزروها و لغوها

-   **Endpoint:**
    `GET /api/organizations/{org_id}/reservations/?resource_type_id=1&date=2026-11-15`
-   **دسترسی:** مدیر سازمان و دانشجوی مسئول همان `resource_type_id`

**Response `200 OK` (JSON):**

``` json
[
  {
    "reservation_id": 890,
    "device_name": "ماشین لباس‌شویی شماره ۱ (سامسونگ)",
    "start_datetime": "2026-11-15T09:30:00Z",
    "end_datetime": "2026-11-15T11:00:00Z",
    "status": "ACTIVE",
    "student": {
      "full_name": "سارا محمدی",
      "student_number": "400123456",
      "room_number": "204"
    }
  }
]
```

------------------------------------------------------------------------
