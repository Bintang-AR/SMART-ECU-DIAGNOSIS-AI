# AUDRIVE : "Listen Early, Drive Safer"
Anggota :
- Andika Bintang Ramadhan
- Muhammad Iqbal
- Muhamad Ikhsan Ramadhan
- Rasyiq Surya Ramadhan


Aplikasi/layanan yang mendiagnosis masalah mesin kendaraan (motor/mobil/fleet) dari audio + getaran + telemetri menggunakan model deep learning. 
Hasil: jenis kerusakan, tingkat keparahan, rekomendasi tindakan, dan estimasi biaya servis

Masalah yang diangkat :
- Pemilik kendaraan tidak bisa mengenali suara mesin abnormal sejak dini
- Diagnosa mesin masih bergantung pada mekanik & alat mahal (Scanner)
- Tidak ada alat diagnosa murah berbasis suara yang bisa digunakan semua orang


Teknologi yang digunakan :
- Machine Learning (CNN)
- Python Programming Language
- Audio processing 
- Front End Web
- Back End API




*note : 
1. pastikan anda menginstall node.js
   lalu cek dengan cmd/bash :

   npm -v

   atau

   node -v
2. pastikan ffmpeg di install
3. install semua yang ada di requirements.txt
   bash :
   
   pip install -r requirements.txt

Panduan Menjalankan Aplikasi
Berikut adalah langkah-langkah yang diperlukan untuk menjalankan aplikasi (baik backend maupun frontend):

1. Menjalankan Layanan Backend
- Layanan backend harus dijalankan terlebih dahulu.

- Arahkan ke Direktori: Buka Terminal atau Command Prompt (CMD) dan navigasikan ke direktori src/backend.

- Jalankan Server: Eksekusi perintah berikut untuk memulai server backend:

Bash : 

py -m uvicorn app:app --reload --port 8000

- Verifikasi: Tunggu hingga Anda melihat pesan yang mengindikasikan bahwa aplikasi telah berhasil dimulai (misalnya, "Application startup complete" atau sejenisnya). Layanan sekarang berjalan di port 8000.

2. Menjalankan Layanan Frontend
Setelah backend berjalan, Anda dapat menjalankan frontend.

- Buka Terminal Baru: Buka jendela Terminal atau Command Prompt kedua (pastikan server backend tetap berjalan di jendela pertama).

- Arahkan ke Direktori: Navigasikan ke direktori src.

- Jalankan Aplikasi: Eksekusi perintah berikut untuk memulai aplikasi frontend:

Bash : 

npm run dev



Setelah kedua langkah selesai, aplikasi seharusnya sudah dapat diakses melalui browser.
