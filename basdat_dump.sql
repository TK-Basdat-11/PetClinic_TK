
CREATE SCHEMA IF NOT EXISTS PETCLINIC;
SET search_path TO PETCLINIC;
SET datestyle = 'DMY';
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. USERS Table
CREATE TABLE USERS (
   email VARCHAR(50) PRIMARY KEY,
   password_user VARCHAR(100) NOT NULL,
   alamat TEXT NOT NULL,
   nomor_telepon VARCHAR(15) NOT NULL
);

-- 2. PEGAWAI Table
CREATE TABLE PEGAWAI (
	no_pegawai UUID PRIMARY KEY,
	tanggal_mulai_kerja DATE NOT NULL,
	tanggal_akhir_kerja DATE,
	email VARCHAR(50) NOT NULL,
	FOREIGN KEY (email) REFERENCES USERS(email) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 3. KLIEN Table
CREATE TABLE KLIEN (
	no_identitas UUID PRIMARY KEY,
	tanggal_registrasi DATE NOT NULL,
	email VARCHAR(50) NOT NULL,
	FOREIGN KEY (email) REFERENCES USERS(email) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 4. INDIVIDU Table
CREATE TABLE INDIVIDU (
   no_identitas_klien UUID PRIMARY KEY,
   nama_depan VARCHAR(50) NOT NULL,
   nama_tengah VARCHAR(50),
   nama_belakang VARCHAR(50) NOT NULL,
   FOREIGN KEY (no_identitas_klien) REFERENCES KLIEN(no_identitas) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 5. PERUSAHAAN Table
CREATE TABLE PERUSAHAAN (
	no_identitas_klien UUID PRIMARY KEY,
	nama_perusahaan VARCHAR(100) NOT NULL,
	FOREIGN KEY (no_identitas_klien) REFERENCES KLIEN(no_identitas) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 6. FRONT_DESK Table
CREATE TABLE FRONT_DESK (
	no_front_desk UUID PRIMARY KEY,
	FOREIGN KEY (no_front_desk) REFERENCES PEGAWAI(no_pegawai) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 7. TENAGA_MEDIS Table
CREATE TABLE TENAGA_MEDIS (
	no_tenaga_medis UUID PRIMARY KEY,
	no_izin_praktik VARCHAR(20) UNIQUE NOT NULL,
	FOREIGN KEY (no_tenaga_medis) REFERENCES PEGAWAI(no_pegawai) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 8. PERAWAT_HEWAN Table
CREATE TABLE PERAWAT_HEWAN (
	no_perawat_hewan UUID PRIMARY KEY,
	FOREIGN KEY (no_perawat_hewan) REFERENCES TENAGA_MEDIS(no_tenaga_medis) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 9. DOKTER_HEWAN Table
CREATE TABLE DOKTER_HEWAN (
	no_dokter_hewan UUID PRIMARY KEY,
	FOREIGN KEY (no_dokter_hewan) REFERENCES TENAGA_MEDIS(no_tenaga_medis) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 10. JENIS_HEWAN Table
CREATE TABLE JENIS_HEWAN (
	id UUID PRIMARY KEY,
	nama_jenis VARCHAR(50) NOT NULL
);

-- 11. HEWAN Table
CREATE TABLE HEWAN (
	nama VARCHAR(50) NOT NULL,
	no_identitas_klien UUID NOT NULL,
	tanggal_lahir DATE NOT NULL,
	id_jenis UUID NOT NULL,
	url_foto VARCHAR(255) NOT NULL,
	PRIMARY KEY (nama, no_identitas_klien),
	FOREIGN KEY (no_identitas_klien) REFERENCES KLIEN(no_identitas) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (id_jenis) REFERENCES JENIS_HEWAN(id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 12. OBAT Table
CREATE TABLE OBAT (
	kode VARCHAR(10) PRIMARY KEY,
	nama VARCHAR(100) NOT NULL,
	harga INT NOT NULL,
	stok INT NOT NULL,
	dosis TEXT NOT NULL
);

-- 13. VAKSIN Table
CREATE TABLE VAKSIN (
	kode VARCHAR(6) PRIMARY KEY,
	nama VARCHAR(50) NOT NULL,
	harga INT NOT NULL CHECK (harga >= 0),
	stok INT NOT NULL CHECK (stok >= 0)
);

-- 14. PERAWATAN Table
CREATE TABLE PERAWATAN (
	kode_perawatan VARCHAR(10) PRIMARY KEY,
	nama_perawatan VARCHAR(100) NOT NULL,
	biaya_perawatan INT NOT NULL
);

-- 15. PERAWATAN_OBAT Table
CREATE TABLE PERAWATAN_OBAT (
	kode_perawatan VARCHAR(10) NOT NULL,
	kode_obat VARCHAR(10) NOT NULL,
	kuantitas_obat INT NOT NULL,
	PRIMARY KEY (kode_perawatan, kode_obat),
	FOREIGN KEY (kode_perawatan) REFERENCES PERAWATAN(kode_perawatan) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (kode_obat) REFERENCES OBAT(kode) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 16. SERTIFIKAT_KOMPETENSI Table
CREATE TABLE SERTIFIKAT_KOMPETENSI (
	no_sertifikat_kompetensi VARCHAR(10) PRIMARY KEY,
	no_tenaga_medis UUID NOT NULL,
	nama_sertifikat VARCHAR(100) NOT NULL,
	FOREIGN KEY (no_tenaga_medis) REFERENCES TENAGA_MEDIS(no_tenaga_medis) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 17. KUNJUNGAN Table
CREATE TABLE KUNJUNGAN (
	id_kunjungan UUID PRIMARY KEY,
	nama_hewan VARCHAR(50) NOT NULL,
	no_identitas_klien UUID NOT NULL,
	no_front_desk UUID NOT NULL,
	no_perawat_hewan UUID,
	no_dokter_hewan UUID,
	kode_vaksin VARCHAR(6),
	tipe_kunjungan VARCHAR(10) NOT NULL,
	timestamp_awal TIMESTAMP NOT NULL,
	timestamp_akhir TIMESTAMP,
	suhu INT,
	berat_badan NUMERIC(5,2),
	catatan TEXT,
	FOREIGN KEY (nama_hewan, no_identitas_klien) REFERENCES HEWAN(nama, no_identitas_klien) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (no_front_desk) REFERENCES FRONT_DESK(no_front_desk) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (no_perawat_hewan) REFERENCES PERAWAT_HEWAN(no_perawat_hewan) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (no_dokter_hewan) REFERENCES DOKTER_HEWAN(no_dokter_hewan) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (kode_vaksin) REFERENCES VAKSIN(kode) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 18. KUNJUNGAN_KEPERAWATAN Table
CREATE TABLE KUNJUNGAN_KEPERAWATAN (
	id_kunjungan UUID,
	nama_hewan VARCHAR(50),
	no_identitas_klien UUID,
	no_front_desk UUID,
	no_perawat_hewan UUID,
	no_dokter_hewan UUID,
	kode_perawatan VARCHAR(10),
	PRIMARY KEY (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan),
	FOREIGN KEY (id_kunjungan) REFERENCES KUNJUNGAN(id_kunjungan) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (nama_hewan, no_identitas_klien) REFERENCES HEWAN(nama, no_identitas_klien) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (no_front_desk) REFERENCES FRONT_DESK(no_front_desk) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (no_perawat_hewan) REFERENCES PERAWAT_HEWAN(no_perawat_hewan) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (no_dokter_hewan) REFERENCES DOKTER_HEWAN(no_dokter_hewan) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (kode_perawatan) REFERENCES PERAWATAN(kode_perawatan) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 19. JADWAL_PRAKTIK Table
CREATE TABLE JADWAL_PRAKTIK ( no_dokter_hewan UUID, hari VARCHAR(10), jam VARCHAR(20), PRIMARY KEY (no_dokter_hewan, hari, jam), FOREIGN KEY (no_dokter_hewan) REFERENCES DOKTER_HEWAN(no_dokter_hewan) ON UPDATE CASCADE ON DELETE CASCADE );

-- INSERT DATA
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user1@gmail.com', 'password01', 'Jl. Anggrek No. 1', '08120000001');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user2@gmail.com', 'password02', 'Jl. Mawar No. 2', '08120000002');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user3@gmail.com', 'password03', 'Jl. Melati No. 3', '08120000003');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user4@gmail.com', 'password04', 'Jl. Flamboyan No. 4', '08120000004');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user5@gmail.com', 'password05', 'Jl. Kenanga No. 5', '08120000005');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user6@gmail.com', 'password06', 'Jl. Cempaka No. 6', '08120000006');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user7@gmail.com', 'password07', 'Jl. Teratai No. 7', '08120000007');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user8@gmail.com', 'password08', 'Jl. Dahlia No. 8', '08120000008');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user9@gmail.com', 'password09', 'Jl. Sedap Malam No. 9', '08120000009');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user10@gmail.com', 'password10', 'Jl. Bougenville No. 10', '08120000010');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user11@gmail.com', 'password11', 'Jl. Kamboja No. 11', '08120000011');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user12@gmail.com', 'password12', 'Jl. Kemuning No. 12', '08120000012');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user13@gmail.com', 'password13', 'Jl. Rajawali No. 13', '08120000013');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user14@gmail.com', 'password14', 'Jl. Cemara No. 14', '08120000014');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user15@gmail.com', 'password15', 'Jl. Sawo Manila No. 15', '08120000015');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user16@gmail.com', 'password16', 'Jl. Bulan No. 16', '08120000016');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user17@gmail.com', 'password17', 'Jl. Mentari No. 17', '08120000017');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user18@gmail.com', 'password18', 'Jl. Pinus No. 18', '08120000018');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user19@gmail.com', 'password19', 'Jl. Rusa No. 19', '08120000019');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user20@gmail.com', 'password20', 'Jl. Lumba-Lumba No. 20', '08120000020');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user21@gmail.com', 'password21', 'Jl. Kelapa No. 21', '08120000021');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user22@gmail.com', 'password22', 'Jl. Durian No. 22', '08120000022');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user23@gmail.com', 'password23', 'Jl. Merpati No. 23', '08120000023');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user24@gmail.com', 'password24', 'Jl. Garuda No. 24', '08120000024');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user25@gmail.com', 'password25', 'Jl. Bukit No. 25', '08120000025');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user26@gmail.com', 'password26', 'Jl. Sungai No. 26', '08120000026');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user27@gmail.com', 'password27', 'Jl. Pantai No. 27', '08120000027');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user28@gmail.com', 'password28', 'Jl. Gunung No. 28', '08120000028');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user29@gmail.com', 'password29', 'Jl. Pendidikan No. 29', '08120000029');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user30@gmail.com', 'password30', 'Jl. Kesehatan No. 30', '08120000030');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user31@gmail.com', 'password31', 'Jl. Olahraga No. 31', '08120000031');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user32@gmail.com', 'password32', 'Jl. Industri No. 32', '08120000032');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user33@gmail.com', 'password33', 'Jl. Kemakmuran No. 33', '08120000033');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user34@gmail.com', 'password34', 'Jl. Persahabatan No. 34', '08120000034');
INSERT INTO users (email, password_user, alamat, nomor_telepon) VALUES ('user35@gmail.com', 'password35', 'Jl. Kebajikan No. 35', '08120000035');

INSERT INTO pegawai (no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email) VALUES ('8451fbbf-e73b-4f4b-90cb-2066e1f34685', '17-01-2023', NULL, 'user1@gmail.com');
INSERT INTO pegawai (no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email) VALUES ('c872f0ce-ffd3-4908-aa27-49974751ebc2', '20-04-2023', NULL, 'user2@gmail.com');
INSERT INTO pegawai (no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email) VALUES ('3c8c19ef-d569-4815-ba00-833cdc6111fd', '27-04-2023', NULL, 'user3@gmail.com');
INSERT INTO pegawai (no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email) VALUES ('b4aa4388-05bf-48e8-91c8-0e0a158cd56b', '14-05-2023', NULL, 'user4@gmail.com');
INSERT INTO pegawai (no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email) VALUES ('37c4e97c-3aa7-43b7-a583-03f47b92eb4e', '01-06-2023', '01-06-2024', 'user5@gmail.com');
INSERT INTO pegawai (no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email) VALUES ('e0bca1e9-7a9b-4ef5-90a8-ab27392995d0', '09-08-2023', NULL, 'user6@gmail.com');
INSERT INTO pegawai (no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email) VALUES ('06d274ce-f64f-4690-94ae-ade80f9ae6f0', '18-01-2024', NULL, 'user7@gmail.com');
INSERT INTO pegawai (no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email) VALUES ('1e865074-4237-4f5b-98f8-20fdf24eaa62', '03-03-2024', '03-03-2025', 'user8@gmail.com');
INSERT INTO pegawai (no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email) VALUES ('b643f56b-90c7-45ff-9cbe-3e4873ff0b70', '20-04-2024', NULL, 'user9@gmail.com');
INSERT INTO pegawai (no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email) VALUES ('5abc7d6a-e48f-46a3-9ee6-df5096da1049', '14-05-2024', NULL, 'user10@gmail.com');
INSERT INTO pegawai (no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email) VALUES ('7840c75f-a611-4036-9bdf-e095c6cbeb64', '05-08-2024', NULL, 'user11@gmail.com');
INSERT INTO pegawai (no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email) VALUES ('878b4bba-013f-4b5b-9f41-30c88fa94db1', '01-09-2024', NULL, 'user12@gmail.com');
INSERT INTO pegawai (no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email) VALUES ('d638c464-69ad-4fba-a82c-4892f15891ee', '23-12-2024', NULL, 'user13@gmail.com');
INSERT INTO pegawai (no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email) VALUES ('a84f8227-093e-4749-a62c-4508c82c928a', '19-06-2025', NULL, 'user14@gmail.com');
INSERT INTO pegawai (no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email) VALUES ('dd07aa17-898b-4d58-b08f-621d8b801ed2', '26-07-2025', NULL, 'user15@gmail.com');


INSERT INTO klien (no_identitas, tanggal_registrasi, email) VALUES ('3a94232d-8824-46d8-a4bf-2fbf6b4c4cd8', '17-09-2024', 'user16@gmail.com');
INSERT INTO klien (no_identitas, tanggal_registrasi, email) VALUES ('cc9bf851-835d-4f8e-8170-3bb8efefac68', '26-07-2024', 'user17@gmail.com');
INSERT INTO klien (no_identitas, tanggal_registrasi, email) VALUES ('64bf941b-1989-42fe-b88d-4bf9a55c66d3', '30-12-2024', 'user18@gmail.com');
INSERT INTO klien (no_identitas, tanggal_registrasi, email) VALUES ('c8916d2a-c1f8-40b5-afb4-20aaa70c0493', '04-10-2024', 'user19@gmail.com');
INSERT INTO klien (no_identitas, tanggal_registrasi, email) VALUES ('29fd603f-c1b0-4d0f-8155-9b64141282d0', '19-05-2024', 'user20@gmail.com');
INSERT INTO klien (no_identitas, tanggal_registrasi, email) VALUES ('b7104154-7db2-4f20-aa96-1be414b50966', '28-09-2024', 'user21@gmail.com');
INSERT INTO klien (no_identitas, tanggal_registrasi, email) VALUES ('5cd27a98-fa11-4959-b8ac-dc33fd87fef6', '10-11-2024', 'user22@gmail.com');
INSERT INTO klien (no_identitas, tanggal_registrasi, email) VALUES ('cdedd83b-e519-471b-ae8a-6059a0d4b0b9', '15-07-2024', 'user23@gmail.com');
INSERT INTO klien (no_identitas, tanggal_registrasi, email) VALUES ('626c9bcf-e15e-4930-972c-2025f24b7096', '09-10-2024', 'user24@gmail.com');
INSERT INTO klien (no_identitas, tanggal_registrasi, email) VALUES ('1547aba3-cd73-4a59-8ac9-0786256c97aa', '08-07-2024', 'user25@gmail.com');
INSERT INTO klien (no_identitas, tanggal_registrasi, email) VALUES ('4791bf9b-b9ec-4f1a-a128-4c6160356015', '19-02-2025', 'user26@gmail.com');
INSERT INTO klien (no_identitas, tanggal_registrasi, email) VALUES ('6c844274-d378-4380-8450-2121c9326477', '29-04-2024', 'user27@gmail.com');
INSERT INTO klien (no_identitas, tanggal_registrasi, email) VALUES ('0b1da535-e152-4493-afe9-eecab6ce41c1', '17-04-2025', 'user28@gmail.com');
INSERT INTO klien (no_identitas, tanggal_registrasi, email) VALUES ('1bafd5cb-ae9f-4dd2-a920-4d1ec1d14c8a', '10-03-2025', 'user29@gmail.com');
INSERT INTO klien (no_identitas, tanggal_registrasi, email) VALUES ('8790d01e-a149-4abe-92a7-874786c51076', '30-11-2024', 'user30@gmail.com');
INSERT INTO klien (no_identitas, tanggal_registrasi, email) VALUES ('ed775071-29ce-4e57-965e-dd8fd34ca070', '10-07-2024', 'user31@gmail.com');
INSERT INTO klien (no_identitas, tanggal_registrasi, email) VALUES ('af7c31e5-7e1c-477c-bd78-5dfa621fd996', '12-08-2024', 'user32@gmail.com');
INSERT INTO klien (no_identitas, tanggal_registrasi, email) VALUES ('24f5edf2-a0f9-4db1-af9a-610773a4037e', '09-12-2024', 'user33@gmail.com');
INSERT INTO klien (no_identitas, tanggal_registrasi, email) VALUES ('709365fb-9597-430e-b235-958fe82e3d13', '24-03-2025', 'user34@gmail.com');
INSERT INTO klien (no_identitas, tanggal_registrasi, email) VALUES ('7ea7f7d4-ec67-40f0-8e91-de1d8bcdc541', '01-05-2024', 'user35@gmail.com');


INSERT INTO individu (no_identitas_klien, nama_depan, nama_tengah, nama_belakang) VALUES ('3a94232d-8824-46d8-a4bf-2fbf6b4c4cd8', 'Andi', 'Budi', 'Santoso');
INSERT INTO individu (no_identitas_klien, nama_depan, nama_tengah, nama_belakang) VALUES ('cc9bf851-835d-4f8e-8170-3bb8efefac68', 'Citra', 'Dewi', 'Lestari');
INSERT INTO individu (no_identitas_klien, nama_depan, nama_tengah, nama_belakang) VALUES ('64bf941b-1989-42fe-b88d-4bf9a55c66d3', 'Dedi', '', 'Prasetyo');
INSERT INTO individu (no_identitas_klien, nama_depan, nama_tengah, nama_belakang) VALUES ('c8916d2a-c1f8-40b5-afb4-20aaa70c0493', 'Eka', 'Nur', 'Prasetyo');
INSERT INTO individu (no_identitas_klien, nama_depan, nama_tengah, nama_belakang) VALUES ('29fd603f-c1b0-4d0f-8155-9b64141282d0', 'Fajar', 'Rizky', 'Ramadhan');
INSERT INTO individu (no_identitas_klien, nama_depan, nama_tengah, nama_belakang) VALUES ('b7104154-7db2-4f20-aa96-1be414b50966', 'Gita', '', 'Anggraini');
INSERT INTO individu (no_identitas_klien, nama_depan, nama_tengah, nama_belakang) VALUES ('5cd27a98-fa11-4959-b8ac-dc33fd87fef6', 'Hendra', 'Saputra', 'Widodo');
INSERT INTO individu (no_identitas_klien, nama_depan, nama_tengah, nama_belakang) VALUES ('cdedd83b-e519-471b-ae8a-6059a0d4b0b9', 'Indah', 'Permata', 'Sari');
INSERT INTO individu (no_identitas_klien, nama_depan, nama_tengah, nama_belakang) VALUES ('626c9bcf-e15e-4930-972c-2025f24b7096', 'Joko', 'Budi', 'Susanto');
INSERT INTO individu (no_identitas_klien, nama_depan, nama_tengah, nama_belakang) VALUES ('1547aba3-cd73-4a59-8ac9-0786256c97aa', 'Kartika', '', 'Ningsih');

INSERT INTO perusahaan (no_identitas_klien, nama_perusahaan) VALUES ('4791bf9b-b9ec-4f1a-a128-4c6160356015', 'PT Upin Ipin');
INSERT INTO perusahaan (no_identitas_klien, nama_perusahaan) VALUES ('6c844274-d378-4380-8450-2121c9326477', 'PT Sehat Sejahtera');
INSERT INTO perusahaan (no_identitas_klien, nama_perusahaan) VALUES ('0b1da535-e152-4493-afe9-eecab6ce41c1', 'PT Tadika Mesra');
INSERT INTO perusahaan (no_identitas_klien, nama_perusahaan) VALUES ('1bafd5cb-ae9f-4dd2-a920-4d1ec1d14c8a', 'PT Spongebob Patrick');
INSERT INTO perusahaan (no_identitas_klien, nama_perusahaan) VALUES ('8790d01e-a149-4abe-92a7-874786c51076', 'PT Plankton');
INSERT INTO perusahaan (no_identitas_klien, nama_perusahaan) VALUES ('ed775071-29ce-4e57-965e-dd8fd34ca070', 'PT Krabby Patty');
INSERT INTO perusahaan (no_identitas_klien, nama_perusahaan) VALUES ('af7c31e5-7e1c-477c-bd78-5dfa621fd996', 'PT Krusty Krab');
INSERT INTO perusahaan (no_identitas_klien, nama_perusahaan) VALUES ('24f5edf2-a0f9-4db1-af9a-610773a4037e', 'PT Miaw');
INSERT INTO perusahaan (no_identitas_klien, nama_perusahaan) VALUES ('709365fb-9597-430e-b235-958fe82e3d13', 'PT Kucing Imut');
INSERT INTO perusahaan (no_identitas_klien, nama_perusahaan) VALUES ('7ea7f7d4-ec67-40f0-8e91-de1d8bcdc541', 'PT Manusia Harimau');

INSERT INTO tenaga_medis (no_tenaga_medis, no_izin_praktik) VALUES ('e0bca1e9-7a9b-4ef5-90a8-ab27392995d0', 'SIP-HEWAN-0001');
INSERT INTO tenaga_medis (no_tenaga_medis, no_izin_praktik) VALUES ('06d274ce-f64f-4690-94ae-ade80f9ae6f0', 'SIP-HEWAN-0002');
INSERT INTO tenaga_medis (no_tenaga_medis, no_izin_praktik) VALUES ('1e865074-4237-4f5b-98f8-20fdf24eaa62', 'SIP-HEWAN-0003');
INSERT INTO tenaga_medis (no_tenaga_medis, no_izin_praktik) VALUES ('b643f56b-90c7-45ff-9cbe-3e4873ff0b70', 'SIP-HEWAN-0004');
INSERT INTO tenaga_medis (no_tenaga_medis, no_izin_praktik) VALUES ('5abc7d6a-e48f-46a3-9ee6-df5096da1049', 'SIP-HEWAN-0005');
INSERT INTO tenaga_medis (no_tenaga_medis, no_izin_praktik) VALUES ('7840c75f-a611-4036-9bdf-e095c6cbeb64', 'SIP-HEWAN-0006');
INSERT INTO tenaga_medis (no_tenaga_medis, no_izin_praktik) VALUES ('878b4bba-013f-4b5b-9f41-30c88fa94db1', 'SIP-HEWAN-0007');
INSERT INTO tenaga_medis (no_tenaga_medis, no_izin_praktik) VALUES ('d638c464-69ad-4fba-a82c-4892f15891ee', 'SIP-HEWAN-0008');
INSERT INTO tenaga_medis (no_tenaga_medis, no_izin_praktik) VALUES ('a84f8227-093e-4749-a62c-4508c82c928a', 'SIP-HEWAN-0009');
INSERT INTO tenaga_medis (no_tenaga_medis, no_izin_praktik) VALUES ('dd07aa17-898b-4d58-b08f-621d8b801ed2', 'SIP-HEWAN-0010');



INSERT INTO dokter_hewan (no_dokter_hewan) VALUES ('7840c75f-a611-4036-9bdf-e095c6cbeb64');
INSERT INTO dokter_hewan (no_dokter_hewan) VALUES ('878b4bba-013f-4b5b-9f41-30c88fa94db1');
INSERT INTO dokter_hewan (no_dokter_hewan) VALUES ('d638c464-69ad-4fba-a82c-4892f15891ee');
INSERT INTO dokter_hewan (no_dokter_hewan) VALUES ('a84f8227-093e-4749-a62c-4508c82c928a');
INSERT INTO dokter_hewan (no_dokter_hewan) VALUES ('dd07aa17-898b-4d58-b08f-621d8b801ed2');

INSERT INTO perawat_hewan (no_perawat_hewan) VALUES ('e0bca1e9-7a9b-4ef5-90a8-ab27392995d0');
INSERT INTO perawat_hewan (no_perawat_hewan) VALUES ('06d274ce-f64f-4690-94ae-ade80f9ae6f0');
INSERT INTO perawat_hewan (no_perawat_hewan) VALUES ('1e865074-4237-4f5b-98f8-20fdf24eaa62');
INSERT INTO perawat_hewan (no_perawat_hewan) VALUES ('b643f56b-90c7-45ff-9cbe-3e4873ff0b70');
INSERT INTO perawat_hewan (no_perawat_hewan) VALUES ('5abc7d6a-e48f-46a3-9ee6-df5096da1049');


INSERT INTO jenis_hewan (id, nama_jenis) VALUES ('1af3c05b-89f1-4fe6-a0b5-7cb491ff8311', 'Kucing');
INSERT INTO jenis_hewan (id, nama_jenis) VALUES ('4b07c9a2-44dd-4cc0-b423-efdb4baae250', 'Anjing');
INSERT INTO jenis_hewan (id, nama_jenis) VALUES ('40d37d54-63a8-47e9-b8ba-275ebd6492a5', 'Kelinci');
INSERT INTO jenis_hewan (id, nama_jenis) VALUES ('f1de2453-4a47-4fda-aefa-62c3a7a10405', 'Hamster');
INSERT INTO jenis_hewan (id, nama_jenis) VALUES ('6a2b5d70-08f6-4f64-96cc-95c24d83bd8d', 'Burung');



INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Bella', '3a94232d-8824-46d8-a4bf-2fbf6b4c4cd8', '1996-04-03', '1af3c05b-89f1-4fe6-a0b5-7cb491ff8311', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Babel', '3a94232d-8824-46d8-a4bf-2fbf6b4c4cd8', '1996-04-03', '1af3c05b-89f1-4fe6-a0b5-7cb491ff8311', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Mika', 'cc9bf851-835d-4f8e-8170-3bb8efefac68', '1996-07-25', '4b07c9a2-44dd-4cc0-b423-efdb4baae250', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Milo', 'cc9bf851-835d-4f8e-8170-3bb8efefac68', '1996-07-25', '4b07c9a2-44dd-4cc0-b423-efdb4baae250', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Lupis', '64bf941b-1989-42fe-b88d-4bf9a55c66d3', '1999-02-13', '40d37d54-63a8-47e9-b8ba-275ebd6492a5', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Luna', '64bf941b-1989-42fe-b88d-4bf9a55c66d3', '1999-02-13', '40d37d54-63a8-47e9-b8ba-275ebd6492a5', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Rori', 'c8916d2a-c1f8-40b5-afb4-20aaa70c0493', '2000-09-01', 'f1de2453-4a47-4fda-aefa-62c3a7a10405', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Rocky', 'c8916d2a-c1f8-40b5-afb4-20aaa70c0493', '2000-09-01', 'f1de2453-4a47-4fda-aefa-62c3a7a10405', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Caca', '29fd603f-c1b0-4d0f-8155-9b64141282d0', '1990-08-02', '6a2b5d70-08f6-4f64-96cc-95c24d83bd8d', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Coco', '29fd603f-c1b0-4d0f-8155-9b64141282d0', '1990-08-02', '6a2b5d70-08f6-4f64-96cc-95c24d83bd8d', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Singa', 'b7104154-7db2-4f20-aa96-1be414b50966', '1992-04-15', '1af3c05b-89f1-4fe6-a0b5-7cb491ff8311', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Simba', 'b7104154-7db2-4f20-aa96-1be414b50966', '1992-04-15', '1af3c05b-89f1-4fe6-a0b5-7cb491ff8311', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Nita', '5cd27a98-fa11-4959-b8ac-dc33fd87fef6', '1994-07-24', '4b07c9a2-44dd-4cc0-b423-efdb4baae250', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Nala', '5cd27a98-fa11-4959-b8ac-dc33fd87fef6', '1994-07-24', '4b07c9a2-44dd-4cc0-b423-efdb4baae250', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Catur', 'cdedd83b-e519-471b-ae8a-6059a0d4b0b9', '1991-01-24', '40d37d54-63a8-47e9-b8ba-275ebd6492a5', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Charlie', 'cdedd83b-e519-471b-ae8a-6059a0d4b0b9', '1991-01-24', '40d37d54-63a8-47e9-b8ba-275ebd6492a5', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Rafa', '626c9bcf-e15e-4930-972c-2025f24b7096', '1992-09-14', 'f1de2453-4a47-4fda-aefa-62c3a7a10405', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Ruby', '626c9bcf-e15e-4930-972c-2025f24b7096', '1992-09-14', 'f1de2453-4a47-4fda-aefa-62c3a7a10405', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Mamet', '1547aba3-cd73-4a59-8ac9-0786256c97aa', '1995-10-18', '6a2b5d70-08f6-4f64-96cc-95c24d83bd8d', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Max', '1547aba3-cd73-4a59-8ac9-0786256c97aa', '1995-10-18', '6a2b5d70-08f6-4f64-96cc-95c24d83bd8d', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Mafu', '4791bf9b-b9ec-4f1a-a128-4c6160356015', '2003-03-28', '1af3c05b-89f1-4fe6-a0b5-7cb491ff8311', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Mochi', '4791bf9b-b9ec-4f1a-a128-4c6160356015', '2003-03-28', '1af3c05b-89f1-4fe6-a0b5-7cb491ff8311', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Omeng', '6c844274-d378-4380-8450-2121c9326477', '1995-11-20', '4b07c9a2-44dd-4cc0-b423-efdb4baae250', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Oyen', '6c844274-d378-4380-8450-2121c9326477', '1995-11-20', '4b07c9a2-44dd-4cc0-b423-efdb4baae250', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Bikun', '0b1da535-e152-4493-afe9-eecab6ce41c1', '1995-09-22', '40d37d54-63a8-47e9-b8ba-275ebd6492a5', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Bintang', '0b1da535-e152-4493-afe9-eecab6ce41c1', '1995-09-22', '40d37d54-63a8-47e9-b8ba-275ebd6492a5', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Zesha', '1bafd5cb-ae9f-4dd2-a920-4d1ec1d14c8a', '1993-01-10', 'f1de2453-4a47-4fda-aefa-62c3a7a10405', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Zara', '1bafd5cb-ae9f-4dd2-a920-4d1ec1d14c8a', '1993-01-10', 'f1de2453-4a47-4fda-aefa-62c3a7a10405', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Lany', '8790d01e-a149-4abe-92a7-874786c51076', '2000-08-19', '6a2b5d70-08f6-4f64-96cc-95c24d83bd8d', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Leo', '8790d01e-a149-4abe-92a7-874786c51076', '2000-08-19', '6a2b5d70-08f6-4f64-96cc-95c24d83bd8d', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Keeki', 'ed775071-29ce-4e57-965e-dd8fd34ca070', '1996-12-01', '1af3c05b-89f1-4fe6-a0b5-7cb491ff8311', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Kiki', 'ed775071-29ce-4e57-965e-dd8fd34ca070', '1996-12-01', '1af3c05b-89f1-4fe6-a0b5-7cb491ff8311', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Lala', 'af7c31e5-7e1c-477c-bd78-5dfa621fd996', '2001-05-12', '4b07c9a2-44dd-4cc0-b423-efdb4baae250', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Lilo', 'af7c31e5-7e1c-477c-bd78-5dfa621fd996', '2001-05-12', '4b07c9a2-44dd-4cc0-b423-efdb4baae250', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Tango', '24f5edf2-a0f9-4db1-af9a-610773a4037e', '2000-01-19', '40d37d54-63a8-47e9-b8ba-275ebd6492a5', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Teddy', '24f5edf2-a0f9-4db1-af9a-610773a4037e', '2000-01-19', '40d37d54-63a8-47e9-b8ba-275ebd6492a5', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Ori', '709365fb-9597-430e-b235-958fe82e3d13', '1996-10-09', 'f1de2453-4a47-4fda-aefa-62c3a7a10405', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Oreo', '709365fb-9597-430e-b235-958fe82e3d13', '1996-10-09', 'f1de2453-4a47-4fda-aefa-62c3a7a10405', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Siomay', '7ea7f7d4-ec67-40f0-8e91-de1d8bcdc541', '2003-09-30', '6a2b5d70-08f6-4f64-96cc-95c24d83bd8d', 'https://picsum.photos/200');
INSERT INTO hewan (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES ('Sushi', '7ea7f7d4-ec67-40f0-8e91-de1d8bcdc541', '2003-09-30', '6a2b5d70-08f6-4f64-96cc-95c24d83bd8d', 'https://picsum.photos/200');

INSERT INTO obat (kode, nama, harga, stok, dosis) VALUES ('MED001', 'Amoxicillin 250 mg', '75000', '50', '10 mg/kg, 2× sehari, oral');
INSERT INTO obat (kode, nama, harga, stok, dosis) VALUES ('MED002', 'Ivermectin 1% injeksi', '120000', '30', '0,2 mg/kg, satu kali suntik SC');
INSERT INTO obat (kode, nama, harga, stok, dosis) VALUES ('MED003', 'Metronidazole 500 mg', '60000', '40', '15 mg/kg, 1× sehari, oral');
INSERT INTO obat (kode, nama, harga, stok, dosis) VALUES ('MED004', 'Cefalexin 250 mg', '80000', '45', '22 mg/kg, 2× sehari, oral');
INSERT INTO obat (kode, nama, harga, stok, dosis) VALUES ('MED005', 'Vitamin C Kapsul 500 mg', '50000', '60', '50 mg/kg, 1× sehari, oral');
INSERT INTO obat (kode, nama, harga, stok, dosis) VALUES ('MED006', 'Enrofloxacin 100 mg', '110000', '35', '5 mg/kg, 1× sehari, oral');
INSERT INTO obat (kode, nama, harga, stok, dosis) VALUES ('MED007', 'Ketoprofen 50 mg', '90000', '25', '2 mg/kg, 1× sehari, oral');
INSERT INTO obat (kode, nama, harga, stok, dosis) VALUES ('MED008', 'Meloxicam 15 mg', '95000', '28', '0,1 mg/kg, 1× sehari, oral');
INSERT INTO obat (kode, nama, harga, stok, dosis) VALUES ('MED009', 'Clindamycin 150 mg', '85000', '32', '11 mg/kg, 2× sehari, oral');
INSERT INTO obat (kode, nama, harga, stok, dosis) VALUES ('MED010', 'Dexamethasone 0,5 mg', '70000', '20', '0,25 mg/kg, 1× sehari, oral');

INSERT INTO vaksin (kode, nama, harga, stok) VALUES ('VAC001', 'Rabies Vaccine', '100000', '10');
INSERT INTO vaksin (kode, nama, harga, stok) VALUES ('VAC002', 'Distemper Vaccine', '150000', '20');
INSERT INTO vaksin (kode, nama, harga, stok) VALUES ('VAC003', 'Parvovirus Vaccine', '200000', '30');
INSERT INTO vaksin (kode, nama, harga, stok) VALUES ('VAC004', 'Adenovirus Vaccine', '250000', '40');
INSERT INTO vaksin (kode, nama, harga, stok) VALUES ('VAC005', 'Leptospirosis Vaccine', '300000', '50');
INSERT INTO vaksin (kode, nama, harga, stok) VALUES ('VAC006', 'Bordetella Vaccine', '350000', '60');
INSERT INTO vaksin (kode, nama, harga, stok) VALUES ('VAC007', 'Canine Influenza Vaccine', '400000', '70');
INSERT INTO vaksin (kode, nama, harga, stok) VALUES ('VAC008', 'Lyme Disease Vaccine', '450000', '80');
INSERT INTO vaksin (kode, nama, harga, stok) VALUES ('VAC009', 'Canine Coronavirus Vaccine', '500000', '90');
INSERT INTO vaksin (kode, nama, harga, stok) VALUES ('VAC010', 'Parainfluenza Vaccine', '550000', '100');

INSERT INTO perawatan (kode_perawatan, nama_perawatan, biaya_perawatan) VALUES ('TRM001', 'Cek Kesehatan Umum', '200000');
INSERT INTO perawatan (kode_perawatan, nama_perawatan, biaya_perawatan) VALUES ('TRM002', 'Sterilisasi Hewan', '500000');
INSERT INTO perawatan (kode_perawatan, nama_perawatan, biaya_perawatan) VALUES ('TRM003', 'Perawatan Gigi & Mulut', '250000');
INSERT INTO perawatan (kode_perawatan, nama_perawatan, biaya_perawatan) VALUES ('TRM004', 'Pengobatan Kutu & Tungau', '180000');
INSERT INTO perawatan (kode_perawatan, nama_perawatan, biaya_perawatan) VALUES ('TRM005', 'Perawatan Luka & Jahitan', '350000');


INSERT INTO perawatan_obat (kode_perawatan, kode_obat, kuantitas_obat) VALUES ('TRM001', 'MED001', '1');
INSERT INTO perawatan_obat (kode_perawatan, kode_obat, kuantitas_obat) VALUES ('TRM002', 'MED002', '2');
INSERT INTO perawatan_obat (kode_perawatan, kode_obat, kuantitas_obat) VALUES ('TRM003', 'MED003', '1');
INSERT INTO perawatan_obat (kode_perawatan, kode_obat, kuantitas_obat) VALUES ('TRM004', 'MED004', '2');
INSERT INTO perawatan_obat (kode_perawatan, kode_obat, kuantitas_obat) VALUES ('TRM005', 'MED005', '1');
INSERT INTO perawatan_obat (kode_perawatan, kode_obat, kuantitas_obat) VALUES ('TRM001', 'MED006', '2');
INSERT INTO perawatan_obat (kode_perawatan, kode_obat, kuantitas_obat) VALUES ('TRM002', 'MED007', '1');
INSERT INTO perawatan_obat (kode_perawatan, kode_obat, kuantitas_obat) VALUES ('TRM003', 'MED008', '2');
INSERT INTO perawatan_obat (kode_perawatan, kode_obat, kuantitas_obat) VALUES ('TRM004', 'MED009', '1');
INSERT INTO perawatan_obat (kode_perawatan, kode_obat, kuantitas_obat) VALUES ('TRM005', 'MED010', '2');

INSERT INTO sertifikat_kompetensi (no_sertifikat_kompetensi, no_tenaga_medis, nama_sertifikat) VALUES ('SP-PH-001', 'e0bca1e9-7a9b-4ef5-90a8-ab27392995d0', 'Sertifikat Keperawatan Dasar pada Hewan');
INSERT INTO sertifikat_kompetensi (no_sertifikat_kompetensi, no_tenaga_medis, nama_sertifikat) VALUES ('SP-PH-002', '06d274ce-f64f-4690-94ae-ade80f9ae6f0', 'Sertifikat Asuhan Keperawatan Pasien Hewan');
INSERT INTO sertifikat_kompetensi (no_sertifikat_kompetensi, no_tenaga_medis, nama_sertifikat) VALUES ('SP-PH-003', '1e865074-4237-4f5b-98f8-20fdf24eaa62', 'Sertifikat Manajemen Obat dan Terapi Veteriner');
INSERT INTO sertifikat_kompetensi (no_sertifikat_kompetensi, no_tenaga_medis, nama_sertifikat) VALUES ('SP-PH-004', 'b643f56b-90c7-45ff-9cbe-3e4873ff0b70', 'Sertifikat Keperawatan Anestesi pada Hewan');
INSERT INTO sertifikat_kompetensi (no_sertifikat_kompetensi, no_tenaga_medis, nama_sertifikat) VALUES ('SP-PH-005', '5abc7d6a-e48f-46a3-9ee6-df5096da1049', 'Sertifikat Nutrisi dan Dietetik Hewan');
INSERT INTO sertifikat_kompetensi (no_sertifikat_kompetensi, no_tenaga_medis, nama_sertifikat) VALUES ('SP-PH-006', '7840c75f-a611-4036-9bdf-e095c6cbeb64', 'Sertifikat Praktik Dokter Hewan Umum');
INSERT INTO sertifikat_kompetensi (no_sertifikat_kompetensi, no_tenaga_medis, nama_sertifikat) VALUES ('SP-PH-007', '878b4bba-013f-4b5b-9f41-30c88fa94db1', 'Sertifikat Keterampilan Bedah Veteriner');
INSERT INTO sertifikat_kompetensi (no_sertifikat_kompetensi, no_tenaga_medis, nama_sertifikat) VALUES ('SP-PH-008', 'd638c464-69ad-4fba-a82c-4892f15891ee', 'Sertifikat Pelayanan Gawat Darurat Veteriner');
INSERT INTO sertifikat_kompetensi (no_sertifikat_kompetensi, no_tenaga_medis, nama_sertifikat) VALUES ('SP-PH-009', 'a84f8227-093e-4749-a62c-4508c82c928a', 'Sertifikat Diagnostik Pencitraan Veteriner');
INSERT INTO sertifikat_kompetensi (no_sertifikat_kompetensi, no_tenaga_medis, nama_sertifikat) VALUES ('SP-PH-010', 'dd07aa17-898b-4d58-b08f-621d8b801ed2', 'Sertifikat Manajemen Klinik dan Kesehatan Hewan');

INSERT INTO front_desk (no_front_desk) VALUES ('8451fbbf-e73b-4f4b-90cb-2066e1f34685');
INSERT INTO front_desk (no_front_desk) VALUES ('c872f0ce-ffd3-4908-aa27-49974751ebc2');
INSERT INTO front_desk (no_front_desk) VALUES ('3c8c19ef-d569-4815-ba00-833cdc6111fd');
INSERT INTO front_desk (no_front_desk) VALUES ('b4aa4388-05bf-48e8-91c8-0e0a158cd56b');
INSERT INTO front_desk (no_front_desk) VALUES ('37c4e97c-3aa7-43b7-a583-03f47b92eb4e');



INSERT INTO kunjungan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu, berat_badan, catatan) VALUES ('bd5269d7-aa31-4951-81e3-97eda257b98c', 'Bella', '3a94232d-8824-46d8-a4bf-2fbf6b4c4cd8', '8451fbbf-e73b-4f4b-90cb-2066e1f34685', 'e0bca1e9-7a9b-4ef5-90a8-ab27392995d0', '7840c75f-a611-4036-9bdf-e095c6cbeb64', 'VAC001', 'Janji Temu', '2025-04-28 08:15:00', '2025-04-28 08:55:00', '24', '12.3', 'Test Catatan 1');
INSERT INTO kunjungan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu, berat_badan, catatan) VALUES ('e8aa54ce-24f6-4c2d-8f2b-6b18e9718554', 'Milo', 'cc9bf851-835d-4f8e-8170-3bb8efefac68', '8451fbbf-e73b-4f4b-90cb-2066e1f34685', 'e0bca1e9-7a9b-4ef5-90a8-ab27392995d0', '7840c75f-a611-4036-9bdf-e095c6cbeb64', 'VAC002', 'Walk-In', '2025-04-28 09:05:00', '2025-04-28 09:50:00', '28', '1.2', 'Test Catatan 2');
INSERT INTO kunjungan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu, berat_badan, catatan) VALUES ('9157b607-0ddd-4c54-8fd4-4c450749e7ff', 'Luna', '64bf941b-1989-42fe-b88d-4bf9a55c66d3', '8451fbbf-e73b-4f4b-90cb-2066e1f34685', 'e0bca1e9-7a9b-4ef5-90a8-ab27392995d0', '7840c75f-a611-4036-9bdf-e095c6cbeb64', 'VAC003', 'Janji Temu', '2025-04-28 08:45:00', '2025-04-28 09:30:00', '28', '1.4', 'Test Catatan 3');
INSERT INTO kunjungan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu, berat_badan, catatan) VALUES ('3c3927dc-3a13-4156-aacf-8bf1341770b0', 'Rocky', 'c8916d2a-c1f8-40b5-afb4-20aaa70c0493', '8451fbbf-e73b-4f4b-90cb-2066e1f34685', 'e0bca1e9-7a9b-4ef5-90a8-ab27392995d0', '7840c75f-a611-4036-9bdf-e095c6cbeb64', 'VAC004', 'Walk-In', '2025-04-28 10:00:00', '2025-04-28 10:45:00', '28', '5.2', 'Test Catatan 4');
INSERT INTO kunjungan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu, berat_badan, catatan) VALUES ('2764a35b-a520-4541-a693-3b79997bb36a', 'Coco', '29fd603f-c1b0-4d0f-8155-9b64141282d0', 'c872f0ce-ffd3-4908-aa27-49974751ebc2', '06d274ce-f64f-4690-94ae-ade80f9ae6f0', '878b4bba-013f-4b5b-9f41-30c88fa94db1', 'VAC005', 'Darurat', '2025-04-28 11:20:00', '2025-04-28 12:10:00', '30', '2.2', 'Test Catatan 5');
INSERT INTO kunjungan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu, berat_badan, catatan) VALUES ('2dc03986-13fd-44a7-ba1e-69a2bee8f557', 'Simba', 'b7104154-7db2-4f20-aa96-1be414b50966', 'c872f0ce-ffd3-4908-aa27-49974751ebc2', '06d274ce-f64f-4690-94ae-ade80f9ae6f0', '878b4bba-013f-4b5b-9f41-30c88fa94db1', 'VAC006', 'Janji Temu', '2025-04-28 08:30:00', '2025-04-28 09:15:00', '29', '2.5', 'Test Catatan 6');
INSERT INTO kunjungan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu, berat_badan, catatan) VALUES ('9f21d139-b70b-485e-9c85-a7b55e8aa58e', 'Nala', '5cd27a98-fa11-4959-b8ac-dc33fd87fef6', 'c872f0ce-ffd3-4908-aa27-49974751ebc2', '06d274ce-f64f-4690-94ae-ade80f9ae6f0', '878b4bba-013f-4b5b-9f41-30c88fa94db1', 'VAC007', 'Walk-In', '2025-04-28 13:10:00', '2025-04-28 14:00:00', '26', '1.5', 'Test Catatan 7');
INSERT INTO kunjungan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu, berat_badan, catatan) VALUES ('a45aeb50-164e-4f0e-abe2-e88fa6351ab6', 'Charlie', 'cdedd83b-e519-471b-ae8a-6059a0d4b0b9', 'c872f0ce-ffd3-4908-aa27-49974751ebc2', '06d274ce-f64f-4690-94ae-ade80f9ae6f0', '878b4bba-013f-4b5b-9f41-30c88fa94db1', 'VAC008', 'Janji Temu', '2025-04-28 12:00:00', '2025-04-28 12:40:00', '21', '2.5', 'Test Catatan 8');
INSERT INTO kunjungan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu, berat_badan, catatan) VALUES ('2d57965c-a05d-43b3-a57c-1d48d9b649c5', 'Ruby', '626c9bcf-e15e-4930-972c-2025f24b7096', '3c8c19ef-d569-4815-ba00-833cdc6111fd', '1e865074-4237-4f5b-98f8-20fdf24eaa62', 'd638c464-69ad-4fba-a82c-4892f15891ee', 'VAC009', 'Walk-In', '2025-04-28 14:20:00', '2025-04-28 15:05:00', '23', '6', 'Test Catatan 9');
INSERT INTO kunjungan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu, berat_badan, catatan) VALUES ('c3ab6ad4-752c-4207-922c-00183de5c3bd', 'Max', '1547aba3-cd73-4a59-8ac9-0786256c97aa', '3c8c19ef-d569-4815-ba00-833cdc6111fd', '1e865074-4237-4f5b-98f8-20fdf24eaa62', 'd638c464-69ad-4fba-a82c-4892f15891ee', 'VAC010', 'Darurat', '2025-04-28 15:30:00', '2025-04-28 16:20:00', '30', '6.23', 'Test Catatan 10');
INSERT INTO kunjungan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu, berat_badan, catatan) VALUES ('30909312-cebb-4177-952c-ffc079a2a80c', 'Mochi', '4791bf9b-b9ec-4f1a-a128-4c6160356015', '3c8c19ef-d569-4815-ba00-833cdc6111fd', '1e865074-4237-4f5b-98f8-20fdf24eaa62', 'd638c464-69ad-4fba-a82c-4892f15891ee', 'VAC001', 'Janji Temu', '2025-04-28 09:40:00', '2025-04-28 10:20:00', '28', '5.13', 'Test Catatan 11');
INSERT INTO kunjungan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu, berat_badan, catatan) VALUES ('bc9dee84-fa11-4785-81d7-741776b6caa1', 'Oyen', '6c844274-d378-4380-8450-2121c9326477', '3c8c19ef-d569-4815-ba00-833cdc6111fd', '1e865074-4237-4f5b-98f8-20fdf24eaa62', 'd638c464-69ad-4fba-a82c-4892f15891ee', 'VAC002', 'Walk-In', '2025-04-28 10:30:00', '2025-04-28 11:15:00', '28', '5.5', 'Test Catatan 12');
INSERT INTO kunjungan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu, berat_badan, catatan) VALUES ('01ee9b4f-e9db-4e61-b96b-7c0914c0bb22', 'Bintang', '0b1da535-e152-4493-afe9-eecab6ce41c1', 'b4aa4388-05bf-48e8-91c8-0e0a158cd56b', 'b643f56b-90c7-45ff-9cbe-3e4873ff0b70', 'a84f8227-093e-4749-a62c-4508c82c928a', 'VAC003', 'Janji Temu', '2025-04-28 11:45:00', '2025-04-28 12:30:00', '29', '10.2', 'Test Catatan 13');
INSERT INTO kunjungan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu, berat_badan, catatan) VALUES ('15f29be3-c4fb-4fa8-9273-78770c6b7f9f', 'Zara', '1bafd5cb-ae9f-4dd2-a920-4d1ec1d14c8a', 'b4aa4388-05bf-48e8-91c8-0e0a158cd56b', 'b643f56b-90c7-45ff-9cbe-3e4873ff0b70', 'a84f8227-093e-4749-a62c-4508c82c928a', 'VAC004', 'Walk-In', '2025-04-28 13:30:00', '2025-04-28 14:15:00', '27', '10', 'Test Catatan 14');
INSERT INTO kunjungan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu, berat_badan, catatan) VALUES ('5888fcc1-4bf7-4a72-abf9-f0b9c2a19b97', 'Leo', '8790d01e-a149-4abe-92a7-874786c51076', 'b4aa4388-05bf-48e8-91c8-0e0a158cd56b', 'b643f56b-90c7-45ff-9cbe-3e4873ff0b70', 'a84f8227-093e-4749-a62c-4508c82c928a', 'VAC005', 'Darurat', '2025-04-28 14:50:00', '2025-04-28 15:30:00', '21', '6.8', 'Test Catatan 15');
INSERT INTO kunjungan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu, berat_badan, catatan) VALUES ('7bc31a8f-3583-4741-ac10-7bc6de1be1b3', 'Kiki', 'ed775071-29ce-4e57-965e-dd8fd34ca070', 'b4aa4388-05bf-48e8-91c8-0e0a158cd56b', 'b643f56b-90c7-45ff-9cbe-3e4873ff0b70', 'a84f8227-093e-4749-a62c-4508c82c928a', 'VAC006', 'Janji Temu', '2025-04-28 08:10:00', '2025-04-28 08:50:00', '27', '12', 'Test Catatan 16');
INSERT INTO kunjungan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu, berat_badan, catatan) VALUES ('87d152e4-d787-433a-87aa-2b55665ba9e6', 'Lilo', 'af7c31e5-7e1c-477c-bd78-5dfa621fd996', '37c4e97c-3aa7-43b7-a583-03f47b92eb4e', '5abc7d6a-e48f-46a3-9ee6-df5096da1049', 'dd07aa17-898b-4d58-b08f-621d8b801ed2', 'VAC007', 'Walk-In', '2025-04-28 09:25:00', '2025-04-28 10:00:00', '21', '17', 'Test Catatan 17');
INSERT INTO kunjungan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu, berat_badan, catatan) VALUES ('cd86a143-b8c2-4567-a9d4-61a7b700870c', 'Teddy', '24f5edf2-a0f9-4db1-af9a-610773a4037e', '37c4e97c-3aa7-43b7-a583-03f47b92eb4e', '5abc7d6a-e48f-46a3-9ee6-df5096da1049', 'dd07aa17-898b-4d58-b08f-621d8b801ed2', 'VAC008', 'Janji Temu', '2025-04-28 10:50:00', '2025-04-28 11:40:00', '21', '5.6', 'Test Catatan 18');
INSERT INTO kunjungan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu, berat_badan, catatan) VALUES ('f843fc76-9440-4e76-a8b0-db14be24604c', 'Oreo', '709365fb-9597-430e-b235-958fe82e3d13', '37c4e97c-3aa7-43b7-a583-03f47b92eb4e', '5abc7d6a-e48f-46a3-9ee6-df5096da1049', 'dd07aa17-898b-4d58-b08f-621d8b801ed2', 'VAC009', 'Walk-In', '2025-04-28 13:00:00', '2025-04-28 13:50:00', '26', '2.3', 'Test Catatan 19');
INSERT INTO kunjungan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu, berat_badan, catatan) VALUES ('35673fd0-f071-4065-badf-920bcdccf958', 'Sushi', '7ea7f7d4-ec67-40f0-8e91-de1d8bcdc541', '37c4e97c-3aa7-43b7-a583-03f47b92eb4e', '5abc7d6a-e48f-46a3-9ee6-df5096da1049', 'dd07aa17-898b-4d58-b08f-621d8b801ed2', 'VAC010', 'Darurat', '2025-04-28 15:10:00', '2025-04-28 16:00:00', '28', '1.2', 'Test Catatan 20');


INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('bd5269d7-aa31-4951-81e3-97eda257b98c', 'Bella', '3a94232d-8824-46d8-a4bf-2fbf6b4c4cd8', '8451fbbf-e73b-4f4b-90cb-2066e1f34685', 'e0bca1e9-7a9b-4ef5-90a8-ab27392995d0', '7840c75f-a611-4036-9bdf-e095c6cbeb64', 'TRM001');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('bd5269d7-aa31-4951-81e3-97eda257b98c', 'Bella', '3a94232d-8824-46d8-a4bf-2fbf6b4c4cd8', '8451fbbf-e73b-4f4b-90cb-2066e1f34685', 'e0bca1e9-7a9b-4ef5-90a8-ab27392995d0', '7840c75f-a611-4036-9bdf-e095c6cbeb64', 'TRM002');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('e8aa54ce-24f6-4c2d-8f2b-6b18e9718554', 'Milo', 'cc9bf851-835d-4f8e-8170-3bb8efefac68', '8451fbbf-e73b-4f4b-90cb-2066e1f34685', 'e0bca1e9-7a9b-4ef5-90a8-ab27392995d0', '7840c75f-a611-4036-9bdf-e095c6cbeb64', 'TRM003');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('e8aa54ce-24f6-4c2d-8f2b-6b18e9718554', 'Milo', 'cc9bf851-835d-4f8e-8170-3bb8efefac68', '8451fbbf-e73b-4f4b-90cb-2066e1f34685', 'e0bca1e9-7a9b-4ef5-90a8-ab27392995d0', '7840c75f-a611-4036-9bdf-e095c6cbeb64', 'TRM004');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('9157b607-0ddd-4c54-8fd4-4c450749e7ff', 'Luna', '64bf941b-1989-42fe-b88d-4bf9a55c66d3', '8451fbbf-e73b-4f4b-90cb-2066e1f34685', 'e0bca1e9-7a9b-4ef5-90a8-ab27392995d0', '7840c75f-a611-4036-9bdf-e095c6cbeb64', 'TRM005');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('9157b607-0ddd-4c54-8fd4-4c450749e7ff', 'Luna', '64bf941b-1989-42fe-b88d-4bf9a55c66d3', '8451fbbf-e73b-4f4b-90cb-2066e1f34685', 'e0bca1e9-7a9b-4ef5-90a8-ab27392995d0', '7840c75f-a611-4036-9bdf-e095c6cbeb64', 'TRM001');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('3c3927dc-3a13-4156-aacf-8bf1341770b0', 'Rocky', 'c8916d2a-c1f8-40b5-afb4-20aaa70c0493', '8451fbbf-e73b-4f4b-90cb-2066e1f34685', 'e0bca1e9-7a9b-4ef5-90a8-ab27392995d0', '7840c75f-a611-4036-9bdf-e095c6cbeb64', 'TRM002');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('3c3927dc-3a13-4156-aacf-8bf1341770b0', 'Rocky', 'c8916d2a-c1f8-40b5-afb4-20aaa70c0493', '8451fbbf-e73b-4f4b-90cb-2066e1f34685', 'e0bca1e9-7a9b-4ef5-90a8-ab27392995d0', '7840c75f-a611-4036-9bdf-e095c6cbeb64', 'TRM003');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('2764a35b-a520-4541-a693-3b79997bb36a', 'Coco', '29fd603f-c1b0-4d0f-8155-9b64141282d0', 'c872f0ce-ffd3-4908-aa27-49974751ebc2', '06d274ce-f64f-4690-94ae-ade80f9ae6f0', '878b4bba-013f-4b5b-9f41-30c88fa94db1', 'TRM004');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('2764a35b-a520-4541-a693-3b79997bb36a', 'Coco', '29fd603f-c1b0-4d0f-8155-9b64141282d0', 'c872f0ce-ffd3-4908-aa27-49974751ebc2', '06d274ce-f64f-4690-94ae-ade80f9ae6f0', '878b4bba-013f-4b5b-9f41-30c88fa94db1', 'TRM005');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('2dc03986-13fd-44a7-ba1e-69a2bee8f557', 'Simba', 'b7104154-7db2-4f20-aa96-1be414b50966', 'c872f0ce-ffd3-4908-aa27-49974751ebc2', '06d274ce-f64f-4690-94ae-ade80f9ae6f0', '878b4bba-013f-4b5b-9f41-30c88fa94db1', 'TRM001');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('2dc03986-13fd-44a7-ba1e-69a2bee8f557', 'Simba', 'b7104154-7db2-4f20-aa96-1be414b50966', 'c872f0ce-ffd3-4908-aa27-49974751ebc2', '06d274ce-f64f-4690-94ae-ade80f9ae6f0', '878b4bba-013f-4b5b-9f41-30c88fa94db1', 'TRM002');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('9f21d139-b70b-485e-9c85-a7b55e8aa58e', 'Nala', '5cd27a98-fa11-4959-b8ac-dc33fd87fef6', 'c872f0ce-ffd3-4908-aa27-49974751ebc2', '06d274ce-f64f-4690-94ae-ade80f9ae6f0', '878b4bba-013f-4b5b-9f41-30c88fa94db1', 'TRM003');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('9f21d139-b70b-485e-9c85-a7b55e8aa58e', 'Nala', '5cd27a98-fa11-4959-b8ac-dc33fd87fef6', 'c872f0ce-ffd3-4908-aa27-49974751ebc2', '06d274ce-f64f-4690-94ae-ade80f9ae6f0', '878b4bba-013f-4b5b-9f41-30c88fa94db1', 'TRM004');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('a45aeb50-164e-4f0e-abe2-e88fa6351ab6', 'Charlie', 'cdedd83b-e519-471b-ae8a-6059a0d4b0b9', 'c872f0ce-ffd3-4908-aa27-49974751ebc2', '06d274ce-f64f-4690-94ae-ade80f9ae6f0', '878b4bba-013f-4b5b-9f41-30c88fa94db1', 'TRM005');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('a45aeb50-164e-4f0e-abe2-e88fa6351ab6', 'Charlie', 'cdedd83b-e519-471b-ae8a-6059a0d4b0b9', 'c872f0ce-ffd3-4908-aa27-49974751ebc2', '06d274ce-f64f-4690-94ae-ade80f9ae6f0', '878b4bba-013f-4b5b-9f41-30c88fa94db1', 'TRM001');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('2d57965c-a05d-43b3-a57c-1d48d9b649c5', 'Ruby', '626c9bcf-e15e-4930-972c-2025f24b7096', '3c8c19ef-d569-4815-ba00-833cdc6111fd', '1e865074-4237-4f5b-98f8-20fdf24eaa62', 'd638c464-69ad-4fba-a82c-4892f15891ee', 'TRM002');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('c3ab6ad4-752c-4207-922c-00183de5c3bd', 'Max', '1547aba3-cd73-4a59-8ac9-0786256c97aa', '3c8c19ef-d569-4815-ba00-833cdc6111fd', '1e865074-4237-4f5b-98f8-20fdf24eaa62', 'd638c464-69ad-4fba-a82c-4892f15891ee', 'TRM003');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('c3ab6ad4-752c-4207-922c-00183de5c3bd', 'Max', '1547aba3-cd73-4a59-8ac9-0786256c97aa', '3c8c19ef-d569-4815-ba00-833cdc6111fd', '1e865074-4237-4f5b-98f8-20fdf24eaa62', 'd638c464-69ad-4fba-a82c-4892f15891ee', 'TRM004');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('30909312-cebb-4177-952c-ffc079a2a80c', 'Mochi', '4791bf9b-b9ec-4f1a-a128-4c6160356015', '3c8c19ef-d569-4815-ba00-833cdc6111fd', '1e865074-4237-4f5b-98f8-20fdf24eaa62', 'd638c464-69ad-4fba-a82c-4892f15891ee', 'TRM005');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('30909312-cebb-4177-952c-ffc079a2a80c', 'Mochi', '4791bf9b-b9ec-4f1a-a128-4c6160356015', '3c8c19ef-d569-4815-ba00-833cdc6111fd', '1e865074-4237-4f5b-98f8-20fdf24eaa62', 'd638c464-69ad-4fba-a82c-4892f15891ee', 'TRM001');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('bc9dee84-fa11-4785-81d7-741776b6caa1', 'Oyen', '6c844274-d378-4380-8450-2121c9326477', '3c8c19ef-d569-4815-ba00-833cdc6111fd', '1e865074-4237-4f5b-98f8-20fdf24eaa62', 'd638c464-69ad-4fba-a82c-4892f15891ee', 'TRM002');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('01ee9b4f-e9db-4e61-b96b-7c0914c0bb22', 'Bintang', '0b1da535-e152-4493-afe9-eecab6ce41c1', 'b4aa4388-05bf-48e8-91c8-0e0a158cd56b', 'b643f56b-90c7-45ff-9cbe-3e4873ff0b70', 'a84f8227-093e-4749-a62c-4508c82c928a', 'TRM003');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('15f29be3-c4fb-4fa8-9273-78770c6b7f9f', 'Zara', '1bafd5cb-ae9f-4dd2-a920-4d1ec1d14c8a', 'b4aa4388-05bf-48e8-91c8-0e0a158cd56b', 'b643f56b-90c7-45ff-9cbe-3e4873ff0b70', 'a84f8227-093e-4749-a62c-4508c82c928a', 'TRM004');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('5888fcc1-4bf7-4a72-abf9-f0b9c2a19b97', 'Leo', '8790d01e-a149-4abe-92a7-874786c51076', 'b4aa4388-05bf-48e8-91c8-0e0a158cd56b', 'b643f56b-90c7-45ff-9cbe-3e4873ff0b70', 'a84f8227-093e-4749-a62c-4508c82c928a', 'TRM005');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('7bc31a8f-3583-4741-ac10-7bc6de1be1b3', 'Kiki', 'ed775071-29ce-4e57-965e-dd8fd34ca070', 'b4aa4388-05bf-48e8-91c8-0e0a158cd56b', 'b643f56b-90c7-45ff-9cbe-3e4873ff0b70', 'a84f8227-093e-4749-a62c-4508c82c928a', 'TRM001');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('87d152e4-d787-433a-87aa-2b55665ba9e6', 'Lilo', 'af7c31e5-7e1c-477c-bd78-5dfa621fd996', '37c4e97c-3aa7-43b7-a583-03f47b92eb4e', '5abc7d6a-e48f-46a3-9ee6-df5096da1049', 'dd07aa17-898b-4d58-b08f-621d8b801ed2', 'TRM002');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('cd86a143-b8c2-4567-a9d4-61a7b700870c', 'Teddy', '24f5edf2-a0f9-4db1-af9a-610773a4037e', '37c4e97c-3aa7-43b7-a583-03f47b92eb4e', '5abc7d6a-e48f-46a3-9ee6-df5096da1049', 'dd07aa17-898b-4d58-b08f-621d8b801ed2', 'TRM003');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('f843fc76-9440-4e76-a8b0-db14be24604c', 'Oreo', '709365fb-9597-430e-b235-958fe82e3d13', '37c4e97c-3aa7-43b7-a583-03f47b92eb4e', '5abc7d6a-e48f-46a3-9ee6-df5096da1049', 'dd07aa17-898b-4d58-b08f-621d8b801ed2', 'TRM004');
INSERT INTO kunjungan_keperawatan (id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan) VALUES ('35673fd0-f071-4065-badf-920bcdccf958', 'Sushi', '7ea7f7d4-ec67-40f0-8e91-de1d8bcdc541', '37c4e97c-3aa7-43b7-a583-03f47b92eb4e', '5abc7d6a-e48f-46a3-9ee6-df5096da1049', 'dd07aa17-898b-4d58-b08f-621d8b801ed2', 'TRM005');

INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam) VALUES ('7840c75f-a611-4036-9bdf-e095c6cbeb64', 'Senin', '08.00 – 12.00');
INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam) VALUES ('7840c75f-a611-4036-9bdf-e095c6cbeb64', 'Rabu', '14.00 – 18.00');
INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam) VALUES ('7840c75f-a611-4036-9bdf-e095c6cbeb64', 'Jumat', '09.00 – 13.00');
INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam) VALUES ('7840c75f-a611-4036-9bdf-e095c6cbeb64', 'Sabtu', '10.00 – 14.00');
INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam) VALUES ('878b4bba-013f-4b5b-9f41-30c88fa94db1', 'Selasa', '08.00 – 12.00');
INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam) VALUES ('878b4bba-013f-4b5b-9f41-30c88fa94db1', 'Kamis', '14.00 – 18.00');
INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam) VALUES ('878b4bba-013f-4b5b-9f41-30c88fa94db1', 'Sabtu', '09.00 – 13.00');
INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam) VALUES ('878b4bba-013f-4b5b-9f41-30c88fa94db1', 'Minggu', '10.00 – 14.00');
INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam) VALUES ('d638c464-69ad-4fba-a82c-4892f15891ee', 'Senin', '13.00 – 17.00');
INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam) VALUES ('d638c464-69ad-4fba-a82c-4892f15891ee', 'Selasa', '09.00 – 13.00');
INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam) VALUES ('d638c464-69ad-4fba-a82c-4892f15891ee', 'Kamis', '08.00 – 12.00');
INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam) VALUES ('d638c464-69ad-4fba-a82c-4892f15891ee', 'Jumat', '14.00 – 18.00');
INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam) VALUES ('a84f8227-093e-4749-a62c-4508c82c928a', 'Rabu', '08.00 – 12.00');
INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam) VALUES ('a84f8227-093e-4749-a62c-4508c82c928a', 'Kamis', '13.00 – 17.00');
INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam) VALUES ('a84f8227-093e-4749-a62c-4508c82c928a', 'Jumat', '10.00 – 14.00');
INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam) VALUES ('a84f8227-093e-4749-a62c-4508c82c928a', 'Sabtu', '14.00 – 18.00');
INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam) VALUES ('dd07aa17-898b-4d58-b08f-621d8b801ed2', 'Senin', '09.00 – 13.00');
INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam) VALUES ('dd07aa17-898b-4d58-b08f-621d8b801ed2', 'Rabu', '10.00 – 14.00');
INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam) VALUES ('dd07aa17-898b-4d58-b08f-621d8b801ed2', 'Jumat', '08.00 – 12.00');
INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam) VALUES ('dd07aa17-898b-4d58-b08f-621d8b801ed2', 'Minggu', '13.00 – 17.00');