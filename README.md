# Crypto Project 🎉

این فایل README تمامی توضیحات مورد نیاز برای اجرای کامل پروژه، ساختار سرویس‌ها، نحوه اجرای Docker، مسیرهای لازم، و نکات مهم را به صورت کامل در اختیار شما قرار می‌دهد.


# 📌 مقدمه
پروژه **Crypto** یک خط داده ایی است با استفاده از ابزار زیر که داده های رمز ارز های بازار را بافاصله زمانی هر 1 دقیقه به شما نمایش میدهد.

- **Airflow** (Webserver + Scheduler + Worker)
- **PostgreSQL** (پایگاه داده)
- **Kafka Broker** + **Zookeeper**
- **Kafka Connect**
- **Elasticsearch**
- **Kibana**
- **Logstash**

تمامی این سرویس‌ها از طریق یک فایل `docker-compose.yml` مدیریت و اجرا می‌شوند.


# 🧱 ساختار پروژه
```
sepahram/
│── docker-compose.yml
│── airflow/
│   ├── dags/
│   ├── logs/
│   └── plugins/
│── logstash/
│   └── logstash.conf
│── elasticsearch/
│── kafka/
│   ├── connectors/
│   └── configs/
└── README.md
```
>در این پروژه شما داده های دریافتی را در دیتابیس ذخیره کرده، به تاپیک کافکا منتقل میکنید و سپس از تاپیک کافکا به الستیک منتقل میکنید و در نهایت به کمک کیبانا از داده های خود نمودار رسم میکنید.


# 🐳 پیش‌نیازها
برای اجرای پروژه باید موارد زیر نصب باشد:

- Docker Desktop
- Docker Engine
- Docker Compose V2  
- (Postgres)  
- (Airflow Webserver)  
- (Kafka Broker)  
- (Elasticsearch)  
- (Kibana)  
- (Logstash Beats Input)

>💡 قبل از هر چیزی به سایت https://brsapi.ir مراجعه کرده و api_key منحصر به فرد خود را دریافت کنید.
سپس در دگ crypto_fetch_price.py قرار دهید، محل قرار دادن api_key

```
API_URL = "https://BrsApi.ir/Api/Market/Cryptocurrency.php?key=your_api_key"
```

# 🚀 راه اندازی پروژه

### 1️⃣ حذف نسخه‌های قبلی یا خراب
```
docker-compose down -v
```

### 2️⃣ ساخت مجدد کانتینرها
```
docker-compose build
```
> اگر هشدار `version is obsolete` دیدید طبیعی است و مشکلی ندارد.

### 3️⃣ بالا آوردن همه سرویس‌ها
```
docker-compose up -d
```

### 4️⃣ چک کردن وضعیت
```
docker ps -a
```

### 5️⃣ ساخت connection های مورد نیاز در airflow
#### 💡 برای اجرا صحیح دگ ها حتما باید connection های لازم هر دگ در ایرفلو تعریف شده باشد. به ایرفلو بروید  یک connection ایجاد کنید با مشخصات زیر
```
name => crypto_prices
type => postgres
host => postgres
database => airflowdb
login => mamali
passwod => 123456
port => 5432
```

### 6️⃣ ساخت جدول در دیتابیس

```
docker exec -it postgres psql -U mamali -d airflowdb

 CREATE TABLE IF NOT EXISTS crypto_prices (
    id SERIAL PRIMARY KEY,
    date VARCHAR(20),
    time VARCHAR(20),
    time_unix BIGINT,
    name_en VARCHAR(100),
    name_fa VARCHAR(100),
    price DOUBLE PRECISION,
    price_toman BIGINT,
    change_percent DOUBLE PRECISION,
    market_cap BIGINT,
    link_icon TEXT,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 7️⃣ اجرا دگ crypto_fetch_price 
این دگ هر دقیقه به api که در آن قرار داده شده درخواست ارسال کرده و بعد از دریافت اطلاعات آنرا در جدول crypto_prices که قبل تر ساختید منتقل میکند.


# 🔗 آدرس‌های مهم سرویس‌ها
پس از اجرای موفق `docker-compose up -d` می‌توانید سرویس‌های زیر را باز کنید:

| سرویس | آدرس | یوزر/پسورد
|-------|-------|-------|
| Airflow Web UI | http://localhost:8080 | admin/admin
| Kibana | http://localhost:5601 | none
| Elasticsearch Info | http://localhost:9200 | none
| Kafka UI | http://localhost:8085 | none
| Logstash Beats Input | `localhost:5044` | none
 | Postgres | `localhost:5432` | none

---

# 🗄 تنظیمات PostgreSQL
در فایل Docker Compose شما برای Postgres چیزی شبیه این دارید:

```
postgres:
  image: postgres:15
  environment:
    POSTGRES_USER: mamali
    POSTGRES_PASSWORD: 123456
    POSTGRES_DB: airflowdb
```

### اتصال Airflow به Postgres
در Airflow باید یوزر و پسورد و دیتابیس مطابق Postgres باشد:
```
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://mamali:123456@postgres:5432/airflowdb
```

---

# ☁ Kafka اتصال Airflow → Kafka
شما 2 دگ دارید با نام های : 
```
crypto_fetch_price.py 
postgres_crypto_to_kafka.py
```
دگ اول داده های رمزارز ها را در جدول crypto_prices در دیتابیس airflowdb درج میکند.
اگر این دگ هنگام اجرا خطا داشت مطمئن شوید که جدول ساخته شده باشد. 
دگ دوم نیز داده هایی که در جدول درج شده اند را به تاپیک کافکا crypto_prices منتقل میکند.

# 📊 ELK Stack (Elasticsearch + Logstash + Kibana)

## فایل کانفیگ Logstash 
این پایپ لاین داده موجود در کافکا را به ایندکس ذکر شده در الستیک منتقل میکند.

```
input {
  kafka {
    bootstrap_servers => "kafka:9092"
    topics => ["crypto_prices"]
    group_id => "logstash-crypto"
    codec => json
  }
}

filter {
  mutate {
    convert => { "id" => "integer" }
  }
}

output {
  elasticsearch {
    hosts => ["http://elasticsearch:9200"]
    index => "crypto_prices"
  }
  stdout { codec => rubydebug }
}

```

### مشکل رایج: پورت 5044 خطا می‌دهد
اگر این خطا را دیدید:
```
Error: ports are not available: 0.0.0.0:5044
```
یعنی پورت 5044 روی سیستم شما قبلاً در حال استفاده است.

### رفع مشکل:
```
netstat -ano | findstr 5044
```
سپس پردازش را Kill کنید:
```
taskkill /PID <ID> /F
```
یا در docker-compose پورت را تغییر دهید:
```
5045:5044
```

---

# ⚙ دستورات مفید Docker

### مشاهده لاگ یک سرویس
```
docker logs airflow-webserver -f
```

### ریستارت کردن یک سرویس
```
docker restart kafka
```

### ورود به کانتینر
```
docker exec -it postgres bash
```

### حذف کامل تمام کانتینرها و ایمیج‌ها
☠️ خطرناک! در صورت اعمال این دستور تمامی image هایی که دانلود کرده بودید حذف میشوند. (اینترنت به فنا)
```
docker system prune -a
```

---

# 🪄 ترفندهای مهم برای جلوگیری از خطا
 همیشه قبل از اجرای مجدد:
```
docker-compose down -v
```
#### . مطمئن باشید پورت‌ها آزاد باشند
#### . اسامی سرویس‌ها در docker-compose باید در DAGها دقیقاً همان باشند

---

# 🤝 در صورت نیاز به کمک
هرجا گیر کردی، به پشتیبانی سایت پیام دهید یا به آیدی @mamaliebi پیام دهید.
