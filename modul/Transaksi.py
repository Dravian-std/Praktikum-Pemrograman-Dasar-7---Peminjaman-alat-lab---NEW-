from datetime import date, timedelta, datetime

class TransaksiPeminjaman:
    def __init__(self, id_transaksi, mahasiswa, daftar_alat, daftar_dikembalikan=None, tgl_peminjaman=None, batas_waktu=None, status_transaksi="dipinjam"):
        self.id_transaksi = id_transaksi
        self.mahasiswa = mahasiswa
        self.daftar_alat_dipinjam = daftar_alat  # List dinamis
        self.daftar_alat_dikembalikan = daftar_dikembalikan if daftar_dikembalikan is not None else []
        # Penanganan konversi string tanggal CSV ke objek date
        if isinstance(tgl_peminjaman, str):
            self.tgl_peminjaman = datetime.strptime(tgl_peminjaman, "%Y-%m-%d").date()
        elif isinstance(tgl_peminjaman, date):
            self.tgl_peminjaman = tgl_peminjaman
        else:
            self.tgl_peminjaman = date.today()

        if isinstance(batas_waktu, str):
            self.batas_waktu = datetime.strptime(batas_waktu, "%Y-%m-%d").date()
        elif isinstance(batas_waktu, date):
             self.batas_waktu = batas_waktu
        else:
            self.batas_waktu = self.tgl_peminjaman + timedelta(days=7)  # Maks 7 Hari
        self.status_transaksi = status_transaksi

    def proses_pengembalian_alat(self, kode_alat, kondisi_baru):
        alat_ditemukan = None
        for alat in self.daftar_alat_dipinjam:
            if alat.kode_alat == kode_alat and alat not in self.daftar_alat_dikembalikan:
                alat_ditemukan = alat
                break
        
        if alat_ditemukan:
            alat_ditemukan.update_kondisi(kondisi_baru)
            if alat_ditemukan.kondisi == "baik":
                alat_ditemukan.set_ketersediaan(True)
            
            self.daftar_alat_dikembalikan.append(alat_ditemukan)
            self.update_status()
            return True
        return False

    def update_status(self):
        # Aturan 4: Pengembalian sebagian
        if len(self.daftar_alat_dikembalikan) == len(self.daftar_alat_dipinjam):
            self.status_transaksi = "selesai"
            self.mahasiswa.kurangi_transaksi()
        elif len(self.daftar_alat_dikembalikan) > 0:
            self.status_transaksi = "sebagian dikembalikan"