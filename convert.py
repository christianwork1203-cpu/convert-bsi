import os
import re
import csv
import pandas as pd
from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

BASE_DIR = Path(__file__).parent

INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "result" / "va" / "bsi"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
# GET ALL CSV FILES
# =========================================================

csv_files = list(INPUT_DIR.glob("*.csv"))

if not csv_files:
    print("Tidak ada file CSV pada folder input")
    input("Tekan ENTER untuk keluar...")
    exit()

# =========================================================
# PROCESS FILES
# =========================================================

for input_file in csv_files:

    print(f"\nProcessing : {input_file.name}")

    # =====================================================
    # AMBIL TANGGAL DARI FILENAME
    # contoh:
    # rekon_451_1200_20260522_2_rev20260523083341.csv
    # =====================================================

    match = re.search(r'_(\d{8})_', input_file.name)

    if not match:
        print(f"Gagal ambil tanggal dari filename: {input_file.name}")
        continue

    tanggal_file = match.group(1)

    # =====================================================
    # OUTPUT FILE NAME
    # =====================================================

    output_filename = f"VABSI_{tanggal_file}.csv"
    output_file = OUTPUT_DIR / output_filename

    # =====================================================
    # CEK FILE SUDAH DIPROSES
    # =====================================================

    if output_file.exists():
        print(f"SKIP - File hasil sudah ada: {output_filename}")
        continue

    try:

        # =================================================
        # READ SOURCE FILE
        # =================================================

        df = pd.read_csv(input_file, sep=';')

        # =================================================
        # SORT DATA
        # =================================================

        df = df.sort_values(by="wkt_transaksi", ascending=False)

        # =================================================
        # PREPARE OUTPUT
        # =================================================

        output_rows = []

        # =================================================
        # HEADER TANGGAL
        # =================================================

        output_rows.append([
            tanggal_file,
            "", "", "", "", "", "", "", "", "", "", ""
        ])

        # =================================================
        # EMPTY ROW
        # =================================================

        output_rows.append([
            "", "", "", "", "", "", "", "", "", "", "", ""
        ])

        # =================================================
        # CSV HEADER
        # =================================================

        header = [
            "no",
            "nomor_invoice",
            "nomor_pembayaran",
            "nama",
            "informasi_tagihan",
            "waktu_transaksi",
            "total_nominal_pembayaran",
            "status_transaksi",
            "ca_reff",
            "kode_unik_transaksi_bank",
            "info_judul_1",
            "info_isi_1"
        ]

        output_rows.append(header)

        # =================================================
        # DETAIL DATA
        # =================================================

        for index, row in enumerate(df.itertuples(index=False), start=1):

            nomor_invoice = str(row.nomor_invoice)

            # =============================================
            # TAMBAH PREFIX 00
            # contoh:
            # 500190968 -> 00500190968
            # =============================================

            nomor_pembayaran = str(row.nomor_pembayaran)

            if not nomor_pembayaran.startswith("00"):
                nomor_pembayaran = "00" + nomor_pembayaran

            output_rows.append([
                index,
                nomor_invoice,
                nomor_pembayaran,
                row.nama,
                f"REF_NUM {nomor_invoice}",
                row.wkt_transaksi,
                row.total_pembayaran,
                "Sukses",
                row.kode_ft,
                row.nomor_jurnal_pembukuan,
                "REF_NUM",
                nomor_invoice
            ])

        # =================================================
        # WRITE OUTPUT CSV
        # =================================================

        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            for row_data in output_rows:
                writer.writerow(row_data)


        print(f"SUCCESS -> {output_filename}")

    except Exception as e:
        print(f"ERROR -> {input_file.name}")
        print(str(e))

# =========================================================
# FINISH
# =========================================================

print("\nSemua proses selesai")
input("Tekan ENTER untuk keluar...")