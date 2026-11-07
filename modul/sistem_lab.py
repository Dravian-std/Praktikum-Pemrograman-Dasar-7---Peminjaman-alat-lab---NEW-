from modul.Mahasiswa import Mahasiswa
from modul.Peralatan import Peralatan
from modul.Transaksi import TransaksiPeminjaman
from datetime import datetime  # Tantangan D: untuk jam dan tanggal log

class SistemLaboratorium:
    def __init__(self):
        self.daftar_mahasiswa = {}
        self.daftar_peralatan = {}
        self.daftar_transaksi = []
        self.counter_trx = 1
        self.log_aktivitas = []  # Tantangan D: list khusus penyimpan log

    # ==========================================
    # TANTANGAN D: LOG AKTIVITAS (Danang)
    # ==========================================
    def catat_log(self, pesan):
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_aktivitas.append(f"[{waktu}] {pesan}")

    def tampilkan_log(self):
        print("\n--- Riwayat Log Aktivitas ---")
        if not self.log_aktivitas:
            print("Belum ada log aktivitas.")
        for log in self.log_aktivitas:
            print(log)

    # TANTANGAN A: Pencarian Fleksibel (Keisha) ---
    # (Ganti fungsi cari_alat yang lama dengan ini)
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

    def cari_alat(self, keyword):
        # Tantangan A: pencarian fleksibel (kode, sebagian nama, atau kategori)
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
