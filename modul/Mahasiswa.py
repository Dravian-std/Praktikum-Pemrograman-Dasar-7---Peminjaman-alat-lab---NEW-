class Mahasiswa:
    def __init__(self, nim, nama, no_hp, jumlah_transaksi_aktif=0):
        self.nim = nim
        self.nama = nama
        self.no_hp = no_hp
        self.jumlah_transaksi_aktif = int(jumlah_transaksi_aktif)

    def tambah_transaksi(self):
        self.jumlah_transaksi_aktif += 1

    def kurangi_transaksi(self):
        if self.jumlah_transaksi_aktif > 0:
            self.jumlah_transaksi_aktif -= 1

    def bisa_meminjam(self):
        return self.jumlah_transaksi_aktif < 2
