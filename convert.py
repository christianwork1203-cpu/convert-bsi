import re
import csv
import pandas as pd
from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent


INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "result" / "va" / "bsi"

print(f"BASE_DIR  : {BASE_DIR}")
print(f"INPUT_DIR : {INPUT_DIR}")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
# CHECK INPUT FOLDER
# =========================================================

if not INPUT_DIR.exists():
    INPUT_DIR.mkdir(parents=True)

# =========================================================
# GET FILES
# =========================================================

input_files = list(INPUT_DIR.iterdir())

if not input_files:
    print(input_files)
    print("Tidak ada file pada folder input")
    input("Tekan ENTER untuk keluar...")
    exit()

# =========================================================
# PROCESS FILES
# =========================================================

for input_file in input_files:

    if not input_file.is_file():
        continue

    extension = input_file.suffix.lower()

    print(f"\nProcessing : {input_file.name}")

    # =====================================================
    # XLSX FILE
    # =====================================================

    if extension == ".xlsx":

        try:

            # baca seluruh sheet apa adanya
            df_raw = pd.read_excel(
                input_file,
                header=None,
                dtype=str
            )

            # ambil header dari baris ke-3
            header_row = 2

            header_values = [
                str(x).strip()
                if pd.notna(x)
                else ""
                for x in df_raw.iloc[header_row]
            ]

            try:
                waktu_transaksi_col = header_values.index(
                    "waktu_transaksi"
                )
            except ValueError:
                print("ERROR SKIP - Kolom waktu_transaksi tidak ditemukan pada baris 3")
                continue

            # data pertama setelah header
            first_data_row = header_row + 1

            if first_data_row >= len(df_raw):
                print("ERROR SKIP - Tidak ada data")
                continue

            waktu_transaksi = df_raw.iloc[
                first_data_row,
                waktu_transaksi_col
            ]

            tanggal_file = pd.to_datetime(
                waktu_transaksi
            ).strftime("%Y%m%d")

            output_filename = f"VABSI_{tanggal_file}.csv"
            output_file = OUTPUT_DIR / output_filename

            if output_file.exists():
                print(f"SKIP - {output_filename} sudah ada")
                continue

            # tulis seluruh file persis seperti excel
            with open(
                output_file,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as f:

                writer = csv.writer(f)

                for _, row in df_raw.iterrows():

                    writer.writerow([
                        "" if pd.isna(x) else str(x)
                        for x in row
                    ])

            print(f"SUCCESS -> {output_filename}")

        except Exception as e:
            print(f"ERROR -> {input_file.name}")
            print(str(e))

        continue

    # =====================================================
    # CSV FILE (FORMAT BSI REKON)
    # =====================================================

    if extension == ".csv":

        try:

            # =================================================
            # AMBIL TANGGAL DARI NAMA FILE
            # contoh:
            # rekon_451_1200_20260522_2_rev20260523083341.csv
            # =================================================

            match = re.search(r'_(\d{8})_', input_file.name)

            if not match:
                print("SKIP - Format filename tidak dikenali")
                continue

            tanggal_file = match.group(1)

            output_filename = f"VABSI_{tanggal_file}.csv"
            output_file = OUTPUT_DIR / output_filename

            if output_file.exists():
                print(f"SKIP - {output_filename} sudah ada")
                continue

            # =================================================
            # READ SOURCE FILE
            # =================================================

            df = pd.read_csv(input_file, sep=';')

            # =================================================
            # SORT TERBARU DI ATAS
            # =================================================

            if "wkt_transaksi" in df.columns:
                df = df.sort_values(
                    by="wkt_transaksi",
                    ascending=False
                )

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

            for index, row in enumerate(
                df.itertuples(index=False),
                start=1
            ):

                nomor_invoice = str(row.nomor_invoice)

                nomor_pembayaran = str(row.nomor_pembayaran)

                # tambah prefix 00
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
            # WRITE OUTPUT
            # =================================================

            with open(
                output_file,
                mode="w",
                newline="",
                encoding="utf-8"
            ) as file:

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