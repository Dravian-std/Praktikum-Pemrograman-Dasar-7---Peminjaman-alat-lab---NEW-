import os
import csv
from modul.Mahasiswa import Mahasiswa
from modul.Peralatan import Peralatan
from modul.Transaksi import TransaksiPeminjaman
from datetime import datetime, date  # Tantangan D: untuk jam dan tanggal log

class SistemLaboratorium:
    def __init__(self):
        self.daftar_mahasiswa = {}
        self.daftar_peralatan = {}
        self.daftar_transaksi = []
        self.counter_trx = 1
        self.log_aktivitas = []  # Tantangan D: list khusus penyimpan log

        # --- PENYIMPANAN TETAP (file persistence): file disimpan di folder utama proyek ---
        folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.file_mahasiswa = os.path.join(folder, "mahasiswa.csv")
        self.file_peralatan = os.path.join(folder, "peralatan.csv")
        self.file_transaksi = os.path.join(folder, "transaksi.csv")
        self.file_log = os.path.join(folder, "log_aktivitas.txt")
        self.boleh_simpan = True
        self.muat_data()  # data lama dibaca dari file saat program mulai

    # ==========================================
    # PENYIMPANAN TETAP / FILE PERSISTENCE (Danang)
    # ==========================================
    def simpan_data(self):
        if not self.boleh_simpan:
            print("Peringatan: data tidak disimpan karena file gagal dibaca saat program dimulai.")
            return

        with open(self.file_mahasiswa, mode="w", newline="", encoding="utf-8") as f:
            penulis = csv.writer(f)
            penulis.writerow(["nim", "nama", "no_hp", "jumlah_transaksi_aktif"])
            for mhs in self.daftar_mahasiswa.values():
                penulis.writerow([mhs.nim, mhs.nama, mhs.no_hp, mhs.jumlah_transaksi_aktif])

        with open(self.file_peralatan, mode="w", newline="", encoding="utf-8") as f:
            penulis = csv.writer(f)
            penulis.writerow(["kode_alat", "nama_alat", "kategori", "kondisi", "status_tersedia"])
            for alat in self.daftar_peralatan.values():
                penulis.writerow([alat.kode_alat, alat.nama_alat, alat.kategori, alat.kondisi, alat.status_tersedia])

        with open(self.file_transaksi, mode="w", newline="", encoding="utf-8") as f:
            penulis = csv.writer(f)
            penulis.writerow(["id_transaksi", "nim_peminjam", "kode_alat_dipinjam",
                              "kode_alat_dikembalikan", "tgl_peminjaman", "batas_waktu", "status_transaksi"])
            for trx in self.daftar_transaksi:
                dipinjam = ";".join([alat.kode_alat for alat in trx.daftar_alat_dipinjam])
                dikembalikan = ";".join([alat.kode_alat for alat in trx.daftar_alat_dikembalikan])
                penulis.writerow([trx.id_transaksi, trx.mahasiswa.nim, dipinjam, dikembalikan,
                                  trx.tgl_peminjaman, trx.batas_waktu, trx.status_transaksi])

        with open(self.file_log, mode="w", encoding="utf-8") as f:
            for log in self.log_aktivitas:
                f.write(log + "\n")

    def muat_data(self):
        try:
            if os.path.exists(self.file_mahasiswa):
                with open(self.file_mahasiswa, mode="r", newline="", encoding="utf-8") as f:
                    for baris in csv.DictReader(f):
                        mhs = Mahasiswa(baris["nim"], baris["nama"], baris["no_hp"])
                        mhs.jumlah_transaksi_aktif = int(baris["jumlah_transaksi_aktif"])
                        self.daftar_mahasiswa[mhs.nim] = mhs

            if os.path.exists(self.file_peralatan):
                with open(self.file_peralatan, mode="r", newline="", encoding="utf-8") as f:
                    for baris in csv.DictReader(f):
                        alat = Peralatan(baris["kode_alat"], baris["nama_alat"], baris["kategori"])
                        alat.kondisi = baris["kondisi"]
                        alat.status_tersedia = (baris["status_tersedia"] == "True")
                        self.daftar_peralatan[alat.kode_alat] = alat

            if os.path.exists(self.file_transaksi):
                with open(self.file_transaksi, mode="r", newline="", encoding="utf-8") as f:
                    nomor_terbesar = 0
                    for baris in csv.DictReader(f):
                        # Mahasiswa/alat yang sudah dihapus diganti objek kosong supaya riwayat tidak hilang
                        mhs = self.daftar_mahasiswa.get(baris["nim_peminjam"])
                        if mhs is None:
                            mhs = Mahasiswa(baris["nim_peminjam"], "(data dihapus)", "-")

                        alat_transaksi = {}
                        alat_dipinjam = []
                        for kode in baris["kode_alat_dipinjam"].split(";"):
                            if kode == "":
                                continue
                            alat = self.daftar_peralatan.get(kode)
                            if alat is None:
                                alat = Peralatan(kode, "(data dihapus)", "-")
                            alat_transaksi[kode] = alat
                            alat_dipinjam.append(alat)
                        alat_dikembalikan = [alat_transaksi[k] for k in baris["kode_alat_dikembalikan"].split(";")
                                             if k in alat_transaksi]

                        trx = TransaksiPeminjaman(baris["id_transaksi"], mhs, alat_dipinjam)
                        trx.daftar_alat_dikembalikan = alat_dikembalikan
                        trx.tgl_peminjaman = date.fromisoformat(baris["tgl_peminjaman"])
                        trx.batas_waktu = date.fromisoformat(baris["batas_waktu"])
                        trx.status_transaksi = baris["status_transaksi"]
                        self.daftar_transaksi.append(trx)

                        nomor_terbesar = max(nomor_terbesar, int(baris["id_transaksi"].replace("TRX", "")))
                    self.counter_trx = nomor_terbesar + 1

            if os.path.exists(self.file_log):
                with open(self.file_log, mode="r", encoding="utf-8") as f:
                    self.log_aktivitas = [baris.strip() for baris in f if baris.strip()]
        except Exception as e:
            # Kalau file gagal dibaca, jangan menimpa file lama dengan data setengah jadi
            self.boleh_simpan = False
            print(f"Gagal membaca file data: {e}")

    # ==========================================
    # TANTANGAN D: LOG AKTIVITAS (Danang)
    # ==========================================
    def catat_log(self, pesan):
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_aktivitas.append(f"[{waktu}] {pesan}")
        self.simpan_data()  # setiap ada perubahan data langsung disimpan ke file

    def tampilkan_log(self):
        print("\n--- Riwayat Log Aktivitas ---")
        if not self.log_aktivitas:
            print("Belum ada log aktivitas.")
        for log in self.log_aktivitas:
            print(log)

    # ==========================================
    # WILAYAH AKSYA (KELOLA MAHASISWA)
    # ==========================================
    def tambah_mahasiswa(self, nim, nama, no_hp):
        if nim not in self.daftar_mahasiswa:
            self.daftar_mahasiswa[nim] = Mahasiswa(nim, nama, no_hp)
            print("Mahasiswa berhasil ditambahkan.")
            self.catat_log(f"Mahasiswa {nim} ({nama}) ditambahkan")
            self.simpan_data()
        else:
            print("Gagal! NIM sudah terdaftar.")

    def edit_mahasiswa(self, nim, nama_baru, no_hp_baru):
        if nim in self.daftar_mahasiswa:
            self.daftar_mahasiswa[nim].nama = nama_baru
            self.daftar_mahasiswa[nim].no_hp = no_hp_baru
            print("Data mahasiswa berhasil diperbarui.")
            self.catat_log(f"Data mahasiswa {nim} diperbarui")
            self.simpan_data()
        else:
            print("Mahasiswa tidak ditemukan.")

    def hapus_mahasiswa(self, nim):
        if nim in self.daftar_mahasiswa:
            if self.daftar_mahasiswa[nim].jumlah_transaksi_aktif > 0:
                print("Gagal! Mahasiswa memiliki transaksi aktif.")
            else:
                del self.daftar_mahasiswa[nim]
                print("Mahasiswa berhasil dihapus.")
                self.catat_log(f"Mahasiswa {nim} dihapus")
                self.simpan_data()
        else:
            print("Mahasiswa tidak ditemukan.")

    def cari_mahasiswa(self, nim):
        if nim in self.daftar_mahasiswa:
            mhs = self.daftar_mahasiswa[nim]
            print(f"NIM: {mhs.nim} | Nama: {mhs.nama} | No HP: {mhs.no_hp} | Transaksi Aktif: {mhs.jumlah_transaksi_aktif}")
        else:
            print("Mahasiswa tidak ditemukan.")

    # ==========================================
    # WILAYAH KEISHA (KELOLA PERALATAN)
    # ==========================================
    def tambah_alat(self, kode, nama, kategori):
        if kode not in self.daftar_peralatan:
            self.daftar_peralatan[kode] = Peralatan(kode, nama, kategori)
            print("Alat berhasil ditambahkan.")
            self.catat_log(f"Alat {kode} ({nama}) ditambahkan")
        else:
            print("Gagal! Kode alat sudah terdaftar.")

    def edit_alat(self, kode, nama_baru, kategori_baru):
        if kode in self.daftar_peralatan:
            self.daftar_peralatan[kode].nama_alat = nama_baru
            self.daftar_peralatan[kode].kategori = kategori_baru
            print("Data alat berhasil diperbarui.")
            self.catat_log(f"Data alat {kode} diperbarui")
        else:
            print("Alat tidak ditemukan.")

    def hapus_alat(self, kode):
        if kode in self.daftar_peralatan:
            alat = self.daftar_peralatan[kode]
            if not alat.status_tersedia and alat.kondisi == "baik":
                print("Gagal! Alat sedang dalam status dipinjam.")
            else:
                del self.daftar_peralatan[kode]
                print("Alat berhasil dihapus.")
                self.catat_log(f"Alat {kode} dihapus")
        else:
            print("Alat tidak ditemukan.")

        # Tantangan A: pencarian fleksibel (kode, sebagian nama, atau kategori)
    def cari_alat(self, keyword):
        keyword_lower = keyword.lower()
        hasil_pencarian = []

        for alat in self.daftar_peralatan.values():
            # Cek kode, sebagian nama, atau kategori
            if (keyword_lower in alat.kode_alat.lower() or
                keyword_lower in alat.nama_alat.lower() or
                keyword_lower in alat.kategori.lower()):
                hasil_pencarian.append(alat)

        if hasil_pencarian:
            print(f"\n--- Hasil Pencarian '{keyword}' ---")
            for alat in hasil_pencarian:
                print(f"{alat.kode_alat} | {alat.nama_alat} | {alat.kategori} | Kondisi: {alat.kondisi}")
        else:
            print(f"Tidak ditemukan alat dengan kata kunci '{keyword}'.")

    def tampilkan_alat_tersedia(self):
        print("--- Alat Tersedia ---")
        for alat in self.daftar_peralatan.values():
            if alat.status_tersedia:
                print(f"{alat.kode_alat} | {alat.nama_alat} | {alat.kategori}")

    def tampilkan_alat_rusak(self):
        print("--- Daftar Alat Rusak ---")
        for alat in self.daftar_peralatan.values():
            if alat.kondisi in ["rusak ringan", "rusak berat"]:
                print(f"{alat.kode_alat} | {alat.nama_alat} | Kondisi: {alat.kondisi}")
    

    # ==========================================
    # WILAYAH AMEL (KELOLA TRANSAKSI)
    # ==========================================

    def buat_transaksi(self, nim, daftar_kode):
        # Validasi mahasiswa
        if nim not in self.daftar_mahasiswa:
            print("Gagal! Mahasiswa tidak ditemukan.")
            return

        mhs = self.daftar_mahasiswa[nim]

        # Aturan 2: maksimal 2 transaksi aktif per mahasiswa
        if not mhs.bisa_meminjam():
            print("Gagal! Mahasiswa sudah memiliki 2 transaksi aktif.")
            return

        # Buang kode kosong/duplikat, urutan input tetap dijaga
        kode_unik = []
        for kode in daftar_kode:
            if kode not in kode_unik:
                kode_unik.append(kode)

        if not kode_unik:
            print("Gagal! Minimal pilih 1 alat.")
            return

        # Aturan 1: semua alat harus ada dan tersedia, kalau tidak transaksi dibatalkan
        alat_dipinjam = []
        for kode in kode_unik:
            if kode not in self.daftar_peralatan:
                print(f"Gagal! Alat {kode} tidak ditemukan. Transaksi dibatalkan.")
                return
            alat = self.daftar_peralatan[kode]
            if not alat.status_tersedia:
                print(f"Gagal! Alat {kode} ({alat.nama_alat}) tidak tersedia. Transaksi dibatalkan.")
                return
            alat_dipinjam.append(alat)

        # Aturan 3: satu transaksi bisa berisi banyak alat (list)
        id_trx = f"TRX{self.counter_trx:03d}"
        self.counter_trx += 1
        transaksi = TransaksiPeminjaman(id_trx, mhs, alat_dipinjam)
        self.daftar_transaksi.append(transaksi)

        for alat in alat_dipinjam:
            alat.set_ketersediaan(False)
        mhs.tambah_transaksi()

        print(f"Transaksi {id_trx} berhasil dibuat untuk {mhs.nama}.")
        print(f"Batas pengembalian: {transaksi.batas_waktu}")
        self.catat_log(f"Transaksi {id_trx} dibuat oleh {nim}, {len(alat_dipinjam)} alat dipinjam")

    def tampilkan_transaksi(self):
        print("--- Daftar Semua Transaksi ---")
        if not self.daftar_transaksi:
            print("Belum ada transaksi.")
            return
        for trx in self.daftar_transaksi:
            self._cetak_transaksi(trx)

    def proses_pengembalian(self, id_transaksi, kode_alat, kondisi_baru):
        trx = self._cari_transaksi(id_transaksi)
        if trx is None:
            print("Transaksi tidak ditemukan.")
            return

        if trx.status_transaksi == "selesai":
            print("Transaksi ini sudah selesai, semua alat sudah dikembalikan.")
            return

        berhasil = trx.proses_pengembalian_alat(kode_alat, kondisi_baru)
        if not berhasil:
            print("Gagal! Alat tidak ada di transaksi ini atau sudah dikembalikan.")
            return

        print(f"Alat {kode_alat} berhasil dikembalikan (kondisi: {kondisi_baru}).")
        print(f"Status transaksi: {trx.status_transaksi}")
        self.catat_log(f"Alat {kode_alat} dikembalikan pada {trx.id_transaksi} (kondisi: {kondisi_baru}), status: {trx.status_transaksi}")

        from datetime import date
        if date.today() > trx.batas_waktu:
            print(f"Catatan: pengembalian melewati batas waktu ({trx.batas_waktu}).")

    def riwayat_peminjaman(self, nim):
        print(f"--- Riwayat Peminjaman NIM {nim} ---")
        ditemukan = False
        for trx in self.daftar_transaksi:
            if trx.mahasiswa.nim == nim:
                self._cetak_transaksi(trx)
                ditemukan = True
        if not ditemukan:
            print("Tidak ada riwayat transaksi untuk NIM ini.")

    def tampilkan_alat_dipinjam(self):
        print("--- Alat Sedang Dipinjam ---")
        ada = False
        for trx in self.daftar_transaksi:
            for alat in trx.daftar_alat_dipinjam:
                if alat not in trx.daftar_alat_dikembalikan:
                    print(f"{alat.kode_alat} | {alat.nama_alat} | Dipinjam oleh {trx.mahasiswa.nama} ({trx.id_transaksi})")
                    ada = True
        if not ada:
            print("Tidak ada alat yang sedang dipinjam.")

    # --- Fungsi bantu (internal) ---
    def _cari_transaksi(self, id_transaksi):
        for trx in self.daftar_transaksi:
            if trx.id_transaksi.upper() == id_transaksi.strip().upper():
                return trx
        return None

    def _cetak_transaksi(self, trx):
        print(f"{trx.id_transaksi} | {trx.mahasiswa.nim} - {trx.mahasiswa.nama} | "
              f"Pinjam: {trx.tgl_peminjaman} | Batas: {trx.batas_waktu} | Status: {trx.status_transaksi}")
        for alat in trx.daftar_alat_dipinjam:
            tanda = "sudah dikembalikan" if alat in trx.daftar_alat_dikembalikan else "belum dikembalikan"
            print(f"    - {alat.kode_alat} {alat.nama_alat} ({tanda})")
